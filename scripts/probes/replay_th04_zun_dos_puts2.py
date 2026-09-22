#!/usr/bin/env python3
"""Cold-replace ZUN's DOS_PUTS2 library member after local DOS_AXDX support."""

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
    BASELINE_COMPONENT_SHA256, LINK_RESPONSE, LOCAL_GRAPH_CLEAR,
    LOCAL_RESDATA, MASTER_LIB, MASTER_LIB_SHA256, PAYLOAD, PAYLOAD_SHA256,
    ROOT, SOURCES, TARGET_COMPONENT_SHA256, build, dos_tool, link_component,
    original_physical_order, sha, source_closure,
)

sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402

LOCAL_FILE_READ = ROOT / "src/shared/dos/file_read.asm"
FILE_READ_OMF_CODE_SHA256 = "ca364a9a2ea5d5c4f5303dad086217316cadf8cee8240b4a41e4986ba5dee047"
FILE_READ_TARGET_SHA256 = "ba0aa97e36e670ba472356fe022772f3d69e574dea729ecce208691030209280"
LOCAL_DOS_FREE = ROOT / "src/shared/dos/dos_free.asm"
DOS_FREE_CODE_SHA256 = "5074e39dcddfb569b7591d0fd1011e50037012f444ab42bf95bc2b4053353d3f"
DOS_FREE_MEMBER_POSITION = 211
DOS_FREE_TARGET_OFFSET = 0x131E
DOS_FREE_TARGET_SIZE = 0x10
DOS_FREE_CANDIDATE_OFFSET = 0x7B0
LOCAL_DOS_AXDX = ROOT / "src/shared/dos/dos_axdx.asm"
DOS_AXDX_BODY_SHA256 = "ccf3bedd3a955505f0d5111f13dea7907ceb8d536d024bb9d69a21c8f2a35dd3"
DOS_AXDX_MODULE_SHA256 = "2653d1bfa735f07b9c6ec5f03aef2e0af2f64efdab15850ff42252cd6d9fc4db"
DOS_AXDX_MEMBER_POSITION = 216
DOS_AXDX_TARGET_OFFSET = 0x132E
DOS_AXDX_BODY_SIZE = 0x15
DOS_AXDX_MODULE_SIZE = 0x16
DOS_AXDX_CANDIDATE_OFFSET = 0x7C0
LOCAL_DOS_PUTS2 = ROOT / "src/shared/dos/dos_puts2.asm"
DOS_PUTS2_BODY_SHA256 = "90259993539788eb6cc440e98400c1551f6502aa42c64d1fe8d5860539b9c981"
DOS_PUTS2_MODULE_SHA256 = "c346fe75402242d9b1348e634244efb9e94ba1b8dc637602d8767f0c6c5fb3d9"
DOS_PUTS2_LINK_RELEVANT_OMF_SHA256 = "7106e7fd80b01134a9fbc76229f8dd09a62945bc67da0547d0ff237bff1e7a4d"
DOS_PUTS2_MEMBER_POSITION = 221
DOS_PUTS2_TARGET_OFFSET = 0x1344
DOS_PUTS2_BODY_SIZE = 0x27
DOS_PUTS2_MODULE_SIZE = 0x28
DOS_PUTS2_CANDIDATE_OFFSET = 0x7D6


def object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != 180:
        raise RuntimeError("FILE_READ OMF CODE layout changed")
    return sections[0]


def dos_free_object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != DOS_FREE_TARGET_SIZE:
        raise RuntimeError("DOS_FREE OMF CODE layout changed")
    return sections[0]


def dos_axdx_object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != DOS_AXDX_MODULE_SIZE:
        raise RuntimeError("DOS_AXDX OMF CODE layout changed")
    return sections[0]


def dos_puts2_object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != DOS_PUTS2_MODULE_SIZE:
        raise RuntimeError("DOS_PUTS2 OMF CODE layout changed")
    return sections[0]


