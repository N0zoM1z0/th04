#!/usr/bin/env python3
"""Build a pinned private DOSBox-X normal-core, read-only demo observer."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import shutil
import subprocess
import tarfile
import time

from build_th04_cpu_fault_emulator import ARCHIVE_SHA256, COMMIT, FLAGS, PRIVATE, sha


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(PRIVATE):
        parser.error('use a fresh private emulator directory')
    if sha(args.archive) != ARCHIVE_SHA256:
        raise ValueError('emulator archive identity drift')
    source = output / 'source'
    source.mkdir(parents=True)
    with tarfile.open(args.archive) as archive:
        archive.extractall(source, filter='data')
    trees = list(source.iterdir())
    if len(trees) != 1:
        raise ValueError('unexpected archive roots')
    work = trees[0]
    core = work / 'src/cpu/core_normal.cpp'
    before = sha(core)
    observer = Path(__file__).with_name('th04_demo_observer.inl')
    observer_bytes = observer.read_bytes()
    (output / observer.name).write_bytes(observer_bytes)
    original = core.read_text()
    anchor = 'Bits CPU_Core_Normal_Run(void) {'
    instruction = '\t\tLOADIP;\n\t\tlast_prefix=MP_NONE;'
    if original.count(anchor) != 1 or original.count(instruction) != 1:
        raise ValueError('normal-core instruction hook drift')
    core.write_text(original.replace(anchor, observer_bytes.decode()+'\n'+anchor).replace(
        instruction, '\t\tth04_demo_observer::observe();\n'+instruction))
    os.nice(15)
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    resource.setrlimit(resource.RLIMIT_AS, (1024*1024*1024, 1024*1024*1024))
    commands = [['bash', 'autogen.sh'], ['./configure', *FLAGS], ['make', '-j1'],
                ['strip', '--strip-debug', 'src/dosbox-x']]
    logs = []
    for i, command in enumerate(commands):
        with (output / f'build-{i}.log').open('w') as stream:
            child = subprocess.Popen(command, cwd=work, stdout=stream,
                                     stderr=subprocess.STDOUT, start_new_session=True)
            try:
                # Bound this owned process group to half of one host CPU. The
                # rest of the machine and other reconstruction sessions are untouched.
                while child.poll() is None:
                    time.sleep(.1)
                    try:
                        os.killpg(child.pid, signal.SIGSTOP)
                    except ProcessLookupError:
                        break
                    time.sleep(.1)
                    try:
                        os.killpg(child.pid, signal.SIGCONT)
                    except ProcessLookupError:
                        break
                if child.wait() != 0:
                    raise subprocess.CalledProcessError(child.returncode, command)
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGCONT)
                    os.killpg(child.pid, signal.SIGTERM)
                    child.wait()
        logs.append(dict(command=command, log_sha256=sha(output / f'build-{i}.log')))
    binary = work / 'src/dosbox-x'
    compilers = {}
    for name in ('gcc', 'g++'):
        path = Path(shutil.which(name)).resolve()
        compilers[name] = dict(path=str(path), sha256=sha(path), version=subprocess.check_output(
            [str(path), '--version'], text=True).splitlines()[0])
    record = dict(schema_version=1, scope='normal-core read-only demo observer; no timing/cross-emulator acceptance',
                  source_commit=COMMIT, source_archive_sha256=ARCHIVE_SHA256,
                  observer_source_sha256=hashlib.sha256(observer_bytes).hexdigest(), core_before_sha256=before,
                  core_after_sha256=sha(core), commands=logs, compilers=compilers,
                  config_header_sha256=sha(work / 'config.h'), binary=str(binary), binary_sha256=sha(binary))
    record['resource_budget'] = dict(cpu_affinity=sorted(os.sched_getaffinity(0)), nice=15,
                                    address_space_bytes=1024*1024*1024, compile_jobs=1, cpu_duty_fraction=.5)
    (output / 'receipt.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(dict(binary=str(binary), sha256=sha(binary))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
