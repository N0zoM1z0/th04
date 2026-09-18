#!/usr/bin/env python3
"""Cold-replace ZUN's FILE_READ library member with checked-in TASM source."""

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

from replay_th04_zun_resdata import (
    BASELINE_COMPONENT_SHA256, HEADERS, LINK_RESPONSE, LOCAL_GRAPH_CLEAR,
    LOCAL_RESDATA, MASTER_LIB, MASTER_LIB_SHA256, PAYLOAD, PAYLOAD_SHA256,
    ROOT, SOURCES, TARGET_COMPONENT_SHA256, build, dos_tool, link_component,
    original_physical_order, sha,
)

sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402

LOCAL_FILE_READ = ROOT / "src/shared/dos/file_read.asm"
FILE_READ_OMF_CODE_SHA256 = "ca364a9a2ea5d5c4f5303dad086217316cadf8cee8240b4a41e4986ba5dee047"
FILE_READ_TARGET_SHA256 = "ba0aa97e36e670ba472356fe022772f3d69e574dea729ecce208691030209280"


def object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != 180:
        raise RuntimeError("FILE_READ OMF CODE layout changed")
    return sections[0]


def link(label: str, output: Path) -> dict[str, object]:
    saved = output / label
    saved.mkdir()
    compiled = output / "compile" / label
    environment = os.environ.copy()
    environment.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    with tempfile.TemporaryDirectory(prefix=f"zun-filread-{label}-", dir=output) as temporary:
        work = Path(temporary)
        (work / "obj/th04").mkdir(parents=True)
        (work / "bin/th04").mkdir(parents=True)
        for name in ("cfg_init", "main"):
            shutil.copyfile(compiled / f"{name}.obj", work / "obj/th04" / f"{name}.obj")
        shutil.copyfile(MASTER_LIB, work / "masters.lib")
        sources = (("GRPCLEAR", LOCAL_GRAPH_CLEAR), ("RESDATA", LOCAL_RESDATA),
                   ("FILREAD", LOCAL_FILE_READ))
        for name, source in sources:
            local = work / f"{name}.ASM"
            shutil.copyfile(source, local)
            os.utime(local, (946684800, 946684800))
            command = ["wine", r"C:\TASM50\bin\TASM32.EXE", "/m", "/mx", "/kh32768",
                       f"{name}.ASM,{name}.OBJ,{name}.LST"]
            completed = subprocess.run(command, cwd=work, env=environment,
                                       capture_output=True, text=True, timeout=120)
            (saved / f"{name.lower()}-assemble.log").write_text(
                json.dumps(command) + f"\nexit={completed.returncode}\n"
                + completed.stdout + completed.stderr, encoding="utf-8")
            obj = work / f"{name}.OBJ"
            if completed.returncode or not obj.is_file():
                raise RuntimeError(f"{label}: {name} assembly failed")
            parse_omf(obj.read_bytes())
            (saved / f"{name.lower()}.obj").write_bytes(obj.read_bytes())
            obj.unlink()
        local_code = object_code(saved / "filread.obj")
        if sha(local_code) != FILE_READ_OMF_CODE_SHA256:
            raise RuntimeError(f"{label}: local FILE_READ OMF CODE changed")
        dos_tool(work, saved / "library-list.log", environment, label, "tlib",
                 "masters.lib", ",", "MEMBERS.LST")
        listing = (work / "MEMBERS.LST").read_text(encoding="cp437")
        names = re.findall(r"^([^ \t\r\n]+)\s+size = ", listing, re.M)
        if len(names) != 640 or names.count("filread") != 1:
            raise RuntimeError(f"{label}: master library inventory changed")
        (work / "EXTRACT.RSP").write_text(
            " &\n".join("*" + name for name in names) + "\n", encoding="ascii")
        dos_tool(work, saved / "library-extract.log", environment, label, "tlib",
                 "masters.lib", "@EXTRACT.RSP")
        original_object = work / "filread.OBJ"
        original_code = object_code(original_object)
        if original_code != local_code:
            raise RuntimeError(f"{label}: local FILE_READ differs from original member")
        (saved / "filread-original.obj").write_bytes(original_object.read_bytes())
        order = original_physical_order(MASTER_LIB.read_bytes(), work, names)
        if order.index("filread") != 165:
            raise RuntimeError(f"{label}: FILE_READ library member moved")
        (saved / "library-physical-order.txt").write_text("\n".join(order) + "\n")
        (work / "local").mkdir()
        shutil.copyfile(saved / "grpclear.obj", work / "local/GRPCLEAR.OBJ")
        (work / "BUILD.RSP").write_text(
            " &\n".join("+" + name + ".OBJ" for name in order) + "\n",
            encoding="ascii")
        (work / "obj/th04/res_huma.@l").write_bytes(LINK_RESPONSE.encode("ascii"))
        dos_tool(work, saved / "original-library-build.log", environment, label,
                 "tlib", "ORIG.LIB", "@BUILD.RSP")
        original_component, original_map = link_component(
            work, saved, environment, work / "ORIG.LIB", "original")
        if sha(original_component) != BASELINE_COMPONENT_SHA256:
            raise RuntimeError(f"{label}: original archive recreation changed component")
        shutil.copyfile(saved / "resdata.obj", work / "resdata.OBJ")
        shutil.copyfile(saved / "filread.obj", original_object)
        dos_tool(work, saved / "local-library-build.log", environment, label,
                 "tlib", "LOCAL.LIB", "@BUILD.RSP")
        component, map_data = link_component(
            work, saved, environment, work / "LOCAL.LIB", "local")
        if component != original_component or sha(component) != BASELINE_COMPONENT_SHA256:
            raise RuntimeError(f"{label}: local FILE_READ changed component bytes")
        if map_data != original_map:
            raise RuntimeError(f"{label}: local FILE_READ changed MAP")
        map_text = map_data.decode("cp437")
        expected = (
            "0000:05D8 00B4 C=CODE", "M=filread", "0000:17AA 0000 C=DATA",
            "0000:051A 00BE C=CODE", "M=resdata", "0000:04F6 0024 C=CODE",
            "M=GRPCLEAR.ASM", "0000:05D8       FILE_READ",
        )
        if not all(fragment in map_text for fragment in expected) or "M=grpclear " in map_text:
            raise RuntimeError(f"{label}: local MAP ownership changed")
        (saved / "res_huma.com").write_bytes(component)
        (saved / "res_huma.map").write_bytes(map_data)
        return {
            "component_size": len(component),
            "component_sha256": sha(component),
            "map_sha256": sha(map_data),
            "original_library_sha256": sha((work / "ORIG.LIB").read_bytes()),
            "local_library_sha256": sha((work / "LOCAL.LIB").read_bytes()),
            "filread_member_position": order.index("filread"),
            "filread_original_object_sha256": sha((saved / "filread-original.obj").read_bytes()),
            "filread_local_object_sha256": sha((saved / "filread.obj").read_bytes()),
            "filread_omf_code_sha256": sha(local_code),
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
    target_code = payload[0x1046:0x10FA]
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target changed")
    if sha(payload) != PAYLOAD_SHA256 or sha(target_component) != TARGET_COMPONENT_SHA256:
        raise RuntimeError("attested decoded ZUN component changed")
    if (len(target_code), sha(target_code)) != (180, FILE_READ_TARGET_SHA256):
        raise RuntimeError("attested target FILE_READ CODE changed")
    if sha(MASTER_LIB.read_bytes()) != MASTER_LIB_SHA256:
        raise RuntimeError("pinned external master library changed")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    inputs = {relative: sha((ROOT / relative).read_bytes()) for relative in (*SOURCES.values(), *HEADERS)}
    for source in (LOCAL_GRAPH_CLEAR, LOCAL_RESDATA, LOCAL_FILE_READ):
        inputs[str(source.relative_to(ROOT))] = sha(source.read_bytes())
    output.mkdir(parents=True)
    (output / "compile").mkdir()
    compiled = {label: build(label, output / "compile", inputs) for label in ("a", "b")}
    if compiled["a"] != compiled["b"]:
        raise RuntimeError("cold source-only object rounds differ")
    linked = {label: link(label, output) for label in ("a", "b")}
    if linked["a"] != linked["b"]:
        raise RuntimeError("cold component link rounds differ")
    candidate = (output / "a/res_huma.com").read_bytes()
    if candidate[0x4D8:0x58C] != target_code:
        raise RuntimeError("local FILE_READ linked CODE differs from target")
    differences = sum(a != b for a, b in zip(candidate, target_component))
    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04-owned FILE_READ CODE replaces external library member; no target exact claim",
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_component_sha256": TARGET_COMPONENT_SHA256,
        "target_file_read_extent": "decoded ZUN.COM 0x1046..0x10F9",
        "target_file_read_sha256": FILE_READ_TARGET_SHA256,
        "local_file_read_omf_code_sha256": FILE_READ_OMF_CODE_SHA256,
        "input_sha256": inputs,
        "external_master_lib_sha256": MASTER_LIB_SHA256,
        "link_response": LINK_RESPONSE,
        "compile": compiled,
        "link": linked,
        "component_raw_difference_count": differences,
        "file_read_raw_equal": True,
        "exact": differences == 0,
        "limit": "External support, composite inputs, and the six-byte _main gap remain; full packed artifact exact acceptance is open.",
    }
    if receipt["exact"]:
        raise RuntimeError("component unexpectedly matches; run full exact Oracle set")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"component {len(candidate)} bytes; {differences} raw differences; A/B SHA {linked['a']['component_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
