#!/usr/bin/env python3
"""Cold-replace ZUN's graph clear library member with checked-in TASM source."""

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
    PAYLOAD, PAYLOAD_SHA256, ROOT, RUNNER, SOURCES, build, sha, source_closure,
)
from replay_th04_zun_cfg_init import code

MASTER_LIB = ROOT / (
    ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source/bin/masters.lib"
)
MASTER_LIB_SHA256 = "6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6"
TARGET_COMPONENT_SHA256 = "cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110"
TARGET_GRAPH_CLEAR_SHA256 = "a210c6bc7dcf7fb2fb44e2e37d14d82d535f71511f0bbfda30d481c5da6c2a07"
LOCAL_GRAPH_CLEAR = ROOT / "src/shared/pc98/graph_clear.asm"
LOCAL_GRAPH_CLEAR_CODE_SHA256 = "46f3bad51bb1860265b7b30d15fe7ae8e5a0fa0b7f169f8e85711ff71acc0e75"
BASELINE_COMPONENT_SHA256 = "a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab"
LINK_RESPONSE = (
    "-c -s -t c0t.obj obj\\th04\\cfg_init.obj obj\\th04\\main.obj GRPCLEAR.OBJ, "
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
        shutil.copyfile(LOCAL_GRAPH_CLEAR, work / "GRPCLEAR.ASM")
        os.utime(work / "GRPCLEAR.ASM", (946684800, 946684800))
        assemble_command = [
            "wine", r"C:\TASM50\bin\TASM32.EXE", "/m", "/mx", "/kh32768",
            "GRPCLEAR.ASM,GRPCLEAR.OBJ,GRPCLEAR.LST",
        ]
        assembled = subprocess.run(
            assemble_command, cwd=work, env=environment,
            capture_output=True, text=True, timeout=120,
        )
        (saved / "assemble.log").write_text(
            json.dumps(assemble_command) + f"\nexit={assembled.returncode}\n"
            + assembled.stdout + assembled.stderr,
            encoding="utf-8",
        )
        graph_object = work / "GRPCLEAR.OBJ"
        if assembled.returncode or not graph_object.is_file():
            raise RuntimeError(f"{label}: local GRAPH_CLEAR assembly failed")
        graph_code = code(graph_object)
        if len(graph_code) != 36 or sha(graph_code) != LOCAL_GRAPH_CLEAR_CODE_SHA256:
            raise RuntimeError(f"{label}: local GRAPH_CLEAR CODE changed")
        (saved / "graph_clear.obj").write_bytes(graph_object.read_bytes())
        (saved / "graph_clear.code").write_bytes(graph_code)
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
            "0000:04F6 0024 C=CODE", "M=GRPCLEAR.ASM",
        )
        if not all(fragment in map_text for fragment in expected) or "M=grpclear " in map_text:
            raise RuntimeError(f"{label}: maintained C++ MAP contributions changed")
        if sha(component) != BASELINE_COMPONENT_SHA256:
            raise RuntimeError(f"{label}: local GRAPH_CLEAR changed linked component bytes")
        return {
            "component_size": len(component),
            "component_sha256": sha(component),
            "map_sha256": sha(map_data),
            "graph_clear_object_sha256": sha(graph_object.read_bytes()),
            "graph_clear_code_sha256": sha(graph_code),
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
    target_graph_clear = payload[0xF64:0xF88]
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target changed")
    if sha(payload) != PAYLOAD_SHA256 or sha(target_component) != TARGET_COMPONENT_SHA256:
        raise RuntimeError("attested decoded ZUN component changed")
    if len(target_graph_clear) != 36 or sha(target_graph_clear) != TARGET_GRAPH_CLEAR_SHA256:
        raise RuntimeError("attested target GRAPH_CLEAR extent changed")
    if sha(MASTER_LIB.read_bytes()) != MASTER_LIB_SHA256:
        raise RuntimeError("pinned external master library changed")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)

    inputs = {
        relative: sha((ROOT / relative).read_bytes())
        for relative in source_closure(ROOT, tuple(SOURCES.values()))
    }
    output.mkdir(parents=True)
    (output / "compile").mkdir()
    compiled = {label: build(label, output / "compile", inputs) for label in ("a", "b")}
    if compiled["a"] != compiled["b"]:
        raise RuntimeError("cold source-only object rounds differ")
    linked = {label: link(label, output) for label in ("a", "b")}
    if linked["a"] != linked["b"]:
        raise RuntimeError("cold component link rounds differ")
    candidate = (output / "a/res_huma.com").read_bytes()
    candidate_graph_clear = candidate[0x3F6:0x41A]
    if candidate_graph_clear != target_graph_clear:
        raise RuntimeError("local GRAPH_CLEAR linked bytes differ from target extent")
    if len(candidate) != len(target_component):
        raise RuntimeError("component size changed; review MAP and boundaries")
    differences = sum(a != b for a, b in zip(candidate, target_component))
    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04-owned PC-98 GRAPH_CLEAR replaces external library member without changing linked ZUN resident bytes; no target exact claim",
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_component_extent": "decoded ZUN.COM 0xB68..0x243F",
        "target_component_sha256": TARGET_COMPONENT_SHA256,
        "target_graph_clear_extent": "decoded ZUN.COM _TEXT 0xF64..0xF87",
        "target_graph_clear_sha256": TARGET_GRAPH_CLEAR_SHA256,
        "input_sha256": inputs,
        "local_graph_clear_source_sha256": sha(LOCAL_GRAPH_CLEAR.read_bytes()),
        "external_master_lib_sha256": MASTER_LIB_SHA256,
        "external_master_lib_source": str(MASTER_LIB.relative_to(ROOT)),
        "link_response": LINK_RESPONSE,
        "compile": compiled,
        "link": linked,
        "component_raw_difference_count": differences,
        "graph_clear_raw_equal": True,
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
