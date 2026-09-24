#!/usr/bin/env python3
"""Diagnose natural-C++ codegen for OP snd_se_update without granting exactness."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from replay_th04_op_playchar_title_box_put import (  # noqa: E402
    SNAPSHOT, loose_segment_bytes, tcc_op,
)
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
SOURCE = ROOT / "src/op/sound/se_update.cpp"
BODY = ROOT / "src/op/sound/se_update.inl"
DEPENDENCIES = (
    "src/shared/platform/x86.hpp",
    "src/shared/platform/types.hpp",
)
START = 0xE32C
SIZE = 0x4C
TARGET_SHA = "a9e451577270f1d448bd39c71b2c4e69570357b1090111740df0b440931cf5f5"
NATURAL_SIZE = 0x4D
NATURAL_CODE_SHA = "4e317f24d1f54c95e37ce43450bb187bdec40909a30c3898e0ec3e55959106a1"
NATURAL_FIXUPS = [
    (1, 73), (1, 68), (1, 62), (1, 58), (1, 50), (1, 47),
    (3, 41), (1, 26), (1, 22), (1, 16), (1, 9), (1, 2),
]
HELPER_FIXUPS = [
    (1, 72), (1, 67), (1, 61), (1, 57), (1, 51), (1, 47),
    (3, 41), (1, 26), (1, 22), (1, 16), (1, 9), (1, 2),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def code_and_fixups(obj: Path) -> tuple[bytes, list[tuple[int, int]]]:
    code = loose_segment_bytes(obj, "SHARED")
    fixups = [
        item
        for record in parse_omf(obj.read_bytes())
        if record.record_type == 0x9C
        for item in fixup_locations(record.data)
    ]
    return code, fixups


def copy_inputs(work: Path) -> None:
    copy_compact_snapshot(SNAPSHOT, work, "op")
    for rel in ("src/op/sound/se_update.cpp", "src/op/sound/se_update.inl", *DEPENDENCIES):
        dst = work / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)


def compile_one(work: Path, output: Path, label: str) -> tuple[bytes, list[tuple[int, int]]]:
    before = {p.name for p in (work / "obj/th04").glob("*.obj")}
    tcc_op(work, output, label, "src/op/sound/se_update.cpp")
    objects = [p for p in (work / "obj/th04").glob("*.obj") if p.name not in before]
    if len(objects) != 1:
        raise RuntimeError(f"{label}: expected one standalone object")
    return code_and_fixups(objects[0])


def mask(data: bytes, fixups: list[tuple[int, int]]) -> bytes:
    out = bytearray(data)
    for kind, offset in fixups:
        width = 2 if kind == 1 else 4
        out[offset:offset + width] = b"\0" * width
    return bytes(out)


def install_helper_diagnostic(work: Path) -> None:
    src = work / "src/op/sound/se_update.cpp"
    text = src.read_text()
    anchor = 'extern "C" int far pascal bgm_sound(int num);\n'
    helper = '''extern "C" int far pascal bgm_sound(int num);

inline unsigned int target_shape_current_index(void)
{
	_BL = snd_se_playing;
	_BH ^= _BH;
	return _BX;
}
'''
    if text.count(anchor) != 1:
        raise RuntimeError("helper diagnostic source anchor drift")
    src.write_text(text.replace(anchor, helper, 1))

    body = work / "src/op/sound/se_update.inl"
    text = body.read_text()
    old = "(unsigned int)snd_se_playing"
    if text.count(old) != 1:
        raise RuntimeError("helper diagnostic index anchor drift")
    body.write_text(text.replace(old, "target_shape_current_index()", 1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output must be a new direct child of .analysis/reconstruction/probes")
    output.mkdir(parents=True)

    target_mz = parse_mz(TARGET.read_bytes())
    target = target_mz.program_image[START:START + SIZE]
    if len(target) != SIZE or sha(target) != TARGET_SHA:
        raise RuntimeError("OP snd_se_update target identity drift")

    source_hashes = {
        "src/op/sound/se_update.cpp": sha(SOURCE.read_bytes()),
        "src/op/sound/se_update.inl": sha(BODY.read_bytes()),
        **{rel: sha((ROOT / rel).read_bytes()) for rel in DEPENDENCIES},
    }

    naturals: list[dict[str, object]] = []
    natural_codes: list[bytes] = []
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        copy_inputs(work)
        code, fixups = compile_one(work, output, f"natural-{label}")
        if len(code) != NATURAL_SIZE or sha(code) != NATURAL_CODE_SHA or fixups != NATURAL_FIXUPS:
            raise RuntimeError(f"{label}: natural codegen drift")
        natural_codes.append(code)
        naturals.append({
            "label": label,
            "code_size": len(code),
            "code_sha256": sha(code),
            "fixups": [list(x) for x in fixups],
        })
    if natural_codes[0] != natural_codes[1]:
        raise RuntimeError("natural cold codegen differs")

    # After masking relocatable operands, the 77-byte natural output differs
    # only because ordinary byte-array indexing lowers through AL/AH then BX
    # (7 bytes) instead of loading BL and clearing BH directly (6 bytes). That
    # one-byte growth also increments the two earlier forward-branch distances.
    natural_masked = mask(natural_codes[0], NATURAL_FIXUPS)
    target_masked = mask(target, HELPER_FIXUPS)
    expected_natural = bytearray(target_masked)
    expected_natural[6] += 1
    expected_natural[13] += 1
    expected_natural = (
        expected_natural[:49]
        + bytes.fromhex("a0 00 00 b4 00 8b d8")
        + expected_natural[55:]
    )
    isolated_index_lowering = natural_masked == bytes(expected_natural)
    shifted_tail_equal = natural_masked[56:] == target_masked[55:]
    if not isolated_index_lowering or not shifted_tail_equal:
        raise RuntimeError("natural mismatch is no longer isolated to index lowering")

    helper_work = output / "helper-diagnostic/op/source"
    helper_work.parent.mkdir(parents=True)
    copy_inputs(helper_work)
    install_helper_diagnostic(helper_work)
    helper_code, helper_fixups = compile_one(helper_work, output, "helper-diagnostic")
    helper_masked = mask(helper_code, helper_fixups)
    helper_exact = (
        len(helper_code) == SIZE
        and helper_fixups == HELPER_FIXUPS
        and helper_masked == target_masked
    )
    if not helper_exact:
        raise RuntimeError("register-helper diagnostic no longer explains target codegen")

    if {
        "src/op/sound/se_update.cpp": sha(SOURCE.read_bytes()),
        "src/op/sound/se_update.inl": sha(BODY.read_bytes()),
        **{rel: sha((ROOT / rel).read_bytes()) for rel in DEPENDENCIES},
    } != source_hashes:
        raise RuntimeError("maintained natural source changed during probe")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-op",
        "function": "_snd_se_update",
        "payload_offset": hex(START),
        "target_size": SIZE,
        "target_sha256": TARGET_SHA,
        "source_sha256": source_hashes,
        "natural": {
            "rounds": naturals,
            "size_delta": NATURAL_SIZE - SIZE,
            "mismatch_matches_expected_index_lowering": isolated_index_lowering,
            "tail_equal_after_one_byte_index_shift": shifted_tail_equal,
            "mismatch": "TC86 lowers ordinary unsigned-byte array indexing through AL/AH then BX; target loads BL and clears BH directly.",
        },
        "register_helper_diagnostic": {
            "code_size": len(helper_code),
            "code_sha256": sha(helper_code),
            "fixups": [list(x) for x in helper_fixups],
            "masked_target_equal": helper_exact,
            "source_credit": False,
        },
        "limit": (
            "Diagnostic codegen evidence only. The exact helper variant uses explicit "
            "_BL/_BH register shaping from a MODDERS-style candidate helper and grants "
            "no source or decoded-exact credit."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "natural_size": NATURAL_SIZE,
        "target_size": SIZE,
        "helper_diagnostic_exact": helper_exact,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
