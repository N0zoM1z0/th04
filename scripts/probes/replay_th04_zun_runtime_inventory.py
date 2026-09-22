#!/usr/bin/env python3
"""Drop unused EMU/MATHS from TH04 ZUN resident and inventory pulled CT modules."""

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
import replay_th04_zun_compact_master as compact

base = compact.base

REDUCED_LINK_RESPONSE = (
    "-c -s -t c0t.obj obj\\th04\\cfg_init.obj obj\\th04\\main.obj "
    "local\\GRPCLEAR.OBJ, bin\\th04\\res_huma.com, obj\\th04\\res_huma.map, "
    "bin\\masters.lib ct.lib\r\n"
)

TOOLCHAIN_LIB = base.ROOT / ".analysis/toolchain/wineprefix/drive_c/TC4/LIB"
RUNTIME_INPUTS = {
    "c0t.obj": (
        TOOLCHAIN_LIB / "C0T.OBJ",
        "27169f062a9b77bf4accfb9550ca4ccbf0fd710d4b1232768630d53bb6305f7c",
    ),
    "emu.lib": (
        TOOLCHAIN_LIB / "EMU.LIB",
        "e702f1f5dc95d61bdb1689af746d69ac5e303e38ebf77175cd6fd600eb3edc74",
    ),
    "maths.lib": (
        TOOLCHAIN_LIB / "MATHS.LIB",
        "ad76cb7f5b81105d4cc83691c74c030a6f5e1a56be0d1f5b5eca43f3124693cd",
    ),
    "ct.lib": (
        TOOLCHAIN_LIB / "CT.LIB",
        "b665d5d30f0d3bafe3023ee45eeef183811c87201e9a1876f011acf5699261af",
    ),
}

LOCAL_MAP_MODULES = {
    "src/zun/config/cfg_init.cpp",
    "src/zun/resident/main.cpp",
    "GRPCLEAR.ASM",
    "version",
    "grp",
    "resdata",
    "fil",
    "filread",
    "filclose",
    "filropen",
    "filwrite",
    "filcreat",
    "filseek",
    "filapend",
    "dosfree",
    "dosc",
    "dosputs2",
    "fontopen",
}

EXPECTED_CT_MODULES = (
    "_abort",
    "_pathops",
    "atexit",
    "brk",
    "errormsg",
    "exit",
    "fflush",
    "files",
    "files2",
    "flushall",
    "fseek",
    "heaplen",
    "ioerror",
    "isatty",
    "lseek",
    "n_scopy",
    "nearheap",
    "setargv",
    "setupio",
    "setvbuf",
    "stklen",
    "strlen",
    "sysnerr",
    "write",
    "writea",
    "xfflush",
)

EXPECTED_C0_MODULE = "c0.ASM"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def map_modules(map_data: bytes) -> list[str]:
    pattern = re.compile(
        r"^\s*[0-9A-F]{4}:[0-9A-F]{4}\s+[0-9A-F]{4}\s+C=[A-Z]+"
        r"\s+S=[^\s]+.*?\bM=([^\s]+)",
        re.I | re.M,
    )
    result: list[str] = []
    for match in pattern.finditer(map_data.decode("cp437")):
        module = match.group(1)
        if module not in result:
            result.append(module)
    return result