def link_relevant_omf_sha(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x88:
            continue
        digest.update(bytes([record.record_type]))
        digest.update(len(record.data).to_bytes(2, "little"))
        digest.update(record.data)
    return digest.hexdigest()


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
                   ("FILREAD", LOCAL_FILE_READ), ("DOSFREE", LOCAL_DOS_FREE),
                   ("DOSC", LOCAL_DOS_AXDX), ("DOSPUTS2", LOCAL_DOS_PUTS2))
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
        local_dos_free = dos_free_object_code(saved / "dosfree.obj")
        if sha(local_dos_free) != DOS_FREE_CODE_SHA256:
            raise RuntimeError(f"{label}: local DOS_FREE OMF CODE changed")
        local_dos_axdx = dos_axdx_object_code(saved / "dosc.obj")
        if sha(local_dos_axdx) != DOS_AXDX_MODULE_SHA256:
            raise RuntimeError(f"{label}: local DOS_AXDX OMF CODE changed")
        local_dos_puts2 = dos_puts2_object_code(saved / "dosputs2.obj")
        if sha(local_dos_puts2) != DOS_PUTS2_MODULE_SHA256:
            raise RuntimeError(f"{label}: local DOS_PUTS2 OMF CODE changed")
        if link_relevant_omf_sha(saved / "dosputs2.obj") != DOS_PUTS2_LINK_RELEVANT_OMF_SHA256:
            raise RuntimeError(f"{label}: local DOS_PUTS2 link-relevant OMF changed")
        dos_tool(work, saved / "library-list.log", environment, label, "tlib",
                 "masters.lib", ",", "MEMBERS.LST")
        listing = (work / "MEMBERS.LST").read_text(encoding="cp437")
        names = re.findall(r"^([^ \t\r\n]+)\s+size = ", listing, re.M)
        if (len(names) != 640 or names.count("filread") != 1
                or names.count("dosfree") != 1 or names.count("dosc") != 1
                or names.count("dosputs2") != 1):
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
        original_dos_free = work / "dosfree.OBJ"
        original_dos_free_code = dos_free_object_code(original_dos_free)
        if original_dos_free_code != local_dos_free:
            raise RuntimeError(f"{label}: local DOS_FREE differs from original member")
        (saved / "dosfree-original.obj").write_bytes(original_dos_free.read_bytes())
        original_dos_axdx = work / "dosc.OBJ"
        original_dos_axdx_code = dos_axdx_object_code(original_dos_axdx)
        if original_dos_axdx_code != local_dos_axdx:
            raise RuntimeError(f"{label}: local DOS_AXDX differs from original member")
        (saved / "dosc-original.obj").write_bytes(original_dos_axdx.read_bytes())
        original_dos_puts2 = work / "dosputs2.OBJ"
        original_dos_puts2_code = dos_puts2_object_code(original_dos_puts2)
        if original_dos_puts2_code != local_dos_puts2:
            raise RuntimeError(f"{label}: local DOS_PUTS2 differs from original member")
        (saved / "dosputs2-original.obj").write_bytes(original_dos_puts2.read_bytes())
        order = original_physical_order(MASTER_LIB.read_bytes(), work, names)
        if order.index("filread") != 165:
            raise RuntimeError(f"{label}: FILE_READ library member moved")
        if order.index("dosfree") != DOS_FREE_MEMBER_POSITION:
            raise RuntimeError(f"{label}: DOS_FREE library member moved")
        if order.index("dosc") != DOS_AXDX_MEMBER_POSITION:
            raise RuntimeError(f"{label}: DOS_AXDX library member moved")
        if order.index("dosputs2") != DOS_PUTS2_MEMBER_POSITION:
            raise RuntimeError(f"{label}: DOS_PUTS2 library member moved")
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
        shutil.copyfile(saved / "dosfree.obj", original_dos_free)
        shutil.copyfile(saved / "dosc.obj", original_dos_axdx)
        shutil.copyfile(saved / "dosputs2.obj", original_dos_puts2)
        dos_tool(work, saved / "local-library-build.log", environment, label,
                 "tlib", "LOCAL.LIB", "@BUILD.RSP")
        component, map_data = link_component(
            work, saved, environment, work / "LOCAL.LIB", "local")
        if component != original_component or sha(component) != BASELINE_COMPONENT_SHA256:
            raise RuntimeError(f"{label}: local DOS_PUTS2 changed component bytes")
        if map_data != original_map:
            raise RuntimeError(f"{label}: local DOS_PUTS2 changed MAP")
        map_text = map_data.decode("cp437")
        expected = (
            "0000:05D8 00B4 C=CODE", "M=filread", "0000:17AA 0000 C=DATA",
            "0000:051A 00BE C=CODE", "M=resdata", "0000:04F6 0024 C=CODE",
            "M=GRPCLEAR.ASM", "0000:05D8       FILE_READ",
            "0000:08B0 0010 C=CODE", "M=dosfree", "0000:08B0       DOS_FREE",
            "0000:08C0 0016 C=CODE", "M=dosc", "0000:08C0       DOS_AXDX",
            "0000:08D6 0028 C=CODE", "M=dosputs2", "0000:08D6       DOS_PUTS2",
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
            "dos_free_member_position": order.index("dosfree"),
            "dos_free_original_object_sha256": sha((saved / "dosfree-original.obj").read_bytes()),
            "dos_free_local_object_sha256": sha((saved / "dosfree.obj").read_bytes()),
            "dos_free_omf_code_sha256": sha(local_dos_free),
            "dos_axdx_member_position": order.index("dosc"),
            "dos_axdx_original_object_sha256": sha((saved / "dosc-original.obj").read_bytes()),
            "dos_axdx_local_object_sha256": sha((saved / "dosc.obj").read_bytes()),
            "dos_axdx_module_code_sha256": sha(local_dos_axdx),
            "dos_puts2_member_position": order.index("dosputs2"),
            "dos_puts2_original_object_sha256": sha((saved / "dosputs2-original.obj").read_bytes()),
            "dos_puts2_local_object_sha256": sha((saved / "dosputs2.obj").read_bytes()),
            "dos_puts2_link_relevant_omf_sha256": link_relevant_omf_sha(saved / "dosputs2.obj"),
            "dos_puts2_module_code_sha256": sha(local_dos_puts2),
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
    target_file_read = payload[0x1046:0x10FA]
    target_dos_free = payload[
        DOS_FREE_TARGET_OFFSET:DOS_FREE_TARGET_OFFSET + DOS_FREE_TARGET_SIZE
    ]
    target_dos_axdx_module = payload[
        DOS_AXDX_TARGET_OFFSET:DOS_AXDX_TARGET_OFFSET + DOS_AXDX_MODULE_SIZE
    ]
    target_dos_axdx_body = target_dos_axdx_module[:DOS_AXDX_BODY_SIZE]
    target_dos_puts2_module = payload[
        DOS_PUTS2_TARGET_OFFSET:DOS_PUTS2_TARGET_OFFSET + DOS_PUTS2_MODULE_SIZE
    ]
    target_dos_puts2_body = target_dos_puts2_module[:DOS_PUTS2_BODY_SIZE]
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target changed")
    if sha(payload) != PAYLOAD_SHA256 or sha(target_component) != TARGET_COMPONENT_SHA256:
        raise RuntimeError("attested decoded ZUN component changed")
    if (len(target_file_read), sha(target_file_read)) != (180, FILE_READ_TARGET_SHA256):
        raise RuntimeError("attested target FILE_READ CODE changed")
    if (len(target_dos_free), sha(target_dos_free)) != (
        DOS_FREE_TARGET_SIZE, DOS_FREE_CODE_SHA256
    ):
        raise RuntimeError("attested target DOS_FREE CODE changed")
    if (len(target_dos_axdx_body), sha(target_dos_axdx_body)) != (
        DOS_AXDX_BODY_SIZE, DOS_AXDX_BODY_SHA256
    ):
        raise RuntimeError("attested target DOS_AXDX body changed")
    if (len(target_dos_axdx_module), sha(target_dos_axdx_module)) != (
        DOS_AXDX_MODULE_SIZE, DOS_AXDX_MODULE_SHA256
    ) or target_dos_axdx_module[-1] != 0x90:
        raise RuntimeError("attested target DOS_AXDX module/padding changed")
    if (len(target_dos_puts2_body), sha(target_dos_puts2_body)) != (
        DOS_PUTS2_BODY_SIZE, DOS_PUTS2_BODY_SHA256
    ):
        raise RuntimeError("attested target DOS_PUTS2 body changed")
    if (len(target_dos_puts2_module), sha(target_dos_puts2_module)) != (
        DOS_PUTS2_MODULE_SIZE, DOS_PUTS2_MODULE_SHA256
    ) or target_dos_puts2_module[-1] != 0x90:
        raise RuntimeError("attested target DOS_PUTS2 module/padding changed")
    if sha(MASTER_LIB.read_bytes()) != MASTER_LIB_SHA256:
        raise RuntimeError("pinned external master library changed")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    inputs = {
        relative: sha((ROOT / relative).read_bytes())
        for relative in source_closure(ROOT, tuple(SOURCES.values()))
    }
    for source in (
        LOCAL_GRAPH_CLEAR, LOCAL_RESDATA, LOCAL_FILE_READ, LOCAL_DOS_FREE,
        LOCAL_DOS_AXDX, LOCAL_DOS_PUTS2,
    ):
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
    if candidate[0x4D8:0x58C] != target_file_read:
        raise RuntimeError("local FILE_READ linked CODE differs from target")
    if candidate[
        DOS_FREE_CANDIDATE_OFFSET:DOS_FREE_CANDIDATE_OFFSET + DOS_FREE_TARGET_SIZE
    ] != target_dos_free:
        raise RuntimeError("local DOS_FREE linked CODE differs from target")
    if candidate[
        DOS_AXDX_CANDIDATE_OFFSET:DOS_AXDX_CANDIDATE_OFFSET + DOS_AXDX_MODULE_SIZE
    ] != target_dos_axdx_module:
        raise RuntimeError("local DOS_AXDX linked module differs from target")
    if candidate[
        DOS_PUTS2_CANDIDATE_OFFSET:DOS_PUTS2_CANDIDATE_OFFSET + DOS_PUTS2_MODULE_SIZE
    ] != target_dos_puts2_module:
        raise RuntimeError("local DOS_PUTS2 linked module differs from target")
    differences = sum(a != b for a, b in zip(candidate, target_component))
    receipt = {
        "schema_version": 1,
        "claim_scope": "repository-owned DOS_PUTS2 support replaces external library member after local DOS_AXDX support; no authored or target exact claim",
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_component_sha256": TARGET_COMPONENT_SHA256,
        "target_file_read_extent": "decoded ZUN.COM 0x1046..0x10F9",
        "target_file_read_sha256": FILE_READ_TARGET_SHA256,
        "local_file_read_omf_code_sha256": FILE_READ_OMF_CODE_SHA256,
        "target_dos_free_extent": "decoded ZUN.COM 0x131E..0x132D",
        "target_dos_free_sha256": DOS_FREE_CODE_SHA256,
        "target_dos_axdx_extent": "decoded ZUN.COM function 0x132E..0x1342",
        "target_dos_axdx_body_sha256": DOS_AXDX_BODY_SHA256,
        "target_dos_axdx_module_extent": "decoded ZUN.COM 0x132E..0x1343",
        "target_dos_axdx_module_sha256": DOS_AXDX_MODULE_SHA256,
        "target_dos_axdx_padding": {"offset": "0x1343", "value": 0x90},
        "target_dos_puts2_extent": "decoded ZUN.COM function 0x1344..0x136A",
        "target_dos_puts2_body_sha256": DOS_PUTS2_BODY_SHA256,
        "target_dos_puts2_module_extent": "decoded ZUN.COM 0x1344..0x136B",
        "target_dos_puts2_module_sha256": DOS_PUTS2_MODULE_SHA256,
        "target_dos_puts2_padding": {"offset": "0x136B", "value": 0x90},
        "input_sha256": inputs,
        "external_master_lib_sha256": MASTER_LIB_SHA256,
        "link_response": LINK_RESPONSE,
        "compile": compiled,
        "link": linked,
        "component_raw_difference_count": differences,
        "file_read_raw_equal": True,
        "dos_free_raw_equal": True,
        "dos_axdx_body_raw_equal": True,
        "dos_axdx_module_raw_equal": True,
        "dos_puts2_body_raw_equal": True,
        "dos_puts2_module_raw_equal": True,
        "exact": differences == 0,
        "limit": "DOS_PUTS2 is library-origin support; its trailing module NOP is alignment outside the 0x27-byte function owner. External support, composite inputs, and the blocked resident layout remain; full packed artifact exact acceptance is open.",
    }
    if receipt["exact"]:
        raise RuntimeError("component unexpectedly matches; run full exact Oracle set")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"component {len(candidate)} bytes; {differences} raw differences; A/B SHA {linked['a']['component_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
