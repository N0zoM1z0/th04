#!/usr/bin/env python3
"""Build a private, pinned DOSBox-X observer without changing game bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / ".analysis/runtime/emulators"
COMMIT = "199aa35f34ea637cca901ada3a431939fcca13f2"
ARCHIVE_SHA256 = "d990ece1dd3ba7ca5c72b35bbfba0a2d2841826452676098e1a09b3dde43bf69"
FLAGS = ["--enable-sdl2", "--disable-sdlnet", "--disable-debug",
         "--disable-libfluidsynth", "--disable-avcodec", "--disable-opengl"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def attest(receipt_path: Path) -> dict:
    receipt_path = receipt_path.resolve()
    if not receipt_path.is_relative_to(PRIVATE):
        raise ValueError("emulator attestation must be private")
    record = json.loads(receipt_path.read_text())
    binary = Path(record["binary"]).resolve()
    observer = Path(__file__).with_name("th04_emulator_fault_observer.inl")
    if (record["source_commit"] != COMMIT
            or record["source_archive_sha256"] != ARCHIVE_SHA256
            or record["observer_source_sha256"] != sha(observer)
            or not binary.is_relative_to(receipt_path.parent)
            or sha(binary) != record["binary_sha256"]):
        raise ValueError("private CPU-observer emulator identity drift")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(PRIVATE):
        parser.error("use a new private emulator directory")
    if sha(args.archive) != ARCHIVE_SHA256:
        raise ValueError("pinned emulator source archive identity drift")
    source = output / "source"
    source.mkdir(parents=True)
    with tarfile.open(args.archive) as archive:
        archive.extractall(source, filter="data")
    trees = list(source.iterdir())
    if len(trees) != 1 or not trees[0].is_dir():
        raise ValueError("unexpected emulator archive root")
    work = trees[0]
    cpu = work / "src/cpu/cpu.cpp"
    before = sha(cpu)
    observer = Path(__file__).with_name("th04_emulator_fault_observer.inl")
    hook = "void CPU_Exception(Bitu which,Bitu error ) {"
    original = cpu.read_text()
    if original.count(hook) != 1:
        raise ValueError("pinned CPU exception hook changed")
    cpu.write_text(original.replace(hook,
        "#include <cstdio>\n#include <cstdlib>\n" + observer.read_text()
        + "\n" + hook + "\n    th04_cpu_fault_observe(which);"))
    commands = [["bash", "autogen.sh"], ["./configure", *FLAGS], ["make", "-j4"]]
    records = []
    for index, command in enumerate(commands):
        log = output / f"build-{index}.log"
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdout=stream,
                           stderr=subprocess.STDOUT, check=True)
        records.append(dict(command=command, log_sha256=sha(log)))
    binary = work / "src/dosbox-x"
    compilers = {}
    for name in ("gcc", "g++"):
        executable = Path(shutil.which(name)).resolve()
        compilers[name] = dict(path=str(executable), sha256=sha(executable),
            version=subprocess.check_output([str(executable), "--version"], text=True).splitlines()[0])
    receipt = dict(scope="private DOSBox-X CPU observer; no primary-profile or gameplay acceptance",
        source_commit=COMMIT, source_archive_sha256=ARCHIVE_SHA256,
        source_url=f"https://codeload.github.com/joncampbell123/dosbox-x/tar.gz/{COMMIT}",
        observer_source_sha256=sha(observer), cpu_before_sha256=before,
        cpu_after_sha256=sha(cpu), commands=records, compilers=compilers,
        config_header_sha256=sha(work / "config.h"), binary=str(binary), binary_sha256=sha(binary))
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(dict(binary=str(binary), sha256=sha(binary))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
