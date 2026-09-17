#!/usr/bin/env python3
"""Test a source-level pause split and byte-aligned DEMO code segments.

This is an isolated compiler/linker diagnostic, not an exact-unit replay.
The two new segment names are hypotheses, not claims about the target OMF.
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

SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001/a/source"
SNAPSHOT_HASHES = {
    "obj/th04/main.@l": "b2ce7be007aa044e83321333bd3a0febc85496d2035cf66be37f863b6bcba2fe",
    "obj/th04/sess.obj": "3816b5f0aaabe5e8646243d22fbe13d40e97f53f012a398ae95ec76ae426f6ad",
    "bin/th04/main.exe": "1c1bcec509b775a6fa994d403d573ede75e74b8781ac5f0db06eb124d5fbae21",
    "obj/th04/main.obj": "4ca3fdc4a7933b4da18a9cd291753fa2438506196c9fd83e7e5fdd63291a9e0a",
    "obj/th04/coanch.obj": "0fbd8400a575e862d9b4f62e4931be08a49c8d6dedf73dc059671e52b9ea0fe9",
}
TCC_FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th04/")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(data: bytes, old: bytes, new: bytes) -> bytes:
    if data.count(old) != 1:
        raise ValueError(f"expected one occurrence of {old[:60]!r}")
    return data.replace(old, new)


def code(obj: bytes, segment: str) -> bytes:
    records = parse_omf(obj)
    chunks = code_ledata(records, segment)
    if not chunks or chunks[0][0] != 0:
        raise ValueError(f"missing {segment} CODE at offset zero")
    output = bytearray(chunks[-1][1])
    cursor = 0
    for start, end, number, _ in chunks:
        if start != cursor:
            raise ValueError(f"non-contiguous {segment} CODE")
        output[start:end] = records[number - 1].data[3:]
        cursor = end
    return bytes(output)


def relocations(image: bytes) -> list[int]:
    if image[:2] != b"MZ":
        raise ValueError("not an MZ image")
    count = int.from_bytes(image[6:8], "little")
    table = int.from_bytes(image[0x18:0x1A], "little")
    if table + count * 4 > len(image):
        raise ValueError("invalid MZ relocation table")
    return [
        int.from_bytes(image[table + i * 4:table + i * 4 + 2], "little")
        + 16 * int.from_bytes(image[table + i * 4 + 2:table + i * 4 + 4], "little")
        for i in range(count)
    ]


def run(name: str, command: list[str], work: Path, output: Path, env: dict[str, str]) -> None:
    result = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=180)
    (output / f"{name}.log").write_text(
        json.dumps(command) + f"\nexit={result.returncode}\n" + result.stdout + "\n" + result.stderr
    )
    if result.returncode:
        raise ValueError(f"{name} failed; see {output / (name + '.log')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to((ROOT / ".analysis").resolve()):
        parser.error("output directory must be new and below .analysis")
    output.mkdir(parents=True)

    targets = tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
    target_info = next(item for item in targets if item["id"] == "th04-main")
    target = (ROOT / target_info["private_path"]).read_bytes()
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise ValueError("MAIN target identity failed")
    if int.from_bytes(target[8:10], "little") * 16 != 0x1800:
        raise ValueError("MAIN MZ header size changed")
    target_slice = target[0x1800 + 0xAED0:0x1800 + 0xB3EE]
    target_sites = [s for s in relocations(target) if 0xAED0 <= s < 0xB3EE]
    if len(target_slice) != 0x51E or len(target_sites) != 52 or target_sites[0] != 0xB2DA:
        raise ValueError("target DEMO owner changed")
    for path, expected in SNAPSHOT_HASHES.items():
        if sha((SNAPSHOT / path).read_bytes()) != expected:
            raise ValueError(f"retained v214 snapshot changed: {path}")
    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    for identifier in ("active-tcc", "active-tasm32", "active-tlink"):
        item = next(x for x in surfaces if x["id"] == identifier)
        if sha((ROOT / item["path"]).read_bytes()) != item["sha256"]:
            raise ValueError(f"toolchain changed: {identifier}")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")

    with tempfile.TemporaryDirectory(prefix="demo-split-", dir=output) as scratch:
        work = Path(scratch) / "source"
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        old_code = code((work / "obj/th04/sess.obj").read_bytes(), "DEMO_TEXT")
        old_demo_code = code((work / "obj/th04/demo.obj").read_bytes(), "DEMO_TEXT")

        session = (work / "th04/sess.cpp").read_text()
        marker = '#include "th04/hardware/input.h"'
        if session.count(marker) != 1:
            raise ValueError("session/pause split marker changed")
        first_function = session.index("void near stage_session_init(void)")
        before_pause, pause_tail = session.split(marker, 1)
        pause_source = session[:first_function].replace(
            "#pragma option -zCDEMO_TEXT -zPmain_01",
            "#pragma option -zCPAUSE_TEXT -zPmain_01", 1
        ) + marker + pause_tail
        (work / "th04/sess.cpp").write_text(before_pause)
        (work / "th04/pause.cpp").write_text(pause_source)
        demo = work / "th04/demo.cpp"
        demo.write_text("#pragma option -zCDEMO_TAIL_TEXT -zPmain_01\n" + demo.read_text())

        coanch = work / "th04/coanch.asm"
        data = coanch.read_bytes()
        data = replace_once(data, b"DEMO_TEXT ends\n", b"DEMO_TEXT ends\n"
            b"PAUSE_TEXT segment byte public 'CODE' use16\nPAUSE_TEXT ends\n"
            b"DEMO_TAIL_TEXT segment byte public 'CODE' use16\nDEMO_TAIL_TEXT ends\n")
        data = replace_once(data, b"DEMO_TEXT, EMS_TEXT", b"DEMO_TEXT, PAUSE_TEXT, DEMO_TAIL_TEXT, EMS_TEXT")
        coanch.write_bytes(data)
        main_asm = work / "th04_main.asm"
        data = main_asm.read_bytes()
        data = replace_once(data, b"DEMO_TEXT\tends\r\n", b"DEMO_TEXT\tends\r\n"
            b"PAUSE_TEXT segment byte public 'CODE' use16\r\nPAUSE_TEXT ends\r\n"
            b"DEMO_TAIL_TEXT segment byte public 'CODE' use16\r\nDEMO_TAIL_TEXT ends\r\n")
        data = replace_once(data, b"DEMO_TEXT, EMS_TEXT", b"DEMO_TEXT, PAUSE_TEXT, DEMO_TAIL_TEXT, EMS_TEXT")
        main_asm.write_bytes(data)
        response = work / "obj/th04/main.@l"
        response.write_bytes(replace_once(response.read_bytes(),
            b"obj\\th04\\main.obj obj\\th04\\sess.obj",
            b"obj\\th04\\main.obj obj\\th04\\pause.obj obj\\th04\\sess.obj"))

        for name in ("sess", "pause", "demo"):
            run(name, ["wine", str(runner), "-e", "-x", "tcc", *TCC_FLAGS,
                       f"th04/{name}.cpp"], work, output, env)
        for name, source, obj in (
            ("coanch", r"th04\coanch.asm", r"obj\th04\coanch.obj"),
            ("main-asm", "th04_main.asm", r"obj\th04\main.obj"),
        ):
            run(name, ["wine", r"C:\TASM50\bin\TASM32.EXE", "/m", "/mx",
                       "/kh32768", "/t", "/dGAME=4", source, obj], work, output, env)
        core = code((work / "obj/th04/sess.obj").read_bytes(), "DEMO_TEXT")
        pause = code((work / "obj/th04/pause.obj").read_bytes(), "PAUSE_TEXT")
        tail = code((work / "obj/th04/demo.obj").read_bytes(), "DEMO_TAIL_TEXT")
        if (len(core), len(pause), len(tail)) != (0x3FF, 0x11F, 0x9A):
            raise ValueError("unexpected split CODE sizes")
        if core + pause != old_code or tail != old_demo_code:
            raise ValueError("split changed compiler CODE bytes")
        run("link", ["wine", str(runner), "-e", "-x", "tlink",
                     r"@obj\th04\main.@l"], work, output, env)
        candidate = (work / "bin/th04/main.exe").read_bytes()
        if int.from_bytes(candidate[8:10], "little") * 16 != 0x1800:
            raise ValueError("candidate MZ header size changed")
        candidate_slice = candidate[0x1800 + 0xAED0:0x1800 + 0xB3EE]
        candidate_sites = [s for s in relocations(candidate) if 0xAED0 <= s < 0xB3EE]
        if candidate_slice != target_slice or sorted(candidate_sites) != sorted(target_sites):
            raise ValueError("split did not preserve target owner bytes and relocation sites")
        map_text = (work / "obj/th04/main.map").read_text(errors="replace")
        for line in (
            "0AAF:03E0 03FF C=CODE   S=DEMO_TEXT      G=MAIN_01 M=th04/sess.cpp",
            "0AAF:07DF 011F C=CODE   S=PAUSE_TEXT     G=MAIN_01 M=th04/pause.cpp",
            "0AAF:08FE 009A C=CODE   S=DEMO_TAIL_TEXT G=MAIN_01 M=th04/demo.cpp",
        ):
            if line not in map_text:
                raise ValueError(f"split MAP contribution changed: {line}")
        receipt = {
            "claim_scope": "MAIN DEMO_TEXT stage-session source split and synthetic byte-aligned segments; diagnostic only",
            "target_sha256": target_info["sha256"],
            "snapshot_hashes": SNAPSHOT_HASHES,
            "target_extent": "DEMO_TEXT 0AAF:03E0; load 0xAED0..0xB3ED; 0x51E bytes",
            "target_slice_sha256": sha(target_slice),
            "candidate_image_sha256": sha(candidate),
            "candidate_slice_sha256": sha(candidate_slice),
            "code_lengths": {"core": len(core), "pause": len(pause), "demo_tail": len(tail)},
            "split_compiler_code_equals_monolith": True,
            "demo_tail_compiler_code_equals_original": True,
            "candidate_sites_equal_unordered": True,
            "target_ordered_sites": target_sites,
            "candidate_ordered_sites": candidate_sites,
            "ordered_sites_equal": candidate_sites == target_sites,
            "target_session_global_relocation_indices": [i for i, s in enumerate(relocations(target)) if 0xAED0 <= s < 0xB3EE],
            "candidate_session_global_relocation_indices": [i for i, s in enumerate(relocations(candidate)) if 0xAED0 <= s < 0xB3EE],
            "result": "raw owner exact; ordered relocations fail; synthetic segment identity is unproved",
        }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "raw_equal": True,
                      "ordered_sites_equal": receipt["ordered_sites_equal"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
