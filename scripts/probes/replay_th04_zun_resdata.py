#!/usr/bin/env python3
"""Cold-replace ZUN's resident-data library member with checked-in TASM source."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

from replay_th04_zun_graph_clear import (
    BASELINE_COMPONENT_SHA256, LOCAL_GRAPH_CLEAR,
    MASTER_LIB, MASTER_LIB_SHA256, PAYLOAD, PAYLOAD_SHA256, ROOT,
    RUNNER, SOURCES, TARGET_COMPONENT_SHA256, build, sha, source_closure,
)

sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402

LOCAL_RESDATA = ROOT / "src/shared/dos/resdata.asm"
RESDATA_CODE_SHA256 = "cd6d5f0b78835208fd872ae3a3a39028edad3eb99a74a9e5b22158f3fcc7187d"
RESDATA_DATA_SHA256 = "f9031965db29afa581cffeff71a7a1038ab9036eb9feba4c3ddb2dab61cc52f5"
LINK_RESPONSE = (
    "-c -s -t c0t.obj obj\\th04\\cfg_init.obj obj\\th04\\main.obj "
    "local\\GRPCLEAR.OBJ, bin\\th04\\res_huma.com, "
    "obj\\th04\\res_huma.map, bin\\masters.lib emu.lib maths.lib ct.lib\r\n"
)


def object_sections(path: Path) -> tuple[bytes, bytes]:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if sorted(map(len, sections)) != [10, 190]:
        raise RuntimeError("RESDATA OMF LEDATA layout changed")
    return next(data for data in sections if len(data) == 190), next(
        data for data in sections if len(data) == 10)


def dos_tool(work: Path, saved: Path, environment: dict[str, str],
             name: str, tool: str, *args: str) -> None:
    command = ["wine", str(RUNNER), "-e", "-x", tool, *args]
    completed = subprocess.run(command, cwd=work, env=environment,
                               capture_output=True, text=True, timeout=300)
    saved.write_text(json.dumps(command) + f"\nexit={completed.returncode}\n"
                     + completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(f"{name}: {tool} failed: {saved}")


def original_physical_order(library: bytes, extracted: Path, names: list[str]) -> list[str]:
    # TLIB's text listing is alphabetic; TLINK's member search follows the
    # library's physical order. The pinned library uses 16-byte pages.
    if library[0] != 0xF0 or int.from_bytes(library[1:3], "little") + 3 != 16:
        raise RuntimeError("master library page format changed")
    by_header: dict[str, str] = {}
    for name in names:
        records = parse_omf((extracted / f"{name}.OBJ").read_bytes())
        header = records[0].data
        title = header[1:1 + header[0]].decode("ascii")
        if title in by_header:
            raise RuntimeError(f"duplicate library THEADR {title}")
        by_header[title] = name
    physical = []
    for offset in range(16, len(library), 16):
        if library[offset] != 0x80 or offset + 4 >= len(library):
            continue
        length = library[offset + 3]
        raw = library[offset + 4:offset + 4 + length]
        if not raw.isascii() or not all(32 <= byte < 127 for byte in raw):
            continue
        title = raw.decode("ascii")
        if title in by_header:
            physical.append(by_header[title])
    if len(physical) != len(names) or set(physical) != set(names):
        raise RuntimeError("master library physical member order is incomplete")
    if physical.index("resdata") != 162:
        raise RuntimeError("RESDATA member position changed")
    return physical


def link_component(work: Path, saved: Path, environment: dict[str, str],
                   archive: Path, prefix: str) -> tuple[bytes, bytes]:
    shutil.copyfile(archive, work / "bin/masters.lib")
    dos_tool(work, saved / f"{prefix}-link.log", environment, prefix, "tlink",
             r"@obj\th04\res_huma.@l")
    component_path = work / "bin/th04/res_huma.com"
    map_path = work / "obj/th04/res_huma.map"
    if not component_path.is_file() or not map_path.is_file():
        raise RuntimeError(f"{prefix}: TLINK omitted component or MAP")
    component, map_data = component_path.read_bytes(), map_path.read_bytes()
    (saved / f"{prefix}-res_huma.com").write_bytes(component)
    (saved / f"{prefix}-res_huma.map").write_bytes(map_data)
    component_path.unlink()
    map_path.unlink()
    return component, map_data


def link(label: str, output: Path) -> dict[str, object]:
    saved = output / label
    saved.mkdir()
    compiled = output / "compile" / label
    environment = os.environ.copy()
    environment.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    with tempfile.TemporaryDirectory(prefix=f"zun-resdata-{label}-", dir=output) as temporary:
        work = Path(temporary)
        (work / "obj/th04").mkdir(parents=True)
        (work / "bin/th04").mkdir(parents=True)
        for name in ("cfg_init", "main"):
            shutil.copyfile(compiled / f"{name}.obj", work / "obj/th04" / f"{name}.obj")
        shutil.copyfile(MASTER_LIB, work / "masters.lib")
        for name, source in (("GRPCLEAR", LOCAL_GRAPH_CLEAR), ("RESDATA", LOCAL_RESDATA)):
            local = work / f"{name}.ASM"
            shutil.copyfile(source, local)
            os.utime(local, (946684800, 946684800))
            assemble_command = [
                "wine", r"C:\TASM50\bin\TASM32.EXE", "/m", "/mx", "/kh32768",
                f"{name}.ASM,{name}.OBJ,{name}.LST",
            ]
            assembled = subprocess.run(
                assemble_command, cwd=work, env=environment,
                capture_output=True, text=True, timeout=120,
            )
            (saved / f"{name.lower()}-assemble.log").write_text(
                json.dumps(assemble_command) + f"\nexit={assembled.returncode}\n"
                + assembled.stdout + assembled.stderr,
                encoding="utf-8",
            )
            obj = work / f"{name}.OBJ"
            if assembled.returncode or not obj.is_file():
                raise RuntimeError(f"{label}: {name} assembly failed")
            parse_omf(obj.read_bytes())
            (saved / f"{name.lower()}.obj").write_bytes(obj.read_bytes())
        resdata_code, resdata_data = object_sections(work / "RESDATA.OBJ")
        if (len(resdata_code), sha(resdata_code)) != (190, RESDATA_CODE_SHA256):
            raise RuntimeError(f"{label}: local RESDATA CODE changed")
        if (len(resdata_data), sha(resdata_data)) != (10, RESDATA_DATA_SHA256):
            raise RuntimeError(f"{label}: local RESDATA DATA changed")
        (work / "RESDATA.OBJ").unlink()
        (work / "GRPCLEAR.OBJ").unlink()
        dos_tool(work, saved / "library-list.log", environment, label, "tlib",
                 "masters.lib", ",", "MEMBERS.LST")
        listing = (work / "MEMBERS.LST").read_text(encoding="cp437")
        names = re.findall(r"^([^ \t\r\n]+)\s+size = ", listing, re.M)
        if len(names) != 640 or names.count("resdata") != 1:
            raise RuntimeError(f"{label}: master library inventory changed")
        (work / "EXTRACT.RSP").write_text(
            " &\n".join("*" + name for name in names) + "\n", encoding="ascii")
        dos_tool(work, saved / "library-extract.log", environment, label, "tlib",
                 "masters.lib", "@EXTRACT.RSP")
        original_object = work / "resdata.OBJ"
        original_code, original_data = object_sections(original_object)
        if (original_code, original_data) != (resdata_code, resdata_data):
            raise RuntimeError(f"{label}: local RESDATA differs from original library member")
        (saved / "resdata-original.obj").write_bytes(original_object.read_bytes())
        order = original_physical_order(MASTER_LIB.read_bytes(), work, names)
        (saved / "library-physical-order.txt").write_text("\n".join(order) + "\n")
        (work / "local").mkdir()
        shutil.copyfile(saved / "grpclear.obj", work / "local/GRPCLEAR.OBJ")
        (work / "BUILD.RSP").write_text(
            " &\n".join("+" + name + ".OBJ" for name in order) + "\n",
            encoding="ascii",
        )
        (work / "obj/th04/res_huma.@l").write_bytes(LINK_RESPONSE.encode("ascii"))
        dos_tool(work, saved / "original-library-build.log", environment, label,
                 "tlib", "ORIG.LIB", "@BUILD.RSP")
        original_component, original_map = link_component(
            work, saved, environment, work / "ORIG.LIB", "original")
        if sha(original_component) != BASELINE_COMPONENT_SHA256:
            raise RuntimeError(f"{label}: archive recreation changed original component")
        shutil.copyfile(saved / "resdata.obj", original_object)
        dos_tool(work, saved / "local-library-build.log", environment, label,
                 "tlib", "LOCAL.LIB", "@BUILD.RSP")
        component, map_data = link_component(
            work, saved, environment, work / "LOCAL.LIB", "local")
        (saved / "res_huma.com").write_bytes(component)
        (saved / "res_huma.map").write_bytes(map_data)
        map_text = map_data.decode("cp437")
        expected = (
            "0000:0367 0098 C=CODE", "M=src/zun/config/cfg_init.cpp",
            "0000:03FF 00F6 C=CODE", "M=src/zun/resident/main.cpp",
            "0000:04F6 0024 C=CODE", "M=GRPCLEAR.ASM",
            "0000:051A 00BE C=CODE", "M=resdata",
            "0000:179C 000A C=DATA", "0000:051A       RESDATA_EXIST",
            "0000:0562       RESDATA_CREATE",
        )
        if not all(fragment in map_text for fragment in expected):
            raise RuntimeError(f"{label}: local MAP contributions changed")
        if "M=grpclear " in map_text:
            raise RuntimeError(f"{label}: GRAPH_CLEAR library member still linked")
        if sha(component) != BASELINE_COMPONENT_SHA256:
            raise RuntimeError(f"{label}: local RESDATA changed linked component bytes")
        if component != original_component:
            raise RuntimeError(f"{label}: local member changed original component")
        return {
            "component_size": len(component),
            "component_sha256": sha(component),
            "map_sha256": sha(map_data),
            "original_component_sha256": sha(original_component),
            "original_map_sha256": sha(original_map),
            "original_library_sha256": sha((work / "ORIG.LIB").read_bytes()),
            "local_library_sha256": sha((work / "LOCAL.LIB").read_bytes()),
            "original_resdata_object_sha256": sha((saved / "resdata-original.obj").read_bytes()),
            "resdata_member_position": order.index("resdata"),
            "resdata_object_sha256": sha((saved / "resdata.obj").read_bytes()),
            "resdata_code_sha256": sha(resdata_code),
            "resdata_data_sha256": sha(resdata_data),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")
    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    target_info = next(item for item in manifest["artifacts"] if item["id"] == "th04-zun")
    target = (ROOT / target_info["private_path"]).read_bytes()
    payload = PAYLOAD.read_bytes()
    target_component = payload[0xB68:0x2440]
    target_code = payload[0xF88:0x1046]
    target_data = payload[0x2204:0x220E]
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target changed")
    if sha(payload) != PAYLOAD_SHA256 or sha(target_component) != TARGET_COMPONENT_SHA256:
        raise RuntimeError("attested decoded ZUN component changed")
    if (len(target_code), sha(target_code)) != (190, RESDATA_CODE_SHA256):
        raise RuntimeError("attested target RESDATA CODE changed")
    if (len(target_data), sha(target_data)) != (10, RESDATA_DATA_SHA256):
        raise RuntimeError("attested target RESDATA DATA changed")
    if sha(MASTER_LIB.read_bytes()) != MASTER_LIB_SHA256:
        raise RuntimeError("pinned external master library changed")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)

    inputs = {
        relative: sha((ROOT / relative).read_bytes())
        for relative in source_closure(ROOT, tuple(SOURCES.values()))
    }
    inputs[str(LOCAL_GRAPH_CLEAR.relative_to(ROOT))] = sha(LOCAL_GRAPH_CLEAR.read_bytes())
    inputs[str(LOCAL_RESDATA.relative_to(ROOT))] = sha(LOCAL_RESDATA.read_bytes())
    output.mkdir(parents=True)
    (output / "compile").mkdir()
    compiled = {label: build(label, output / "compile", inputs) for label in ("a", "b")}
    if compiled["a"] != compiled["b"]:
        raise RuntimeError("cold source-only object rounds differ")
    linked = {label: link(label, output) for label in ("a", "b")}
    if linked["a"] != linked["b"]:
        raise RuntimeError("cold component link rounds differ")
    candidate = (output / "a/res_huma.com").read_bytes()
    if candidate[0x41A:0x4D8] != target_code:
        raise RuntimeError("local RESDATA linked CODE differs from target")
    if candidate[0x169C:0x16A6] != target_data:
        raise RuntimeError("local RESDATA linked DATA differs from target")
    if len(candidate) != len(target_component):
        raise RuntimeError("component size changed; review MAP and boundaries")
    differences = sum(a != b for a, b in zip(candidate, target_component))
    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04-owned RESDATA CODE and DATA replace the external library member; no target exact claim",
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_component_extent": "decoded ZUN.COM 0xB68..0x243F",
        "target_component_sha256": TARGET_COMPONENT_SHA256,
        "target_resdata_code_extent": "decoded ZUN.COM _TEXT 0xF88..0x1045",
        "target_resdata_data_extent": "decoded ZUN.COM _DATA 0x2204..0x220D",
        "target_resdata_code_sha256": RESDATA_CODE_SHA256,
        "target_resdata_data_sha256": RESDATA_DATA_SHA256,
        "input_sha256": inputs,
        "external_master_lib_sha256": MASTER_LIB_SHA256,
        "link_response": LINK_RESPONSE,
        "compile": compiled,
        "link": linked,
        "component_raw_difference_count": differences,
        "resdata_code_and_data_raw_equal": True,
        "exact": differences == 0,
        "limit": "Most support still comes from external master library; _main remains 246 versus 252 target bytes, and ZUNINIT/MEMCHK/ONGCHK/DIET product inputs are not source-closed.",
    }
    if receipt["exact"]:
        raise RuntimeError("component unexpectedly matches; run full exact Oracle set")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"component {len(candidate)} bytes; {differences} raw differences; A/B SHA {linked['a']['component_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
