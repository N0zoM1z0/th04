#!/usr/bin/env python3
"""Cold-build TH04 MEMCHK from natural C++ main plus shared DOS support."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import describe_omf, parse_omf
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from replay_th04_zun_cfg_init import code as text_code
from replay_th04_op_playchar_menu_initial import loose_segment_bytes
from replay_th04_zun_dos_puts2 import (
    DOS_PUTS2_BODY_SHA256,
    DOS_PUTS2_MODULE_SHA256,
    LOCAL_DOS_PUTS2,
    dos_puts2_object_code,
    link_relevant_omf_sha,
)
from replay_th04_zun_resdata import MASTER_LIB, MASTER_LIB_SHA256, dos_tool
from replay_th04_zun_source_only import PAYLOAD, PAYLOAD_SHA256, RUNNER, sha

MAIN_SOURCE = ROOT / "src/zun/memchk/main.cpp"
DOS_MAXFREE_SOURCE = ROOT / "src/shared/dos/dos_maxfree.asm"

COMPONENT_START = 0x2440
COMPONENT_SIZE = 0x0FE2
COMPONENT_SHA256 = "2531795670b5cafb65bf261f499d5d77b71aeaf26015f8481000cdbb96272dfc"
MAIN_START = 0x26A7
MAIN_SIZE = 0x26
MAIN_SHA256 = "fcae0651ecf250e505e236d10abe035ab9ef7caddf19ffa0067c0c9b0f4339bc"
MAIN_PAD_OFFSET = 0x26CD
PUTS_START = 0x26CE
PUTS_SIZE = 0x27
PUTS_PAD_OFFSET = 0x26F5
MAXFREE_START = 0x26F6
MAXFREE_SIZE = 0x14
MAXFREE_SHA256 = "eace7619d9439c5097dcb03308fa5f5efb74e4219454a45d7c7b068daa6840fc"
DATA_START = 0x31CE
DATA_SIZE = 0x50
DATA_SHA256 = "5bf241f61d6f017181d12cd3ba92c897b74d5e36167b25fcac8b48b2b24e9218"

MAIN_SOURCE_SHA256 = "e048abf518c9370e139bea933f3cc02cf4b30f0cb107cd7b2e08c1941ca2d6ef"
DOS_MAXFREE_SOURCE_SHA256 = "e8b650ced3c46e55d25ba407a3fd7ec9c4e723127ebc6edbcd1a2cd06625be43"
DOS_PUTS2_SOURCE_SHA256 = "eb9ce7e41c0c2293c69c72cd96d608db3b31c1a71176c00962daa9243e1fdd9d"
DOS_MAXFREE_ORIGINAL_OBJ_SHA256 = "301a1fa664180fb4888371da1ba2b7d7283fecf0133c064cce1d1020bce9c389"


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def dos_maxfree_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    pieces = [
        record.data[3:]
        for record in records
        if record.record_type == 0xA0 and record.data[1:3] == b"\0\0"
    ]
    if len(pieces) != 1 or len(pieces[0]) != MAXFREE_SIZE:
        raise RuntimeError("DOS_MAXFREE OMF CODE layout drift")
    return pieces[0]


def environment() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    return env


def run(command: list[str], cwd: Path, log: Path, env: dict[str, str]) -> None:
    done = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=180)
    log.write_text(json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + done.stderr)
    if done.returncode:
        raise RuntimeError(f"command failed: {log}")


def assemble(source: Path, name: str, work: Path, saved: Path, env: dict[str, str]) -> Path:
    asm = work / f"{name}.ASM"
    shutil.copyfile(source, asm)
    os.utime(asm, (946684800, 946684800))
    obj = work / "obj/th04" / f"{name}.OBJ"
    lst = work / "obj/th04" / f"{name}.LST"
    run(
        [
            "wine", r"C:\TASM50\bin\TASM32.EXE", "/m", "/mx", "/kh32768",
            f"{name}.ASM,obj\\th04\\{name}.OBJ,obj\\th04\\{name}.LST",
        ],
        work,
        saved / f"{name.lower()}-assemble.log",
        env,
    )
    if not obj.is_file() or not lst.is_file():
        raise RuntimeError(f"missing {name} assembly output")
    return obj


def extract_original_maxfree(work: Path, saved: Path, env: dict[str, str]) -> Path:
    archive = work / "archive"
    archive.mkdir()
    shutil.copyfile(MASTER_LIB, archive / "masters.lib")
    (archive / "EXTRACT.RSP").write_text("*dosmaxfr\n", encoding="ascii")
    dos_tool(archive, saved / "dosmaxfr-extract.log", env, "dosmaxfr", "tlib", "masters.lib", "@EXTRACT.RSP")
    obj = archive / "dosmaxfr.OBJ"
    if not obj.is_file() or sha_file(obj) != DOS_MAXFREE_ORIGINAL_OBJ_SHA256:
        raise RuntimeError("historical DOSMAXFR archive member identity drift")
    desc = describe_omf(obj.read_bytes())
    if desc["module_name"] != "DOSMAXFR.ASM" or b"DOS_MAXFREE" not in obj.read_bytes():
        raise RuntimeError("historical DOSMAXFR module/public identity drift")
    if dos_maxfree_code(obj) != bytes.fromhex(
        "b4 48 bb ff ff cd 21 3d 08 00 75 04 8b c3 f8 c3 33 c0 f9 c3"
    ):
        raise RuntimeError("historical DOSMAXFR CODE drift")
    shutil.copyfile(obj, saved / "dosmaxfr-original.obj")
    return obj


def build(label: str, output: Path, target_component: bytes) -> dict[str, object]:
    saved = output / label
    work = saved / "work"
    (work / "obj/th04").mkdir(parents=True)
    (work / "bin/th04").mkdir(parents=True)
    env = environment()

    # Compile natural Tiny-model main source from the checked-in UTF-8 text.
    main = work / "src/zun/memchk/main.cpp"
    main.parent.mkdir(parents=True)
    main.write_bytes(MAIN_SOURCE.read_text(encoding="utf-8").encode("cp932"))
    os.utime(main, (946684800, 946684800))
    run(
        [
            "wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O", "-b-", "-3",
            "-Z", "-d", "-DGAME=4", "-mt", "-nobj/th04/", "src/zun/memchk/main.cpp",
        ],
        work,
        saved / "main-compile.log",
        env,
    )
    main_obj = work / "obj/th04/main.obj"
    main_code = text_code(main_obj)
    main_data = loose_segment_bytes(main_obj, "_DATA")
    if len(main_code) != MAIN_SIZE:
        raise RuntimeError("natural MEMCHK main CODE size drift")
    if len(main_data) != DATA_SIZE or sha(main_data) != DATA_SHA256:
        raise RuntimeError("natural MEMCHK string DATA drift")

    puts_obj = assemble(LOCAL_DOS_PUTS2, "DOSPUTS2", work, saved, env)
    maxfree_obj = assemble(DOS_MAXFREE_SOURCE, "DOSMAXFR", work, saved, env)
    if sha(dos_puts2_object_code(puts_obj)) != DOS_PUTS2_MODULE_SHA256:
        raise RuntimeError("maintained DOS_PUTS2 module drift")
    if sha(dos_maxfree_code(maxfree_obj)) != MAXFREE_SHA256:
        raise RuntimeError("maintained DOS_MAXFREE CODE drift")
    original_maxfree = extract_original_maxfree(work, saved, env)
    if dos_maxfree_code(original_maxfree) != dos_maxfree_code(maxfree_obj):
        raise RuntimeError("maintained DOS_MAXFREE differs from historical MASTER member")

    response = (
        "-c -s -t c0t.obj obj\\th04\\main.obj obj\\th04\\DOSPUTS2.OBJ "
        "obj\\th04\\DOSMAXFR.OBJ, bin\\th04\\memchk.com, obj\\th04\\memchk.map, "
        "emu.lib maths.lib ct.lib\r\n"
    )
    (work / "obj/th04/memchk.@l").write_bytes(response.encode("ascii"))
    run(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\memchk.@l"],
        work,
        saved / "link.log",
        env,
    )
    component = (work / "bin/th04/memchk.com").read_bytes()
    map_bytes = (work / "obj/th04/memchk.map").read_bytes()
    map_text = map_bytes.decode("cp437")
    required = (
        "0000:0367       _main",
        "0000:038E       DOS_PUTS2",
        "0000:03B6       DOS_MAXFREE",
        "0000:0E8E 0050 C=DATA   S=_DATA",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("natural MEMCHK MAP layout drift")
    if component != target_component or sha(component) != COMPONENT_SHA256:
        raise RuntimeError("natural MEMCHK component is not target-exact")

    return {
        "main_object_sha256": sha_file(main_obj),
        "main_code_size": len(main_code),
        "main_code_sha256": sha(main_code),
        "main_data_size": len(main_data),
        "main_data_sha256": sha(main_data),
        "dos_puts2_object_sha256": sha_file(puts_obj),
        "dos_puts2_link_relevant_omf_sha256": link_relevant_omf_sha(puts_obj),
        "dos_maxfree_object_sha256": sha_file(maxfree_obj),
        "historical_dosmaxfr_object_sha256": sha_file(original_maxfree),
        "dos_maxfree_code_sha256": sha(dos_maxfree_code(maxfree_obj)),
        "linked_component_size": len(component),
        "linked_component_sha256": sha(component),
        "linked_map_sha256": sha(map_bytes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output must be new directly below .analysis/reconstruction/probes")

    if sha_file(MAIN_SOURCE) != MAIN_SOURCE_SHA256:
        raise RuntimeError("MEMCHK main source identity drift")
    if sha_file(DOS_MAXFREE_SOURCE) != DOS_MAXFREE_SOURCE_SHA256:
        raise RuntimeError("DOS_MAXFREE source identity drift")
    if sha_file(LOCAL_DOS_PUTS2) != DOS_PUTS2_SOURCE_SHA256:
        raise RuntimeError("DOS_PUTS2 source identity drift")
    if sha_file(MASTER_LIB) != MASTER_LIB_SHA256:
        raise RuntimeError("historical masters.lib identity drift")

    payload = PAYLOAD.read_bytes()
    if sha(payload) != PAYLOAD_SHA256:
        raise RuntimeError("decoded ZUN payload identity drift")
    target_component = payload[COMPONENT_START:COMPONENT_START + COMPONENT_SIZE]
    if len(target_component) != COMPONENT_SIZE or sha(target_component) != COMPONENT_SHA256:
        raise RuntimeError("target MEMCHK component identity drift")
    if sha(payload[MAIN_START:MAIN_START + MAIN_SIZE]) != MAIN_SHA256:
        raise RuntimeError("target MEMCHK main identity drift")
    if payload[MAIN_PAD_OFFSET:MAIN_PAD_OFFSET + 1] != b"\x00":
        raise RuntimeError("target MEMCHK main alignment drift")
    if sha(payload[PUTS_START:PUTS_START + PUTS_SIZE]) != DOS_PUTS2_BODY_SHA256:
        raise RuntimeError("target MEMCHK DOS_PUTS2 identity drift")
    if payload[PUTS_PAD_OFFSET:PUTS_PAD_OFFSET + 1] != b"\x90":
        raise RuntimeError("target MEMCHK DOS_PUTS2 alignment drift")
    if sha(payload[MAXFREE_START:MAXFREE_START + MAXFREE_SIZE]) != MAXFREE_SHA256:
        raise RuntimeError("target MEMCHK DOS_MAXFREE identity drift")
    if sha(payload[DATA_START:DATA_START + DATA_SIZE]) != DATA_SHA256:
        raise RuntimeError("target MEMCHK data identity drift")

    output.mkdir()
    a = build("a", output, target_component)
    b = build("b", output, target_component)
    stable = (
        "main_code_size", "main_code_sha256", "main_data_size", "main_data_sha256",
        "dos_puts2_link_relevant_omf_sha256", "historical_dosmaxfr_object_sha256",
        "dos_maxfree_code_sha256", "linked_component_size", "linked_component_sha256",
        "linked_map_sha256",
    )
    if any(a[key] != b[key] for key in stable):
        raise RuntimeError("independent natural MEMCHK cold rounds differ")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 ZUN MEMCHK complete natural-source component replay",
        "artifact": "th04-zun",
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_component": {
            "payload_offset": hex(COMPONENT_START),
            "size": COMPONENT_SIZE,
            "sha256": COMPONENT_SHA256,
        },
        "maintained_source_sha256": {
            "src/zun/memchk/main.cpp": MAIN_SOURCE_SHA256,
            "src/shared/dos/dos_puts2.asm": DOS_PUTS2_SOURCE_SHA256,
            "src/shared/dos/dos_maxfree.asm": DOS_MAXFREE_SOURCE_SHA256,
        },
        "function_extents": {
            "main": {"offset": hex(MAIN_START), "size": MAIN_SIZE, "sha256": MAIN_SHA256},
            "DOS_PUTS2": {"offset": hex(PUTS_START), "size": PUTS_SIZE, "sha256": DOS_PUTS2_BODY_SHA256},
            "DOS_MAXFREE": {"offset": hex(MAXFREE_START), "size": MAXFREE_SIZE, "sha256": MAXFREE_SHA256},
        },
        "layout": {
            "main_following_linker_pad": {"offset": hex(MAIN_PAD_OFFSET), "byte": 0},
            "dos_puts2_following_even_pad": {"offset": hex(PUTS_PAD_OFFSET), "byte": 0x90},
            "data_offset": hex(DATA_START),
            "data_size": DATA_SIZE,
            "data_sha256": DATA_SHA256,
            "historical_dosmaxfr_archive_member_sha256": DOS_MAXFREE_ORIGINAL_OBJ_SHA256,
        },
        "builds": {"a": a, "b": b},
        "result": "complete-memchk-component-raw-exact",
        "limit": (
            "This proves natural source ownership for MEMCHK _main and shared-library ownership for "
            "DOS_PUTS2/DOS_MAXFREE. It does not grant exactness to other ZUN components or the full ZUN.COM."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "component_sha256": COMPONENT_SHA256,
        "component_raw_equal": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
