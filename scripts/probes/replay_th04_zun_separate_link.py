#!/usr/bin/env python3
"""Cold-link the two checked-in ZUN C++ units with pinned external support."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

from replay_th04_zun_source_only import (
    HEADERS, PAYLOAD, PAYLOAD_SHA256, ROOT, RUNNER, SOURCES, build, sha,
)

MASTER_LIB = ROOT / (
    ".analysis/reconstruction/exact-unit-replay/"
    "gptweb-v214-demo-fixupp-diagnostic-001/a/source/bin/masters.lib"
)
MASTER_LIB_SHA256 = "6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6"
TARGET_COMPONENT_SHA256 = "cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110"
LINK_RESPONSE = (
    "-c -s -t c0t.obj obj\\th04\\cfg_init.obj obj\\th04\\main.obj, "
    "bin\\th04\\res_huma.com, obj\\th04\\res_huma.map, "
    "bin\\masters.lib emu.lib maths.lib ct.lib\r\n"
)


def link(label: str, output: Path) -> dict[str, object]:
    saved = output / label
    saved.mkdir()
    compiled = output / "compile" / label
    environment = os.environ.copy()
    environment.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    with tempfile.TemporaryDirectory(prefix=f"zun-link-{label}-", dir=output) as temporary:
        work = Path(temporary)
        (work / "obj/th04").mkdir(parents=True)
        (work / "bin/th04").mkdir(parents=True)
        for name in ("cfg_init", "main"):
            shutil.copyfile(compiled / f"{name}.obj", work / "obj/th04" / f"{name}.obj")
        shutil.copyfile(MASTER_LIB, work / "bin/masters.lib")
        (work / "obj/th04/res_huma.@l").write_bytes(LINK_RESPONSE.encode("ascii"))
        command = ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\res_huma.@l"]
        completed = subprocess.run(
            command, cwd=work, env=environment, capture_output=True, text=True, timeout=120,
        )
        (saved / "link.log").write_text(
            json.dumps(command) + f"\nexit={completed.returncode}\n"
            + completed.stdout + completed.stderr,
            encoding="utf-8",
        )
        component_path = work / "bin/th04/res_huma.com"
        map_path = work / "obj/th04/res_huma.map"
        if completed.returncode or not component_path.is_file() or not map_path.is_file():
            raise RuntimeError(f"{label}: TLINK failed: {saved / 'link.log'}")
        component = component_path.read_bytes()
        map_data = map_path.read_bytes()
        (saved / "res_huma.com").write_bytes(component)
        (saved / "res_huma.map").write_bytes(map_data)
        map_text = map_data.decode("cp437")
        expected = (
            "0000:0367 0098 C=CODE", "M=src/zun/config/cfg_init.cpp",
            "0000:03FF 00F6 C=CODE", "M=src/zun/resident/main.cpp",
        )
        if not all(fragment in map_text for fragment in expected):
            raise RuntimeError(f"{label}: maintained C++ MAP contributions changed")
        return {
            "component_size": len(component),
            "component_sha256": sha(component),
            "map_sha256": sha(map_data),
            "cfg_code_start": "_TEXT 0x367",
            "cfg_code_size": 152,
            "main_code_start": "_TEXT 0x3FF",
            "main_code_size": 246,
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
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target changed")
    if sha(payload) != PAYLOAD_SHA256 or sha(target_component) != TARGET_COMPONENT_SHA256:
        raise RuntimeError("attested decoded ZUN component changed")
    if sha(MASTER_LIB.read_bytes()) != MASTER_LIB_SHA256:
        raise RuntimeError("pinned external master library changed")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)

    inputs = {relative: sha((ROOT / relative).read_bytes()) for relative in (*SOURCES.values(), *HEADERS)}
    output.mkdir(parents=True)
    (output / "compile").mkdir()
    compiled = {label: build(label, output / "compile", inputs) for label in ("a", "b")}
    if compiled["a"] != compiled["b"]:
        raise RuntimeError("cold source-only object rounds differ")
    linked = {label: link(label, output) for label in ("a", "b")}
    if linked["a"] != linked["b"]:
        raise RuntimeError("cold component link rounds differ")
    candidate = (output / "a/res_huma.com").read_bytes()
    if len(candidate) != len(target_component):
        raise RuntimeError("component size changed; review MAP and boundaries")
    differences = sum(a != b for a, b in zip(candidate, target_component))
    receipt = {
        "schema_version": 1,
        "claim_scope": "separate ZUN C++ link using checked-in source/header and external pinned library; no exact/product build claim",
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_component_extent": "decoded ZUN.COM 0xB68..0x243F",
        "target_component_sha256": TARGET_COMPONENT_SHA256,
        "input_sha256": inputs,
        "external_master_lib_sha256": MASTER_LIB_SHA256,
        "external_master_lib_source": str(MASTER_LIB.relative_to(ROOT)),
        "link_response": LINK_RESPONSE,
        "compile": compiled,
        "link": linked,
        "component_raw_difference_count": differences,
        "exact": differences == 0,
        "limit": "Support master library is external, _main remains 246 versus 252 target bytes, and ZUNINIT/MEMCHK/ONGCHK/DIET product inputs are not source-closed.",
    }
    if receipt["exact"]:
        raise RuntimeError("component unexpectedly matches; run full exact Oracle set")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"component {len(candidate)} bytes; {differences} raw differences; A/B SHA {linked['a']['component_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
