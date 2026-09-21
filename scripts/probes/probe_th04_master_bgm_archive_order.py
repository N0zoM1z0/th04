#!/usr/bin/env python3
"""Inspect independent historical MASTER.LIB BGM object boundaries and FIXUPP.

This probe uses only the locally pinned ReC98 support archive and pinned Borland
TLIB. It does not modify the archive. The question is whether the final two
MAINE DIET-restored relocation-order differences justify reversing source/object
order. They do not if the historical library itself keeps READ_SDATA before
TIMER as independent objects.
"""
from __future__ import annotations

import argparse
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
from inspect_dialog_fixup_order import code_ledata  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

ARCHIVE = ROOT / "_reference/ReC98/bin/masters.lib"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
TLIB = ROOT / ".analysis/toolchain/wineprefix/drive_c/TC4/BIN/TLIB.EXE"
ARCHIVE_SHA = "6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6"
RUNNER_SHA = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
TLIB_SHA = "2d65d72b8800f7f3d4716218ed508bdd198e73b5f96f4830c1e14d1bb56546e2"
EXPECTED_OBJECTS = {
    "b_r_sdat": {
        "sha256": "4840e85e4dadc80791a2214ee02cde1edc8c60081f690b11b8aa2fafe98cbf58",
        "size": 626,
        "code_size": 0x130,
        "segment_fixups": [0xB7],
    },
    "b_timer": {
        "sha256": "651bfe73ac4ef8fc5261513cde4e6ae82cc1cb30fdd166f8403663f1076c0c68",
        "size": 407,
        "code_size": 0x6A,
        "segment_fixups": [0x13],
    },
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="master-bgm-order-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def run_tlib(work: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN",
    )
    return subprocess.run(
        ["wine", str(RUNNER), "-e", "-x", "tlib", *args],
        cwd=work,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def inspect_object(path: Path) -> dict[str, object]:
    records = parse_omf(path.read_bytes())
    ledatas = code_ledata(records, "_TEXT")
    if len(ledatas) != 1:
        raise ValueError(f"{path.name}: expected one _TEXT LEDATA, got {len(ledatas)}")
    start, end, fixrec, fixupp = ledatas[0]
    locations = fixup_locations(fixupp)
    segment_fixups = [start + offset for kind, offset in locations if kind == 2]
    return {
        "size": path.stat().st_size,
        "sha256": sha(path),
        "code_start": start,
        "code_end": end,
        "code_size": end - start,
        "fixupp_record": fixrec,
        "fixup_locations": [[kind, start + offset] for kind, offset in locations],
        "segment_fixups": segment_fixups,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output = output_dir(args.output_dir)

    for path, expected in ((ARCHIVE, ARCHIVE_SHA), (RUNNER, RUNNER_SHA), (TLIB, TLIB_SHA)):
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"identity drift: {path}")

    shutil.copy2(ARCHIVE, output / "masters.lib")
    listing = run_tlib(output, "masters.lib,masters.lst")
    (output / "list.log").write_text(listing.stdout + listing.stderr)
    list_path = output / "masters.lst"
    if listing.returncode or not list_path.is_file():
        raise RuntimeError("TLIB listing failed")
    list_text = list_path.read_bytes().decode("cp437", errors="replace")
    positions = {}
    for module in EXPECTED_OBJECTS:
        pos = list_text.find(module)
        if pos < 0:
            raise ValueError(f"module absent from library listing: {module}")
        positions[module] = pos
    if not positions["b_r_sdat"] < positions["b_timer"]:
        raise ValueError(f"historical archive module order drift: {positions}")

    objects: dict[str, dict[str, object]] = {}
    for module, expected in EXPECTED_OBJECTS.items():
        rsp = output / ("E1.RSP" if module == "b_r_sdat" else "E2.RSP")
        rsp.write_text(f"*{module}\n")
        done = run_tlib(output, "masters.lib", f"@{rsp.name}")
        (output / f"extract-{module}.log").write_text(done.stdout + done.stderr)
        obj = output / f"{module}.OBJ"
        if done.returncode or not obj.is_file():
            raise RuntimeError(f"TLIB extraction failed: {module}")
        info = inspect_object(obj)
        if (
            info["sha256"] != expected["sha256"]
            or info["size"] != expected["size"]
            or info["code_size"] != expected["code_size"]
            or info["segment_fixups"] != expected["segment_fixups"]
        ):
            raise ValueError(f"historical object identity/OMF drift: {module}: {info}")
        objects[module] = info

    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04 MAINE historical MASTER.LIB BGM object-order/FIXUPP diagnostic",
        "archive_sha256": ARCHIVE_SHA,
        "tlib_sha256": TLIB_SHA,
        "runner_sha256": RUNNER_SHA,
        "archive_listing_sha256": sha(list_path),
        "archive_module_order": ["b_r_sdat", "b_timer"],
        "archive_listing_positions": positions,
        "objects": objects,
        "mapping": {
            "b_r_sdat": "BGM_READ_SDATA; historical segment fixup local +0xB7",
            "b_timer": "_BGM_TIMER_INIT/_BGM_TIMER_FINISH; historical segment fixup local +0x13",
        },
        "conclusion": (
            "The independent historical MASTER.LIB already stores BGM_READ_SDATA and "
            "BGM_TIMER as separate OMF members, with b_r_sdat before b_timer in the "
            "library listing. Each object contains its own segment-word fixup. This "
            "supports the natural read-before-timer producer topology and gives no "
            "historical reason to reverse those two source/object fixups merely to "
            "match the final two entries of the DIET-restored relocation view."
        ),
        "limit": (
            "Library member order is historical support-library evidence, not proof of "
            "the original TH04 executable's TLINK extraction order. DIET -RA order remains "
            "a diagnostic view, so no ordered-relocation exactness claim is made."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "module_order": receipt["archive_module_order"],
        "object_sha256": {k: v["sha256"] for k, v in objects.items()},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
