#!/usr/bin/env python3
"""Cold-replace ZUN's FILE_FLUSH/FILE_CLOSE library member after local FILE_APPEND support."""

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
LOCAL_FILE_CREATE = ROOT / "src/shared/dos/file_create.asm"
FILE_CREATE_BODY_SHA256 = "afff204a724a02973d7a5ccaad7a755d86a3d466baf2d2554ea62bb86fd0f5b1"
FILE_CREATE_MODULE_SHA256 = "935b2c0a3b3c7fab8c5dc101d9067fc7cbf47178d5647cb476203e7cb3269143"
FILE_CREATE_OMF_CODE_SHA256 = "298acf4d14307f246e62648794288bdd2a4cf5a3ea027b14dfeae18e13b6ce2e"
FILE_CREATE_LINK_RELEVANT_OMF_SHA256 = "81dc1ba9da568ea7b113af23815d6c70089218f9f9fe7b33213d4920e1d593da"
FILE_CREATE_MEMBER_POSITION = 172
FILE_CREATE_TARGET_OFFSET = 0x1250
FILE_CREATE_BODY_SIZE = 0x3B
FILE_CREATE_MODULE_SIZE = 0x3C
FILE_CREATE_CANDIDATE_OFFSET = 0x6E2
LOCAL_FILE_ROPEN = ROOT / "src/shared/dos/file_ropen.asm"
FILE_ROPEN_MODULE_SHA256 = "93f82add9fb6bbde2532b0fe425029be749eea77f8582977456e8676ead80e3b"
FILE_ROPEN_OMF_CODE_SHA256 = "b6e5775192cd434cd3496033afd2c01cf67af3ed9a7a68ffc3046df29c0e1e0c"
FILE_ROPEN_LINK_RELEVANT_OMF_SHA256 = "f1f2405a71273620bd5090b1f98a1dede77a40f7c01cf6f77b424c6b72d79bc6"
FILE_ROPEN_MEMBER_POSITION = 170
FILE_ROPEN_TARGET_OFFSET = 0x1174
FILE_ROPEN_MODULE_SIZE = 0x36
FILE_ROPEN_CANDIDATE_OFFSET = 0x606
LOCAL_FILE_WRITE = ROOT / "src/shared/dos/file_write.asm"
FILE_WRITE_MODULE_SHA256 = "aedf0cf1cbc8b4a9a2ca24475d02b761019148143de91f412e1274fa6167ae71"
FILE_WRITE_OMF_CODE_SHA256 = "b0b3dee01db46e8000b8b335e32f6270a9940a067a75c700a833775e89433c90"
FILE_WRITE_LINK_RELEVANT_OMF_SHA256 = "b73370867ca98773148bba4b0d333669cde6e61107705fbd88c3bc70e693ac5a"
FILE_WRITE_MEMBER_POSITION = 171
FILE_WRITE_TARGET_OFFSET = 0x11AA
FILE_WRITE_MODULE_SIZE = 0xA6
FILE_WRITE_CANDIDATE_OFFSET = 0x63C
LOCAL_FILE_SEEK = ROOT / "src/shared/dos/file_seek.asm"
FILE_SEEK_BODY_SHA256 = "349277df795d98cd8cbca8f33bd67d2f28823948cbd173101008fbe4ff571575"
FILE_TELL_BODY_SHA256 = "1b1850b8e4c09cf4a123667471565abb6b30ed80b4e646ef89a18efd4324b897"
FILE_SEEK_MODULE_SHA256 = "97d28f9689f230c9d01bb0a1006619bb489bac5672d6c43fa1392279e141df01"
FILE_SEEK_OMF_CODE_SHA256 = "d28bd048ef86f5b1a8ef5d70c2945e36d93938cf0f614f6bc794034be7040cc2"
FILE_SEEK_LINK_RELEVANT_OMF_SHA256 = "c8d1da245194db17e821ec1ed1e58022a24b29897ae787d976dcd8c1e63879bd"
FILE_SEEK_MEMBER_POSITION = 177
FILE_SEEK_TARGET_OFFSET = 0x128C
FILE_SEEK_BODY_SIZE = 0x33
FILE_SEEK_PADDING_OFFSET = 0x33
FILE_TELL_BODY_SIZE = 0x0E
FILE_SEEK_MODULE_SIZE = 0x42
FILE_SEEK_CANDIDATE_OFFSET = 0x71E
LOCAL_FILE_APPEND = ROOT / "src/shared/dos/file_append.asm"
FILE_APPEND_MODULE_SHA256 = "ae7738e040ed138bb1e8b0d6a29e589d163c9e579f1584431db598f3b5825df5"
FILE_APPEND_OMF_CODE_SHA256 = "d696c040bb4e1a86f4028d0777fa6ef9af1c56ecd2a8dc8372e718a29de7cec5"
FILE_APPEND_LINK_RELEVANT_OMF_SHA256 = "d258612419a3b108b3da62949d10264564281df0551d32b15bbf957bda00de68"
FILE_APPEND_MEMBER_POSITION = 182
FILE_APPEND_TARGET_OFFSET = 0x12CE
FILE_APPEND_MODULE_SIZE = 0x50
FILE_APPEND_CANDIDATE_OFFSET = 0x760
LOCAL_FILE_CLOSE = ROOT / "src/shared/dos/file_close.asm"
FILE_FLUSH_BODY_SHA256 = "d1d0993554f298bde55a09b8e79a49e7f3819db9ec869c903937347af8e495da"
FILE_CLOSE_BODY_SHA256 = "9af8f01eaf9db22dbf91343f0fcdfa1d579951320cfdd11181622cccb6bc21ca"
FILE_CLOSE_MODULE_SHA256 = "90029ad4fbf09f328e31116ad1618037ef39a6866b05f661842142fba3f438ac"
FILE_CLOSE_OMF_CODE_SHA256 = "f7aea53ef369cf41b32b3167382f3f5aa60e1c0b139b767af1b1c03869a30a15"
FILE_CLOSE_LINK_RELEVANT_OMF_SHA256 = "327f736eb0c0b24d9159c63993414d375331b97b7ac64d90ef02c2dca4a8c69b"
FILE_CLOSE_MEMBER_POSITION = 167
FILE_CLOSE_TARGET_OFFSET = 0x10FA
FILE_FLUSH_BODY_SIZE = 0x6B
FILE_CLOSE_PADDING_OFFSET = 0x6B
FILE_CLOSE_BODY_SIZE = 0x0E
FILE_CLOSE_MODULE_SIZE = 0x7A
FILE_CLOSE_CANDIDATE_OFFSET = 0x58C


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


