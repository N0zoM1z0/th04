#!/usr/bin/env python3
"""Test a target-motivated conditional-expression producer in gameplay_loop.

This is an isolated compiler diagnostic, not an exact unit or source promotion.
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
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402

SOURCE = ROOT / "src/main/core/gameplay_loop.cpp"
SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001/a/source"
OLD = """        int frames_per_playperf_raise = resident->rem_lives;
        if(frames_per_playperf_raise >= 10) {
            frames_per_playperf_raise = 1000;
        } else {
            frames_per_playperf_raise = (6000 - (frames_per_playperf_raise * 500));
        }"""
NEW = """        int frames_per_playperf_raise = resident->rem_lives;
        frames_per_playperf_raise = (frames_per_playperf_raise >= 10)
            ? 1000 : (6000 - (frames_per_playperf_raise * 500));"""
OLD_FRAME = """        stage_frame++;
        stage_frame_mod16 = (stage_frame & 15);"""
NEW_FRAME = """        stage_frame_mod16 = ((stage_frame = stage_frame + 1) & 15);"""
OLD_FRAME_CODE_SHA256 = "54c691f5ea776a4b71003c10f772c825e729ea852eb494fa65a364710c8c6ebc"
NEW_FRAME_CODE_SHA256 = "e3d6e451f5c5988c21c885be406815bf8c8fd23c181494db67bea74001b245ed"
BRANCH = bytes.fromhex(
    "83 FE 0A 7C 05 B8 E8 03 EB 0D 8B C6 69 C0 F4 01 "
    "50 B8 70 17 5A 2B C2 8B F0"
)
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th04/")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_code(obj: bytes) -> tuple[bytes, int]:
    records = parse_omf(obj)
    groups = code_ledata(records, "DEMO_TEXT")
    if not groups or groups[0][0] != 0:
        raise ValueError("missing DEMO_TEXT LEDATA")
    code = bytearray(groups[-1][1])
    cursor = 0
    for start, end, record_number, _ in groups:
        if start != cursor:
            raise ValueError("non-contiguous DEMO_TEXT")
        code[start:end] = records[record_number - 1].data[3:]
        cursor = end
    return bytes(code), len(records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="gameplay-ternary-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)

    source = SOURCE.read_text()
    if source.count(NEW) != 1 or source.count(NEW_FRAME) != 1:
        raise ValueError("maintained source no longer contains the expected bounded expressions")
    variants = {
        "baseline": source.replace(NEW, OLD),
        "prior_frame": source.replace(NEW_FRAME, OLD_FRAME),
        "ternary": source,
    }
    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    target_info = next(item for item in manifest["artifacts"] if item["id"] == "th04-main")
    target = (ROOT / target_info["private_path"]).read_bytes()
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise ValueError("MAIN target identity failed")
    header_size = int.from_bytes(target[8:10], "little") * 16
    target_body = target[header_size + 0xAB88:header_size + 0xAB88 + 379]
    if len(target_body) != 379 or target_body.count(BRANCH) != 1 or target_body.find(BRANCH) != 319:
        raise ValueError("target branch or gameplay extent differs")
    (output / "target.code").write_bytes(target_body)

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(item for item in surfaces if item["id"] == "active-tcc")
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise ValueError("active TCC identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    results = {}
    with tempfile.TemporaryDirectory(prefix="work-", dir=output) as scratch:
        work = Path(scratch) / "source"
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        source_path = work / "th04/looptry.cpp"
        for label, text in variants.items():
            source_path.write_text(text)
            os.utime(source_path, (946684800, 946684800))
            object_path = work / "obj/th04/looptry.obj"
            object_path.unlink(missing_ok=True)
            command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS, "th04/looptry.cpp"]
            done = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=120)
            (output / f"{label}.log").write_text(
                json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr
            )
            if done.returncode or not object_path.is_file():
                raise ValueError(f"{label}: TCC compilation failed")
            obj = object_path.read_bytes()
            code, records = extract_code(obj)
            (output / f"{label}.obj").write_bytes(obj)
            (output / f"{label}.code").write_bytes(code)
            results[label] = {
                "source_sha256": sha(text.encode()), "object_sha256": sha(obj),
                "omf_record_count": records, "code_size": len(code), "code_sha256": sha(code),
                "target_branch_occurrences": code.count(BRANCH),
                "target_branch_code_offset": code.find(BRANCH),
            }
    if (results["baseline"]["code_size"], results["ternary"]["code_size"]) != (370, 372):
        raise ValueError("unexpected gameplay code lengths")
    if results["baseline"]["target_branch_occurrences"] != 0:
        raise ValueError("baseline already contains target branch")
    if results["ternary"]["target_branch_occurrences"] != 1 or results["ternary"]["target_branch_code_offset"] != 314:
        raise ValueError("ternary did not reproduce bounded target branch")
    if results["prior_frame"]["code_sha256"] != OLD_FRAME_CODE_SHA256:
        raise ValueError("prior maintained frame producer changed")
    if results["ternary"]["code_sha256"] != NEW_FRAME_CODE_SHA256:
        raise ValueError("revised maintained frame producer changed")
    if target_body[0x115:0x121] != bytes.fromhex("a1 8a 53 8b d0 40 a3 8a 53 25 0f 00"):
        raise ValueError("target frame-counter sequence changed")
    revised_code = (output / "ternary.code").read_bytes()
    if revised_code[0x113:0x11D] != bytes.fromhex("a1 00 00 40 a3 00 00 24 0f a2"):
        raise ValueError("revised source did not emit the target-like frame counter prefix")
    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN DEMO_TEXT gameplay_loop conditional branch and frame-counter producer; no exact promotion",
        "target_sha256": target_info["sha256"], "target_body_sha256": sha(target_body),
        "target_load_extent": "0xAB88..0xAD02", "target_branch_load_offset": "0xACC7",
        "target_branch_sha256": sha(BRANCH), "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(runner.read_bytes()), "flags": list(FLAGS),
        "variants": results,
        "result": "maintained source reproduces the 25-byte AX-result branch and MOV AX/INC AX/store frame-counter shape; complete CODE is 372 versus 379 target bytes",
        "limit": "No linked MAP/relocation/raw unit or cold aggregate exactness gate is passed.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
