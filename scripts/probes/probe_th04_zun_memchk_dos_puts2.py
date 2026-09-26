#!/usr/bin/env python3
"""Prove MEMCHK sub_38E is the maintained shared DOS_PUTS2 source instance."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from replay_th04_zun_dos_puts2 import (
    DOS_PUTS2_BODY_SHA256,
    DOS_PUTS2_LINK_RELEVANT_OMF_SHA256,
    DOS_PUTS2_MODULE_SHA256,
    DOS_PUTS2_BODY_SIZE,
    DOS_PUTS2_MODULE_SIZE,
    LOCAL_DOS_PUTS2,
    dos_puts2_object_code,
    link_relevant_omf_sha,
)
from replay_th04_zun_source_only import (
    PAYLOAD,
    PAYLOAD_SHA256,
    RUNNER,
    sha,
)

MEMCHK_BODY_OFFSET = 0x26CE
MEMCHK_PAD_OFFSET = 0x26F5
RESIDENT_BODY_OFFSET = 0x1344
RESIDENT_PAD_OFFSET = 0x136B
TARGET_MODULE_SHA256 = "c346fe75402242d9b1348e634244efb9e94ba1b8dc637602d8767f0c6c5fb3d9"


def assemble(label: str, output: Path) -> dict[str, object]:
    saved = output / label
    saved.mkdir()
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    with tempfile.TemporaryDirectory(prefix=f"zun-memchk-puts-{label}-", dir=output) as td:
        work = Path(td)
        source = work / "DOSPUTS2.ASM"
        shutil.copyfile(LOCAL_DOS_PUTS2, source)
        os.utime(source, (946684800, 946684800))
        command = [
            "wine", r"C:\TASM50\bin\TASM32.EXE",
            "/m", "/mx", "/kh32768",
            "DOSPUTS2.ASM,DOSPUTS2.OBJ,DOSPUTS2.LST",
        ]
        done = subprocess.run(
            command, cwd=work, env=env, capture_output=True, text=True, timeout=120,
        )
        (saved / "assemble.log").write_text(
            json.dumps(command) + f"\nexit={done.returncode}\n"
            + done.stdout + done.stderr,
            encoding="utf-8",
        )
        obj = work / "DOSPUTS2.OBJ"
        listing = work / "DOSPUTS2.LST"
        if done.returncode or not obj.is_file() or not listing.is_file():
            raise RuntimeError(f"{label}: TASM32 DOS_PUTS2 assembly failed")
        shutil.copyfile(obj, saved / "dosputs2.obj")
        shutil.copyfile(listing, saved / "dosputs2.lst")
        code = dos_puts2_object_code(saved / "dosputs2.obj")
        (saved / "dosputs2.code").write_bytes(code)
        if len(code) != DOS_PUTS2_MODULE_SIZE or sha(code) != DOS_PUTS2_MODULE_SHA256:
            raise RuntimeError(f"{label}: maintained DOS_PUTS2 module CODE drift")
        if sha(code[:DOS_PUTS2_BODY_SIZE]) != DOS_PUTS2_BODY_SHA256:
            raise RuntimeError(f"{label}: maintained DOS_PUTS2 body drift")
        if code[-1:] != b"\x90":
            raise RuntimeError(f"{label}: maintained DOS_PUTS2 EVEN padding drift")
        if link_relevant_omf_sha(saved / "dosputs2.obj") != DOS_PUTS2_LINK_RELEVANT_OMF_SHA256:
            raise RuntimeError(f"{label}: maintained DOS_PUTS2 link-relevant OMF drift")
        return {
            "object_sha256": sha((saved / "dosputs2.obj").read_bytes()),
            "link_relevant_omf_sha256": link_relevant_omf_sha(saved / "dosputs2.obj"),
            "module_code_size": len(code),
            "module_code_sha256": sha(code),
            "body_sha256": sha(code[:DOS_PUTS2_BODY_SIZE]),
            "padding_byte": code[-1],
            "listing_sha256": sha((saved / "dosputs2.lst").read_bytes()),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/attest_toolchain.py"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )

    payload = PAYLOAD.read_bytes()
    if sha(payload) != PAYLOAD_SHA256:
        raise RuntimeError("decoded ZUN payload identity drift")

    memchk_module = payload[MEMCHK_BODY_OFFSET:MEMCHK_BODY_OFFSET + DOS_PUTS2_MODULE_SIZE]
    resident_module = payload[RESIDENT_BODY_OFFSET:RESIDENT_BODY_OFFSET + DOS_PUTS2_MODULE_SIZE]
    memchk_body = memchk_module[:DOS_PUTS2_BODY_SIZE]
    resident_body = resident_module[:DOS_PUTS2_BODY_SIZE]

    if sha(memchk_body) != DOS_PUTS2_BODY_SHA256:
        raise RuntimeError("MEMCHK sub_38E body identity drift")
    if sha(resident_body) != DOS_PUTS2_BODY_SHA256:
        raise RuntimeError("resident DOS_PUTS2 body identity drift")
    if memchk_module != resident_module:
        raise RuntimeError("MEMCHK and resident DOS_PUTS2 module instances differ")
    if sha(memchk_module) != TARGET_MODULE_SHA256 or memchk_module[-1:] != b"\x90":
        raise RuntimeError("target DOS_PUTS2 body+pad module identity drift")

    output.mkdir()
    a = assemble("a", output)
    b = assemble("b", output)
    stable_keys = (
        "link_relevant_omf_sha256", "module_code_size", "module_code_sha256",
        "body_sha256", "padding_byte",
    )
    if any(a[key] != b[key] for key in stable_keys):
        raise RuntimeError("independent DOS_PUTS2 assembly rounds differ")

    local_code = (output / "a/dosputs2.code").read_bytes()
    if local_code != memchk_module or local_code != resident_module:
        raise RuntimeError("maintained DOS_PUTS2 module is not target-instance exact")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 ZUN MEMCHK sub_38E source ownership via maintained shared DOS_PUTS2",
        "artifact": "th04-zun",
        "target_payload_sha256": PAYLOAD_SHA256,
        "maintained_source": "src/shared/dos/dos_puts2.asm",
        "maintained_source_sha256": sha(LOCAL_DOS_PUTS2.read_bytes()),
        "memchk_instance": {
            "body_extent": "payload 0x26CE..0x26F4",
            "body_size": DOS_PUTS2_BODY_SIZE,
            "body_sha256": sha(memchk_body),
            "padding_offset": hex(MEMCHK_PAD_OFFSET),
            "padding_byte": memchk_module[-1],
            "body_plus_padding_sha256": sha(memchk_module),
        },
        "resident_instance": {
            "body_extent": "payload 0x1344..0x136A",
            "body_size": DOS_PUTS2_BODY_SIZE,
            "body_sha256": sha(resident_body),
            "padding_offset": hex(RESIDENT_PAD_OFFSET),
            "padding_byte": resident_module[-1],
            "body_plus_padding_sha256": sha(resident_module),
        },
        "cross_instance_raw_equal": memchk_module == resident_module,
        "builds": {"a": a, "b": b},
        "result": "maintained-source-body-and-padding-exact",
        "source_credit": "shared-library-source",
        "limit": (
            "This proves source ownership only for MEMCHK sub_38E and its compiler/assembler "
            "alignment byte. The surrounding MEMCHK _main and sub_3B6 target-derived assembly "
            "remain uncredited scaffold and are not accepted by this receipt."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "memchk_body_sha256": sha(memchk_body),
        "module_sha256": sha(memchk_module),
        "source_sha256": sha(LOCAL_DOS_PUTS2.read_bytes()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