def file_create_object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != FILE_CREATE_MODULE_SIZE:
        raise RuntimeError("FILE_CREATE OMF CODE layout changed")
    return sections[0]


def file_ropen_object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != FILE_ROPEN_MODULE_SIZE:
        raise RuntimeError("FILE_ROPEN OMF CODE layout changed")
    return sections[0]


def file_write_object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != FILE_WRITE_MODULE_SIZE:
        raise RuntimeError("FILE_WRITE OMF CODE layout changed")
    return sections[0]


def file_seek_object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != FILE_SEEK_MODULE_SIZE:
        raise RuntimeError("FILE_SEEK OMF CODE layout changed")
    return sections[0]


def file_append_object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != FILE_APPEND_MODULE_SIZE:
        raise RuntimeError("FILE_APPEND OMF CODE layout changed")
    return sections[0]


def file_close_object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [record.data[3:] for record in records if record.record_type == 0xA0
                and record.data[1:3] == b"\0\0"]
    if len(sections) != 1 or len(sections[0]) != FILE_CLOSE_MODULE_SIZE:
        raise RuntimeError("FILE_CLOSE OMF CODE layout changed")
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
                   ("FILREAD", LOCAL_FILE_READ), ("DOSFREE", LOCAL_DOS_FREE),
                   ("DOSC", LOCAL_DOS_AXDX), ("DOSPUTS2", LOCAL_DOS_PUTS2),
                   ("FILCREAT", LOCAL_FILE_CREATE), ("FILROPEN", LOCAL_FILE_ROPEN),
                   ("FILWRITE", LOCAL_FILE_WRITE), ("FILSEEK", LOCAL_FILE_SEEK),
                   ("FILAPEND", LOCAL_FILE_APPEND), ("FILCLOSE", LOCAL_FILE_CLOSE))
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
        local_file_create = file_create_object_code(saved / "filcreat.obj")
        if sha(local_file_create) != FILE_CREATE_OMF_CODE_SHA256:
            raise RuntimeError(f"{label}: local FILE_CREATE OMF CODE changed")
        if link_relevant_omf_sha(saved / "filcreat.obj") != FILE_CREATE_LINK_RELEVANT_OMF_SHA256:
            raise RuntimeError(f"{label}: local FILE_CREATE link-relevant OMF changed")
        local_file_ropen = file_ropen_object_code(saved / "filropen.obj")
        if sha(local_file_ropen) != FILE_ROPEN_OMF_CODE_SHA256:
            raise RuntimeError(f"{label}: local FILE_ROPEN OMF CODE changed")
        if link_relevant_omf_sha(saved / "filropen.obj") != FILE_ROPEN_LINK_RELEVANT_OMF_SHA256:
            raise RuntimeError(f"{label}: local FILE_ROPEN link-relevant OMF changed")
        local_file_write = file_write_object_code(saved / "filwrite.obj")
        if sha(local_file_write) != FILE_WRITE_OMF_CODE_SHA256:
            raise RuntimeError(f"{label}: local FILE_WRITE OMF CODE changed")
        if link_relevant_omf_sha(saved / "filwrite.obj") != FILE_WRITE_LINK_RELEVANT_OMF_SHA256:
            raise RuntimeError(f"{label}: local FILE_WRITE link-relevant OMF changed")
        local_file_seek = file_seek_object_code(saved / "filseek.obj")
        if sha(local_file_seek) != FILE_SEEK_OMF_CODE_SHA256:
            raise RuntimeError(f"{label}: local FILE_SEEK OMF CODE changed")
        if link_relevant_omf_sha(saved / "filseek.obj") != FILE_SEEK_LINK_RELEVANT_OMF_SHA256:
            raise RuntimeError(f"{label}: local FILE_SEEK link-relevant OMF changed")
        local_file_append = file_append_object_code(saved / "filapend.obj")
        if sha(local_file_append) != FILE_APPEND_OMF_CODE_SHA256:
            raise RuntimeError(f"{label}: local FILE_APPEND OMF CODE changed")
        if link_relevant_omf_sha(saved / "filapend.obj") != FILE_APPEND_LINK_RELEVANT_OMF_SHA256:
            raise RuntimeError(f"{label}: local FILE_APPEND link-relevant OMF changed")
        local_file_close = file_close_object_code(saved / "filclose.obj")
        if sha(local_file_close) != FILE_CLOSE_OMF_CODE_SHA256:
            raise RuntimeError(f"{label}: local FILE_CLOSE OMF CODE changed")
        if link_relevant_omf_sha(saved / "filclose.obj") != FILE_CLOSE_LINK_RELEVANT_OMF_SHA256:
            raise RuntimeError(f"{label}: local FILE_CLOSE link-relevant OMF changed")
        dos_tool(work, saved / "library-list.log", environment, label, "tlib",
                 "masters.lib", ",", "MEMBERS.LST")
        listing = (work / "MEMBERS.LST").read_text(encoding="cp437")
        names = re.findall(r"^([^ \t\r\n]+)\s+size = ", listing, re.M)
        if (len(names) != 640 or names.count("filread") != 1
                or names.count("dosfree") != 1 or names.count("dosc") != 1
                or names.count("dosputs2") != 1 or names.count("filcreat") != 1
                or names.count("filropen") != 1 or names.count("filwrite") != 1
                or names.count("filseek") != 1 or names.count("filapend") != 1
                or names.count("filclose") != 1):
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
        original_file_create = work / "filcreat.OBJ"
        original_file_create_code = file_create_object_code(original_file_create)
        if original_file_create_code != local_file_create:
            raise RuntimeError(f"{label}: local FILE_CREATE LEDATA differs from original member")
        (saved / "filcreat-original.obj").write_bytes(original_file_create.read_bytes())
        original_file_ropen = work / "filropen.OBJ"
        original_file_ropen_code = file_ropen_object_code(original_file_ropen)
        if original_file_ropen_code != local_file_ropen:
            raise RuntimeError(f"{label}: local FILE_ROPEN LEDATA differs from original member")
        (saved / "filropen-original.obj").write_bytes(original_file_ropen.read_bytes())
        original_file_write = work / "filwrite.OBJ"
        original_file_write_code = file_write_object_code(original_file_write)
        if original_file_write_code != local_file_write:
            raise RuntimeError(f"{label}: local FILE_WRITE LEDATA differs from original member")
        (saved / "filwrite-original.obj").write_bytes(original_file_write.read_bytes())
        original_file_seek = work / "filseek.OBJ"
        original_file_seek_code = file_seek_object_code(original_file_seek)
        if original_file_seek_code != local_file_seek:
            raise RuntimeError(f"{label}: local FILE_SEEK LEDATA differs from original member")
        (saved / "filseek-original.obj").write_bytes(original_file_seek.read_bytes())
        original_file_append = work / "filapend.OBJ"
        original_file_append_code = file_append_object_code(original_file_append)
        if original_file_append_code != local_file_append:
            raise RuntimeError(f"{label}: local FILE_APPEND LEDATA differs from original member")
        (saved / "filapend-original.obj").write_bytes(original_file_append.read_bytes())
        original_file_close = work / "filclose.OBJ"
        original_file_close_code = file_close_object_code(original_file_close)
        if original_file_close_code != local_file_close:
            raise RuntimeError(f"{label}: local FILE_CLOSE LEDATA differs from original member")
        (saved / "filclose-original.obj").write_bytes(original_file_close.read_bytes())
        order = original_physical_order(MASTER_LIB.read_bytes(), work, names)
        if order.index("filread") != 165:
            raise RuntimeError(f"{label}: FILE_READ library member moved")
        if order.index("dosfree") != DOS_FREE_MEMBER_POSITION:
            raise RuntimeError(f"{label}: DOS_FREE library member moved")
        if order.index("dosc") != DOS_AXDX_MEMBER_POSITION:
            raise RuntimeError(f"{label}: DOS_AXDX library member moved")
        if order.index("dosputs2") != DOS_PUTS2_MEMBER_POSITION:
            raise RuntimeError(f"{label}: DOS_PUTS2 library member moved")
        if order.index("filcreat") != FILE_CREATE_MEMBER_POSITION:
            raise RuntimeError(f"{label}: FILE_CREATE library member moved")
        if order.index("filropen") != FILE_ROPEN_MEMBER_POSITION:
            raise RuntimeError(f"{label}: FILE_ROPEN library member moved")
        if order.index("filwrite") != FILE_WRITE_MEMBER_POSITION:
            raise RuntimeError(f"{label}: FILE_WRITE library member moved")
        if order.index("filseek") != FILE_SEEK_MEMBER_POSITION:
            raise RuntimeError(f"{label}: FILE_SEEK library member moved")
        if order.index("filapend") != FILE_APPEND_MEMBER_POSITION:
            raise RuntimeError(f"{label}: FILE_APPEND library member moved")
        if order.index("filclose") != FILE_CLOSE_MEMBER_POSITION:
            raise RuntimeError(f"{label}: FILE_CLOSE library member moved")
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
        shutil.copyfile(saved / "filcreat.obj", original_file_create)
        shutil.copyfile(saved / "filropen.obj", original_file_ropen)
        shutil.copyfile(saved / "filwrite.obj", original_file_write)
        shutil.copyfile(saved / "filseek.obj", original_file_seek)
        shutil.copyfile(saved / "filapend.obj", original_file_append)
        shutil.copyfile(saved / "filclose.obj", original_file_close)
        dos_tool(work, saved / "local-library-build.log", environment, label,
                 "tlib", "LOCAL.LIB", "@BUILD.RSP")
        component, map_data = link_component(
            work, saved, environment, work / "LOCAL.LIB", "local")
        if component != original_component or sha(component) != BASELINE_COMPONENT_SHA256:
            raise RuntimeError(f"{label}: local FILE_CLOSE changed component bytes")
        if map_data != original_map:
            raise RuntimeError(f"{label}: local FILE_CLOSE changed MAP")
        map_text = map_data.decode("cp437")
        expected = (
            "0000:05D8 00B4 C=CODE", "M=filread", "0000:17AA 0000 C=DATA",
            "0000:051A 00BE C=CODE", "M=resdata", "0000:04F6 0024 C=CODE",
            "M=GRPCLEAR.ASM", "0000:05D8       FILE_READ",
            "0000:08B0 0010 C=CODE", "M=dosfree", "0000:08B0       DOS_FREE",
            "0000:08C0 0016 C=CODE", "M=dosc", "0000:08C0       DOS_AXDX",
            "0000:08D6 0028 C=CODE", "M=dosputs2", "0000:08D6       DOS_PUTS2",
            "0000:07E2 003C C=CODE", "M=filcreat", "0000:07E2       FILE_CREATE",
            "0000:0706 0036 C=CODE", "M=filropen", "0000:0706       FILE_ROPEN",
            "0000:073C 00A6 C=CODE", "M=filwrite", "0000:073C       FILE_WRITE",
            "0000:081E 0042 C=CODE", "M=filseek",
            "0000:081E       FILE_SEEK", "0000:0852 idle  FILE_TELL",
            "0000:0860 0050 C=CODE", "M=filapend", "0000:0860       FILE_APPEND",
            "0000:068C 007A C=CODE", "M=filclose",
            "0000:068C       FILE_FLUSH", "0000:06F8       FILE_CLOSE",
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
            "file_create_member_position": order.index("filcreat"),
            "file_create_original_object_sha256": sha((saved / "filcreat-original.obj").read_bytes()),
            "file_create_local_object_sha256": sha((saved / "filcreat.obj").read_bytes()),
            "file_create_link_relevant_omf_sha256": link_relevant_omf_sha(saved / "filcreat.obj"),
            "file_create_module_code_sha256": sha(local_file_create),
            "file_ropen_member_position": order.index("filropen"),
            "file_ropen_original_object_sha256": sha((saved / "filropen-original.obj").read_bytes()),
            "file_ropen_local_object_sha256": sha((saved / "filropen.obj").read_bytes()),
            "file_ropen_link_relevant_omf_sha256": link_relevant_omf_sha(saved / "filropen.obj"),
            "file_ropen_module_code_sha256": sha(local_file_ropen),
            "file_write_member_position": order.index("filwrite"),
            "file_write_original_object_sha256": sha((saved / "filwrite-original.obj").read_bytes()),
            "file_write_local_object_sha256": sha((saved / "filwrite.obj").read_bytes()),
            "file_write_link_relevant_omf_sha256": link_relevant_omf_sha(saved / "filwrite.obj"),
            "file_write_module_code_sha256": sha(local_file_write),
            "file_seek_member_position": order.index("filseek"),
            "file_seek_original_object_sha256": sha((saved / "filseek-original.obj").read_bytes()),
            "file_seek_local_object_sha256": sha((saved / "filseek.obj").read_bytes()),
            "file_seek_link_relevant_omf_sha256": link_relevant_omf_sha(saved / "filseek.obj"),
            "file_seek_module_code_sha256": sha(local_file_seek),
            "file_append_member_position": order.index("filapend"),
            "file_append_original_object_sha256": sha((saved / "filapend-original.obj").read_bytes()),
            "file_append_local_object_sha256": sha((saved / "filapend.obj").read_bytes()),
            "file_append_link_relevant_omf_sha256": link_relevant_omf_sha(saved / "filapend.obj"),
            "file_append_module_code_sha256": sha(local_file_append),
            "file_close_member_position": order.index("filclose"),
            "file_close_original_object_sha256": sha((saved / "filclose-original.obj").read_bytes()),
            "file_close_local_object_sha256": sha((saved / "filclose.obj").read_bytes()),
            "file_close_link_relevant_omf_sha256": link_relevant_omf_sha(saved / "filclose.obj"),
            "file_close_module_code_sha256": sha(local_file_close),
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
    target_file_create_module = payload[
        FILE_CREATE_TARGET_OFFSET:FILE_CREATE_TARGET_OFFSET + FILE_CREATE_MODULE_SIZE
    ]
    target_file_create_body = target_file_create_module[:FILE_CREATE_BODY_SIZE]
    target_file_ropen_module = payload[
        FILE_ROPEN_TARGET_OFFSET:FILE_ROPEN_TARGET_OFFSET + FILE_ROPEN_MODULE_SIZE
    ]
    target_file_write_module = payload[
        FILE_WRITE_TARGET_OFFSET:FILE_WRITE_TARGET_OFFSET + FILE_WRITE_MODULE_SIZE
    ]
    target_file_seek_module = payload[
        FILE_SEEK_TARGET_OFFSET:FILE_SEEK_TARGET_OFFSET + FILE_SEEK_MODULE_SIZE
    ]
    target_file_seek_body = target_file_seek_module[:FILE_SEEK_BODY_SIZE]
    target_file_tell_body = target_file_seek_module[
        FILE_SEEK_PADDING_OFFSET + 1:
    ]
    target_file_append_module = payload[
        FILE_APPEND_TARGET_OFFSET:FILE_APPEND_TARGET_OFFSET + FILE_APPEND_MODULE_SIZE
    ]
    target_file_close_module = payload[
        FILE_CLOSE_TARGET_OFFSET:FILE_CLOSE_TARGET_OFFSET + FILE_CLOSE_MODULE_SIZE
    ]
    target_file_flush_body = target_file_close_module[:FILE_FLUSH_BODY_SIZE]
    target_file_close_body = target_file_close_module[
        FILE_CLOSE_PADDING_OFFSET + 1:
    ]
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
    if (len(target_file_create_body), sha(target_file_create_body)) != (
        FILE_CREATE_BODY_SIZE, FILE_CREATE_BODY_SHA256
    ):
        raise RuntimeError("attested target FILE_CREATE body changed")
    if (len(target_file_create_module), sha(target_file_create_module)) != (
        FILE_CREATE_MODULE_SIZE, FILE_CREATE_MODULE_SHA256
    ) or target_file_create_module[-1] != 0x90:
        raise RuntimeError("attested target FILE_CREATE module/padding changed")
    if (len(target_file_ropen_module), sha(target_file_ropen_module)) != (
        FILE_ROPEN_MODULE_SIZE, FILE_ROPEN_MODULE_SHA256
    ):
        raise RuntimeError("attested target FILE_ROPEN module changed")
    if (len(target_file_write_module), sha(target_file_write_module)) != (
        FILE_WRITE_MODULE_SIZE, FILE_WRITE_MODULE_SHA256
    ):
        raise RuntimeError("attested target FILE_WRITE module changed")
    if (len(target_file_seek_body), sha(target_file_seek_body)) != (
        FILE_SEEK_BODY_SIZE, FILE_SEEK_BODY_SHA256
    ):
        raise RuntimeError("attested target FILE_SEEK body changed")
    if target_file_seek_module[FILE_SEEK_PADDING_OFFSET] != 0x90:
        raise RuntimeError("attested FILE_SEEK/FILE_TELL padding changed")
    if (len(target_file_tell_body), sha(target_file_tell_body)) != (
        FILE_TELL_BODY_SIZE, FILE_TELL_BODY_SHA256
    ):
        raise RuntimeError("attested target FILE_TELL body changed")
    if (len(target_file_seek_module), sha(target_file_seek_module)) != (
        FILE_SEEK_MODULE_SIZE, FILE_SEEK_MODULE_SHA256
    ):
        raise RuntimeError("attested target FILE_SEEK module changed")
    if (len(target_file_append_module), sha(target_file_append_module)) != (
        FILE_APPEND_MODULE_SIZE, FILE_APPEND_MODULE_SHA256
    ):
        raise RuntimeError("attested target FILE_APPEND module changed")
    if (len(target_file_flush_body), sha(target_file_flush_body)) != (
        FILE_FLUSH_BODY_SIZE, FILE_FLUSH_BODY_SHA256
    ):
        raise RuntimeError("attested target FILE_FLUSH body changed")
    if target_file_close_module[FILE_CLOSE_PADDING_OFFSET] != 0x90:
        raise RuntimeError("attested FILE_FLUSH/FILE_CLOSE padding changed")
    if (len(target_file_close_body), sha(target_file_close_body)) != (
        FILE_CLOSE_BODY_SIZE, FILE_CLOSE_BODY_SHA256
    ):
        raise RuntimeError("attested target FILE_CLOSE body changed")
    if (len(target_file_close_module), sha(target_file_close_module)) != (
        FILE_CLOSE_MODULE_SIZE, FILE_CLOSE_MODULE_SHA256
    ):
        raise RuntimeError("attested target FILE_CLOSE module changed")
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
        LOCAL_DOS_AXDX, LOCAL_DOS_PUTS2, LOCAL_FILE_CREATE, LOCAL_FILE_ROPEN,
        LOCAL_FILE_WRITE, LOCAL_FILE_SEEK, LOCAL_FILE_APPEND, LOCAL_FILE_CLOSE,
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
    if candidate[
        FILE_CREATE_CANDIDATE_OFFSET:FILE_CREATE_CANDIDATE_OFFSET + FILE_CREATE_MODULE_SIZE
    ] != target_file_create_module:
        raise RuntimeError("local FILE_CREATE linked module differs from target")
    if candidate[
        FILE_ROPEN_CANDIDATE_OFFSET:FILE_ROPEN_CANDIDATE_OFFSET + FILE_ROPEN_MODULE_SIZE
    ] != target_file_ropen_module:
        raise RuntimeError("local FILE_ROPEN linked module differs from target")
    if candidate[
        FILE_WRITE_CANDIDATE_OFFSET:FILE_WRITE_CANDIDATE_OFFSET + FILE_WRITE_MODULE_SIZE
    ] != target_file_write_module:
        raise RuntimeError("local FILE_WRITE linked module differs from target")
    if candidate[
        FILE_SEEK_CANDIDATE_OFFSET:FILE_SEEK_CANDIDATE_OFFSET + FILE_SEEK_MODULE_SIZE
    ] != target_file_seek_module:
        raise RuntimeError("local FILE_SEEK module differs from target")
    if candidate[
        FILE_APPEND_CANDIDATE_OFFSET:FILE_APPEND_CANDIDATE_OFFSET + FILE_APPEND_MODULE_SIZE
    ] != target_file_append_module:
        raise RuntimeError("local FILE_APPEND module differs from target")
    if candidate[
        FILE_CLOSE_CANDIDATE_OFFSET:FILE_CLOSE_CANDIDATE_OFFSET + FILE_CLOSE_MODULE_SIZE
    ] != target_file_close_module:
        raise RuntimeError("local FILE_CLOSE module differs from target")
    differences = sum(a != b for a, b in zip(candidate, target_component))
    receipt = {
        "schema_version": 1,
        "claim_scope": "repository-owned FILE_FLUSH and FILE_CLOSE support replace one external library member after local FILE_APPEND support; no authored or target exact claim",
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
        "target_file_create_extent": "decoded ZUN.COM function 0x1250..0x128A",
        "target_file_create_body_sha256": FILE_CREATE_BODY_SHA256,
        "target_file_create_module_extent": "decoded ZUN.COM 0x1250..0x128B",
        "target_file_create_module_sha256": FILE_CREATE_MODULE_SHA256,
        "target_file_create_padding": {"offset": "0x128B", "value": 0x90},
        "target_file_ropen_extent": "decoded ZUN.COM 0x1174..0x11A9",
        "target_file_ropen_sha256": FILE_ROPEN_MODULE_SHA256,
        "target_file_write_extent": "decoded ZUN.COM 0x11AA..0x124F",
        "target_file_write_sha256": FILE_WRITE_MODULE_SHA256,
        "target_file_seek_extent": "decoded ZUN.COM function 0x128C..0x12BE",
        "target_file_seek_sha256": FILE_SEEK_BODY_SHA256,
        "target_file_seek_padding": {"offset": "0x12BF", "value": 0x90},
        "target_file_tell_extent": "decoded ZUN.COM function 0x12C0..0x12CD",
        "target_file_tell_sha256": FILE_TELL_BODY_SHA256,
        "target_file_seek_module_extent": "decoded ZUN.COM 0x128C..0x12CD",
        "target_file_seek_module_sha256": FILE_SEEK_MODULE_SHA256,
        "target_file_append_extent": "decoded ZUN.COM 0x12CE..0x131D",
        "target_file_append_sha256": FILE_APPEND_MODULE_SHA256,
        "target_file_flush_extent": "decoded ZUN.COM function 0x10FA..0x1164",
        "target_file_flush_sha256": FILE_FLUSH_BODY_SHA256,
        "target_file_close_padding": {"offset": "0x1165", "value": 0x90},
        "target_file_close_extent": "decoded ZUN.COM function 0x1166..0x1173",
        "target_file_close_sha256": FILE_CLOSE_BODY_SHA256,
        "target_file_close_module_extent": "decoded ZUN.COM 0x10FA..0x1173",
        "target_file_close_module_sha256": FILE_CLOSE_MODULE_SHA256,
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
        "file_create_body_raw_equal": True,
        "file_create_module_raw_equal": True,
        "file_ropen_raw_equal": True,
        "file_write_raw_equal": True,
        "file_seek_raw_equal": True,
        "file_tell_raw_equal": True,
        "file_seek_module_raw_equal": True,
        "file_append_raw_equal": True,
        "file_flush_raw_equal": True,
        "file_close_raw_equal": True,
        "file_close_module_raw_equal": True,
        "exact": differences == 0,
        "limit": "FILE_FLUSH and FILE_CLOSE are library-origin support. The one-byte 0x90 between them is module alignment outside both function owners. External support, composite inputs, and the blocked resident layout remain; full packed artifact exact acceptance is open.",
    }
    if receipt["exact"]:
        raise RuntimeError("component unexpectedly matches; run full exact Oracle set")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"component {len(candidate)} bytes; {differences} raw differences; A/B SHA {linked['a']['component_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