def list_members(
    lib_name: str,
    source: Path,
    output: Path,
    environment: dict[str, str],
) -> list[str]:
    work = output / ("inventory-" + lib_name.replace(".", "-"))
    work.mkdir()
    local = work / lib_name
    shutil.copyfile(source, local)
    listing = work / "members.lst"
    base.dos_tool(
        work,
        work / "tlib.log",
        environment,
        "inventory-" + lib_name,
        "tlib",
        lib_name,
        ",",
        "members.lst",
    )
    text = listing.read_text(encoding="cp437")
    names = re.findall(r"^([^ \t\r\n]+)\s+size = ", text, re.M)
    if not names:
        raise RuntimeError(f"{lib_name}: empty TLIB inventory")
    return names


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
        cwd=base.ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [sys.executable, "scripts/attest_toolchain.py"],
        cwd=base.ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    manifest = tomllib.loads((base.ROOT / "config/targets.toml").read_text())
    target_info = next(
        item for item in manifest["artifacts"] if item["id"] == "th04-zun"
    )
    target = (base.ROOT / target_info["private_path"]).read_bytes()
    payload = base.PAYLOAD.read_bytes()
    target_component = payload[
        compact.TARGET_COMPONENT_START:compact.TARGET_COMPONENT_END
    ]
    if len(target) != target_info["size"] or base.sha(target) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target changed")
    if base.sha(payload) != base.PAYLOAD_SHA256:
        raise RuntimeError("attested decoded ZUN payload changed")
    if base.sha(target_component) != base.TARGET_COMPONENT_SHA256:
        raise RuntimeError("attested target resident component changed")

    for name, (path, expected) in RUNTIME_INPUTS.items():
        if not path.is_file() or sha(path.read_bytes()) != expected:
            raise RuntimeError(f"pinned runtime input changed: {name}")

    # Prove c0t.obj is the direct c0.ASM startup producer.
    c0_records = compact.parse_omf(RUNTIME_INPUTS["c0t.obj"][0].read_bytes())
    c0_headers = [
        record.data[1:1 + record.data[0]].decode("ascii")
        for record in c0_records
        if record.record_type == 0x80
    ]
    if c0_headers != [EXPECTED_C0_MODULE]:
        raise RuntimeError(f"c0t.obj THEADR drift: {c0_headers!r}")

    input_hashes = {
        relative: base.sha((base.ROOT / relative).read_bytes())
        for relative in base.source_closure(base.ROOT, tuple(base.SOURCES.values()))
    }
    for source in compact.SOURCES.values():
        input_hashes[str(source.relative_to(base.ROOT))] = base.sha(source.read_bytes())

    output.mkdir(parents=True)
    (output / "compile").mkdir()
    compiled = {
        label: base.build(label, output / "compile", input_hashes)
        for label in ("a", "b")
    }
    if compiled["a"] != compiled["b"]:
        raise RuntimeError("cold C++ source-only object rounds differ")

    original_response = base.LINK_RESPONSE
    if "emu.lib maths.lib ct.lib" not in original_response:
        raise RuntimeError("full resident link response drifted")
    linked = {}
    try:
        base.LINK_RESPONSE = REDUCED_LINK_RESPONSE
        for label in ("a", "b"):
            _saved, linked[label] = compact.assemble_all(label, output)
    finally:
        base.LINK_RESPONSE = original_response
    if linked["a"] != linked["b"]:
        raise RuntimeError("cold reduced-runtime link rounds differ")

    candidate = (output / "a/res_huma.com").read_bytes()
    map_data = (output / "a/res_huma.map").read_bytes()
    if sha(candidate) != compact.EXPECTED_COMPONENT_SHA256:
        raise RuntimeError("dropping EMU/MATHS changed resident bytes")
    if sha(map_data) != compact.EXPECTED_COMPACT_MAP_SHA256:
        raise RuntimeError("dropping EMU/MATHS changed resident MAP")

    modules = map_modules(map_data)
    if EXPECTED_C0_MODULE not in modules:
        raise RuntimeError("c0 startup module missing from MAP")
    external = [
        module
        for module in modules
        if module not in LOCAL_MAP_MODULES and module != EXPECTED_C0_MODULE
    ]
    if tuple(sorted(external, key=str.lower)) != tuple(
        sorted(EXPECTED_CT_MODULES, key=str.lower)
    ):
        raise RuntimeError(f"runtime MAP module inventory drift: {external!r}")

    environment = os.environ.copy()
    environment.update(
        WINEPREFIX=str(base.ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    inventories = {}
    for lib_name in ("emu.lib", "maths.lib", "ct.lib"):
        inventories[lib_name] = list_members(
            lib_name, RUNTIME_INPUTS[lib_name][0], output, environment
        )
    external_lower = {module.lower() for module in external}
    emu_hits = [
        name for name in inventories["emu.lib"] if name.lower() in external_lower
    ]
    maths_hits = [
        name for name in inventories["maths.lib"] if name.lower() in external_lower
    ]
    if emu_hits or maths_hits:
        raise RuntimeError(
            f"runtime module aliases unexpectedly overlap EMU/MATHS: "
            f"{emu_hits!r} {maths_hits!r}"
        )
    ct_index = {name.lower(): i for i, name in enumerate(inventories["ct.lib"])}
    ct_members = []
    for module in EXPECTED_CT_MODULES:
        key = module.lower()
        if key not in ct_index:
            raise RuntimeError(f"CT.LIB no longer contains mapped module {module}")
        ct_members.append(
            {"module": module, "member": inventories["ct.lib"][ct_index[key]],
             "zero_based_index": ct_index[key]}
        )

    differences = sum(a != b for a, b in zip(candidate, target_component))
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": (
            "TH04 ZUN resident runtime inventory; EMU.LIB and MATHS.LIB removed "
            "from link response with byte-identical output"
        ),
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": base.PAYLOAD_SHA256,
        "target_component_sha256": base.TARGET_COMPONENT_SHA256,
        "input_sha256": input_hashes,
        "runtime_input_sha256": {
            name: expected for name, (_path, expected) in RUNTIME_INPUTS.items()
        },
        "full_link_response": original_response,
        "reduced_link_response": REDUCED_LINK_RESPONSE,
        "removed_link_inputs": ["emu.lib", "maths.lib"],
        "remaining_external_link_inputs": ["c0t.obj", "ct.lib"],
        "c0_module": EXPECTED_C0_MODULE,
        "ct_pulled_members": ct_members,
        "ct_pulled_member_count": len(ct_members),
        "emu_pulled_members": [],
        "maths_pulled_members": [],
        "compile": compiled,
        "link": linked,
        "component_raw_difference_count": differences,
        "reduced_component_equals_v536_control": True,
        "reduced_map_equals_v536_control": True,
        "exact": differences == 0,
        "limit": (
            "EMU/MATHS are proven unused for this resident link. c0t.obj and 26 "
            "CT.LIB members remain compiler/runtime inputs; no CRT member is "
            "reclassified as authored source. Resident _main/cfg_init and "
            "component provenance blockers remain."
        ),
    }
    if receipt["exact"]:
        raise RuntimeError("resident unexpectedly matches target; run full exact Oracle set")
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        f"removed EMU/MATHS; CT pulled={len(ct_members)}; "
        f"resident differences={differences}"
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
