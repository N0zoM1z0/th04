#!/usr/bin/env python3
"""Cold-check complete default bullet renderer OMF against a source revision.

This source-regression control does not replace a historical full-link replay
or promote target exactness. Native TH04_LARGE_PRODUCT is deliberately absent.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from lib.omf import describe_omf, parse_omf
from probe_th04_native_main_link import body_wrapper

SOURCES = ("src/main/bullet/pellet_render.asm", "src/main/formats/z_super_roll_put_tiny.asm")
FLAGS = ["/m","/mx","/kh32768","/dGAME=4"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def link_records(blob):
    digest = hashlib.sha256()
    for record in parse_omf(blob):
        if record.record_type != 0x88:
            digest.update(bytes((record.record_type,)))
            digest.update(len(record.data).to_bytes(2,"little"))
            digest.update(record.data)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-revision",required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists() or not out.is_relative_to(ROOT/".analysis/reconstruction/probes"):
        parser.error("use a new private output directory")
    revision = subprocess.check_output(["git","rev-parse","--verify",args.baseline_revision+"^{commit}"],cwd=ROOT,text=True).strip()
    subprocess.run([sys.executable,"scripts/attest_toolchain.py"],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    env = dict(os.environ,WINEPREFIX=str(ROOT/".analysis/toolchain/wineprefix"),WINEDEBUG="-all",MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    out.mkdir()
    observations = {}
    for index, relative in enumerate(SOURCES):
        baseline = subprocess.check_output(["git","show",revision+":"+relative],cwd=ROOT)
        current = (ROOT/relative).read_bytes()
        rounds = {}
        for label,data in (("baseline",baseline),("a",current),("b",current)):
            work = out/str(index)/label
            path = work/relative
            path.parent.mkdir(parents=True)
            path.write_bytes(data)
            if index == 0:
                context = (ROOT/relative).with_suffix(".context.inc")
                path.with_suffix(".context.inc").write_bytes(context.read_bytes())
                path = body_wrapper(ROOT/relative,work,index)
            (work/"obj").mkdir()
            source = path.relative_to(work).as_posix().replace("/","\\")
            command = ["wine",r"C:\TASM50\bin\TASM32.EXE",*FLAGS,source+r",obj\renderer.obj"]
            run = subprocess.run(command,cwd=work,env=env,capture_output=True,timeout=240)
            (work/"assemble.log").write_bytes(run.stdout+run.stderr)
            if run.returncode:
                raise RuntimeError(f"default assembler failed: {work}")
            blob = (work/"obj/renderer.obj").read_bytes()
            omf = describe_omf(blob)
            assert omf["valid"] and any("Turbo Assembler  Version 5.0" in s for s in omf["translator_comments"])
            rounds[label] = dict(source_sha256=sha(data),assembly_source_sha256=sha(path.read_bytes()),
                                 object_sha256=sha(blob),link_records_sha256=link_records(blob),command=command)
        equal = len({v["link_records_sha256"] for v in rounds.values()}) == 1
        observations[relative] = dict(rounds=rounds,equal=equal)
    report = dict(observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,
                  baseline_revision=revision,assembler_flags=FLAGS,
                  observations=observations,equal=all(v["equal"] for v in observations.values()))
    (out/"receipt.json").write_text(json.dumps(report,indent=2)+"\n")
    assert report["equal"]
    print("PASS two default renderer owners: baseline and two cold assemblies have identical complete link-relevant OMF")


if __name__ == "__main__":
    main()
