#!/usr/bin/env python3
"""Recover TH04 MAINE sub_BB81() as natural TC86 C++.

Starts from retained v401 source, reconstructs the accepted v474 verdict
frontier, replaces the first 0x577 bytes of the remaining MAINE_01 tail with a
TC86 C++ owner, and relinks MAINE.  No executable, OMF, or relocation bytes are
patched.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
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
from probe_th04_maine_verdict_cpp_v474 import (  # noqa: E402
    FINAL_EXE as V474_EXE,
    FINAL_MAP as V474_MAP,
    EXPECTED_MISMATCHES as V474_MISMATCHES,
    prepare_v473,
    split_verdict_owner,
)
from probe_th04_master_object_split import compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_bb81_v475.cpp.in"
TEMPLATE_SHA = "e9abdca71fddb221835e92e9ef0274444d4fcc80a2bc007120455b863c1017e7"
FINAL_EXE = "10633c16550b1f82cbe15b9ec92abd92aad68649d4ce4257e8b1b7a0c695c161"
FINAL_MAP = "9d831202195630aeeb07842da439c01e81debdb5c8548c8adb12f194fc989332"
BB81_LOAD = 0xBB81
BB81_SIZE = 0x0577
BB81_RAW_SHA = "303a7c12d21ab36596070997e0ed6040c5c1f4cead6a8e873ceb9a3355bcb672"
BB81_LINKED_SHA = "8db6709abadd107aca1437a89d4c050af7b6f4a76d325490b5e86f171e9ecc00"
TAIL_SIZE = 0x0051
EXPECTED_MISMATCHES = 157
FIRST_KIND3 = [
    0x15D, 0x14C, 0x110, 0x0DD, 0x0CC,
    0x0BB, 0x0AA, 0x099, 0x088, 0x077,
    0x066, 0x055, 0x044, 0x033, 0x022,
]
SECOND_KIND3 = [0x15E, 0x157, 0x150, 0x13F, 0x120, 0x119, 0x10F, 0x104, 0x096, 0x08D]
TARGET_SITES_259_273 = [
    0xBCE0, 0xBCCF, 0xBC93, 0xBC60, 0xBC4F,
    0xBC3E, 0xBC2D, 0xBC1C, 0xBC0B, 0xBBFA,
    0xBBE9, 0xBBD8, 0xBBC7, 0xBBB6, 0xBBA5,
]
EXPECTED_CHANGED = [
    259, 260, 261, 262, 263, 264, 265,
    267, 268, 269, 270, 271, 272, 273,
    274, 275, 276, 277, 278, 279, 280, 281, 282, 283,
]

# TC86 C-linkage aliases to labels that stay physically owned by mainerest.
REST_ALIASES = {
    "_aB_b_b_b_b_b_b": "aB@b@b@b@b@b@b@",
    "_aUqiUx": "aUqiUx",
    "_aNPiuU_": "aNPiuU_",
    "_aGGxi": "aGGxi",
    "_aGGaogcpi": "aGGaogcpi",
    "_aGqbGatbrmcj": "aGqbGatbrmcj",
    "_aIlcSObcj": "aIlcSObcj",
    "_aGagcgegai": "aGagcgegai",
    "_aUU_gagcgeganNv": "aUU_gagcgeganNv",
    "_aLcnzvv": "aLcnzvv",
    "_aPicacovCj": "aPicacovCj",
    "_aVavVVSrso": "aVavVVSrso",
    "_aTimes": "aTimes",
    "_aTimes_0": "aTimes_0",
    "_aPoint": "aPoint",
    "_a_ude_txt": "a_ude_txt",
    "_aBhbhbhbhbhbhu_": "aBhbhbhbhbhbhu_",
    "_aPicacovVVcvsfT": "aPicacovVVcvsfT",
    "_byte_124CC": "byte_124CC",
    "_byte_124EF": "byte_124EF",
    "_unk_124D3": "unk_124D3",
    "_grEASY": "grEASY",
}


def segment_bytes(path: Path, segment: str) -> bytes:
    records = parse_omf(path.read_bytes())
    groups = code_ledata(records, segment)
    if not groups:
        return b""
    end = max(row[1] for row in groups)
    data = bytearray(end)
    for start, stop, recno, _ in groups:
        data[start:stop] = records[recno - 1].data[3:]
    return bytes(data)


def prepare_v474(work: Path, output: Path, label: str) -> None:
    prepare_v473(work, output, label)
    split_verdict_owner(work)
    tcc(work, output, f"v474-verdict-{label}", "th04/gv.cpp")
    tasm(work, output, f"v474-tail-{label}", "th04_maine_01_tail_v474.asm", "m1tail74.obj")
    tasm(work, output, f"v474-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")

    rsp = work / "obj/th04/maine.@l"
    text = rsp.read_text()
    old = (
        r"obj\th04\g3.obj obj\th04\m1mid.obj obj\th04\sk.obj "
        r"obj\th04\fr.obj obj\th04\m1tail73.obj"
    )
    new = r"obj\th04\gv.obj obj\th04\m1tail74.obj"
    if text.count(old) != 1:
        raise ValueError(f"{label}: v473 verdict owner sequence drift")
    rsp.write_text(text.replace(old, new, 1))

    exe = work / "bin/th04/maine.exe"
    map_path = work / "obj/th04/maine.map"
    exe.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
        work,
        output / f"v474-link-{label}.log",
    )
    if sha(exe) != V474_EXE or sha(map_path) != V474_MAP:
        raise ValueError(f"{label}: v474 baseline identity drift")
    image = parse_mz(exe.read_bytes())
    if digest(image.program_image) != PROGRAM_SHA:
        raise ValueError(f"{label}: v474 program-image identity drift")


def split_bb81_owner(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v475 BB81 template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/bb81.cpp")

    # Remaining TASM contains verdict_animate only.
    source = work / "th04_maine_01_tail_v474.asm"
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
        raise ValueError(f"v474 tail segment occurrence drift: {positions}")
    real = positions[1]
    end_marker = "maine_01_TEXT ends"
    seg_end = text.index(end_marker, real)
    common = text[:real]
    body = text[real + len(seg):seg_end]
    start = body.index("public @verdict_animate$qv")
    tail_body = body[start:]

    text_end = common.index("_TEXT ends\r\n") + len("_TEXT ends\r\n")
    if "\textern @sub_BB81$qv:near\r\n" not in common:
        common = (
            common[:text_end]
            + "\r\n\textern @sub_BB81$qv:near\r\n"
            + common[text_end:]
        )
    tail_body = tail_body.replace(
        "\t\tcall\tsub_BB81\r\n",
        "\t\tcall\t@sub_BB81$qv\r\n",
    )
    assume = (
        "\r\n\t\tassume cs:group_01\r\n"
        "\t\tassume es:nothing, ss:nothing, ds:_DATA, fs:nothing, gs:nothing\r\n"
    )
    tail = common + seg + assume + tail_body + end_marker + "\r\n\tend\r\n"
    (work / "th04_maine_01_tail_v475.asm").write_bytes(tail.encode("cp932"))

    # Expose existing rest/data addresses to TC86 using zero-byte aliases.
    rest = work / "th04_maine_rest_v470.asm"
    data = rest.read_bytes().decode("cp932")
    pos = data.index("public ", data.index("\t.data\r\n"))
    line_end = data.index("\r\n", pos)
    for alias in REST_ALIASES:
        if alias not in data[pos:line_end]:
            data = data[:line_end] + ", " + alias + data[line_end:]
            line_end = data.index("\r\n", pos)
    for alias, original in REST_ALIASES.items():
        if original == "grEASY":
            continue
        pattern = re.compile(r"(?m)^" + re.escape(original) + r"(?=[\t ])")
        matches = list(pattern.finditer(data))
        if len(matches) != 1:
            raise ValueError(f"rest label {original}: matches={len(matches)}")
        match = matches[0]
        data = data[:match.start()] + f"{alias} label byte\r\n" + data[match.start():]
    rest.write_bytes(data.encode("cp932"))

    verdict_data = work / "th04/gaiji/verdict[data].asm"
    text = verdict_data.read_bytes().decode("cp932")
    matches = list(re.finditer(r"(?m)^grEASY(?=[\t ])", text))
    if len(matches) != 1:
        raise ValueError(f"grEASY definition matches={len(matches)}")
    match = matches[0]
    text = text[:match.start()] + "_grEASY label byte\r\n" + text[match.start():]
    verdict_data.write_bytes(text.encode("cp932"))


def fixup_kind3_by_record(path: Path) -> list[list[int]]:
    records: list[list[int]] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x9C:
            locs = [loc for kind, loc in fixup_locations(record.data) if kind == 3]
            if locs:
                records.append(locs)
    return records


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
    target_bb81 = target.program_image[BB81_LOAD:BB81_LOAD + BB81_SIZE]
    if digest(target_bb81) != BB81_LINKED_SHA:
        raise ValueError("target BB81 identity drift")

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        prepare_v474(work, output, label)
        baseline = parse_mz((work / "bin/th04/maine.exe").read_bytes())
        baseline_sites = [row.linear for row in baseline.relocations]
        if sum(a != b for a, b in zip(baseline_sites, target_sites)) != V474_MISMATCHES:
            raise ValueError(f"{label}: v474 ordered frontier drift")

        split_bb81_owner(work)
        tcc(work, output, f"v475-bb81-{label}", "th04/bb81.cpp")
        tasm(work, output, f"v475-tail-{label}", "th04_maine_01_tail_v475.asm", "m1tail75.obj")
        tasm(work, output, f"v475-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")

        bb81_obj = work / "obj/th04/bb81.obj"
        bb81 = segment_bytes(bb81_obj, "MAINE_01_TEXT")
        tail = segment_bytes(work / "obj/th04/m1tail75.obj", "MAINE_01_TEXT")
        if len(bb81) != BB81_SIZE or digest(bb81) != BB81_RAW_SHA:
            raise ValueError(f"{label}: BB81 raw CODE is not exact")
        if len(tail) != TAIL_SIZE:
            raise ValueError(f"{label}: verdict_animate tail size drift: {len(tail)}")
        kind3_records = fixup_kind3_by_record(bb81_obj)
        if kind3_records != [FIRST_KIND3, SECOND_KIND3]:
            raise ValueError(f"{label}: BB81 kind-3 FIXUPP order drift: {kind3_records}")

        rsp = work / "obj/th04/maine.@l"
        text = rsp.read_text()
        old = r"obj\th04\m1tail74.obj"
        new = r"obj\th04\bb81.obj obj\th04\m1tail75.obj"
        if text.count(old) != 1:
            raise ValueError(f"{label}: v474 tail response token drift")
        rsp.write_text(text.replace(old, new, 1))

        exe = work / "bin/th04/maine.exe"
        map_path = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True)
        map_path.unlink(missing_ok=True)
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
            work,
            output / f"v475-link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        sites = [row.linear for row in image.relocations]
        payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image or digest(image.program_image) != PROGRAM_SHA:
            raise ValueError(f"{label}: BB81 replacement changed linked program bytes")
        linked_bb81 = image.program_image[BB81_LOAD:BB81_LOAD + BB81_SIZE]
        if linked_bb81 != target_bb81:
            raise ValueError(f"{label}: linked BB81 is not target exact")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: target relocation-site multiset drift")
        ordered = sum(a != b for a, b in zip(sites, target_sites))
        if ordered != EXPECTED_MISMATCHES:
            raise ValueError(f"{label}: v475 ordered mismatch drift: {ordered}")
        changed = [i for i, (a, b) in enumerate(zip(baseline_sites, sites)) if a != b]
        if changed != EXPECTED_CHANGED:
            raise ValueError(f"{label}: v475 changed-index set drift: {changed}")
        if sites[259:274] != TARGET_SITES_259_273 or target_sites[259:274] != TARGET_SITES_259_273:
            raise ValueError(f"{label}: BB81 relocation block is not target-index exact")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: v475 final identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload,
            "bb81_raw_sha256": digest(bb81),
            "bb81_linked_sha256": digest(linked_bb81),
            "bb81_size": len(bb81),
            "bb81_kind3_records": kind3_records,
            "animate_tail_size": len(tail),
            "changed_indices_vs_v474": changed,
            "target_exact_indices": [259, 273],
            "target_exact_sites": sites[259:274],
            "ordered_relocation_mismatches": ordered,
            "same_index_relocations": len(sites) - ordered,
        }

    for key in (
        "exe_sha256", "map_sha256", "program_image_sha256", "bb81_raw_sha256",
        "bb81_linked_sha256", "bb81_size", "bb81_kind3_records", "animate_tail_size",
        "changed_indices_vs_v474", "target_exact_sites", "ordered_relocation_mismatches",
        "same_index_relocations",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B v475 {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE sub_BB81 natural-C++ raw/linked exact relocation-order replay",
        "source_baseline": V401_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "Natural TC86 C++ reproduces all 0x577 bytes of sub_BB81 including both compiler switch tables. Replacing only that TASM owner preserves the complete v474 MAINE program image byte-for-byte and the 559-site relocation multiset. The first TC86 FIXUPP record emits 15 segment relocations high-address first, making target indices 259..273 exact and reducing ordered residual from 170 to 157. Several exact source-shape controls are compiler-observed: a ternary rank assignment keeps rank in AL across the global store and grEASY index; reinterpret_cast<long &>(skill) /= N selects the target signed compound-division load order without changing the global uint32_t ABI; credit_bombs is a switch; and the end-sequence condition is written in target control-flow order."
        ),
        "limit": (
            "The replay uses zero-byte aliases for existing rest/data labels and a source-level near PUBLIC name for sub_BB81 so verdict_animate can call across the new object boundary. Those adapters alter no linked byte or data address. The remaining 0x51 verdict_animate TASM owner still perturbs relocation indices 274..283; recovering that adjacent function is the next natural producer step."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_sha256": FINAL_EXE,
        "bb81_linked_exact": True,
        "ordered_relocation_mismatches": EXPECTED_MISMATCHES,
        "same_index_relocations": 559 - EXPECTED_MISMATCHES,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
