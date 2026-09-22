#!/usr/bin/env python3
"""Probe TC4J debug/line-info modes on representative final TH04 blockers.

This is compiler-mechanism evidence only. It uses natural C++ source and the
attested TCC 4.02. It never injects target bytes or inline assembly and grants
no source/exactness credit.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import parse_omf  # noqa: E402
from probe_tc4_mov_bx_ax_encoding import code_bytes  # noqa: E402

BASE = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
PROFILES = (
    ("baseline", ()),
    ("source_debug_v", ("-v",)),
    ("line_info_y", ("-y",)),
    ("debug_and_line_vy", ("-v", "-y")),
)
PREFIX = "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n#include <dos.h>\n"
SUFFIX = "\n#pragma option -k.\n"
SOURCES = {
    "register_core": (
        "void near probe(void){ "
        "_BX=_AX; _SI=_AX; _DI=_DX; _DX=0; _BX+=_BX; _DI<<=1; "
        "_AX=(_AX*_BX); _ES=_DS; "
        "}"
    ),
    "checker_countdown": (
        "void near probe(void){ "
        "_CX=6; L: _ES=_DX; *((unsigned long __es *)_DI)=_EAX; "
        "_DI+=8; if(--_CX) goto L; "
        "}"
    ),
    "fixed_si_load": (
        "void near probe(void){ _AL = *((unsigned char near *)_SI++); }"
    ),
}
TARGET_REGISTER_PATTERNS = {
    "mov_bx_ax_89c3": bytes.fromhex("89 C3"),
    "mov_si_ax_89c6": bytes.fromhex("89 C6"),
    "mov_di_dx_89d7": bytes.fromhex("89 D7"),
    "xor_dx_31d2": bytes.fromhex("31 D2"),
    "add_bx_01db": bytes.fromhex("01 DB"),
    "shl_di_d1e7": bytes.fromhex("D1 E7"),
    "mul_bx_f7e3": bytes.fromhex("F7 E3"),
    "push_ds_pop_es_1e07": bytes.fromhex("1E 07"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tc4-debug-final-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def compile_one(
    out: Path, profile: str, extra_flags: tuple[str, ...], name: str, body: str
) -> dict[str, object]:
    work = out / name / profile
    work.mkdir(parents=True)
    source = work / "p.cpp"
    source.write_text(PREFIX + body + SUFFIX)
    command = [
        "wine",
        str(compile_one.runner),
        "-e",
        "-x",
        "tcc",
        *BASE,
        *extra_flags,
        f"-I{ROOT / '_reference/ReC98'}",
        source.name,
    ]
    done = subprocess.run(
        command,
        cwd=work,
        env=compile_one.env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    (work / "compile.log").write_text(done.stdout + done.stderr)
    obj = work / "p.obj"
    if done.returncode or not obj.is_file():
        raise RuntimeError(
            f"{name}/{profile} failed: {done.returncode}\n{done.stdout}{done.stderr}"
        )
    obj_bytes = obj.read_bytes()
    records = list(parse_omf(obj_bytes))
    code = code_bytes(obj)
    code_path = work / "p.code"
    code_path.write_bytes(code)
    dis = subprocess.run(
        ["ndisasm", "-b16", str(code_path)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    (work / "p.ndis").write_text(dis)
    counts = Counter(record.record_type for record in records)
    return {
        "source_sha256": sha(source.read_bytes()),
        "object_size": len(obj_bytes),
        "record_type_counts": {
            f"0x{record_type:02X}": count
            for record_type, count in sorted(counts.items())
        },
        "linnum_record_count": counts[0x94] + counts[0x95],
        "code_sha256": sha(code),
        "code_hex": code.hex(),
        "code_size": len(code),
        "disassembly": dis.splitlines(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    out = make_output(args.output_dir)

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(item for item in surfaces if item["id"] == "active-tcc")
    tcc_path = ROOT / tcc["path"]
    if sha(tcc_path.read_bytes()) != tcc["sha256"]:
        raise ValueError("active TC4J identity drift")

    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    compile_one.runner = runner
    compile_one.env = env

    results: dict[str, object] = {}
    any_target_shape = False
    code_changed_profiles: dict[str, list[str]] = {}
    for name, body in SOURCES.items():
        profiles = {
            profile: compile_one(out, profile, extra, name, body)
            for profile, extra in PROFILES
        }
        baseline = profiles["baseline"]
        changed = [
            profile
            for profile, _ in PROFILES
            if profiles[profile]["code_hex"] != baseline["code_hex"]
        ]
        code_changed_profiles[name] = changed
        per_profile = {}
        for profile, _ in PROFILES:
            item = profiles[profile]
            code = bytes.fromhex(str(item["code_hex"]))
            dis = "\n".join(item["disassembly"]).lower()
            hits = {
                key: pattern in code
                for key, pattern in TARGET_REGISTER_PATTERNS.items()
            }
            has_loop = any(
                " loop " in (" " + line.lower() + " ")
                for line in item["disassembly"]
            )
            has_lodsb = "lodsb" in dis
            candidate = (
                any(hits.values())
                or (name == "checker_countdown" and has_loop)
                or (name == "fixed_si_load" and has_lodsb)
            )
            any_target_shape = any_target_shape or candidate
            per_profile[profile] = {
                **item,
                "target_register_pattern_hits": hits,
                "contains_loop_instruction": has_loop,
                "contains_lodsb": has_lodsb,
                "candidate_instruction_selection": candidate,
            }
        results[name] = per_profile

    # The line-info switch must visibly add line-number metadata, or the probe
    # would not prove that this compiler surface was actually active.
    for name in SOURCES:
        if results[name]["line_info_y"]["linnum_record_count"] <= 0:
            raise ValueError(f"{name}: -y did not add LINNUM metadata")
        if results[name]["debug_and_line_vy"]["linnum_record_count"] <= 0:
            raise ValueError(f"{name}: -v -y did not retain LINNUM metadata")
    if any_target_shape:
        raise ValueError("debug/line-info profile emitted a target residual shape")

    probe_sha256 = sha(Path(__file__).read_bytes())
    runner_sha256 = sha(runner.read_bytes())
    input_bundle_sha256 = sha(
        json.dumps(
            {
                "tcc_sha256": tcc["sha256"],
                "runner_sha256": runner_sha256,
                "probe_sha256": probe_sha256,
                "base_flags": BASE,
                "profiles": PROFILES,
                "sources": SOURCES,
                "target_register_patterns": {
                    key: value.hex()
                    for key, value in TARGET_REGISTER_PATTERNS.items()
                },
            },
            sort_keys=True,
        ).encode()
    )

    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J -v/-y final MAIN blocker codegen surface",
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": runner_sha256,
        "probe_sha256": probe_sha256,
        "input_bundle_sha256": input_bundle_sha256,
        "base_flags": list(BASE),
        "profiles": [
            {"name": name, "extra_flags": list(extra)}
            for name, extra in PROFILES
        ],
        "results": results,
        "code_changed_profiles": code_changed_profiles,
        "any_candidate_instruction_selection": any_target_shape,
        "conclusion": (
            "The attested TCC 4.02 -v/-y debug surfaces are active (-y adds "
            "LINNUM metadata, and debug profiles may change surrounding CODE), "
            "but none of baseline, -v, -y, or -v -y selects the remaining TH04 "
            "target forms for the representative register core, counted "
            "checkerboard loop, or fixed-SI byte load."
        ),
        "limit": (
            "This closes only the tested source-debug/line-info compiler surface. "
            "It does not prove original source language, authorize inline "
            "assembly, or grant exactness credit."
        ),
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "receipt": str(path),
                "receipt_sha256": sha(path.read_bytes()),
                "probe_sha256": receipt["probe_sha256"],
                "input_bundle_sha256": receipt["input_bundle_sha256"],
                "code_changed_profiles": code_changed_profiles,
                "any_candidate_instruction_selection": any_target_shape,
                "linnum_counts": {
                    name: {
                        profile: results[name][profile]["linnum_record_count"]
                        for profile, _ in PROFILES
                    }
                    for name in SOURCES
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
