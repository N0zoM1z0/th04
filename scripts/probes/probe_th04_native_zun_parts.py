#!/usr/bin/env python3
"""Build ZUN's maintained COM parts without historical target/snapshot inputs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]
from lib.omf import describe_omf
from replay_th04_zun_selector import (RUNNER, RUNNER_SHA256, TASM, TASM_SHA256,
                                     TLINK, TLINK_SHA256, sha)

PARTS = {
    "selector": [("selector", ["src/zun/launcher/selector.asm"])],
    "launcher_tails": [
        ("moveup", ["src/zun/launcher/selector_moveup.asm"]),
        ("custom", ["src/zun/launcher/customization_stub.asm"])],
    "ongchk": [("ongchk", ["src/zun/ongchk/ongchk.asm"])],
    "zuninit": [("zuninit", ["src/zun/zuninit/" + name + ".asm" for name in
        ("interrupt_ui", "text_support", "messages", "resident_check", "main", "trailing_text")])],
    "memchk": [("memchk", ["src/zun/memchk/main.cpp", "src/shared/dos/dos_puts2.asm",
                            "src/shared/dos/dos_maxfree.asm"])],
}


def execute(command: list[str], work: Path, log: Path) -> None:
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    done = subprocess.run(command, cwd=work, env=env, capture_output=True,
                          text=True, timeout=180)
    log.write_text(json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + done.stderr)
    if done.returncode:
        raise RuntimeError(f"ZUN tool failed: {log}")


def build(component: str, output: Path, label: str) -> dict:
    work = output / label
    work.mkdir()
    products = {}
    for name, sources in PARTS[component]:
        objects = []
        for index, source in enumerate(sources):
            original = ROOT / source
            local = work / (f"{name}{index}" + original.suffix)
            local.write_bytes(original.read_text(encoding="utf-8").encode("cp932"))
            os.utime(local, (946684800, 946684800))
            obj = local.with_suffix(".obj")
            if original.suffix == ".cpp":
                command = ["wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.",
                           "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-mt", local.name]
            else:
                command = ["wine", str(TASM), "/m", "/mx", "/kh32768",
                           f"{local.name},{obj.name}"]
            execute(command, work, work / f"{local.stem}.log")
            if not describe_omf(obj.read_bytes())["valid"]:
                raise RuntimeError(f"invalid ZUN object: {obj}")
            objects.append(obj.name)
        suffix = ".bin" if component in ("selector", "launcher_tails") else ".com"
        binary = work / (name + suffix)
        startup = "c0t.obj " if component == "memchk" else ""
        libraries = "emu.lib maths.lib ct.lib" if component == "memchk" else ""
        response = f"-c -s -t {startup}{' '.join(objects)},{binary.name},{name}.map,{libraries}\r\n"
        (work / "LINK.RSP").write_bytes(response.encode("ascii"))
        execute(["wine", str(RUNNER), "-e", "-x", "tlink", "@LINK.RSP"],
                work, work / f"{name}-link.log")
        data = binary.read_bytes()
        if not data:
            raise RuntimeError(f"empty COM part: {binary}")
        # Preserve the composite input location used for the Tiny MEMCHK part.
        if component == "memchk":
            destination = work / "work/bin/th04/memchk.com"
            destination.parent.mkdir(parents=True)
            destination.write_bytes(data)
        products[name] = {"size": len(data), "sha256": sha(data)}
    return products


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", required=True, choices=PARTS)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or output.parent != ROOT / ".analysis/reconstruction/probes":
        parser.error("use a new direct child of .analysis/reconstruction/probes")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, stdout=subprocess.DEVNULL)
    for tool, digest in ((TASM, TASM_SHA256), (TLINK, TLINK_SHA256), (RUNNER, RUNNER_SHA256)):
        if sha(tool.read_bytes()) != digest:
            raise RuntimeError(f"pinned tool identity drift: {tool}")
    output.mkdir()
    rounds = {label: build(args.component, output, label) for label in ("a", "b")}
    if rounds["a"] != rounds["b"]:
        raise RuntimeError("cold ZUN part builds differ")
    sources = {source: sha((ROOT / source).read_bytes()) for _, paths in PARTS[args.component]
               for source in paths}
    (output / "receipt.json").write_text(json.dumps({
        "observed_utc": datetime.now(timezone.utc).isoformat(), "artifact": "th04-zun",
        "component": args.component, "sources": sources, "rounds": rounds,
        "cold_equal": True, "acceptance": "source build; no target-byte comparison",
    }, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
