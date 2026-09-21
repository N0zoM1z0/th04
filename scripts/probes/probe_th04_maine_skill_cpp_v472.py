#!/usr/bin/env python3
"""Recover TH04 MAINE skill_apply_and_graph_percentage_put() as TC86 C++.

Builds the accepted v471 graph3 topology from retained v401 source, then splits
the remaining MAINE_01 TASM suffix at the adjacent skill helper boundary.  The
natural C++ body is inserted between source-level TASM owners.  No executable,
OMF, or relocation bytes are patched.
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
from probe_th04_maine_graph3_cpp_v471 import (  # noqa: E402
    FINAL_MAP as V471_MAP,
    GRAPH_FIXUPS,
    GRAPH_LINKED_SHA,
    GRAPH_LOAD,
    GRAPH_RAW_SHA,
    GRAPH_SIZE,
    PREFIX_SIZE,
    SUFFIX_SIZE as V471_POST_SIZE,
    prepare_v470,
    split_graph_owner,
)
from probe_th04_maine_master_relocation_order import BASE as V401_BASE  # noqa: E402
from probe_th04_maine_score_producers_v468 import (  # noqa: E402
    RUNNER,
    RUNNER_SHA,
    TARGET_RESTORED_SHA,
    digest,
    run_checked,
)
from probe_th04_maine_segment_topology_v470 import (  # noqa: E402
    FINAL_EXE as V470_EXE,
    PROGRAM_SHA,
    EXPECTED_ORDERED_MISMATCHES as V470_MISMATCHES,
    output_dir,
    tasm,
    tcc,
)
from probe_th04_master_object_split import compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_skill_v472.cpp.in"
TEMPLATE_SHA = "55c25152c9513eb4788c0d94a36555647e75763e2411cdb138179cc5463c370f"
FINAL_EXE = "db8d82aeb64407563a97a77ae285b477296c8f54cccd4ed743a6352d9e5bd418"
FINAL_MAP = "22fab072431657e7d2ec33fb95fe79e1eb61605a5c985782535d25d0c403029a"
SKILL_LOAD = 0x1836
SKILL_SIZE = 0x00F5
SKILL_LINKED_SHA = "1a4143ca6004cfb50313ba830da1d1490eb15de5c0366ce4392403867c5daa79"
SKILL_RAW_SHA = "9d2f2eb5690a82e44ce8b6fb87aa573a0c25752a18f136f952879b435a6e61b7"
MID_SIZE = 0x0069
TAIL_SIZE = 0x07CE
EXPECTED_MISMATCHES = 176
EXPECTED_CHANGED = [254, 255]
EXPECTED_SITES = [0xB973, 0xB963]
SKILL_FIXUPS = [
    (3, 0xEB), (1, 0xE8), (3, 0xDB), (1, 0xD8),
    (1, 0xCC), (1, 0xC8), (1, 0xBC), (1, 0x91),
    (1, 0x78), (1, 0x70), (1, 0x66), (1, 0x5F),
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


def prepare_v471(work: Path, output: Path, label: str) -> None:
    prepare_v470(work, output, label)
    baseline = parse_mz((work / "bin/th04/maine.exe").read_bytes())
    baseline_sites = [row.linear for row in baseline.relocations]

    split_graph_owner(work)
    tasm(work, output, f"v471-graph3-pre-{label}", "th04_maine_01_pre_v471.asm", "m1pre.obj")
    tasm(work, output, f"v471-graph3-post-{label}", "th04_maine_01_post_v471.asm", "m1post.obj")
    tcc(work, output, f"v471-graph3-cpp-{label}", "th04/g3.cpp")
    if segment_bytes(work / "obj/th04/g3.obj", "MAINE_01_TEXT").hex() == "":
        raise ValueError(f"{label}: missing v471 graph3 code")

    rsp = work / "obj/th04/maine.@l"
    text = rsp.read_text()
    old = r"obj\th04\maine01v.obj"
    new = r"obj\th04\m1pre.obj obj\th04\g3.obj obj\th04\m1post.obj"
    if text.count(old) != 1:
        raise ValueError(f"{label}: v470 owner token drift")
    rsp.write_text(text.replace(old, new, 1))
    exe = work / "bin/th04/maine.exe"
    map_path = work / "obj/th04/maine.map"
    exe.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
        work,
        output / f"v471-link-{label}.log",
    )
    if sha(exe) != V470_EXE or sha(map_path) != V471_MAP:
        raise ValueError(f"{label}: v471 baseline identity drift")
    image = parse_mz(exe.read_bytes())
    if image.program_image[GRAPH_LOAD:GRAPH_LOAD + GRAPH_SIZE] is None:
        raise ValueError("unreachable graph3 guard")
    if digest(image.program_image[GRAPH_LOAD:GRAPH_LOAD + GRAPH_SIZE]) != GRAPH_LINKED_SHA:
        raise ValueError(f"{label}: v471 graph3 linked identity drift")
    if [row.linear for row in image.relocations] != baseline_sites:
        raise ValueError(f"{label}: v471 baseline relocation drift")


def split_skill_owner(work: Path) -> None:
    source = work / "th04_maine_01_post_v471.asm"
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
        raise ValueError(f"post segment occurrence drift: {positions}")
    real = positions[1]
    end_marker = "maine_01_TEXT ends"
    seg_end = text.index(end_marker, real)
    common = text[:real]
    body = text[real + len(seg):seg_end]
    start = body.index("public @SKILL_APPLY_AND_GRAPH_PERCENTAGE$QIIUIUI")
    end = body.index("@skill_apply_and_graph_percentage$qiiuiui\tendp", start)
    end += len("@skill_apply_and_graph_percentage$qiiuiui\tendp")
    mid_body = body[:start]
    tail_body = body[end:]

    helper = "sub_B81D\tproc near"
    if mid_body.count(helper) != 1:
        raise ValueError("sub_B81D boundary drift")
    mid_body = mid_body.replace(helper, "public sub_B81D\r\n" + helper, 1)
    mid = common + seg + mid_body + end_marker + "\r\n\tend\r\n"

    assume = (
        "\r\n\t\tassume cs:group_01\r\n"
        "\t\tassume es:nothing, ss:nothing, ds:_DATA, fs:nothing, gs:nothing\r\n"
    )
    tail = common + seg + assume + tail_body + end_marker + "\r\n\tend\r\n"
    text_end = tail.index("_TEXT ends\r\n") + len("_TEXT ends\r\n")
    externs = (
        "\r\n\textern sub_B81D:near\r\n"
        "\textern @SKILL_APPLY_AND_GRAPH_PERCENTAGE$QIIUIUI:near\r\n"
    )
    tail = tail[:text_end] + externs + tail[text_end:]
    (work / "th04_maine_01_mid_v472.asm").write_bytes(mid.encode("cp932"))
    (work / "th04_maine_01_tail_v472.asm").write_bytes(tail.encode("cp932"))

    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("skill template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/sk.cpp")

    # Compiler-visible aliases for reconstructed local string labels.  LABEL
    # emits no data and preserves both bytes and addresses in the rest owner.
    rest = work / "th04_maine_rest_v470.asm"
    data = rest.read_bytes().decode("cp932")
    pos = data.index("public ", data.index("\t.data\r\n"))
    line_end = data.index("\r\n", pos)
    data = data[:line_end] + ", _aBd, _aBu" + data[line_end:]
    replacements = (
        ("aBd\t\tdb '．',0", "_aBd label byte\r\naBd\t\tdb '．',0"),
        ("aBu\t\tdb '％',0", "_aBu label byte\r\naBu\t\tdb '％',0"),
    )
    for old, new in replacements:
        if data.count(old) != 1:
            raise ValueError(f"rest string alias drift: {old}")
        data = data.replace(old, new, 1)
    rest.write_bytes(data.encode("cp932"))


def skill_fixups(path: Path) -> list[tuple[int, int]]:
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
    from probe_th04_maine_segment_topology_v470 import output_dir
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
    target_skill = target.program_image[SKILL_LOAD:SKILL_LOAD + SKILL_SIZE]
    if digest(target_skill) != SKILL_LINKED_SHA:
        raise ValueError("target skill identity drift")

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        prepare_v471(work, output, label)
        baseline = parse_mz((work / "bin/th04/maine.exe").read_bytes())
        baseline_sites = [row.linear for row in baseline.relocations]
        v471_post = segment_bytes(work / "obj/th04/m1post.obj", "MAINE_01_TEXT")
        if len(v471_post) != V471_POST_SIZE:
            raise ValueError(f"{label}: v471 post size drift")
        old_skill = v471_post[MID_SIZE:MID_SIZE + SKILL_SIZE]

        split_skill_owner(work)
        tasm(work, output, f"v472-mid-{label}", "th04_maine_01_mid_v472.asm", "m1mid.obj")
        tasm(work, output, f"v472-tail-{label}", "th04_maine_01_tail_v472.asm", "m1tail.obj")
        tasm(work, output, f"v472-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")
        tcc(work, output, f"v472-skill-{label}", "th04/sk.cpp")

        mid = segment_bytes(work / "obj/th04/m1mid.obj", "MAINE_01_TEXT")
        skill = segment_bytes(work / "obj/th04/sk.obj", "MAINE_01_TEXT")
        tail = segment_bytes(work / "obj/th04/m1tail.obj", "MAINE_01_TEXT")
        if (len(mid), len(skill), len(tail)) != (MID_SIZE, SKILL_SIZE, TAIL_SIZE):
            raise ValueError(f"{label}: skill split owner sizes drift")
        if len(mid) + len(skill) + len(tail) != V471_POST_SIZE:
            raise ValueError(f"{label}: skill split total size drift")
        if skill != old_skill or digest(skill) != SKILL_RAW_SHA:
            raise ValueError(f"{label}: skill raw CODE is not exact")
        fixes = skill_fixups(work / "obj/th04/sk.obj")
        if fixes != SKILL_FIXUPS:
            raise ValueError(f"{label}: skill FIXUPP order drift: {fixes}")

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
        image = parse_mz(exe.read_bytes())
        sites = [row.linear for row in image.relocations]
        payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image or digest(image.program_image) != PROGRAM_SHA:
            raise ValueError(f"{label}: skill replacement changed linked program bytes")
        if sorted(sites) != sorted(target_sites):
            raise ValueError(f"{label}: relocation-site multiset drift")
        changed = [i for i, (left, right) in enumerate(zip(baseline_sites, sites)) if left != right]
        if changed != EXPECTED_CHANGED:
            raise ValueError(f"{label}: changed relocation indices drift: {changed}")
        if sites[254:256] != EXPECTED_SITES or sites[254:256] != target_sites[254:256]:
            raise ValueError(f"{label}: skill segment relocations are not target exact")
        ordered = sum(left != right for left, right in zip(sites, target_sites))
        if ordered != EXPECTED_MISMATCHES:
            raise ValueError(f"{label}: ordered mismatch frontier drift: {ordered}")
        linked_skill = image.program_image[SKILL_LOAD:SKILL_LOAD + SKILL_SIZE]
        if linked_skill != target_skill:
            raise ValueError(f"{label}: linked skill body is not target exact")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: v472 final identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload,
            "skill_raw_sha256": digest(skill),
            "skill_linked_sha256": digest(linked_skill),
            "skill_fixupp_locations": [[kind, loc] for kind, loc in fixes],
            "mid_size": len(mid),
            "skill_size": len(skill),
            "tail_size": len(tail),
            "changed_relocation_indices_vs_v471": changed,
            "skill_segment_sites": sites[254:256],
            "ordered_relocation_mismatches": ordered,
            "same_index_relocations": len(sites) - ordered,
        }

    for key in (
        "exe_sha256", "map_sha256", "program_image_sha256", "skill_raw_sha256",
        "skill_linked_sha256", "skill_fixupp_locations", "mid_size", "skill_size",
        "tail_size", "changed_relocation_indices_vs_v471", "skill_segment_sites",
        "ordered_relocation_mismatches", "same_index_relocations",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B v472 {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE skill percentage helper natural-C++ linked-exact replay",
        "source_baseline": V401_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "Natural TC86 C++ emits all 0xF5 skill_apply_and_graph_percentage_put CODE bytes exactly against the v471 source-split TASM owner. Replacing that body through a TASM mid / C++ skill / TASM tail split keeps the entire linked MAINE program image unchanged. TC86 emits the two graph_putsa_fx segment FIXUPPs high-address first, changing only MZ relocation indices 254 and 255 from 0xB963,0xB973 to target-exact 0xB973,0xB963. Ordered MAINE residual therefore falls 178 to 176 with the 559-site multiset unchanged."
        ),
        "limit": (
            "The C++ replay uses zero-byte rest-owner aliases _aBd/_aBu for reconstructed string labels aBd/aBu, and makes the pre-existing private helper sub_B81D public/near across the new source-level object boundary. These adapters change no program bytes or addresses. Remaining MAINE_01/SCORE/BGIMAGE producer order is unresolved."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_sha256": FINAL_EXE,
        "skill_linked_exact": True,
        "ordered_relocation_mismatches": EXPECTED_MISMATCHES,
        "same_index_relocations": 559 - EXPECTED_MISMATCHES,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
