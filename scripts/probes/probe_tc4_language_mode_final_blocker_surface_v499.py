#!/usr/bin/env python3
"""Probe TC4J C/C++ language modes on representative final TH04 blocker shapes.

This is compiler-mechanism evidence only. It uses natural C/C++ statements,
never inline assembly, target bytes, or product-source modifications.
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

from probe_tc4_mov_bx_ax_encoding import code_bytes  # noqa: E402

FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
PROFILES = (
    ("c_by_extension", "c", ()),
    ("cpp_by_extension", "cpp", ()),
    ("c_forced_cpp", "c", ("-P",)),
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
TARGET_PATTERNS = {
    "mov_bx_ax_89c3": bytes.fromhex("89 C3"),
    "mov_si_ax_89c6": bytes.fromhex("89 C6"),
    "mov_di_dx_89d7": bytes.fromhex("89 D7"),
    "xor_dx_31d2": bytes.fromhex("31 D2"),
    "add_bx_01db": bytes.fromhex("01 DB"),
    "shl_di_d1e7": bytes.fromhex("D1 E7"),
    "mul_bx_f7e3": bytes.fromhex("F7 E3"),
    "push_ds_pop_es_1e07": bytes.fromhex("1E 07"),
    "loop_e2": bytes.fromhex("E2"),
    "lodsb_ac": bytes.fromhex("AC"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tc4-language-final-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def compile_one(
    out: Path,
    profile: str,
    extension: str,
    extra_flags: tuple[str, ...],
    name: str,
    body: str,
) -> dict[str, object]:
    work = out / name / profile
    work.mkdir(parents=True)
    source = work / ("p." + extension)
    source.write_text(PREFIX + body + SUFFIX)
    command = [
        "wine",
        str(compile_one.runner),
        "-e",
        "-x",
        "tcc",
        *FLAGS,
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
    obj = work / "p.obj"
    if done.returncode or not obj.is_file():
        raise RuntimeError(
            f"{name}/{profile} failed: {done.returncode}\n{done.stdout}{done.stderr}"
        )
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
    return {
        "source_sha256": sha(source.read_bytes()),
        "code_sha256": sha(code),
        "code_hex": code.hex(),
        "code_size": len(code),
        "disassembly": dis.splitlines(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    out = output_dir(args.output_dir)

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

    # Prove that the three profile labels really select different front-end modes.
    sentinel = (
        "#ifdef __cplusplus\n"
        "void near probe(void){ _AX=0xC002; }\n"
        "#else\n"
        "void near probe(void){ _AX=0xC001; }\n"
        "#endif"
    )
    sentinel_results = {}
    for profile, extension, extra in PROFILES:
        sentinel_results[profile] = compile_one(
            out, profile, extension, extra, "mode_sentinel", sentinel
        )
    c_hex = sentinel_results["c_by_extension"]["code_hex"]
    cpp_hex = sentinel_results["cpp_by_extension"]["code_hex"]
    forced_hex = sentinel_results["c_forced_cpp"]["code_hex"]
    if c_hex == cpp_hex or cpp_hex != forced_hex:
        raise ValueError("language-mode sentinel did not distinguish C from C++")

    results: dict[str, object] = {}
    for name, body in SOURCES.items():
        modes = {}
        for profile, extension, extra in PROFILES:
            modes[profile] = compile_one(
                out, profile, extension, extra, name, body
            )
        code_hexes = {item["code_hex"] for item in modes.values()}
        if len(code_hexes) != 1:
            raise ValueError(f"{name}: language mode changed CODE bytes")
        code = bytes.fromhex(next(iter(code_hexes)))
        hits = {
            key: pattern in code for key, pattern in TARGET_PATTERNS.items()
        }
        if any(hits.values()):
            raise ValueError(f"{name}: unexpected target residual pattern {hits}")
        results[name] = {
            "profiles": modes,
            "all_code_identical": True,
            "target_pattern_hits": hits,
        }

    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J C/C++ language-mode final MAIN blocker surface",
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "probe_sha256": sha(Path(__file__).read_bytes()),
        "flags": list(FLAGS),
        "profiles": [
            {"name": name, "extension": ext, "extra_flags": list(extra)}
            for name, ext, extra in PROFILES
        ],
        "mode_sentinel": sentinel_results,
        "results": results,
        "conclusion": (
            "The attested TCC 4.02 front end is demonstrably in C mode for .c and "
            "C++ mode for .cpp or .c with -P, but the representative final-blocker "
            "lowerings are byte-identical across all three modes. C mode therefore "
            "does not select the target register directions/zero/doubling/MUL/DS-ES "
            "forms, x86 LOOP, or LODSB for these tested semantics."
        ),
        "limit": (
            "This closes language mode only for the tested representative natural "
            "source shapes. It is not source provenance and grants no exactness credit."
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
                "sentinel": {
                    key: value["code_hex"] for key, value in sentinel_results.items()
                },
                "code_sha256s": {
                    key: value["profiles"]["c_by_extension"]["code_sha256"]
                    for key, value in results.items()
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
