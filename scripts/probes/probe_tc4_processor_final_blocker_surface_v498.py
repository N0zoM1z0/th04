#!/usr/bin/env python3
"""Probe TC4J 16-bit processor targets on the remaining TH04 MAIN blockers.

This is compiler-mechanism evidence only. It tests the compiler's supported
default/-1/-2/-3/-4 processor selections without inline assembly, target byte
injection, or product-source changes.
"""
from __future__ import annotations

import argparse
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
sys.path.insert(0, str(ROOT / "scripts/probes"))

from probe_tc4_checkerboard_loop_forms import VARIANTS as CHECKER_VARIANTS  # noqa: E402
from probe_tc4_mov_bx_ax_encoding import code_bytes  # noqa: E402

BASE = ("-c", "-ml", "-O", "-b-", "-Z", "-d")
PROFILES: tuple[tuple[str, str | None], ...] = (
    ("default", None),
    ("80186", "-1"),
    ("80286", "-2"),
    ("80386", "-3"),
    ("80486", "-4"),
)
PREFIX = "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n#include <dos.h>\n"
SUFFIX = "\n#pragma option -k.\n"
REGISTER_CORE = (
    "void near probe(void) { "
    "_BX=_AX; _SI=_AX; _DI=_DX; _DX=0; _BX+=_BX; _DI<<=1; "
    "_AX=(_AX*_BX); _ES=_DS; "
    "}"
)
TARGET_PATTERNS = {
    "mov_bx_ax_89c3": bytes.fromhex("89 C3"),
    "mov_si_ax_89c6": bytes.fromhex("89 C6"),
    "mov_di_dx_89d7": bytes.fromhex("89 D7"),
    "xor_dx_31d2": bytes.fromhex("31 D2"),
    "add_bx_01db": bytes.fromhex("01 DB"),
    "shl_di_d1e7": bytes.fromhex("D1 E7"),
    "mul_bx_f7e3": bytes.fromhex("F7 E3"),
    "push_ds_pop_es_1e07": bytes.fromhex("1E 07"),
}
LODSB_VARIANTS = {
    "si_postinc_cast":
        "void near probe(void){ _AL = *((unsigned char near *)_SI++); }",
    "si_postinc_reinterpret":
        "void near probe(void){ _AL = "
        "*reinterpret_cast<unsigned char near *>(_SI++); }",
    "si_load_then_inc":
        "void near probe(void){ _AL = "
        "*reinterpret_cast<unsigned char near *>(_SI); _SI++; }",
    "register_ptr":
        "void near probe(void){ register unsigned char near *p = "
        "reinterpret_cast<unsigned char near *>(_SI); _AL = *p++; "
        "_SI = reinterpret_cast<unsigned int>(p); }",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tc4-processor-final-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def compile_one(
    out: Path,
    profile: str,
    cpu_flag: str | None,
    name: str,
    body: str,
) -> dict[str, object]:
    work = out / profile / name
    work.mkdir(parents=True)
    source = work / "p.cpp"
    source.write_text(PREFIX + body + SUFFIX)
    flags = [*BASE]
    if cpu_flag is not None:
        flags.append(cpu_flag)
    command = [
        "wine",
        str(compile_one.runner),
        "-e",
        "-x",
        "tcc",
        *flags,
        f"-I{ROOT / '_reference/ReC98'}",
        "p.cpp",
    ]
    done = subprocess.run(
        command,
        cwd=work,
        env=compile_one.env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    log = done.stdout + done.stderr
    (work / "compile.log").write_text(log)
    result: dict[str, object] = {
        "source_sha256": sha(source.read_bytes()),
        "compile_exit": done.returncode,
    }
    obj = work / "p.obj"
    if done.returncode != 0 or not obj.is_file():
        result["compiled"] = False
        result["error_undefined_eax"] = "Undefined symbol '_EAX'" in log
        return result

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
    result.update(
        {
            "compiled": True,
            "code_hex": code.hex(),
            "code_sha256": sha(code),
            "code_size": len(code),
            "has_loop": any(
                " loop " in (" " + line.lower() + " ")
                for line in dis.splitlines()
            ),
            "has_lodsb": "lodsb" in dis.lower(),
            "target_pattern_hits": {
                key: pattern in code for key, pattern in TARGET_PATTERNS.items()
            },
        }
    )
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    out = make_output(args.output_dir)

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())[
        "surfaces"
    ]
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
    for profile, cpu_flag in PROFILES:
        core = compile_one(
            out, profile, cpu_flag, "register-core", REGISTER_CORE
        )
        checker = {
            name: compile_one(
                out, profile, cpu_flag, f"checker-{name}", body
            )
            for name, body in CHECKER_VARIANTS.items()
        }
        lodsb = {
            name: compile_one(
                out, profile, cpu_flag, f"lodsb-{name}", body
            )
            for name, body in LODSB_VARIANTS.items()
        }
        results[profile] = {
            "cpu_flag": cpu_flag,
            "register_core": core,
            "checkerboard": checker,
            "lodsb": lodsb,
        }

    summary: dict[str, object] = {}
    any_candidate = False
    for profile, _ in PROFILES:
        item = results[profile]
        core = item["register_core"]
        core_hits = (
            [key for key, hit in core["target_pattern_hits"].items() if hit]
            if core["compiled"]
            else []
        )
        checker = item["checkerboard"]
        checker_compiled = [
            name for name, value in checker.items() if value["compiled"]
        ]
        checker_loop_hits = [
            name
            for name, value in checker.items()
            if value["compiled"] and value["has_loop"]
        ]
        lodsb = item["lodsb"]
        lodsb_compiled = [
            name for name, value in lodsb.items() if value["compiled"]
        ]
        lodsb_hits = [
            name
            for name, value in lodsb.items()
            if value["compiled"] and value["has_lodsb"]
        ]
        checker_undefined_eax = [
            name
            for name, value in checker.items()
            if not value["compiled"] and value.get("error_undefined_eax")
        ]
        candidate = bool(core_hits or checker_loop_hits or lodsb_hits)
        any_candidate = any_candidate or candidate
        summary[profile] = {
            "register_core_compiled": core["compiled"],
            "register_core_target_hits": core_hits,
            "checker_compiled_count": len(checker_compiled),
            "checker_total": len(checker),
            "checker_loop_hits": checker_loop_hits,
            "checker_undefined_eax_count": len(checker_undefined_eax),
            "lodsb_compiled_count": len(lodsb_compiled),
            "lodsb_total": len(lodsb),
            "lodsb_hits": lodsb_hits,
            "candidate_instruction_selection": candidate,
        }

    core_hexes = {
        results[profile]["register_core"].get("code_hex")
        for profile, _ in PROFILES
    }
    if None in core_hexes or len(core_hexes) != 1:
        raise ValueError(f"processor profile changed register core: {core_hexes}")
    for profile in ("default", "80186", "80286"):
        item = summary[profile]
        if item["checker_compiled_count"] != 0 or item["checker_undefined_eax_count"] != 14:
            raise ValueError(f"{profile}: expected all checker forms to reject _EAX")
    for profile in ("80386", "80486"):
        item = summary[profile]
        if item["checker_compiled_count"] != 14 or item["checker_loop_hits"]:
            raise ValueError(f"{profile}: checkerboard lowering drift")
    for profile, _ in PROFILES:
        item = summary[profile]
        if item["lodsb_compiled_count"] != 4 or item["lodsb_hits"]:
            raise ValueError(f"{profile}: LODSB surface drift")
        if item["register_core_target_hits"]:
            raise ValueError(f"{profile}: unexpected target register/core encoding")

    receipt = {
        "schema_version": 1,
        "claim_scope": (
            "TC4J default/-1/-2/-3/-4 processor selection over remaining "
            "TH04 MAIN blocker instruction shapes"
        ),
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "base_flags_without_processor": list(BASE),
        "profiles": results,
        "summary": summary,
        "any_candidate_instruction_selection": any_candidate,
        "limit": (
            "Compiler mechanism evidence only. A matching instruction choice "
            "would still require independent source/producer provenance and "
            "full focused replay; this probe never authorizes inline assembly."
        ),
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "receipt": str(path),
                "receipt_sha256": sha(path.read_bytes()),
                "summary": summary,
                "any_candidate_instruction_selection": any_candidate,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
