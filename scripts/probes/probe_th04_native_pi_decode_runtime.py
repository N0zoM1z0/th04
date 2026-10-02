#!/usr/bin/env python3
"""Compare TH04-local packed PI decoding with a pinned historical DOS oracle."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis/reconstruction/probes").resolve()
sys.path.insert(0, str(ROOT))
from scripts.lib.pc98 import parse_mz  # noqa: E402
from scripts.probes.prepare_th04_maine_diagnostic_hdi import Fat12  # noqa: E402
from scripts.probes.probe_th04_pf_archive import ARCHIVES, parse_archive, u16, u32  # noqa: E402

RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
SUPPORT = ROOT / "_reference/ReC98/bin/masters.lib"
SUPPORT_SHA256 = "6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6"
PRODUCT = ("src/shared/formats/pi_decode.cpp", "src/shared/formats/pf_archive.cpp",
           "src/shared/memory/heap.cpp", "src/shared/hardware/graph_pi_free.cpp",
           "src/shared/formats/pi_load.cpp", "src/shared/formats/pi_state.cpp")
ASSEMBLY = ("src/shared/formats/pf_state.asm", "src/shared/formats/pf_int21.asm")
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-DTH04P")
MEMBERS = ("CONG10.PI", "CONG14.PI")

REFERENCE = r'''#include <stdio.h>
#include <dos.h>
struct PiHeader {
    char far *comment; unsigned commentlen;
    unsigned char mode,n,m,plane;
    char machine[4]; unsigned maexlen;
    void far *maex; unsigned xsize,ysize;
    unsigned char palette[48];
};
extern "C" int near pascal mem_assign_dos(unsigned);
extern "C" int near pascal graph_pi_load_pack(const char near *, PiHeader near *, void far *near *);
static PiHeader header;
static void far *image;
int main(void)
{
    if (mem_assign_dos(21000) != 0 || sizeof(PiHeader) != 72) return 1;
    if (graph_pi_load_pack("IMAGE.PI", &header, &image) != 0) return 2;
    if (header.xsize != 640 || header.ysize != 400 || FP_OFF(image) != 640) return 3;
    unsigned base = FP_SEG(image), off = FP_OFF(image);
    unsigned long count = (unsigned long)header.xsize * header.ysize / 2UL;
    unsigned long hash = 2166136261UL;
    for (unsigned long at = 0; at < count; at++) {
        unsigned long linear = (unsigned long)off + at;
        unsigned char value = *(unsigned char far *)MK_FP(base + (unsigned)(linear >> 4),
                                                         (unsigned)(linear & 15u));
        hash = (hash ^ value) * 16777619UL;
    }
    printf("REFERENCE_HASH=%08lX COUNT=%lu\n", hash, count);
    return 0;
}
'''

PRODUCT_TEST = r'''#include <stdio.h>
#include <dos.h>
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/formats/pi.hpp"
#include "src/shared/runtime/api.hpp"
extern "C" unsigned pferrno;
static PiHeader header;
static void far *image;
static int check(const char far *name, unsigned long expected, int number)
{
    int result = graph_pi_load_pack(name, &header, &image);
    if (result || sizeof(PiHeader) != 72 || header.commentlen != 0 ||
        header.xsize != 640 || header.ysize != 400 || header.mode != 0 ||
        header.plane != 4 || FP_OFF(image) != 640) {
        printf("PI_FAIL_%d RESULT=%d\n", number, result);
        return number;
    }
    unsigned base = FP_SEG(image), off = FP_OFF(image);
    unsigned long count = (unsigned long)header.xsize * header.ysize / 2UL;
    unsigned long hash = 2166136261UL;
    for (unsigned long at = 0; at < count; at++) {
        unsigned long linear = (unsigned long)off + at;
        unsigned char value = *(unsigned char far *)MK_FP(base + (unsigned)(linear >> 4),
                                                         (unsigned)(linear & 15u));
        hash = (hash ^ value) * 16777619UL;
    }
    graph_pi_free(&header, image);
    image = 0;
    if (hash != expected) {
        printf("PI_FAIL_%d HASH=%08lX EXPECTED=%08lX\n", number, hash, expected);
        return number;
    }
    return 0;
}
int main(void)
{
    if (mem_assign_dos(21000) != 0) return 1;
    pfstart((const unsigned char far *)"OP.DAT");
    if (pferrno) return 2;
    if (check("CONG10.PI", 0x@HASH10@UL, 10)) return 10;
    if (check("RAW10.PI", 0x@HASH10@UL, 11)) return 11;
    if (check("CONG14.PI", 0x@HASH14@UL, 14)) return 14;
    if (check("RAW14.PI", 0x@HASH14@UL, 15)) return 15;
    if (graph_pi_load_pack("BAD.PI", &header, &image) != -13 || image) return 20;
    if (graph_pi_load_pack("ABSENT.PI", &header, &image) != -2 || image) return 21;
    pfend();
    if (check("RAW10.PI", 0x@HASH10@UL, 22)) return 22;
    if (pi_load(0, "RAW10.PI") != 0 || !pi_buffers[0]) return 24;
    pi_free(0);
    if (pi_buffers[0]) return 25;
    if (pi_load(0, "RAW14.PI") != 0 || !pi_buffers[0]) return 26;
    pi_free(0);
    if (pi_buffers[0]) return 27;
    if (mem_unassign() != 1) return 23;
    puts("PI_PASS");
    return 0;
}
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], work: Path, env: dict[str, str], log: Path) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(command, cwd=work, env=env, capture_output=True, timeout=240)
    log.write_bytes(json.dumps(command).encode() + f"\nexit={result.returncode}\n".encode()
                    + result.stdout + result.stderr)
    return result


def compile_cpp(source: str, model: str, work: Path, env: dict[str, str], log: Path,
                runner: Path, short_name: str) -> str:
    before = set((work / "obj").glob("*.obj"))
    command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS, model, "-nobj/", source]
    if run(command, work, env, log).returncode:
        raise RuntimeError(f"TC4J failed: {log}")
    created = set((work / "obj").glob("*.obj")) - before
    if len(created) != 1:
        raise RuntimeError(f"expected one object from {source}: {created}")
    obj = work / "obj" / f"{short_name}.obj"
    created.pop().rename(obj)
    return "obj\\" + obj.name


def audit_mz(path: Path) -> dict:
    mz = parse_mz(path.read_bytes())
    if not mz.valid:
        raise ValueError(f"invalid MZ: {mz.errors}")
    sites = sorted(rel.linear for rel in mz.relocations)
    values = [u16(mz.program_image, site) for site in sites]
    paragraphs = (len(mz.program_image) + 15) // 16
    if (len(set(sites)) != len(sites)
            or any(site + 2 > len(mz.program_image) for site in sites)
            or any(right < left + 2 for left, right in zip(sites, sites[1:]))
            or any(value >= paragraphs for value in values)):
        raise ValueError("invalid MZ relocation sites or values")
    for load in (0x2000, 0x6000):
        if any(load + value > 0xffff for value in values):
            raise ValueError("MZ relocation would wrap DOS segment")
        mz.relocated_program_image(load)
    return {"relocations": len(sites), "load_segments": [0x2000, 0x6000]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(PRIVATE):
        parser.error("output must be a new private directory")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    if sha(RUNNER) != RUNNER_SHA256 or sha(SUPPORT) != SUPPORT_SHA256:
        raise ValueError("pinned runner or historical library drift")
    config = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    image = (ROOT / config["image"]["path"]).read_bytes()
    if (len(image) != config["image"]["size"]
            or hashlib.sha256(image).hexdigest() != config["image"]["sha256"]):
        raise ValueError("pinned HDI drift")
    fat = Fat12(bytearray(image))
    genso = fat.find_entry([fat.root], b"GENSO      ")
    directory = [fat.cluster_offset(c) for c in fat.chain(u16(fat.image, genso + 26))]
    expected = ARCHIVES["op_end"]
    entry = fat.find_entry(directory, expected["fat_name"])
    blob = fat.file_bytes(u16(fat.image, entry + 26), u32(fat.image, entry + 28))
    if sha_bytes(blob) != expected["sha256"]:
        raise ValueError("pinned PAR archive drift")
    _, members = parse_archive(blob, "op_end", expected)

    output.mkdir(parents=True)
    ref = output / "reference"
    ref.mkdir()
    (ref / "obj").mkdir()
    (ref / "bin").mkdir()
    shutil.copy2(SUPPORT, ref / "bin/masters.lib")
    (ref / "reference.cpp").write_text(REFERENCE, encoding="ascii")
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    ref_obj = compile_cpp("reference.cpp", "-ms", ref, env, output / "reference-compile.log",
                          RUNNER, "reference")
    (ref / "obj/link.rsp").write_text(
        "-c -s -E c0s.obj " + ref_obj +
        ", bin\\reference.exe, obj\\reference.map, bin\\masters.lib emu.lib maths.lib cs.lib\n",
        encoding="ascii")
    if run(["wine", str(RUNNER), "-e", "-x", "tlink", "@obj\\link.rsp"],
           ref, env, output / "reference-link.log").returncode:
        raise RuntimeError("historical reference TLINK failed")
    historical = {}
    for name in MEMBERS:
        (ref / "IMAGE.PI").write_bytes(members[name])
        log = output / f"reference-{name}.log"
        result = run(["wine", str(RUNNER), "-e", "-x", "bin\\reference.exe"],
                     ref, env, log)
        found = re.search(rb"REFERENCE_HASH=([0-9A-F]{8}) COUNT=128000", result.stdout)
        if result.returncode or not found:
            raise RuntimeError(f"historical reference runtime failed: {log}")
        historical[name] = int(found.group(1), 16)

    work = output / "product"
    shutil.copytree(ROOT / "src", work / "src")
    (work / "obj").mkdir()
    (work / "bin").mkdir()
    (work / "OP.DAT").write_bytes(blob)
    for original, loose in (("CONG10.PI", "RAW10.PI"), ("CONG14.PI", "RAW14.PI")):
        (work / loose).write_bytes(members[original])
    (work / "BAD.PI").write_bytes(b"not a PI file\n")
    test = work / "test.cpp"
    test.write_text(PRODUCT_TEST.replace("@HASH10@", f"{historical['CONG10.PI']:08X}")
                    .replace("@HASH14@", f"{historical['CONG14.PI']:08X}"), encoding="ascii")
    objects = []
    for index, source in enumerate((*PRODUCT, "test.cpp")):
        objects.append(compile_cpp(source, "-ml", work, env,
                                   output / f"product-compile-{index}.log", RUNNER,
                                   f"unit{index}"))
    for index, source in enumerate(ASSEMBLY):
        obj = f"obj\\asm{index}.obj"
        command = ["wine", "cmd", "/d", "/c",
                   "set PATH=C:\\TASM50\\BIN;C:\\TC4\\BIN;%PATH%&&"
                   f"tasm32 /m /mx /kh32768 /t /dGAME=4 /dTH04_LARGE_PRODUCT=1 "
                   f"{source.replace('/', chr(92))} {obj}"]
        log = output / f"product-assemble-{index}.log"
        if run(command, work, env, log).returncode:
            raise RuntimeError(f"TASM failed: {log}")
        objects.append(obj)
    (work / "obj/link.rsp").write_text(
        "-c -s -E c0l.obj " + " ".join(objects) +
        ", bin\\pitest.exe, obj\\pitest.map, emu.lib mathl.lib cl.lib\n",
        encoding="ascii")
    if run(["wine", str(RUNNER), "-e", "-x", "tlink", "@obj\\link.rsp"],
           work, env, output / "product-link.log").returncode:
        raise RuntimeError("TH04-only PI test TLINK failed")
    result = run(["wine", str(RUNNER), "-e", "-x", "bin\\pitest.exe"],
                 work, env, output / "product-runtime.log")
    passed = result.returncode == 0 and b"PI_PASS" in result.stdout
    relocation = audit_mz(work / "bin/pitest.exe")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "archive_sha256": sha_bytes(blob),
        "resource_sha256": {name: sha_bytes(members[name]) for name in MEMBERS},
        "source_sha256": {path: sha(ROOT / path) for path in (*PRODUCT, *ASSEMBLY)},
        "runner_sha256": RUNNER_SHA256,
        "historical_library_sha256": SUPPORT_SHA256,
        "historical_mz_sha256": sha(ref / "bin/reference.exe"),
        "historical_hashes": {name: f"{historical[name]:08X}" for name in MEMBERS},
        "product_test_mz_sha256": sha(work / "bin/pitest.exe"),
        "product_test_relocations": relocation,
        "product_runtime_log_sha256": sha(output / "product-runtime.log"),
        "product_exit": result.returncode,
        "passed": passed,
        "limit": "Historical small-model library is a behavioral calibration only; local large-model service is tested in DOS, not an independent MAINE PC-98 launch.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"passed": passed, "historical_hashes": receipt["historical_hashes"],
                      "mz_relocations": relocation["relocations"]}, sort_keys=True))
    return 0 if passed else 1


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
