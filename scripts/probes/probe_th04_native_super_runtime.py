#!/usr/bin/env python3
"""Run a TH04-only BFNT sprite lifecycle and fake-VRAM DOS differential."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.probes.prepare_th04_maine_diagnostic_hdi import Fat12  # noqa: E402
from scripts.probes.probe_th04_pf_archive import ARCHIVES, parse_archive, u16, u32  # noqa: E402
from scripts.probes.probe_th04_native_pi_decode_runtime import (  # noqa: E402
    PRIVATE, RUNNER, RUNNER_SHA256, SUPPORT, SUPPORT_SHA256,
    audit_mz, compile_cpp, run, sha, sha_bytes,
)

PRODUCT = ("src/shared/hardware/super_sprite.cpp", "src/shared/memory/heap.cpp",
           "src/shared/formats/pf_archive.cpp")
ASSEMBLY = ("src/shared/hardware/super_state.asm", "src/shared/hardware/vram_state.asm",
            "src/shared/hardware/planar_blit.asm",
            "src/shared/hardware/palette_state.asm", "src/shared/formats/pf_state.asm",
            "src/shared/formats/pf_int21.asm")
MEMBER = "SCNUM2.BFT"

REFERENCE = r'''#include <stdio.h>
#include <dos.h>
extern "C" int near pascal mem_assign_dos(unsigned);
extern "C" int near pascal super_entry_bfnt(const char near *);
extern "C" unsigned super_patnum;
extern "C" unsigned super_patdata[512];
extern "C" unsigned super_patsize[512];
extern "C" unsigned char Palettes[48];
static unsigned long step(unsigned long h, unsigned char v)
{
    return (h ^ v) * 16777619UL;
}
int main(void)
{
    if (mem_assign_dos(21000) != 0) return 1;
    int count = super_entry_bfnt("SCNUM2.BFT");
    if (count != 20 || super_patnum != 20 || super_patsize[0] != 0x0210) return 2;
    unsigned long pattern = 2166136261UL, palette = 2166136261UL;
    for (unsigned i = 0; i < 20u; i++) {
        unsigned char far *data = (unsigned char far *)MK_FP(super_patdata[i], 0);
        for (unsigned at = 0; at < 160u; at++) pattern = step(pattern, data[at]);
    }
    for (unsigned at = 0; at < 48u; at++) palette = step(palette, Palettes[at]);
    printf("PAT=%08lX PAL=%08lX\n", pattern, palette);
    return 0;
}
'''

TEST = r'''#include <stdio.h>
#include <dos.h>
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/vram_planes.hpp"
#include "src/shared/runtime/api.hpp"
extern "C" unsigned pferrno;
static void __seg *screen[4];
static unsigned long hash_byte(unsigned long hash, unsigned char value)
{
    return (hash ^ value) * 16777619UL;
}
static unsigned long pattern_hash(void)
{
    unsigned long hash = 2166136261UL;
    for (unsigned pat = 0; pat < 20u; pat++) {
        unsigned char far *data = (unsigned char far *)MK_FP(super_patdata[pat], 0);
        for (unsigned at = 0; at < 160u; at++) hash = hash_byte(hash, data[at]);
    }
    return hash;
}
static unsigned long palette_hash(void)
{
    unsigned long hash = 2166136261UL;
    for (unsigned color = 0; color < 16u; color++) {
        for (unsigned comp = 0; comp < 3u; comp++)
            hash = hash_byte(hash, Palettes[color].v[comp]);
    }
    return hash;
}
static unsigned long screen_hash(void)
{
    unsigned long hash = 2166136261UL;
    for (unsigned plane = 0; plane < 4u; plane++) {
        unsigned char far *data = (unsigned char far *)MK_FP((unsigned)screen[plane], 0);
        for (unsigned at = 0; at < 32000u; at++) hash = hash_byte(hash, data[at]);
    }
    return hash;
}
int main(void)
{
    if (mem_assign_dos(21000) != 0) return 1;
    for (unsigned plane = 0; plane < 4u; plane++) {
        screen[plane] = hmem_allocbyte(32000u);
        if (!screen[plane]) return 2;
        unsigned char far *data = (unsigned char far *)MK_FP((unsigned)screen[plane], 0);
        for (unsigned at = 0; at < 32000u; at++)
            data[at] = (unsigned char)((at * 37u + plane * 13u) & 255u);
    }
    VRAM_PLANE_B = (unsigned char far *)MK_FP((unsigned)screen[0], 0);
    VRAM_PLANE_R = (unsigned char far *)MK_FP((unsigned)screen[1], 0);
    VRAM_PLANE_G = (unsigned char far *)MK_FP((unsigned)screen[2], 0);
    VRAM_PLANE_E = (unsigned char far *)MK_FP((unsigned)screen[3], 0);
    pfstart((const unsigned char far *)"OP.DAT");
    if (pferrno || super_entry_bfnt("SCNUM2.BFT") != 20 || super_patnum != 20u ||
        !super_buffer || super_patsize[0] != 0x0210u) return 3;
    unsigned long actual_patterns = pattern_hash();
    unsigned long actual_palette = palette_hash();
    if (actual_patterns != 0x@PATTERN_HASH@UL || actual_palette != 0x@PALETTE_HASH@UL) {
        printf("SPRITE_DATA=%08lX PALETTE=%08lX\n", actual_patterns, actual_palette);
        return 4;
    }
    super_put(123, 45, 3);
    super_put(635, 392, 7);
    super_put(-5, -3, 2);
    unsigned long actual_screen = screen_hash();
    if (actual_screen != 0x@SCREEN_HASH@UL) {
        printf("SPRITE_SCREEN=%08lX EXPECTED=%08lX\n", actual_screen, 0x@SCREEN_HASH@UL);
        return 5;
    }
    if (super_cancel_pat(19) || super_patnum != 19u ||
        super_cancel_pat(19) != -31) return 6;
    super_free();
    if (super_patnum || super_buffer || super_patdata[0] || super_patsize[0]) return 7;
    if (super_entry_bfnt("MISSING.BFT") != -2 ||
        super_entry_bfnt("BAD.BFT") != -13 || super_patnum) return 8;
    pfend();
    if (super_entry_bfnt("LOOSE.BFT") != 20 ||
        pattern_hash() != 0x@PATTERN_HASH@UL) return 9;
    super_free();
    for (unsigned p = 0; p < 4u; p++) hmem_free(screen[p]);
    if (mem_unassign() != 1) return 10;
    puts("SUPER_PASS");
    return 0;
}
'''


def fnv(data: bytes) -> str:
    value = 2166136261
    for byte in data:
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return f"{value:08X}"


def expected_pixels(blob: bytes) -> tuple[bytes, bytes, bytes]:
    if blob[:5] != b"BFNT\x1a" or blob[5] != 0x83 or u16(blob, 8) != 16 or u16(blob, 10) != 16:
        raise ValueError("SCNUM2 BFNT header drift")
    if u16(blob, 12) != 0 or u16(blob, 14) != 19 or u16(blob, 28) != 0:
        raise ValueError("SCNUM2 BFNT counts or extension drift")
    palette = b"".join(bytes((blob[80 - 48 + col * 3 + 1],
                              blob[80 - 48 + col * 3 + 2],
                              blob[80 - 48 + col * 3])) for col in range(16))
    patterns: list[bytes] = []
    colors: list[list[list[int]]] = []
    for num in range(20):
        raw = blob[80 + num * 128:80 + (num + 1) * 128]
        if len(raw) != 128:
            raise ValueError("short SCNUM2 pattern")
        pixels = [[(raw[row * 8 + col] >> shift) & 15
                   for col in range(8) for shift in (4, 0)] for row in range(16)]
        colors.append(pixels)
        planes = [bytearray(32) for _ in range(5)]
        for row in range(16):
            for col in range(16):
                color = pixels[row][col]
                if color == 0:
                    continue
                bit = 0x80 >> (col & 7)
                at = row * 2 + (col >> 3)
                planes[0][at] |= bit
                for plane in range(4):
                    if color & (1 << plane):
                        planes[plane + 1][at] |= bit
        patterns.append(b"".join(planes))
    screen = [bytearray(((at * 37 + plane * 13) & 255) for at in range(32000))
              for plane in range(4)]
    for x, y, num in ((123, 45, 3), (635, 392, 7), (-5, -3, 2)):
        for row in range(16):
            for col in range(16):
                sx, sy = x + col, y + row
                if not (0 <= sx < 640 and 0 <= sy < 400):
                    continue
                color = colors[num][row][col]
                if color == 0:
                    continue
                at = sy * 80 + sx // 8
                bit = 0x80 >> (sx & 7)
                for plane in range(4):
                    if color & (1 << plane):
                        screen[plane][at] |= bit
                    else:
                        screen[plane][at] &= 255 ^ bit
    return b"".join(patterns), palette, b"".join(screen)


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
        raise ValueError("DOS runner or historical library identity drift")
    config = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    image = (ROOT / config["image"]["path"]).read_bytes()
    if len(image) != config["image"]["size"] or sha_bytes(image) != config["image"]["sha256"]:
        raise ValueError("pinned HDI drift")
    fat = Fat12(bytearray(image))
    genso = fat.find_entry([fat.root], b"GENSO      ")
    directory = [fat.cluster_offset(c) for c in fat.chain(u16(fat.image, genso + 26))]
    archive = ARCHIVES["op_end"]
    entry = fat.find_entry(directory, archive["fat_name"])
    blob = fat.file_bytes(u16(fat.image, entry + 26), u32(fat.image, entry + 28))
    if sha_bytes(blob) != archive["sha256"]:
        raise ValueError("pinned PAR drift")
    _, members = parse_archive(blob, "op_end", archive)
    fixture = members[MEMBER]
    pattern, palette, screen = expected_pixels(fixture)
    hashes = {"pattern": fnv(pattern), "palette": fnv(palette), "screen": fnv(screen)}

    output.mkdir(parents=True)
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    reference = output / "reference"
    reference.mkdir()
    (reference / "obj").mkdir()
    (reference / "bin").mkdir()
    shutil.copy2(SUPPORT, reference / "bin/masters.lib")
    (reference / MEMBER).write_bytes(fixture)
    (reference / "reference.cpp").write_text(REFERENCE, encoding="ascii")
    ref_obj = compile_cpp("reference.cpp", "-ms", reference, env,
                          output / "reference-compile.log", RUNNER, "reference")
    (reference / "obj/link.rsp").write_text(
        "-c -s -E c0s.obj " + ref_obj +
        ", bin\\reference.exe, obj\\reference.map, bin\\masters.lib emu.lib maths.lib cs.lib\n",
        encoding="ascii")
    if run(["wine", str(RUNNER), "-e", "-x", "tlink", "@obj\\link.rsp"],
           reference, env, output / "reference-link.log").returncode:
        raise RuntimeError("historical sprite oracle TLINK failed")
    historical = run(["wine", str(RUNNER), "-e", "-x", "bin\\reference.exe"],
                     reference, env, output / "reference-runtime.log")
    match = re.search(rb"PAT=([0-9A-F]{8}) PAL=([0-9A-F]{8})", historical.stdout)
    if historical.returncode or not match:
        raise RuntimeError("historical sprite oracle runtime failed")
    historical_hashes = {"pattern": match.group(1).decode(),
                         "palette": match.group(2).decode()}
    if any(historical_hashes[k] != hashes[k] for k in historical_hashes):
        raise ValueError("host BFNT interpretation differs from historical binary")

    work = output / "source"
    shutil.copytree(ROOT / "src", work / "src")
    (work / "obj").mkdir()
    (work / "bin").mkdir()
    (work / "OP.DAT").write_bytes(blob)
    (work / "LOOSE.BFT").write_bytes(fixture)
    (work / "BAD.BFT").write_bytes(b"bad BFNT\n")
    test = TEST.replace("@PATTERN_HASH@", hashes["pattern"])
    test = test.replace("@PALETTE_HASH@", hashes["palette"])
    test = test.replace("@SCREEN_HASH@", hashes["screen"])
    (work / "test.cpp").write_text(test, encoding="ascii")
    objects = []
    for index, source in enumerate((*PRODUCT, "test.cpp")):
        objects.append(compile_cpp(source, "-ml", work, env,
                                   output / f"compile-{index}.log", RUNNER, f"c{index}"))
    for index, source in enumerate(ASSEMBLY):
        obj = f"obj\\a{index}.obj"
        command = ["wine", "cmd", "/d", "/c",
                   "set PATH=C:\\TASM50\\BIN;C:\\TC4\\BIN;%PATH%&&"
                   f"tasm32 /m /mx /kh32768 /t /dGAME=4 /dTH04_LARGE_PRODUCT=1 "
                   f"{source.replace('/', chr(92))} {obj}"]
        if run(command, work, env, output / f"assemble-{index}.log").returncode:
            raise RuntimeError(f"TASM failed on {source}")
        objects.append(obj)
    (work / "obj/link.rsp").write_text(
        "-c -s -E c0l.obj " + " ".join(objects) +
        ", bin\\supertest.exe, obj\\supertest.map, emu.lib mathl.lib cl.lib\n",
        encoding="ascii")
    if run(["wine", str(RUNNER), "-e", "-x", "tlink", "@obj\\link.rsp"], work, env,
           output / "link.log").returncode:
        raise RuntimeError("TH04-only sprite test TLINK failed")
    result = run(["wine", str(RUNNER), "-e", "-x", "bin\\supertest.exe"],
                 work, env, output / "runtime.log")
    relocation = audit_mz(work / "bin/supertest.exe")
    passed = result.returncode == 0 and b"SUPER_PASS" in result.stdout
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "archive_sha256": sha_bytes(blob), "resource_sha256": sha_bytes(fixture),
        "source_sha256": {p: sha(ROOT / p) for p in (*PRODUCT, *ASSEMBLY)},
        "runner_sha256": RUNNER_SHA256, "historical_library_sha256": SUPPORT_SHA256,
        "historical_mz_sha256": sha(reference / "bin/reference.exe"),
        "historical_hashes": historical_hashes,
        "expected_hashes": hashes,
        "test_mz_sha256": sha(work / "bin/supertest.exe"),
        "test_relocations": relocation,
        "runtime_log_sha256": sha(output / "runtime.log"),
        "runtime_exit": result.returncode, "passed": passed,
        "limit": "DOS fake-VRAM and host BFNT interpretation, not a PC-98 hardware launch or target-byte match.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"passed": passed, "expected_hashes": hashes,
                      "relocations": relocation["relocations"]}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
