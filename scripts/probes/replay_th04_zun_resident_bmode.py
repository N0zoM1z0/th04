#!/usr/bin/env python3
"""Cold-replay the TH04 ZUN resident through TC4J's assembly backend."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

PROBE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROBE_DIR))

import replay_th04_zun_compact_master as compact
import replay_th04_zun_runtime_inventory as runtime
import replay_th04_zun_source_only as source

ROOT = source.ROOT
TARGET_COMPONENT_START = 0xB68
TARGET_COMPONENT_END = 0x2440
TARGET_COMPONENT_SHA256 = "cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110"
TARGET_CFG_START = 0xDCF
TARGET_CFG_END = 0xE67
TARGET_CFG_SHA256 = "8fc23f22f653db2afd65ad4cdab19776f5e9f1cdbbfa9de2dd407426fed9bfa2"
TARGET_MAIN_START = 0xE67
TARGET_MAIN_END = 0xF63
TARGET_MAIN_SHA256 = "db04398b52ca5780c734f839e2cf3768718f7f7c65705a9cdb9e88e34aa64871"
BMODE_MAIN_CODE_SHA256 = "293401ac19a4d186a6a7e4bb3ae51959443bc4706afe148af0a1660a6df03f0a"
EXACT_MAP_SHA256 = "4a0c1878500bde29db8d8d0696a63a9c4cb011868b58ec67d5a6b62a0e2b4ac6"

TASM_COMMAND = (
    r"set PATH=C:\TASM50\BIN;C:\TC4\BIN;%PATH%"
    r"&&tasm32 /m /mx /kh32768 /t obj\th04\main.asm obj\th04\main.obj"
)


def environment() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    return env


def materialize(work: Path, inputs: dict[str, str]) -> None:
    for relative, expected in inputs.items():
        src = ROOT / relative
        data = (
            src.read_text(encoding="utf-8").encode("cp932")
            if relative.endswith(".cpp")
            else src.read_bytes()
        )
        if source.sha((ROOT / relative).read_bytes()) != expected:
            raise RuntimeError(f"source input changed while replaying: {relative}")
        dst = work / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        os.utime(dst, (946684800, 946684800))


def bmode_main(label: str, compile_root: Path, inputs: dict[str, str]) -> dict[str, object]:
    saved = compile_root / label
    direct_obj = saved / "main.obj"
    direct_code = saved / "main.code"
    if not direct_obj.is_file() or not direct_code.is_file():
        raise RuntimeError(f"{label}: direct TC4J control build is missing")
    (saved / "main-direct.obj").write_bytes(direct_obj.read_bytes())
    (saved / "main-direct.code").write_bytes(direct_code.read_bytes())

    with tempfile.TemporaryDirectory(prefix=f"zun-bmode-{label}-", dir=compile_root) as tmp:
        work = Path(tmp)
        (work / "obj/th04").mkdir(parents=True)
        materialize(work, inputs)
        env = environment()
        command = [
            "wine", str(source.RUNNER), "-e", "-x", "tcc", "-B", *source.FLAGS,
            source.SOURCES["main"],
        ]
        completed = subprocess.run(
            command, cwd=work, env=env, capture_output=True, text=True, timeout=120
        )
        log = saved / "main-bmode-tcc.log"
        log.write_text(
            json.dumps(command) + f"\nexit={completed.returncode}\n"
            + completed.stdout + completed.stderr,
            encoding="utf-8",
        )
        asm = work / "obj/th04/main.asm"
        if (
            completed.returncode == 0
            or "Unable to execute command 'tasm.exe'" not in completed.stdout + completed.stderr
            or not asm.is_file()
        ):
            raise RuntimeError(
                f"{label}: TC4J -B did not stop at the expected unavailable tasm.exe boundary"
            )
        (saved / "main-bmode.asm").write_bytes(asm.read_bytes())

        tasm = ["wine", "cmd", "/d", "/c", TASM_COMMAND]
        assembled = subprocess.run(
            tasm, cwd=work, env=env, capture_output=True, text=True, timeout=120
        )
        tasm_log = saved / "main-bmode-tasm.log"
        tasm_log.write_text(
            json.dumps(tasm) + f"\nexit={assembled.returncode}\n"
            + assembled.stdout + assembled.stderr,
            encoding="utf-8",
        )
        obj = work / "obj/th04/main.obj"
        if assembled.returncode or not obj.is_file():
            raise RuntimeError(f"{label}: pinned TASM32 failed on TC4J-generated main.asm")

        object_data = obj.read_bytes()
        source.code(obj)  # Parse/checksum-validate the Intel OMF before copying it.
        code = source.code(obj)
        if len(code) != 0xFC or source.sha(code) != BMODE_MAIN_CODE_SHA256:
            raise RuntimeError(
                f"{label}: TC4J -B/TASM32 _main CODE drift: "
                f"{len(code)} bytes {source.sha(code)}"
            )
        direct = (saved / "main-direct.code").read_bytes()
        if len(direct) != 0xF6 or source.sha(direct) != source.EXPECTED_CODE["main"][1]:
            raise RuntimeError(f"{label}: direct-TC4J 246-byte control drift")

        direct_obj.write_bytes(object_data)
        direct_code.write_bytes(code)
        return {
            "tcc_command": command,
            "tcc_exit": completed.returncode,
            "tasm_command": tasm,
            "asm_sha256": source.sha(asm.read_bytes()),
            "object_sha256": source.sha(object_data),
            "link_relevant_omf_sha256": compact.base.link_relevant_omf_sha(obj),
            "code_size": len(code),
            "code_sha256": source.sha(code),
            "direct_control_code_size": len(direct),
            "direct_control_code_sha256": source.sha(direct),
        }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        ap.error("output directory must be new directly below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    subprocess.run(
        [sys.executable, "scripts/attest_toolchain.py"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )

    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text(encoding="utf-8"))
    target_info = next(row for row in manifest["artifacts"] if row["id"] == "th04-zun")
    packed = (ROOT / target_info["private_path"]).read_bytes()
    payload = source.PAYLOAD.read_bytes()
    target_component = payload[TARGET_COMPONENT_START:TARGET_COMPONENT_END]
    target_cfg = payload[TARGET_CFG_START:TARGET_CFG_END]
    target_main = payload[TARGET_MAIN_START:TARGET_MAIN_END]
    if len(packed) != target_info["size"] or source.sha(packed) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target identity drift")
    if source.sha(payload) != source.PAYLOAD_SHA256:
        raise RuntimeError("attested decoded ZUN payload identity drift")
    if source.sha(target_component) != TARGET_COMPONENT_SHA256:
        raise RuntimeError("target resident component identity drift")
    if source.sha(target_cfg) != TARGET_CFG_SHA256 or source.sha(target_main) != TARGET_MAIN_SHA256:
        raise RuntimeError("target authored ZUN slices changed")

    main_text = (ROOT / source.SOURCES["main"]).read_text(encoding="utf-8")
    required_shape = (
        'dos_puts2(ERROR_NOT_RESIDENT "\\n\\n");\n                goto failure;',
        'dos_puts2("作れません、わたしの居場所がないの！\\n\\n");\nfailure:\n        return 1;',
    )
    if any(shape not in main_text for shape in required_shape):
        raise RuntimeError("maintained _main no longer expresses the shared failure path")

    inputs = {
        relative: source.sha((ROOT / relative).read_bytes())
        for relative in source.source_closure(ROOT, tuple(source.SOURCES.values()))
    }
    for path in compact.SOURCES.values():
        inputs[str(path.relative_to(ROOT))] = source.sha(path.read_bytes())

    output.mkdir()
    compile_root = output / "compile"
    compile_root.mkdir()
    direct = {
        label: source.build(label, compile_root, {
            relative: digest
            for relative, digest in inputs.items()
            if relative in source.source_closure(ROOT, tuple(source.SOURCES.values()))
        })
        for label in ("a", "b")
    }
    stable_direct = ("object_sha256", "code_size", "code_sha256")
    if any(
        direct["a"][unit][key] != direct["b"][unit][key]
        for unit in source.SOURCES for key in stable_direct
    ):
        raise RuntimeError("direct TC4J control rounds differ")

    bmode = {
        label: bmode_main(label, compile_root, {
            relative: digest
            for relative, digest in inputs.items()
            if relative in source.source_closure(ROOT, tuple(source.SOURCES.values()))
        })
        for label in ("a", "b")
    }
    # TASM embeds the current DOS time in a translator COMENT record, so the
    # complete OBJ hash is intentionally diagnostic rather than a determinism
    # oracle. Generated ASM, link-relevant OMF, and CODE must be identical.
    for key in ("asm_sha256", "link_relevant_omf_sha256", "code_size", "code_sha256"):
        if bmode["a"][key] != bmode["b"][key]:
            raise RuntimeError(f"TC4J -B/TASM32 cold rounds differ at {key}")

    old_response = compact.base.LINK_RESPONSE
    old_component = compact.EXPECTED_COMPONENT_SHA256
    old_map = compact.EXPECTED_COMPACT_MAP_SHA256
    linked: dict[str, dict[str, object]] = {}
    try:
        compact.base.LINK_RESPONSE = runtime.REDUCED_LINK_RESPONSE
        compact.EXPECTED_COMPONENT_SHA256 = TARGET_COMPONENT_SHA256
        compact.EXPECTED_COMPACT_MAP_SHA256 = EXACT_MAP_SHA256
        for label in ("a", "b"):
            _saved, linked[label] = compact.assemble_all(label, output)
    finally:
        compact.base.LINK_RESPONSE = old_response
        compact.EXPECTED_COMPONENT_SHA256 = old_component
        compact.EXPECTED_COMPACT_MAP_SHA256 = old_map
    if linked["a"] != linked["b"]:
        raise RuntimeError("cold resident links differ")

    components = [(output / label / "res_huma.com").read_bytes() for label in ("a", "b")]
    maps = [(output / label / "res_huma.map").read_bytes() for label in ("a", "b")]
    if components[0] != components[1] or components[0] != target_component:
        raise RuntimeError("resident component is not raw-identical to target")
    if source.sha(maps[0]) != EXACT_MAP_SHA256 or maps[0] != maps[1]:
        raise RuntimeError("resident MAP is not deterministic")

    cfg = components[0][0x267:0x2FF]
    resident_main = components[0][0x2FF:0x3FB]
    if cfg != target_cfg or resident_main != target_main:
        raise RuntimeError("authored resident slices are not raw-identical to target")

    map_text = maps[0].decode("cp437")
    expected_map = (
        "0000:0367 0098 C=CODE",
        "M=src/zun/config/cfg_init.cpp",
        "0000:03FF 00FC C=CODE",
        r"M=obj\th04\main.asm",
    )
    if not all(fragment in map_text for fragment in expected_map):
        raise RuntimeError("resident authored MAP ownership drift")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": (
            "TH04 ZUN resident exact cold replay: maintained cfg_init C++ plus maintained "
            "_main C++ compiled through TC4J's assembly backend and pinned TASM32, then "
            "linked with the checked-in compact support archive inputs and c0t+CT runtime"
        ),
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": source.PAYLOAD_SHA256,
        "target_component_sha256": TARGET_COMPONENT_SHA256,
        "target_cfg_sha256": TARGET_CFG_SHA256,
        "target_main_sha256": TARGET_MAIN_SHA256,
        "source_input_sha256": inputs,
        "direct_tc4j_control": direct,
        "bmode_main": bmode,
        "link_response": runtime.REDUCED_LINK_RESPONSE,
        "remaining_external_runtime_inputs": ["c0t.obj", "ct.lib"],
        "link": linked,
        "resident_map_sha256": EXACT_MAP_SHA256,
        "component_raw_difference_count": 0,
        "cfg_raw_difference_count": 0,
        "main_raw_difference_count": 0,
        "exact": True,
        "conclusion": (
            "Direct TC4J still folds _main to 246 bytes. The maintained semantic "
            "failure-path source compiled via TC4J -B and pinned TASM32 emits the target "
            "252-byte selective-tail shape. The resulting 6360-byte resident component, "
            "including cfg_init relocation values and _main, is byte-identical to target "
            "in two cold rounds."
        ),
        "limit": (
            "This establishes decoded resident-component exactness only. c0t.obj and "
            "CT.LIB remain pinned compiler/runtime inputs, and ZUNINIT/ONGCHK/DIET plus "
            "packed-file ownership are outside this replay."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        f"resident exact {len(components[0])} bytes {source.sha(components[0])}; "
        f"cfg=0 diffs; main=0 diffs; direct-main=246; bmode-main=252"
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
