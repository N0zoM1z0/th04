#!/usr/bin/env python3
"""Relink the three DOS executables with moved code and DGROUP contributions."""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import defaultdict
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import NamedTuple

from lib.omf import parse_omf
from lib.pc98 import MZImage, parse_mz
from shared_runtime import command as runtime_command

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = (ROOT / ".analysis").resolve()
PROBES = ROOT / "scripts/probes"
sys.path.insert(0, str(PROBES))

from replay_th04_zun_selector import (  # noqa: E402
    RUNNER, RUNNER_SHA256, TASM, TASM_SHA256, TLINK, TLINK_SHA256,
)

EXES = {"main": "MAIN.EXE", "op": "OP.EXE", "maine": "MAINE.EXE"}
MAP_ROW = re.compile(
    r"\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+"
    r"C=(\S+)\s+S=(\S+)\s+G=(\S+)\s+M=(\S+)\s+ACBP=([0-9A-F]{2})"
)
ALIGNMENTS = {1: "byte", 2: "word", 3: "para", 4: "page", 5: "dword"}


class Contribution(NamedTuple):
    frame: int
    offset: int
    size: int
    kind: str
    name: str
    group: str
    module: str
    acbp: int

    @property
    def start(self) -> int:
        return self.frame * 16 + self.offset

    @property
    def owner(self) -> tuple[str, str, str, str]:
        return self.kind, self.name, self.group.lower(), self.module


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def map_rows(path: Path) -> list[Contribution]:
    rows = []
    for line in path.read_text(encoding="cp437").splitlines():
        match = MAP_ROW.fullmatch(line.rstrip())
        if match:
            frame, offset, size, kind, name, group, module, acbp = match.groups()
            rows.append(Contribution(int(frame, 16), int(offset, 16), int(size, 16),
                                     kind, name, group, module, int(acbp, 16)))
    if not rows:
        raise ValueError(f"no detailed TLINK contributions in {path}")
    return rows


