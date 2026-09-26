#!/usr/bin/env python3
"""Check ZUNINIT's 18-byte character converter against independent codecs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import unicorn
from unicorn import UC_ARCH_X86, UC_MODE_16, Uc
from unicorn.x86_const import UC_X86_REG_AX, UC_X86_REG_EFLAGS


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/probes"))
from replay_th04_zun_source_only import PAYLOAD, PAYLOAD_SHA256  # noqa: E402

PAYLOAD_START = 0x7B0
BODY_SIZE = 0x12
BODY_SHA256 = "044ce9480a0506ffac42aeaf78844e0266262c10ffd075d2c861a7a78689adf8"
CODE_ADDRESS = 0x1000


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reference_jis(pair: bytes, codec: str) -> int | None:
    try:
        character = pair.decode(codec)
        encoded = character.encode("euc_jp")
    except UnicodeError:
        return None
    if len(encoded) != 2 or not all(0xA1 <= byte <= 0xFE for byte in encoded):
        return None
    return ((encoded[0] - 0x80) << 8) | (encoded[1] - 0x80)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    preflight = subprocess.run(
        [sys.executable, "scripts/preflight.py"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    payload = PAYLOAD.read_bytes()
    if sha(payload) != PAYLOAD_SHA256:
        raise RuntimeError("decoded ZUN payload identity drift")
    body = payload[PAYLOAD_START:PAYLOAD_START + BODY_SIZE]
    if len(body) != BODY_SIZE or sha(body) != BODY_SHA256 or body[-1] != 0xC3:
        raise RuntimeError("ZUNINIT converter extent/identity drift")

    emulator = Uc(UC_ARCH_X86, UC_MODE_16)
    emulator.mem_map(CODE_ADDRESS, 0x1000)
    emulator.mem_write(CODE_ADDRESS, body)
    strict_count = 0
    strict_mismatches = []
    strict_outputs = hashlib.sha256()
    cp932_count = 0
    cp932_mismatches = []
    for lead in (*range(0x81, 0xA0), *range(0xE0, 0xFD)):
        for trail in (*range(0x40, 0x7F), *range(0x80, 0xFD)):
            pair = bytes((lead, trail))
            strict = reference_jis(pair, "shift_jis")
            cp932 = reference_jis(pair, "cp932")
            if strict is None and cp932 is None:
                continue
            # The caller passes the lead in AH and trail in AL. EFLAGS=2 is a
            # defined starting state; the target overwrites arithmetic flags.
            emulator.reg_write(UC_X86_REG_AX, (lead << 8) | trail)
            emulator.reg_write(UC_X86_REG_EFLAGS, 2)
            emulator.emu_start(CODE_ADDRESS, CODE_ADDRESS + BODY_SIZE - 1)
            actual = emulator.reg_read(UC_X86_REG_AX)
            if strict is not None:
                strict_count += 1
                strict_outputs.update(pair + actual.to_bytes(2, "big"))
                if actual != strict:
                    strict_mismatches.append([pair.hex(), f"{actual:04x}", f"{strict:04x}"])
            if cp932 is not None:
                cp932_count += 1
                if actual != cp932:
                    cp932_mismatches.append([pair.hex(), f"{actual:04x}", f"{cp932:04x}"])

    if strict_count != 6879 or strict_mismatches:
        raise RuntimeError(f"strict Shift-JIS to JIS claim rejected: {strict_count}, {strict_mismatches[:8]}")
    if cp932_count != 6883 or len(cp932_mismatches) != 10:
        raise RuntimeError("CP932 extension control changed")

    unicorn_binary = Path(unicorn.__file__).parent / "lib/libunicorn.so"
    if not unicorn_binary.is_file():
        raise RuntimeError("Unicorn binary path is unavailable")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim": "ZUNINIT runtime 0x1BD converts standard two-byte Shift-JIS to JIS X 0208 row/cell",
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_extent": "th04-zun/com-payload/0x7B0+0x12",
        "target_slice_sha256": BODY_SHA256,
        "probe_source_sha256": sha(Path(__file__).read_bytes()),
        "emulator": {
            "name": "Unicorn x86 16-bit",
            "version": unicorn.__version__,
            "binary_path": str(unicorn_binary),
            "binary_sha256": sha(unicorn_binary.read_bytes()),
            "start_ax": "lead byte in AH, trail byte in AL",
            "start_eflags": "0x2",
            "stop": "before target RET at runtime COM offset 0x1CE",
        },
        "reference": {
            "python": sys.version.split()[0],
            "method": "strict shift_jis decode, euc_jp encode, subtract 0x80 from both EUC bytes",
            "strict_compared": strict_count,
            "strict_equal": strict_count - len(strict_mismatches),
            "strict_outputs_sha256": strict_outputs.hexdigest(),
            "strict_mismatches": strict_mismatches,
            "cp932_compared": cp932_count,
            "cp932_mismatch_count": len(cp932_mismatches),
            "cp932_mismatch_examples": cp932_mismatches[:10],
        },
        "preflight_stdout_sha256": sha(preflight.stdout.encode()),
        "limit": "Semantic cross-check only; no original source, linked component, or exact byte acceptance follows.",
    }
    output.mkdir()
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"strict": strict_count, "equal": strict_count, "cp932_extensions": len(cp932_mismatches)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
