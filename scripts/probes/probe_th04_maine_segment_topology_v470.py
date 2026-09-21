#!/usr/bin/env python3
"""Recover the TH04 MAINE monolith as natural segment-level physical owners.

The v468 packet established producer direction for SND_LOAD_EXT and the
score_e+hi_end TC86 TU.  This replay additionally splits the reconstructed
`th04_maine.asm` source at its two existing code-segment boundaries:
MAINE_01_TEXT and SCORE_TEXT.  A third owner retains the original SHARED/DATA/BSS
surface.  The final object order follows the target-constrained relocation block
order while preserving the linked program image byte-for-byte.

No OMF/MZ bytes or relocation entries are patched or permuted.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_master_relocation_order import (  # noqa: E402
    BASE as V401_BASE,
    NEW_EXE as V425_EXE,
    NEW_MAP as V425_MAP,
    patch as apply_v425,
)
from probe_th04_maine_score_producers_v468 import (  # noqa: E402
    RUNNER,
    RUNNER_SHA,
    TARGET_RESTORED_SHA,
    apply_producer_sources,
    digest,
    env,
    run_checked,
)
from probe_th04_master_object_split import build, compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

FINAL_EXE = "2e4b7bc9abf039a4a0d105cf141c1959f3e54ce5812066e9d409e69b42a72c3c"
FINAL_MAP = "5ebb1b6f5ae0371df3eb9a1ebb72735bfb6f5eef4a43b1660c6f0c19ce9c8636"
PROGRAM_SHA = "0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1"
EXPECTED_ORDERED_MISMATCHES = 178

MAINE_LOCAL_BYTES = [
    "aSff1_pi", "aStaff", "aSff1_cdg", "aSff1b_cdg", "aSff2_cdg", "aSff2b_cdg",
    "aSff3_cdg", "aSff3b_cdg", "aSff2_pi", "aSff4_cdg", "aSff4b_cdg", "aSff5_cdg",
    "aSff5b_cdg", "aSff8_cdg", "aSff8b_cdg", "aSff9_cdg", "aSff9b_cdg", "aSff6_cdg",
    "aSff6b_cdg", "aSff7_cdg", "aSff7b_cdg", "aU_", "aBd", "aBu", "aBd_0", "aBu_0",
    "aB@b@b@b@b@b@b@", "aUqiUx", "aNPiuU_", "aGGxi", "aGGaogcpi", "aGqbGatbrmcj",
    "aIlcSObcj", "aGagcgegai", "aUU_gagcgeganNv", "aLcnzvv", "aPicacovCj", "aVavVVSrso",
    "aTimes", "aTimes_0", "aPoint", "a_ude_txt", "aBhbhbhbhbhbhu_", "aPicacovVVcvsfT", "aUde_pi",
    "_cdg_slot", "_radial_angle", "byte_124CC", "_verdict_rank", "unk_124D3", "byte_124EF",
    "_graph_3_digit_put_as_fixed_2_dig", "_skill_subtract", "grEASY",
]
MAINE_LOCAL_WORDS = ["_dissolve_put_func"]
MAINE_LOCAL_DWORDS = ["_skill"]
SCORE_LOCAL_BYTES = [
    "aHi01_pi", "aScnum2_bft", "aGxgnbGvbGhvVGv", "aGxgnbGvbGhvV_1", "aName",
    "_rank", "_playchar", "_hi", "_entered_place", "_gALPHABET",
]
SCORE_LOCAL_WORDS = ["_key_det"]
REST_PUBLICS = [
    "aSff1_pi", "aStaff", "aSff1_cdg", "aSff1b_cdg", "aSff2_cdg", "aSff2b_cdg",
    "aSff3_cdg", "aSff3b_cdg", "aSff2_pi", "aSff4_cdg", "aSff4b_cdg", "aSff5_cdg",
    "aSff5b_cdg", "aSff8_cdg", "aSff8b_cdg", "aSff9_cdg", "aSff9b_cdg", "aSff6_cdg",
    "aSff6b_cdg", "aSff7_cdg", "aSff7b_cdg", "aU_", "aBd", "aBu", "aBd_0", "aBu_0",
    "aB@b@b@b@b@b@b@", "aUqiUx", "aNPiuU_", "aGGxi", "aGGaogcpi", "aGqbGatbrmcj",
    "aIlcSObcj", "aGagcgegai", "aUU_gagcgeganNv", "aLcnzvv", "aPicacovCj", "aVavVVSrso",
    "aTimes", "aTimes_0", "aPoint", "a_ude_txt", "aBhbhbhbhbhbhu_", "aPicacovVVcvsfT", "aUde_pi",
    "byte_124CC", "_verdict_rank", "unk_124D3", "byte_124EF",
    "aHi01_pi", "aScnum2_bft", "aGxgnbGvbGhvVGv", "aGxgnbGvbGhvV_1", "aName", "grEASY",
]


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="maine-segment-topology-v470-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def replace_rec98_public(work: Path) -> str:
    source = work / "ReC98.inc"
    data = source.read_bytes()
    needle = b"\tpublic _address_0\r\n"
    if data.count(needle) != 1:
        raise ValueError("ReC98 _address_0 public anchor drift")
    name = "ReC98_v470_nopub.inc"
    (work / name).write_bytes(data.replace(needle, b"", 1))
    return name


def extern_block(bytesy: list[str], words: list[str], dwords: list[str]) -> str:
    out = "\t.data\r\n"
    for sym in bytesy:
        if sym == "_cdg_slots":
            out += "\textern _cdg_slots:cdg_t:CDG_SLOT_COUNT\r\n"
        else:
            out += f"\textern {sym}:byte\r\n"
    for sym in words:
        out += f"\textern {sym}:word\r\n"
    for sym in dwords:
        out += f"\textern {sym}:dword\r\n"
    return out + "\r\n"


def generate_split_sources(work: Path) -> None:
    source = work / "th04_maine.asm"
    text = source.read_bytes().decode("cp932")
    nopub = replace_rec98_public(work)

    group_line = "group_01 group maine_01_TEXT, SCORE_TEXT\r\n"
    group_pos = text.index(group_line)
    common_head = text[:group_pos]
    common_head = common_head.replace("include ReC98.inc", f"include {nopub}", 1)

    text_start = text.index("_TEXT segment word public 'CODE' use16")
    text_end = text.index("_TEXT ends", text_start) + len("_TEXT ends")
    text_surface = text[text_start:text_end] + "\r\n\r\n"
    shared_start = text.index("SHARED segment byte public 'CODE' use16")
    shared_end = text.index("SHARED ends", shared_start) + len("SHARED ends")
    shared_surface = text[shared_start:shared_end] + "\r\n\r\n"

    maine_start = text.index("maine_01_TEXT segment byte public 'CODE' use16")
    maine_end = text.index("maine_01_TEXT ends", maine_start) + len("maine_01_TEXT ends")
    score_start = text.index("SCORE_TEXT segment byte public 'CODE' use16", maine_end)
    score_end = text.index("SCORE_TEXT\tends", score_start) + len("SCORE_TEXT\tends")
    maine_body = text[maine_start:maine_end] + "\r\n"
    score_body = text[score_start:score_end] + "\r\n"

    data_externs = (
        "\t.data\r\n"
        "\textern PaletteTone:word\r\n"
        "\textern random_seed:dword\r\n"
        "\textern _SinTable8:word:256\r\n"
        "\textern _CosTable8:word:256\r\n"
        "\textern _graph_putsa_fx_func:word\r\n"
        "\textern _resident:dword\r\n"
        "\textern vsync_Count1:word\r\n"
        "\textern _VRAM_PLANE_B:dword\r\n"
        "\textern _pi_buffers:dword:6\r\n"
        "\textern _pi_headers:PiHeader:6\r\n\r\n"
    )
    dummy = (
        "maine_01_TEXT segment byte public 'CODE' use16\r\nmaine_01_TEXT ends\r\n"
        "SCORE_TEXT segment byte public 'CODE' use16\r\nSCORE_TEXT ends\r\n"
        + group_line + "\r\n"
    )

    # MAINE_01 needs one extra library/BSS surface not detected as monolith-local.
    maine_extra = ["_cdg_slots"] + MAINE_LOCAL_BYTES
    maine = (
        common_head + dummy + text_surface + shared_surface + data_externs
        + extern_block(maine_extra, MAINE_LOCAL_WORDS, MAINE_LOCAL_DWORDS)
        + maine_body + "\tend\r\n"
    )
    (work / "th04_maine_01_v470.asm").write_bytes(maine.encode("cp932"))

    # SCORE was relying on the ASSUME inherited from MAINE_01 in the monolith.
    score_body = score_body.replace(
        "SCORE_TEXT segment byte public 'CODE' use16\r\n",
        "SCORE_TEXT segment byte public 'CODE' use16\r\n"
        "\t\tassume cs:group_01\r\n"
        "\t\tassume es:nothing, ss:nothing, ds:_DATA, fs:nothing, gs:nothing\r\n",
        1,
    )
    score = (
        common_head + dummy + text_surface + shared_surface + data_externs
        + extern_block(SCORE_LOCAL_BYTES, SCORE_LOCAL_WORDS, [])
        + score_body + "\tend\r\n"
    )
    (work / "th04_maine_score_v470.asm").write_bytes(score.encode("cp932"))

    # Rest/data owner: keep everything except the two code bodies, and export
    # only the formerly local data labels now referenced by the split owners.
    rest = text[:maine_start]
    rest += "maine_01_TEXT segment byte public 'CODE' use16\r\nmaine_01_TEXT ends"
    rest += text[maine_end:score_start]
    rest += "SCORE_TEXT segment byte public 'CODE' use16\r\nSCORE_TEXT\tends"
    rest += text[score_end:]
    data_anchor = "\t.data\r\n"
    if data_anchor not in rest:
        raise ValueError("rest .data anchor missing")
    rest = rest.replace(data_anchor, data_anchor + "public " + ", ".join(REST_PUBLICS) + "\r\n", 1)
    (work / "th04_maine_rest_v470.asm").write_bytes(rest.encode("cp932"))


def tasm(work: Path, output: Path, label: str, asm: str, obj: str) -> None:
    command = (
        r"set PATH=C:\TASM50\BIN;C:\TC4\BIN;%PATH%&&"
        + f"tasm32 /m /mx /kh32768 /t /dGAME=4 {asm} obj\\th04\\{obj}"
    )
    run_checked(["wine", "cmd", "/d", "/c", command], work, output / f"assemble-{label}.log")
    if not (work / f"obj/th04/{obj}").is_file():
        raise ValueError(f"missing TASM output {obj}")


def tcc(work: Path, output: Path, label: str, source: str) -> None:
    run_checked(
        [
            "wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O", "-b-", "-3", "-Z", "-d",
            "-DGAME=4", "-ml", "-DBINARY='E'", "-nobj/th04/", source,
        ],
        work,
        output / f"compile-{label}.log",
    )


def apply_target_owner_order(work: Path) -> None:
    rsp = work / "obj/th04/maine.@l"
    raw = rsp.read_text()
    head, tail = raw.split(",", 1)
    tokens = head.split()

    def remove(tok: str) -> None:
        if tokens.count(tok) != 1:
            raise ValueError(f"response token drift: {tok} count={tokens.count(tok)}")
        tokens.remove(tok)

    for tok in (
        r"obj\th04\mainemtail.obj", r"obj\th04\score_e.obj", r"obj\th04\hi_end.obj", r"obj\th04\maine.obj"
    ):
        remove(tok)

    # Rest stays at the old monolith DATA/BSS position.
    pos = tokens.index(r"obj\th04\grppsafx.obj") + 1
    tokens.insert(pos, r"obj\th04\mainerest.obj")
    # Target-constrained relocation owner order.
    pos = tokens.index(r"obj\th03\pi_put_q.obj") + 1
    tokens.insert(pos, r"obj\th04\mainemtail.obj")
    pos = tokens.index(r"obj\th04\snd_load.obj") + 1
    tokens.insert(pos, r"obj\th04\sndlext.obj")
    pos = tokens.index(r"obj\th04\cutscene.obj") + 1
    for tok in (r"obj\th04\maine01v.obj", r"obj\th04\score_hi.obj", r"obj\th04\mainscv.obj"):
        tokens.insert(pos, tok)
        pos += 1
    rsp.write_text(" ".join(tokens) + "," + tail)


def kind3_count(path: Path) -> int:
    total = 0
    for rec in parse_omf(path.read_bytes()):
        if rec.record_type == 0x9C:
            total += sum(kind == 3 for kind, _ in fixup_locations(rec.data))
    return total


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
    target_sites = [r.linear for r in target.relocations]

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        apply_v425(work)
        build(work, output / f"baseline-build-{label}.log")
        baseline_exe = work / "bin/th04/maine.exe"
        baseline_map = work / "obj/th04/maine.map"
        if sha(baseline_exe) != V425_EXE or sha(baseline_map) != V425_MAP:
            raise ValueError(f"{label}: v425 baseline identity drift")
        baseline_program = parse_mz(baseline_exe.read_bytes()).program_image

        # Natural producer packet from v468.
        apply_producer_sources(work)
        # Natural physical split at existing assembly segment boundaries.
        generate_split_sources(work)

        for asm, obj in (
            ("th04_maine_01_v470.asm", "maine01v.obj"),
            ("th04_maine_score_v470.asm", "mainscv.obj"),
            ("th04_maine_rest_v470.asm", "mainerest.obj"),
            ("th04_maine_master_data_tail.asm", "mainemdata.obj"),
        ):
            tasm(work, output, f"{Path(asm).stem}-{label}", asm, obj)
        for cpp in ("th04/sndlext.cpp", "th04/score_hi.cpp"):
            tcc(work, output, f"{Path(cpp).stem}-{label}", cpp)

        apply_target_owner_order(work)
        exe = work / "bin/th04/maine.exe"
        map_path = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True)
        map_path.unlink(missing_ok=True)
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
            work,
            output / f"link-{label}.log",
        )
        if not exe.is_file() or not map_path.is_file():
            raise ValueError(f"{label}: targeted MAINE relink missing outputs")

        image = parse_mz(exe.read_bytes())
        sites = [r.linear for r in image.relocations]
        payload = compare("th04-maine", work)
        if image.program_image != baseline_program or digest(image.program_image) != PROGRAM_SHA:
            raise ValueError(f"{label}: split topology changed linked program bytes")
        if payload["payload_differing_bytes"] != 2 or [r["start"] for r in payload["payload_mismatch_runs"]] != [0xD1D3]:
            raise ValueError(f"{label}: payload frontier drift")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation-site multiset drift")
        ordered = sum(a != b for a, b in zip(sites, target_sites))
        if ordered != EXPECTED_ORDERED_MISMATCHES:
            raise ValueError(f"{label}: ordered mismatch drift: {ordered}")
        differing = [i for i, (a, b) in enumerate(zip(sites, target_sites)) if a != b]
        allowed = set(range(80, 88)) | set(range(152, 291)) | set(range(311, 347))
        if not set(differing).issubset(allowed):
            raise ValueError(f"{label}: mismatch escaped residual owner ranges")
        if sites[58:62] != target_sites[58:62]:
            raise ValueError(f"{label}: SND_LOAD_EXT global block not exact")
        if sites[291:311] != target_sites[291:311]:
            raise ValueError(f"{label}: score_hi global block not exact")
        if kind3_count(work / "obj/th04/maine01v.obj") != 139:
            raise ValueError(f"{label}: MAINE_01 kind3 count drift")
        if kind3_count(work / "obj/th04/mainscv.obj") != 36:
            raise ValueError(f"{label}: SCORE kind3 count drift")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: final identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload,
            "relocation_count": len(sites),
            "relocation_multiset_exact": True,
            "ordered_relocation_mismatches": ordered,
            "same_index_relocations": len(sites) - ordered,
            "mismatch_indices": differing,
            "snd_load_ext_global_exact": sites[58:62] == target_sites[58:62],
            "score_hi_global_exact": sites[291:311] == target_sites[291:311],
            "maine01_kind3_count": 139,
            "score_kind3_count": 36,
        }

    for key in (
        "exe_sha256", "map_sha256", "program_image_sha256", "ordered_relocation_mismatches",
        "same_index_relocations", "mismatch_indices", "snd_load_ext_global_exact", "score_hi_global_exact",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE natural source-level segment ownership + producer topology replay",
        "source_baseline": V401_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "builds": builds,
        "observed_effect": (
            "The reconstructed th04_maine.asm monolith can be split at its existing MAINE_01_TEXT and SCORE_TEXT source segment boundaries into independent TASM owners plus a rest/data owner. Combined with v468 natural TC86 producers and target-constrained physical owner order, the linked program image remains byte-identical to v425 and the 559-site relocation multiset stays exact. Global block positions through SCORE_TEXT become target-aligned; ordered mismatches fall from 299 to 178. The remaining 178 are internal producer-order residuals only: BGIMAGE 8, MAINE_01_TEXT 136/139, and SCORE_TEXT 34/36."
        ),
        "limit": (
            "The split wrappers add only source-level EXTRN/PUBLIC interfaces and restore the SCORE_TEXT ASSUME state inherited inside the original monolith. A replay-only ReC98 include suppresses duplicate publication of the absolute _address_0 symbol while retaining its value and all macros. No OMF records or MZ relocation entries are edited. Internal FIXUPP direction of the two split TASM owners remains unresolved."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_sha256": FINAL_EXE,
        "program_image_unchanged": True,
        "ordered_relocation_mismatches": EXPECTED_ORDERED_MISMATCHES,
        "same_index_relocations": 559 - EXPECTED_ORDERED_MISMATCHES,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
