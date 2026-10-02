#!/usr/bin/env python3
"""Compare bounded OP menu drawing calls with the attested decoded target.

This checks the native call composition, description color and mask ABI.
It does not compare complete function bytes or promote exactness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_16

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact

TARGET_BODIES = {
    "main_unput_and_put": (0xAAB5, 0x115),
    "option_unput_and_put": (0xABD7, 0x240),
}
TARGET_CALLEES = {"mask": 0xDC92, "colors": 0xE00E, "font": 0xDEB4}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def public(map_text: str, name: str, cpp: bool = False) -> tuple[int, int]:
    suffix = r"\([^\n]*\)" if cpp else ""
    matches = re.findall(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?"
                         + re.escape(name) + suffix + r"\s*$", map_text)
    locations = {(int(segment, 16), int(offset, 16)) for segment, offset in matches}
    if len(locations) != 1:
        raise ValueError(f"public is absent or ambiguous: {name}")
    return locations.pop()


def menu_calls(body: bytes, start: int, size: int, callees: dict[str, int]) -> dict:
    decoder = Cs(CS_ARCH_X86, CS_MODE_16)
    instructions = list(decoder.disasm(body[start:start + size], start))
    calls = []
    colors = []
    returned = False
    for i, instruction in enumerate(instructions):
        if instruction.mnemonic == "ret":
            returned = True
            break
        if instruction.mnemonic != "lcall":
            continue
        data = instruction.bytes
        if len(data) != 5 or data[0] != 0x9A:
            raise ValueError("unexpected far call encoding")
        destination = int.from_bytes(data[1:3], "little") + 16 * int.from_bytes(data[3:5], "little")
        kind = next((kind for kind, address in callees.items() if destination == address), None)
        if kind:
            calls.append(kind)
        if kind == "font":
            # TC4J packs top=384 and color into one operand-size-prefixed PUSH.
            values = [int.from_bytes(insn.bytes[2:6], "little")
                      for insn in instructions[max(0, i - 10):i]
                      if len(insn.bytes) == 6 and insn.bytes[:2] == b"\x66\x68"]
            candidates = [value & 65535 for value in values if value >> 16 == 384]
            if len(candidates) != 1:
                raise ValueError("description color PUSH is absent or ambiguous")
            colors.extend(candidates)
    if not returned:
        raise ValueError("bounded menu body has no near return")
    return dict(drawing_calls=calls, description_colors=colors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-observation-dir", required=True, type=Path)
    parser.add_argument("--link-receipt", required=True, type=Path)
    args = parser.parse_args()
    observation = args.target_observation_dir.resolve()
    link_path = args.link_receipt.resolve()
    if not all(path.is_relative_to(ROOT / ".analysis") for path in (observation, link_path)):
        parser.error("inputs must be private")
    target = find_artifact(load_target_manifest(ROOT / "config/targets.toml"), "th04-op")
    packed = read_verified_artifact(ROOT, target)
    unpack = json.loads((observation / "receipt.json").read_text())
    payload = (observation / "payload.bin").read_bytes()
    if (unpack["artifact"] != "th04-op" or unpack["packed_target_sha256"] != sha(packed)
            or unpack["payload_sha256"] != sha(payload) or unpack["relocation_count"] != 804
            or not all(unpack["checks"].values())):
        raise ValueError("target observation identity/integrity failed")
    link = json.loads(link_path.read_text())
    image = (link_path.parent / "source/bin/op-native.exe").read_bytes()
    mz = parse_mz(image)
    if (link["artifact"] != "th04-op" or not link["link_complete"] or not mz.valid
            or sha(image) != link["mz_header"]["sha256"]):
        raise ValueError("native link identity/integrity failed")
    maps = list((link_path.parent / "source/obj").glob("**/op-native.map"))
    if len(maps) != 1:
        raise ValueError("native OP MAP is not unique")
    map_text = maps[0].read_text()
    callees = {kind: segment * 16 + offset for kind, (segment, offset) in (
        (kind, public(map_text, name)) for kind, name in (
            ("mask", "CDG_PUT_NOCOLORS_8"), ("colors", "CDG_PUT_8"), ("font", "GRAPH_PUTSA_FX")))}
    rows = {}
    for name, (target_start, target_size) in TARGET_BODIES.items():
        segment, offset = public(map_text, name, cpp=True)
        expected = menu_calls(payload, target_start, target_size, TARGET_CALLEES)
        candidate = menu_calls(mz.program_image, segment * 16 + offset, 0x400, callees)
        rows[name] = dict(target=expected, candidate=candidate, equal=expected == candidate,
                          target_cs="0A74", target_offset=target_start - 0xA740,
                          candidate_cs=segment, candidate_offset=offset)
    mask_body = mz.program_image[callees["mask"]:callees["mask"] + 0x52]
    returns = [insn.op_str for insn in Cs(CS_ARCH_X86, CS_MODE_16).disasm(mask_body, 0)
               if insn.mnemonic == "retf"]
    abi = returns == ["6"]
    result = dict(scope="bounded native OP drawing composition; no exactness claim",
                  packed_target_sha256=sha(packed), target_payload_sha256=sha(payload),
                  native_executable_sha256=sha(image), map_sha256=sha(maps[0].read_bytes()),
                  bodies=rows, mask_far_pascal_ret6=abi,
                  passed=abi and all(row["equal"] for row in rows.values()))
    (link_path.parent / "op-menu-calls.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(passed=result["passed"], mask_far_pascal_ret6=abi,
                          bodies={name: row["equal"] for name, row in rows.items()})))
    return int(not result["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
