#!/usr/bin/env python3
"""Falsify a private emulator observer using an independent DIV-zero COM."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

from build_th04_cpu_fault_emulator import PRIVATE, ROOT, attest, sha


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    observer = parser.add_mutually_exclusive_group(required=True)
    observer.add_argument("--emulator-receipt", type=Path)
    observer.add_argument("--cpu-debugger-receipt", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--guest-boot", action="store_true",
                        help="run the fixture through the pinned DOS/EMM386 image")
    args = parser.parse_args()
    receipt_path = args.emulator_receipt or args.cpu_debugger_receipt
    if args.cpu_debugger_receipt:
        from prepare_th04_primary_cpu_debugger import attest_debugger, command_prefix
        emulator = attest_debugger(receipt_path)
    else:
        emulator = attest(receipt_path)
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(PRIVATE):
        parser.error("use a new private calibration directory")
    runtime = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    config = ROOT / runtime["primary"]["config"]
    if sha(config) != runtime["primary"]["config_sha256"]:
        raise ValueError("pinned configuration identity drift")
    output.mkdir(parents=True)
    source = Path(__file__).with_name("th04_cpu_fault_fixture.asm")
    fixture = output / "fault.com"
    nasm_name = shutil.which("nasm")
    if nasm_name is None:
        raise ValueError("NASM is required for the independent fixture")
    nasm = Path(nasm_name).resolve()
    assemble = [str(nasm), "-f", "bin", str(source), "-o", str(fixture)]
    subprocess.run(assemble, check=True)
    command = [emulator["binary"], "-defaultconf", "-defaultmapper", "-conf", str(config),
               "-fastlaunch", "-nogui", "-nomenu", "-exit", "-time-limit", "5",
               "-c", f'mount c "{output}"', "-c", "c:", "-c", "fault.com", "-c", "exit"]
    boot_image = None
    if args.guest_boot:
        sys.path.insert(0, str(ROOT / "scripts"))
        from prepare_product_hdi import Fat12, replace_file
        from prepare_th04_maine_diagnostic_hdi import u16
        source_image = ROOT / runtime["image"]["path"]
        if sha(source_image) != runtime["image"]["sha256"]:
            raise ValueError("pinned DOS image identity drift")
        fs = Fat12(bytearray(source_image.read_bytes()))
        folder = fs.find_entry([fs.root], b"DOS        ")
        entries = [fs.cluster_offset(c) for c in fs.chain(u16(fs.image, folder + 26))]
        # This disposable calibration image replaces only the DOS menu utility.
        # AUTOEXEC still follows the original DOS/EMM386 startup route.
        menu = fs.find_entry(entries, b"MENU    COM")
        replace_file(fs, menu, fixture.read_bytes())
        image = output / "calibration.hdi"
        image.write_bytes(fs.image)
        boot_image = dict(source_sha256=sha(source_image), fixture_hdi_sha256=sha(image))
        command = [emulator["binary"], "-defaultconf", "-defaultmapper", "-conf", str(config),
                   "-fastlaunch", "-nogui", "-nomenu", "-exit", "-time-limit", "15",
                   "-c", f'imgmount 2 "{image}" -t hdd -fs none', "-c", "boot -l c"]
    env = os.environ.copy()
    env.update(SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", TH04_CPU_FAULT_DIR=str(output))
    if args.cpu_debugger_receipt:
        command = command_prefix(emulator) + command
        env["TH04_CPU_DEBUG_FILE"] = emulator["debug_file"]
    with (output / "boot.log").open("wb") as stream:
        result = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                timeout=30, check=True)
    packets = re.findall(r"^TH04_CPUFAULT .+$", (output / "boot.log").read_text(), re.M)
    if len(packets) != 1:
        raise ValueError("fixture must record exactly one CPU exception")
    fields = packets[0].split()
    if (len(fields) != 17 or fields[2] != "00" or fields[9] != "0001"
            or fields[10] != "0000" or fields[12] != "0000"
            or not fields[3] == fields[5] == fields[7]):
        raise ValueError("fixture exception registers disagree")
    offset = int(fields[4], 16) - 0x100
    data = fixture.read_bytes()
    # The final four bytes save the old INT0 vector and are mutable data.
    end = len(data) - 4
    code = (output / "cpu-fault-00-code.bin").read_bytes()
    if (not 0 <= offset < end or code[:2] != bytes.fromhex("f7f3")
            or code[:end-offset] != data[offset:end]):
        raise ValueError("fixture exception code disagrees")
    for name, size in (("code", 64), ("stack", 64), ("data", 65536)):
        if (output / f"cpu-fault-00-{name}.bin").stat().st_size != size:
            raise ValueError("fixture memory snapshot is incomplete")
    context = output / "cpu-fault-00-memory.json"
    if args.guest_boot and (not context.exists() or not json.loads(context.read_text())["vm86"]):
        raise ValueError("guest-boot fixture did not observe VM86 memory")
    receipt = dict(scope="independent real-mode DIV-zero observer calibration, not gameplay acceptance",
                   passed=True, returncode=result.returncode, packet=packets[0],
                   emulator_receipt_sha256=sha(receipt_path), config_sha256=sha(config),
                   fixture_source_sha256=sha(source), fixture_sha256=sha(fixture),
                   nasm=dict(path=str(nasm), sha256=sha(nasm),
                             version=subprocess.check_output([str(nasm), "-v"], text=True).strip()),
                   commands=[assemble, command], instruction_bytes_checked=end-offset,
                   mutable_saved_vector_bytes=4,
                   guest_boot_image=boot_image,
                   memory_context_sha256=(sha(context) if context.exists() else None),
                   files={p.name: sha(p) for p in sorted(output.glob("cpu-fault-*.bin"))},
                   boot_log_sha256=sha(output / "boot.log"))
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(dict(passed=True, receipt=str(output / "receipt.json"), packet=packets[0])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
