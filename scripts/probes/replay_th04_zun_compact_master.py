#!/usr/bin/env python3
"""Cold-link the TH04 ZUN resident without the external 640-member masters.lib."""

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
import tempfile
import tomllib

PROBE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROBE_DIR))
import replay_th04_zun_file_state as base

sys.path.insert(0, str(base.ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402


COMPACT_ORDER = (
    "VERSION",
    "GRP",
    "RESDATA",
    "FIL",
    "FILREAD",
    "FILCLOSE",
    "FILROPEN",
    "FILWRITE",
    "FILCREAT",
    "FILSEEK",
    "FILAPEND",
    "DOSFREE",
    "DOSC",
    "DOSPUTS2",
    "FONTOPEN",
)

SOURCES = {
    "GRPCLEAR": base.LOCAL_GRAPH_CLEAR,
    "VERSION": base.LOCAL_VERSION,
    "GRP": base.LOCAL_GRP,
    "RESDATA": base.LOCAL_RESDATA,
    "FIL": base.LOCAL_FILE_STATE,
    "FILREAD": base.LOCAL_FILE_READ,
    "FILCLOSE": base.LOCAL_FILE_CLOSE,
    "FILROPEN": base.LOCAL_FILE_ROPEN,
    "FILWRITE": base.LOCAL_FILE_WRITE,
    "FILCREAT": base.LOCAL_FILE_CREATE,
    "FILSEEK": base.LOCAL_FILE_SEEK,
    "FILAPEND": base.LOCAL_FILE_APPEND,
    "DOSFREE": base.LOCAL_DOS_FREE,
    "DOSC": base.LOCAL_DOS_AXDX,
    "DOSPUTS2": base.LOCAL_DOS_PUTS2,
    "FONTOPEN": base.LOCAL_FONTOPEN,
}

LINK_RELEVANT_OMF = {
    "GRPCLEAR": "abf71764a6f49dd581399a51b2748138a0c3a76814531c6d9b1479f08398a23a",
    "VERSION": "aa110fcf787d004e35e9e16e27ce31954a26d32651467c9d0ce6da50232ff0bc",
    "GRP": "162a24b820624c37dcf701a91c6baf0ea34be15b82fc4af0714a56bb2b79cfb7",
    "RESDATA": "217b5270213847d29fba4e7c8673413a238c040305202531f1a9d28937f6d673",
    "FIL": "70ec111491abefe0181bec46a21a994ab636dbe87991b5ce85a56363726d311b",
    "FILREAD": "8928f15d6d92c8f0535b5b8779d754152ca4460486307c4795f024047c0bde81",
    "FILCLOSE": "327f736eb0c0b24d9159c63993414d375331b97b7ac64d90ef02c2dca4a8c69b",
    "FILROPEN": "f1f2405a71273620bd5090b1f98a1dede77a40f7c01cf6f77b424c6b72d79bc6",
    "FILWRITE": "b73370867ca98773148bba4b0d333669cde6e61107705fbd88c3bc70e693ac5a",
    "FILCREAT": "81dc1ba9da568ea7b113af23815d6c70089218f9f9fe7b33213d4920e1d593da",
    "FILSEEK": "c8d1da245194db17e821ec1ed1e58022a24b29897ae787d976dcd8c1e63879bd",
    "FILAPEND": "d258612419a3b108b3da62949d10264564281df0551d32b15bbf957bda00de68",
    "DOSFREE": "792e5fc12d0ae096e495157cbf799b9e20d5e7d7f12c29c595042f4c5cbd9da6",
    "DOSC": "71bc2945246432493c9e789a7f1285a26c4e3d7332f7b5b9e0ca6ab4c59d72b7",
    "DOSPUTS2": "7106e7fd80b01134a9fbc76229f8dd09a62945bc67da0547d0ff237bff1e7a4d",
    "FONTOPEN": "7468e2b53697ba2426ba9c394e79510246da348935d80c95f49f024031900ac9",
}

EXPECTED_COMPONENT_SHA256 = "a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab"
EXPECTED_COMPACT_MAP_SHA256 = "ebe1475b9e8775e712e0e3ebd045cb1fa578b74592ea0c1dcef3c6e341d329db"
TARGET_COMPONENT_START = 0xB68
TARGET_COMPONENT_END = 0x2440
REMAINING_EXTERNAL_LINK_INPUTS = ("c0t.obj", "emu.lib", "maths.lib", "ct.lib")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive_physical_order(library: bytes, objects: dict[str, Path]) -> list[str]:
    if library[0] != 0xF0 or int.from_bytes(library[1:3], "little") + 3 != 16:
        raise RuntimeError("compact MASTER page format changed")
    by_header: dict[str, str] = {}
    for name, path in objects.items():
        records = parse_omf(path.read_bytes())
        header = records[0].data
        title = header[1:1 + header[0]].decode("ascii")
        if title in by_header:
            raise RuntimeError(f"duplicate compact THEADR {title}")
        by_header[title] = name
    physical: list[str] = []
    for offset in range(16, len(library), 16):
        if library[offset] != 0x80 or offset + 4 >= len(library):
            continue
        length = library[offset + 3]
        raw = library[offset + 4:offset + 4 + length]
        if raw.isascii() and all(32 <= byte < 127 for byte in raw):
            title = raw.decode("ascii")
            if title in by_header:
                physical.append(by_header[title])
    if set(physical) != set(objects) or len(physical) != len(objects):
        raise RuntimeError(f"compact MASTER physical order incomplete: {physical!r}")
    return physical


def assemble_all(label: str, output: Path) -> tuple[Path, dict[str, str]]:
    saved = output / label
    saved.mkdir()
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(base.ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    work = Path(tempfile.mkdtemp(prefix=f"zun-compact-{label}-", dir=output))
    (work / "obj/th04").mkdir(parents=True)
    (work / "bin/th04").mkdir(parents=True)
    (work / "local").mkdir()
    compiled = output / "compile" / label
    for name in ("cfg_init", "main"):
        shutil.copyfile(compiled / f"{name}.obj", work / "obj/th04" / f"{name}.obj")

    object_hashes: dict[str, str] = {}
    for name, source in SOURCES.items():
        local = work / f"{name}.ASM"
        shutil.copyfile(source, local)
        os.utime(local, (946684800, 946684800))
        command = [
            "wine", r"C:\TASM50\bin\TASM32.EXE", "/m", "/mx", "/kh32768",
            f"{name}.ASM,{name}.OBJ,{name}.LST",
        ]
        completed = subprocess.run(
            command, cwd=work, env=env, capture_output=True, text=True, timeout=120
        )
        (saved / f"{name.lower()}-assemble.log").write_text(
            json.dumps(command) + f"\nexit={completed.returncode}\n"
            + completed.stdout + completed.stderr,
            encoding="utf-8",
        )
        obj = work / f"{name}.OBJ"
        if completed.returncode or not obj.is_file():
            raise RuntimeError(f"{label}: {name} assembly failed")
        parse_omf(obj.read_bytes())
        relevant = base.link_relevant_omf_sha(obj)
        if relevant != LINK_RELEVANT_OMF[name]:
            raise RuntimeError(
                f"{label}: {name} link-relevant OMF changed: {relevant}"
            )
        object_hashes[name] = relevant
        (saved / f"{name.lower()}.obj").write_bytes(obj.read_bytes())

    if base.extdef_names(work / "GRP.OBJ") != ("_Master_Version",):
        raise RuntimeError(f"{label}: GRP lost VERSION force-link EXTDEF")

    shutil.copyfile(work / "GRPCLEAR.OBJ", work / "local/GRPCLEAR.OBJ")
    compact_objects = {}
    for name in COMPACT_ORDER:
        archive_path = work / f"{name.lower()}.obj"
        shutil.copyfile(work / f"{name}.OBJ", archive_path)
        compact_objects[name] = archive_path
    response = work / "COMPACT.RSP"
    response.write_text(
        " &\n".join("+" + name.lower() + ".obj" for name in COMPACT_ORDER) + "\n",
        encoding="ascii",
    )
    base.dos_tool(
        work, saved / "compact-library-build.log", env, label,
        "tlib", "masters.lib", "@COMPACT.RSP",
    )
    archive = work / "masters.lib"
    if not archive.is_file():
        raise RuntimeError(f"{label}: compact MASTER archive missing")
    physical = archive_physical_order(archive.read_bytes(), compact_objects)
    if tuple(physical) != COMPACT_ORDER:
        raise RuntimeError(f"{label}: compact MASTER order drift: {physical!r}")

    (work / "obj/th04/res_huma.@l").write_bytes(base.LINK_RESPONSE.encode("ascii"))
    component, map_data = base.link_component(
        work, saved, env, archive, "compact"
    )
    if sha(component) != EXPECTED_COMPONENT_SHA256:
        raise RuntimeError(f"{label}: compact MASTER changed resident bytes")
    if sha(map_data) != EXPECTED_COMPACT_MAP_SHA256:
        raise RuntimeError(f"{label}: compact MASTER MAP changed")

    map_text = map_data.decode("cp437")
    for module in (
        "version", "grp", "resdata", "fil", "filread", "filclose", "filropen",
        "filwrite", "filcreat", "filseek", "filapend", "dosfree", "dosc",
        "dosputs2", "fontopen",
    ):
        if f"M={module}" not in map_text:
            raise RuntimeError(f"{label}: compact MAP omitted {module}")
    (saved / "compact-masters.lib").write_bytes(archive.read_bytes())
    (saved / "res_huma.com").write_bytes(component)
    (saved / "res_huma.map").write_bytes(map_data)
    shutil.rmtree(work)
    return saved, {
        "archive_sha256": sha((saved / "compact-masters.lib").read_bytes()),
        "archive_size": (saved / "compact-masters.lib").stat().st_size,
        "component_sha256": sha(component),
        "map_sha256": sha(map_data),
        "physical_order": list(physical),
        "link_relevant_omf": object_hashes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (base.ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error(
            "output directory must be new directly below .analysis/reconstruction/probes"
        )

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=base.ROOT, check=True, capture_output=True, text=True,
    )
    subprocess.run(
        [sys.executable, "scripts/attest_toolchain.py"],
        cwd=base.ROOT, check=True, capture_output=True, text=True,
    )
    manifest = tomllib.loads((base.ROOT / "config/targets.toml").read_text())
    target_info = next(
        item for item in manifest["artifacts"] if item["id"] == "th04-zun"
    )
    target = (base.ROOT / target_info["private_path"]).read_bytes()
    payload = base.PAYLOAD.read_bytes()
    target_component = payload[TARGET_COMPONENT_START:TARGET_COMPONENT_END]
    if len(target) != target_info["size"] or base.sha(target) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target changed")
    if base.sha(payload) != base.PAYLOAD_SHA256:
        raise RuntimeError("attested decoded ZUN payload changed")
    if base.sha(target_component) != base.TARGET_COMPONENT_SHA256:
        raise RuntimeError("attested target resident component changed")

    input_hashes = {
        relative: base.sha((base.ROOT / relative).read_bytes())
        for relative in base.source_closure(base.ROOT, tuple(base.SOURCES.values()))
    }
    for source in SOURCES.values():
        input_hashes[str(source.relative_to(base.ROOT))] = base.sha(source.read_bytes())

    output.mkdir(parents=True)
    (output / "compile").mkdir()
    compiled = {
        label: base.build(label, output / "compile", input_hashes)
        for label in ("a", "b")
    }
    if compiled["a"] != compiled["b"]:
        raise RuntimeError("cold C++ source-only object rounds differ")

    linked = {}
    for label in ("a", "b"):
        _saved, linked[label] = assemble_all(label, output)
    if linked["a"] != linked["b"]:
        raise RuntimeError("cold compact MASTER link rounds differ")

    candidate = (output / "a/res_huma.com").read_bytes()
    differences = sum(a != b for a, b in zip(candidate, target_component))
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": (
            "TH04 ZUN resident compact local MASTER archive; external 640-member "
            "masters.lib is not read or linked"
        ),
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": base.PAYLOAD_SHA256,
        "target_component_sha256": base.TARGET_COMPONENT_SHA256,
        "input_sha256": input_hashes,
        "compact_member_count": len(COMPACT_ORDER),
        "compact_physical_order": list(COMPACT_ORDER),
        "external_master_lib_used": False,
        "remaining_external_link_inputs": list(REMAINING_EXTERNAL_LINK_INPUTS),
        "compile": compiled,
        "link": linked,
        "component_raw_difference_count": differences,
        "compact_component_equals_v535_control": True,
        "exact": differences == 0,
        "limit": (
            "This closes the external MASTER archive dependency only. Borland startup/"
            "CRT libraries remain external, resident _main/cfg_init remain blocked, and "
            "ZUNINIT/MEMCHK/composite packing are not source-closed."
        ),
    }
    if receipt["exact"]:
        raise RuntimeError("resident unexpectedly matches target; run full exact Oracle set")
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        f"compact MASTER {linked['a']['archive_size']} bytes / "
        f"{len(COMPACT_ORDER)} members; resident differences={differences}"
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
