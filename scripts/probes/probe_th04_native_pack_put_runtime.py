#!/usr/bin/env python3
"""Exercise clipped TH04 packed-pixel rows with four fake VRAM planes."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis/reconstruction/probes").resolve()
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
SOURCES = ("src/shared/hardware/graph_pack_put_8.cpp",
           "src/shared/hardware/graph_pack_put_8_noclip.cpp")
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-DTH04P", "-ml")
TEST = r'''#include <stdio.h>
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/vram_planes.hpp"

extern "C" unsigned __cdecl ClipYT = 0, ClipYH = 399;
unsigned char far *VRAM_PLANE_B;
unsigned char far *VRAM_PLANE_R;
unsigned char far *VRAM_PLANE_G;
unsigned char far *VRAM_PLANE_E;
static unsigned char b[160], r[160], g[160], e[160];
static const unsigned char row[8] = {0x12, 0x34, 0x56, 0x78,
                                     0x87, 0x65, 0x43, 0x21};

static int fail(int n) { printf("PACK_PUT_FAIL_%d\n", n); return n; }
int main(void)
{
    VRAM_PLANE_B = b; VRAM_PLANE_R = r;
    VRAM_PLANE_G = g; VRAM_PLANE_E = e;
    graph_pack_put_8(0, 0, row, 8);
    if(b[0] != 0xAA || r[0] != 0x66 || g[0] != 0x1E || e[0] != 1)
        return fail(1);
    ClipYT = 1; ClipYH = 0;
    graph_pack_put_8(0, 0, row, 8);
    if(b[0] != 0xAA || b[80] != 0) return fail(2);
    graph_pack_put_8(0, 1, row, 8);
    if(b[80] != 0xAA || r[80] != 0x66 || g[80] != 0x1E || e[80] != 1)
        return fail(3);
    ClipYT = 0; ClipYH = 399;
    b[0] = 0; r[0] = 0; g[0] = 0; e[0] = 0;
    graph_pack_put_8(-8, 0, row, 16);
    if(b[0] != 0x55 || r[0] != 0x66 || g[0] != 0x78 || e[0] != 0x80)
        return fail(4);
    graph_pack_put_8(632, 0, row, 16);
    if(b[79] != 0xAA || r[79] != 0x66 || g[79] != 0x1E || e[79] != 1)
        return fail(5);
    // Exercise every packed byte in every position against a scalar pixel
    // interpretation, independent of the product's pair lookup table.
    unsigned char varied[8];
    for(unsigned seed = 0; seed < 256u; seed++) {
        for(unsigned at = 0; at < 8u; at++) varied[at] = (unsigned char)(seed + at * 37u);
        graph_pack_put_8(0, 0, varied, 16);
        for(unsigned byte_x = 0; byte_x < 2u; byte_x++) {
            for(unsigned plane = 0; plane < 4u; plane++) {
                unsigned char expected = 0;
                for(unsigned pixel = 0; pixel < 8u; pixel++) {
                    unsigned char pair = varied[byte_x * 4u + pixel / 2u];
                    unsigned char color = ((pixel & 1u) ? (pair & 15u) : (pair >> 4));
                    if(color & (1u << plane)) expected |= (0x80u >> pixel);
                }
                unsigned char actual = (plane == 0) ? b[byte_x] :
                    ((plane == 1) ? r[byte_x] : ((plane == 2) ? g[byte_x] : e[byte_x]));
                if(actual != expected) return fail(6);
            }
        }
    }
    puts("PACK_PUT_PASS");
    return 0;
}
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], work: Path, env: dict[str, str], log: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=work, env=env, capture_output=True,
                            text=True, timeout=240)
    log.write_text(json.dumps(command) + f"\nexit={result.returncode}\n"
                   + result.stdout + result.stderr, encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(PRIVATE):
        parser.error("output must be a new private directory")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, stdout=subprocess.DEVNULL)
    if sha(RUNNER) != RUNNER_SHA256:
        raise ValueError("MS-DOS Player identity drift")

    output.mkdir(parents=True)
    work = output / "source"
    shutil.copytree(ROOT / "src", work / "src")
    (work / "obj").mkdir()
    (work / "bin").mkdir()
    test = work / "test.cpp"
    test.write_text(TEST, encoding="ascii")
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    objects: list[str] = []
    for index, name in enumerate((*SOURCES, "test.cpp")):
        before = set((work / "obj").glob("*.obj"))
        command = ["wine", str(RUNNER), "-e", "-x", "tcc", *FLAGS, "-nobj/", name]
        log = output / f"compile-{index}.log"
        if run(command, work, env, log).returncode:
            raise RuntimeError(f"TC4J failed: {log}")
        created = set((work / "obj").glob("*.obj")) - before
        if len(created) != 1:
            raise RuntimeError(f"expected one object from {name}: {created}")
        objects.append("obj\\" + created.pop().name)
    (work / "obj/link.rsp").write_text(
        "-c -s -E c0l.obj " + " ".join(objects) +
        ", bin\\packtest.exe, obj\\packtest.map, emu.lib mathl.lib cl.lib\n",
        encoding="ascii",
    )
    if run(["wine", str(RUNNER), "-e", "-x", "tlink", "@obj\\link.rsp"],
           work, env, output / "link.log").returncode:
        raise RuntimeError("TLINK failed; inspect link.log")
    exe = work / "bin/packtest.exe"
    result = run(["wine", str(RUNNER), "-e", "-x", "bin\\packtest.exe"],
                 work, env, output / "runtime.log")
    passed = result.returncode == 0 and "PACK_PUT_PASS" in result.stdout
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_sha256": {name: sha(ROOT / name) for name in SOURCES},
        "harness_sha256": sha(test),
        "runner_sha256": RUNNER_SHA256,
        "mz_sha256": sha(exe),
        "runtime_log_sha256": sha(output / "runtime.log"),
        "returncode": result.returncode,
        "passed": passed,
        "limit": "Fake plane arrays test packed nibbles and clipping; real PC-98 VRAM remains untested.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                                          encoding="utf-8")
    print(json.dumps({"passed": passed, "returncode": result.returncode,
                      "runtime_log": str(output / "runtime.log")}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
