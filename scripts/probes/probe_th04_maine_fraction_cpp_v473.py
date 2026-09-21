#!/usr/bin/env python3
"""Recover TH04 MAINE graph_fraction_of_million_put() as natural TC86 C++.

Starts from retained v401 source, rebuilds the accepted v472 verdict frontier,
then replaces only the first 0x77 bytes of the remaining MAINE_01 tail with a
TC86 C++ owner.  No executable, OMF, or relocation bytes are patched.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from inspect_dialog_fixup_order import code_ledata  # noqa: E402
from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_master_relocation_order import BASE as V401_BASE  # noqa: E402
from probe_th04_maine_score_producers_v468 import (  # noqa: E402
    RUNNER,
    RUNNER_SHA,
    TARGET_RESTORED_SHA,
    digest,
    run_checked,
)
from probe_th04_maine_segment_topology_v470 import (  # noqa: E402
    PROGRAM_SHA,
    output_dir,
    tasm,
    tcc,
)
from probe_th04_maine_skill_cpp_v472 import (  # noqa: E402
    FINAL_EXE as V472_EXE,
    FINAL_MAP as V472_MAP,
    EXPECTED_MISMATCHES as V472_MISMATCHES,
    prepare_v471,
    split_skill_owner,
)
from probe_th04_master_object_split import compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_fraction_v473.cpp.in"
TEMPLATE_SHA = "de15329696cf375ebc370b70f1d0f7b67c5d7ebee1dde4786ea0e7dca9c52a03"
FINAL_EXE = V472_EXE
FINAL_MAP = "5edcd404826e00950979ba8194a09b01e75544ce84cd3145fd41cddedd596409"
FRACTION_LOAD = 0x192B
FRACTION_SIZE = 0x0077
FRACTION_RAW_SHA = "c375f560be88e44c832501be3d83fc628ebc71a86badcf1a1e933185292610b4"
FRACTION_LINKED_SHA = "fc3bf1fc7fb56d0130390936ea4562bdc324920a60fec5b2336a9e5a855a4260"
TAIL_SIZE = 0x0757
FRACTION_FIXUPS = [
    (3, 0x6D), (1, 0x6A), (1, 0x5E),
    (1, 0x5A), (1, 0x4E), (1, 0x23),
]


def segment_bytes(path: Path, segment: str) -> bytes:
    records = parse_omf(path.read_bytes())
    groups = code_ledata(records, segment)
    if not groups:
        return b""
    end = max(row[1] for row in groups)
    out = bytearray(end)
    for start, stop, recno, _ in groups:
        out[start:stop] = records[recno - 1].data[3:]
    return bytes(out)


def prepare_v472(work: Path, output: Path, label: str) -> None:
    prepare_v471(work, output, label)
    baseline = parse_mz((work / "bin/th04/maine.exe").read_bytes())
    baseline_sites = [row.linear for row in baseline.relocations]

    split_skill_owner(work)
    tasm(work, output, f"v472-mid-{label}", "th04_maine_01_mid_v472.asm", "m1mid.obj")
    tasm(work, output, f"v472-tail-{label}", "th04_maine_01_tail_v472.asm", "m1tail.obj")
    tasm(work, output, f"v472-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")
    tcc(work, output, f"v472-skill-{label}", "th04/sk.cpp")

    rsp = work / "obj/th04/maine.@l"
    text = rsp.read_text()
    old = r"obj\th04\m1post.obj"
    new = r"obj\th04\m1mid.obj obj\th04\sk.obj obj\th04\m1tail.obj"
    if text.count(old) != 1:
        raise ValueError(f"{label}: v471 post response token drift")
    rsp.write_text(text.replace(old, new, 1))

    exe = work / "bin/th04/maine.exe"
    map_path = work / "obj/th04/maine.map"
    exe.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
        work,
        output / f"v472-link-{label}.log",
    )
    if sha(exe) != V472_EXE or sha(map_path) != V472_MAP:
        raise ValueError(f"{label}: v472 baseline identity drift")
    image = parse_mz(exe.read_bytes())
    if digest(image.program_image) != PROGRAM_SHA:
        raise ValueError(f"{label}: v472 program-image identity drift")
    if [row.linear for row in image.relocations] != baseline_sites:
        # v471 -> v472 intentionally changes 254..255, so compare count/order
        # against the actual v472 object after relink, not the v471 list.
        pass


def split_fraction_owner(work: Path) -> None:
    source = work / "th04_maine_01_tail_v472.asm"
    text = source.read_bytes().decode("cp932")
    seg = "maine_01_TEXT segment byte public 'CODE' use16"
    positions: list[int] = []
    off = 0
    while True:
        pos = text.find(seg, off)
        if pos < 0:
            break
        positions.append(pos)
        off = pos + 1
    if len(positions) != 2:
        raise ValueError(f"tail segment occurrence drift: {positions}")
    real = positions[1]
    end_marker = "maine_01_TEXT ends"
    seg_end = text.index(end_marker, real)
    common = text[:real]
    body = text[real + len(seg):seg_end]
    start = body.index("public @GRAPH_FRACTION_OF_MILLION_PUT$QIIUL")
    end = body.index("@graph_fraction_of_million_put$qiiul\tendp", start)
    end += len("@graph_fraction_of_million_put$qiiul\tendp")
    if " proc " in body[:start] or "\tproc " in body[:start]:
        raise ValueError("fraction is no longer the first real tail function")
    tail_body = body[end:]

    assume = (
        "\r\n\t\tassume cs:group_01\r\n"
        "\t\tassume es:nothing, ss:nothing, ds:_DATA, fs:nothing, gs:nothing\r\n"
    )
    tail = common + seg + assume + tail_body + end_marker + "\r\n\tend\r\n"
    text_end = tail.index("_TEXT ends\r\n") + len("_TEXT ends\r\n")
    tail = (
        tail[:text_end]
        + "\r\n\textern @GRAPH_FRACTION_OF_MILLION_PUT$QIIUL:near\r\n"
        + tail[text_end:]
    )
    (work / "th04_maine_01_tail_v473.asm").write_bytes(tail.encode("cp932"))

    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("fraction template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/fr.cpp")

    # The original aBd_0 string remains owned by the rest/data object.  Add a
    # zero-byte C-linkage alias so TC86 can address that same byte sequence.
    rest = work / "th04_maine_rest_v470.asm"
    data = rest.read_bytes().decode("cp932")
    pos = data.index("public ", data.index("\t.data\r\n"))
    line_end = data.index("\r\n", pos)
    if "_aBd_0" not in data[pos:line_end]:
        data = data[:line_end] + ", _aBd_0" + data[line_end:]
    needle = "aBd_0\t\tdb '．',0"
    if data.count(needle) != 1:
        raise ValueError("aBd_0 string label drift")
    data = data.replace(needle, "_aBd_0 label byte\r\n" + needle, 1)
    rest.write_bytes(data.encode("cp932"))


def object_fixups(path: Path) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x9C:
            result.extend(fixup_locations(record.data))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--target-restored", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    source = args.source_dir.resolve()
    target_path = args.target_restored.resolve()
    output = output_dir(args.output_dir)

    if sha(RUNNER) != RUNNER_SHA:
        raise ValueError("MS-DOS runner identity drift")
    for rel, expected in V401_BASE.items():
        path = source / rel
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"v401 source identity drift: {rel}")
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA:
        raise ValueError("v228 MAINE target-restored identity drift")
    target = parse_mz(target_path.read_bytes())
    target_sites = [row.linear for row in target.relocations]
    target_fraction = target.program_image[FRACTION_LOAD:FRACTION_LOAD + FRACTION_SIZE]
    if digest(target_fraction) != FRACTION_LINKED_SHA:
        raise ValueError("target fraction identity drift")

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        prepare_v472(work, output, label)
        baseline = parse_mz((work / "bin/th04/maine.exe").read_bytes())
        baseline_sites = [row.linear for row in baseline.relocations]
        if sum(a != b for a, b in zip(baseline_sites, target_sites)) != V472_MISMATCHES:
            raise ValueError(f"{label}: v472 ordered frontier drift")
        old_tail = segment_bytes(work / "obj/th04/m1tail.obj", "MAINE_01_TEXT")
        if len(old_tail) != (FRACTION_SIZE + TAIL_SIZE):
            raise ValueError(f"{label}: v472 tail size drift")
        old_fraction = old_tail[:FRACTION_SIZE]
        if digest(old_fraction) != FRACTION_RAW_SHA:
            raise ValueError(f"{label}: old fraction raw identity drift")

        split_fraction_owner(work)
        tasm(work, output, f"v473-tail-{label}", "th04_maine_01_tail_v473.asm", "m1tail73.obj")
        tasm(work, output, f"v473-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")
        tcc(work, output, f"v473-fraction-{label}", "th04/fr.cpp")

        fraction = segment_bytes(work / "obj/th04/fr.obj", "MAINE_01_TEXT")
        tail = segment_bytes(work / "obj/th04/m1tail73.obj", "MAINE_01_TEXT")
        if len(fraction) != FRACTION_SIZE or digest(fraction) != FRACTION_RAW_SHA:
            raise ValueError(f"{label}: fraction raw CODE is not exact")
        if fraction != old_fraction:
            raise ValueError(f"{label}: fraction differs from v472 TASM owner")
        if len(tail) != TAIL_SIZE:
            raise ValueError(f"{label}: v473 tail size drift")
        fixes = object_fixups(work / "obj/th04/fr.obj")
        if fixes != FRACTION_FIXUPS:
            raise ValueError(f"{label}: fraction FIXUPP order drift: {fixes}")

        rsp = work / "obj/th04/maine.@l"
        text = rsp.read_text()
        old = r"obj\th04\m1tail.obj"
        new = r"obj\th04\fr.obj obj\th04\m1tail73.obj"
        if text.count(old) != 1:
            raise ValueError(f"{label}: v472 tail response token drift")
        rsp.write_text(text.replace(old, new, 1))

        exe = work / "bin/th04/maine.exe"
        map_path = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True)
        map_path.unlink(missing_ok=True)
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
            work,
            output / f"v473-link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        sites = [row.linear for row in image.relocations]
        payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image or digest(image.program_image) != PROGRAM_SHA:
            raise ValueError(f"{label}: fraction replacement changed linked program bytes")
        if sites != baseline_sites:
            raise ValueError(f"{label}: fraction replacement changed relocation table")
        if sorted(sites) != sorted(target_sites):
            raise ValueError(f"{label}: target relocation-site multiset drift")
        ordered = sum(a != b for a, b in zip(sites, target_sites))
        if ordered != V472_MISMATCHES:
            raise ValueError(f"{label}: ordered mismatch frontier drift: {ordered}")
        linked_fraction = image.program_image[FRACTION_LOAD:FRACTION_LOAD + FRACTION_SIZE]
        if linked_fraction != target_fraction:
            raise ValueError(f"{label}: linked fraction body is not target exact")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: v473 final identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload,
            "fraction_raw_sha256": digest(fraction),
            "fraction_linked_sha256": digest(linked_fraction),
            "fraction_fixupp_locations": [[kind, loc] for kind, loc in fixes],
            "fraction_size": len(fraction),
            "tail_size": len(tail),
            "relocation_table_unchanged_vs_v472": True,
            "ordered_relocation_mismatches": ordered,
            "same_index_relocations": len(sites) - ordered,
        }

    for key in (
        "exe_sha256", "map_sha256", "program_image_sha256", "fraction_raw_sha256",
        "fraction_linked_sha256", "fraction_fixupp_locations", "fraction_size",
        "tail_size", "relocation_table_unchanged_vs_v472",
        "ordered_relocation_mismatches", "same_index_relocations",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B v473 {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE fraction-of-million helper natural-C++ linked-exact replay",
        "source_baseline": V401_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "Natural TC86 C++ emits all 0x77 graph_fraction_of_million_put CODE bytes exactly against the v472 TASM tail. Replacing only this body with a C++ owner keeps the complete linked MAINE program image and the entire 559-entry relocation table byte-for-byte unchanged; linked bytes at load 0x192B are target exact. The function's single segment relocation was already at its v472 position, so the ordered residual remains 176."
        ),
        "limit": (
            "The C++ replay exposes the existing rest-owner aBd_0 string through a zero-byte _aBd_0 alias and declares the new cross-object helper near in the remaining TASM tail. These adapters alter no executable bytes or addresses. Further relocation progress requires recovering larger adjacent verdict code, not moving this already-correct single-fixup helper."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_sha256": FINAL_EXE,
        "fraction_linked_exact": True,
        "ordered_relocation_mismatches": V472_MISMATCHES,
        "same_index_relocations": 559 - V472_MISMATCHES,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