def run(work: Path, log: str, *args: str) -> None:
    env = dict(os.environ, WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    command = runtime_command("wine", *args)
    process = subprocess.run(command, cwd=work, env=env, capture_output=True, timeout=120)
    path = work / log
    path.write_bytes(json.dumps(command).encode() + b"\n" + process.stdout + process.stderr)
    if process.returncode or re.search(rb"(?m)^(?:Error|Fatal):", process.stdout + process.stderr):
        raise ValueError(f"tool failed with status {process.returncode}, see {path}")


def omf_module(data: bytes) -> str:
    name = parse_omf(data)[0].data
    return name[1:1 + name[0]].decode("cp437").lower()


def pad_objects(rows: list[Contribution], modules: list[str], work: Path,
                padding: dict[str, int]) -> dict[int, str]:
    """Insert padding after an existing definition, keeping segment discovery order."""
    definitions = defaultdict(list)
    for row in rows:
        if row.kind == "CODE" or (row.kind in {"DATA", "BSS"} and row.group.upper() == "DGROUP"):
            definitions[row.kind, row.name].append(row)
    contents = defaultdict(list)
    for (kind, name), definitions_in_map in definitions.items():
        if not any(row.size for row in definitions_in_map):
            continue
        known = [(modules.index(row.module.lower()), row.acbp)
                 for row in definitions_in_map if row.module.lower() in modules]
        if not known:
            continue
        index, acbp = min(known)
        if (acbp >> 2) & 7 != 2 or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            continue
        alignment = ALIGNMENTS[acbp >> 5]
        fill = {"CODE": "90h", "DATA": "0", "BSS": "?"}[kind]
        contents[index].extend([
            f"{name} segment {alignment} public '{kind}' use16",
            f"    db {padding[kind]} dup({fill})",
            f"{name} ends",
        ])
    if not contents:
        raise ValueError("no eligible CODE or DGROUP segments for padding")
    objects = {}
    for index, lines in sorted(contents.items()):
        stem = f"pi{index:05d}"
        source, obj = stem + ".asm", stem + ".obj"
        (work / source).write_text("\n".join([".386", *lines, "end", ""]), encoding="ascii")
        run(work, stem + ".log", str(TASM), "/m", "/mx", "/kh32768", f"{source},{obj}")
        parse_omf((work / obj).read_bytes())
        objects[index] = obj
    return objects


def direct_offsets(before: bytes, after: bytes,
                   pairs: list[tuple[Contribution, Contribution]]) -> dict:
    """Screen direct CS/DS displacements for review after moving their MAP owners."""
    from capstone import Cs, CS_ARCH_X86, CS_MODE_16
    from capstone.x86_const import X86_OP_MEM, X86_REG_CS, X86_REG_DS, X86_REG_INVALID

    dgroup = next((old.frame, new.frame) for old, new in pairs if old.group.upper() == "DGROUP")
    starts = [old.start for old, _ in pairs]
    decoder = Cs(CS_ARCH_X86, CS_MODE_16)
    decoder.detail = True
    decoder.skipdata = True
    candidates = []
    screened = moved = 0
    for old, new in pairs:
        if old.kind != "CODE":
            continue
        for instruction in decoder.disasm(before[old.start:old.start + old.size], old.offset):
            if not instruction.id or instruction.disp_size != 2:
                continue
            for operand in instruction.operands:
                if operand.type != X86_OP_MEM or operand.mem.base or operand.mem.index:
                    continue
                segment = operand.mem.segment
                if segment not in (X86_REG_CS, X86_REG_DS, X86_REG_INVALID):
                    continue
                cs = segment == X86_REG_CS
                old_base, new_base = (old.frame, new.frame) if cs else dgroup
                offset = operand.mem.disp & 0xFFFF
                target = old_base * 16 + offset
                index = bisect_right(starts, target) - 1
                if index < 0:
                    continue
                old_target, new_target = pairs[index]
                if target >= old_target.start + old_target.size:
                    continue
                if cs and old_target.kind != "CODE":
                    continue
                if not cs and old_target.group.upper() != "DGROUP":
                    continue
                expected = (new_target.start + target - old_target.start - new_base * 16) & 0xFFFF
                at = new.start + instruction.address - old.offset + instruction.disp_offset
                actual = int.from_bytes(after[at:at + 2], "little")
                screened += 1
                if actual != expected:
                    candidates.append({
                        "address": f"{old.frame:04X}:{instruction.address:04X}",
                        "module": old.module, "operand": f"{instruction.mnemonic} {instruction.op_str}",
                        "target_module": old_target.module, "baseline": offset,
                        "shifted": actual, "expected": expected,
                    })
                elif actual != offset:
                    moved += 1
    return {"screened": screened, "moved": moved, "candidates": candidates}


def compare_layout(original: MZImage, shifted: MZImage, old_rows: list[Contribution],
                   new_rows: list[Contribution], synthetic: set[str]) -> tuple[dict, dict]:
    if not original.valid or not shifted.valid:
        raise ValueError("invalid MZ")
    new_by_owner = defaultdict(list)
    for row in new_rows:
        if row.size and row.module.lower() not in synthetic:
            new_by_owner[row.owner].append(row)
    moved = defaultdict(int)
    target_frames = defaultdict(set)
    pairs = []
    for old in old_rows:
        if old.size == 0:
            continue
        if not new_by_owner[old.owner]:
            raise ValueError(f"lost MAP contribution {old.owner}")
        new = new_by_owner[old.owner].pop(0)
        if old.size != new.size:
            raise ValueError(f"size changed for {old.owner}")
        pairs.append((old, new))
        target_frames[old.frame].add(new.frame)
        if old.offset != new.offset:
            moved[old.kind] += 1
    if any(new_by_owner.values()):
        raise ValueError("unexpected extra MAP contributions")
    if any(moved[kind] == 0 for kind in ("CODE", "DATA", "BSS")):
        raise ValueError(f"CODE, DATA, and BSS must all move within their frames: {dict(moved)}")
    # A public segment can have a paragraph frame of its own even when TLINK
    # reports its detailed contributions relative to a wider group.
    sections = []
    for rows in (old_rows, new_rows):
        section_starts = {}
        for row in sorted(rows, key=lambda row: row.start):
            section_starts.setdefault((row.kind, row.name), row.start)
        sections.append(section_starts)
    for section, old_start in sections[0].items():
        if section in sections[1]:
            target_frames[old_start >> 4].add(sections[1][section] >> 4)
    pairs.sort(key=lambda pair: pair[0].start)
    old_starts = [old.start for old, _ in pairs]
    expected = []
    old_image, new_image = original.program_image, shifted.program_image
    unmapped_frames = set()
    far_transfers = 0
    for relocation in original.relocations:
        site = relocation.linear
        index = bisect_right(old_starts, site) - 1
        if index < 0:
            raise ValueError(f"unowned baseline relocation at {site:#x}")
        old, new = pairs[index]
        if site + 2 > old.start + old.size:
            raise ValueError(f"unowned baseline relocation at {site:#x}")
        new_site = new.start + site - old.start
        expected.append(new_site)
        old_frame = int.from_bytes(old_image[site:site + 2], "little")
        new_frame = int.from_bytes(new_image[new_site:new_site + 2], "little")
        if new_frame not in target_frames[old_frame]:
            unmapped_frames.add((old_frame, new_frame))
        # Immediate far CALL/JMP has its offset directly before the MZ segment
        # relocation. Compare the full destination when it resolves to code.
        if old.kind != "CODE" or site - 3 < old.start or old_image[site - 3] not in (0x9A, 0xEA):
            continue
        old_destination = old_frame * 16 + int.from_bytes(old_image[site - 2:site], "little")
        destination_index = bisect_right(old_starts, old_destination) - 1
        if destination_index < 0:
            continue
        old_target, new_target = pairs[destination_index]
        if old_target.kind != "CODE" or old_destination >= old_target.start + old_target.size:
            continue
        new_destination = new_frame * 16 + int.from_bytes(new_image[new_site - 2:new_site], "little")
        if (old_image[site - 3] != new_image[new_site - 3]
                or new_destination != new_target.start + old_destination - old_target.start):
            raise ValueError(f"far transfer at load offset {site - 3:#x} lost its code target")
        far_transfers += 1
    actual = [entry.linear for entry in shifted.relocations]
    ordered_sites = sorted(actual)
    if any(site + 2 > len(new_image) for site in actual) or any(
        right < left + 2 for left, right in zip(ordered_sites, ordered_sites[1:])
    ):
        raise ValueError("invalid shifted MZ relocation sites")
    if sorted(expected) != ordered_sites:
        raise ValueError("MZ relocations no longer cover the same bytes within their owners")
    if unmapped_frames:
        values = ", ".join(f"{old:04X}->{new:04X}" for old, new in sorted(unmapped_frames))
        raise ValueError(f"MZ relocation frame pairs lack MAP ownership: {values}")
    direct = direct_offsets(old_image, new_image, pairs)
    layout = {"moved_offsets_by_class": dict(moved),
              "checked_contributions": len(pairs), "relocations": len(actual),
              "ordered_owner_sites_identical": expected == actual,
              "relocated_far_transfers": far_transfers,
              "direct_offsets_screened": direct["screened"], "direct_offsets_moved": direct["moved"],
              "direct_offsets_for_review": len(direct["candidates"])}
    return layout, direct


def relink(artifact: str, baseline: Path, product: dict, output: Path,
           padding: dict[str, int]) -> tuple[dict, dict]:
    source_receipt = Path(product["build_receipt"]).resolve()
    if not source_receipt.is_relative_to(PRIVATE / "reconstruction/probes"):
        raise ValueError("expected a private product link receipt")
    receipt = json.loads(source_receipt.read_bytes())
    if receipt["artifact"] != f"th04-{artifact}":
        raise ValueError("product link receipt artifact drift")
    relative = Path("obj/main-native.@l" if artifact == "main" else f"obj/product/{artifact}.@l")
    original_work = source_receipt.parent / "source"
    response_bytes = (original_work / relative).read_bytes()
    link_info = receipt["link"] if artifact == "main" else receipt
    if sha(response_bytes) != link_info["response_sha256"]:
        raise ValueError("baseline response identity drift")
    objects_text, files_text = response_bytes.decode("ascii").strip().split(",", 1)
    args = objects_text.split()
    if args[:4] != ["-c", "-s", "-E", "c0l.obj"]:
        raise ValueError("unexpected source-only TLINK response")
    files = [item.strip() for item in files_text.split(",")]
    if len(files) != 3 or files[2] != "emu.lib mathl.lib cl.lib":
        raise ValueError("unexpected source-only TLINK outputs or libraries")
    exe_rel, map_rel = (Path(value.replace("\\", "/")) for value in files[:2])
    if exe_rel != Path(f"bin/{artifact}-native.exe") or map_rel.parent != relative.parent:
        raise ValueError("unexpected baseline build paths")
    original_data = (baseline / EXES[artifact]).read_bytes()
    if len(original_data) != product["size"] or sha(original_data) != product["sha256"]:
        raise ValueError("published baseline EXE identity drift")
    if (original_work / exe_rel).read_bytes() != original_data:
        raise ValueError("published baseline differs from the recorded link")
    if artifact == "main":
        object_rows = (row for key in ("root_records", "state_records", "asm_records", "sprite_sources")
                       for row in receipt[key])
    else:
        object_rows = iter(receipt["objects"])
    hashes = {row["object"] if "object" in row else row["objects"][0]:
              row["object_sha256"] for row in object_rows}
    object_names = [name.replace("\\", "/") for name in args[4:]]
    if len(set(object_names)) != len(object_names) or set(hashes) != set(object_names):
        raise ValueError("response and receipt object inventories differ")
    work = output / artifact / "source"
    (work / "bin").mkdir(parents=True)
    (work / relative.parent).mkdir(parents=True, exist_ok=True)
    startup = TLINK.parents[1] / "LIB/C0L.OBJ"
    modules = [omf_module(startup.read_bytes())]
    for name in object_names:
        path = Path(name)
        if not path.is_relative_to("obj") or ".." in path.parts:
            raise ValueError(f"unexpected object path {name}")
        data = (original_work / path).read_bytes()
        if sha(data) != hashes[name]:
            raise ValueError(f"baseline object identity drift: {name}")
        modules.append(omf_module(data))
        destination = work / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    (work / relative).write_bytes(response_bytes)
    linker_args = str(RUNNER), "-e", "-x", "tlink", "@" + str(relative).replace("/", "\\")
    run(work, "control-link.log", *linker_args)
    if (work / exe_rel).read_bytes() != original_data:
        raise ValueError("unshifted relink failed the whole-file zero-difference control")
    old_map = work / map_rel
    if old_map.read_bytes() != (original_work / map_rel).read_bytes():
        raise ValueError("unshifted relink changed the complete MAP")
    old_rows = map_rows(old_map)
    pads = pad_objects(old_rows, modules, work, padding)
    shifted_objects = []
    for index, name in enumerate(args[3:]):
        shifted_objects.append(name)
        if index in pads:
            shifted_objects.append(pads[index])
    response = " ".join([*args[:3], *shifted_objects]) + "," + files_text + "\n"
    (work / relative).write_text(response, encoding="ascii")
    run(work, "shifted-link.log", *linker_args)
    data = (work / exe_rel).read_bytes()
    linked = parse_mz(data)
    layout, direct = compare_layout(
        parse_mz(original_data), linked, old_rows, map_rows(work / map_rel),
        {Path(name).with_suffix(".asm").name for name in pads.values()},
    )
    direct_report = json.dumps(direct, indent=2).encode() + b"\n"
    (work.parent / "direct-offset-review.json").write_bytes(direct_report)
    mz = {"sha256": sha(data), "relocations": len(linked.relocations), "valid": linked.valid}
    diagnostic_receipt = {
        "artifact": f"th04-{artifact}", "scope": "DOS position independence layout perturbation",
        "link_complete": True,
        "link": {"exit": 0, "errors": [], "map": map_rel.as_posix(),
                 "map_sha256": sha((work / map_rel).read_bytes()), "mz": mz},
        "support_lib_sha256": None, "mz_header": mz,
        "baseline_receipt_sha256": sha(source_receipt.read_bytes()),
        "baseline_sha256": sha(original_data),
        "baseline_response_sha256": sha(response_bytes),
        "shifted_response_sha256": sha(response.encode("ascii")),
        "padding_bytes": padding,
        "padding_objects": {name: sha((work / name).read_bytes()) for name in pads.values()},
        "direct_offset_review_sha256": sha(direct_report),
        "unshifted_control_byte_identical": True, **layout,
    }
    if artifact == "main":
        diagnostic_receipt["root_records"] = receipt["root_records"]
    result_receipt = work.parent / "receipt.json"
    result_receipt.write_text(json.dumps(diagnostic_receipt, indent=2) + "\n", encoding="ascii")
    audits = ["audit_th04_native_irq_vectors.py"]
    if artifact == "main":
        audits.append("audit_th04_native_bullet_switches.py")
    for script in audits:
        subprocess.run([sys.executable, str(PROBES / script), "--link-receipt", str(result_receipt)],
                       cwd=ROOT, check=True)
    shutil.copyfile(work / exe_rel, output / EXES[artifact])
    return {"file": EXES[artifact], "size": len(data), "sha256": sha(data),
            "build_receipt": str(result_receipt)}, layout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--only", nargs="+", choices=EXES, default=list(EXES))
    parser.add_argument("--padding", type=int, nargs=3, default=(16, 32, 48),
                        metavar=("CODE", "DATA", "BSS"), help="bytes to insert per eligible segment")
    args = parser.parse_args()
    if any(size <= 0 for size in args.padding):
        parser.error("padding sizes must be positive")
    padding = dict(zip(("CODE", "DATA", "BSS"), args.padding, strict=True))
    baseline, output = args.baseline.resolve(), args.output_dir.resolve()
    if (not baseline.is_relative_to(PRIVATE) or not output.is_relative_to(PRIVATE)
            or output.exists() or baseline == output):
        parser.error("use private inputs and a fresh output directory")
    manifest = json.loads((baseline / "build.json").read_bytes())
    if manifest["variant"] != "normal":
        parser.error("the replay requires an ordinary DOS product build")
    for path, digest in ((TASM, TASM_SHA256), (TLINK, TLINK_SHA256), (RUNNER, RUNNER_SHA256)):
        if sha(path.read_bytes()) != digest:
            raise ValueError(f"tool identity drift: {path.name}")
    products, layouts = {}, {}
    with (PRIVATE / "native-build.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        output.mkdir(parents=True)
        for artifact in dict.fromkeys(args.only):
            products[artifact], layouts[artifact] = relink(
                artifact, baseline, manifest["products"][artifact], output, padding
            )
    if "zun" in manifest["products"]:
        zun = manifest["products"]["zun"]
        data = (baseline / "ZUN.COM").read_bytes()
        if sha(data) != zun["sha256"] or len(data) != zun["size"]:
            raise ValueError("runtime ZUN.COM support identity drift")
        (output / "ZUN.COM").write_bytes(data)
        products["zun"] = zun
    (output / "build.json").write_text(json.dumps(
        {"variant": "normal", "run_id": output.name, "products": products,
         "acceptance": "private DOS position independence layout diagnostic"}, indent=2) + "\n")
    print(json.dumps(layouts, indent=2))


if __name__ == "__main__":
    main()
