#!/usr/bin/env python3
"""Probe TC4J -WX/DPMI16 codegen on the remaining TH04 MAIN blocker shapes.

The switch is tested only as a compiler mechanism. This probe never injects
inline assembly or target bytes and grants no source/exactness credit.
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
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import parse_omf  # noqa: E402
from probe_tc4_checkerboard_loop_forms import VARIANTS as CHECKER_VARIANTS  # noqa: E402
from probe_tc4_mov_bx_ax_encoding import code_bytes  # noqa: E402

BASE = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
PREFIX = "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n"
SUFFIX = "\n#pragma option -k.\n"
CORE = (
    "_BX=_AX; _SI=_AX; _DI=_DX; _DX=0; _BX+=_BX; _DI<<=1; "
    "_AX=(_AX*_BX);"
)
CORE_EXPECTED = bytes.fromhex(
    "56 57 8B D8 8B F0 8B FA 33 D2 03 DB 03 FF F7 EB 5F 5E C3"
)
TARGET_CORE_FORMS = {
    "mov_bx_ax_89c3": bytes.fromhex("89 C3"),
    "mov_si_ax_89c6": bytes.fromhex("89 C6"),
    "mov_di_dx_89d7": bytes.fromhex("89 D7"),
    "xor_dx_31d2": bytes.fromhex("31 D2"),
    "add_bx_01db": bytes.fromhex("01 DB"),
    "shl_di_d1e7": bytes.fromhex("D1 E7"),
    "mul_bx_f7e3": bytes.fromhex("F7 E3"),
}
LODSB_VARIANTS = {
    "si_postinc_cast": "void near probe(void){ _AL = *((unsigned char near *)_SI++); }",
    "si_postinc_reinterpret": (
        "void near probe(void){ _AL = "
        "*reinterpret_cast<unsigned char near *>(_SI++); }"
    ),
    "si_load_then_inc": (
        "void near probe(void){ _AL = "
        "*reinterpret_cast<unsigned char near *>(_SI); _SI++; }"
    ),
    "register_ptr": (
        "void near probe(void){ register unsigned char near *p = "
        "reinterpret_cast<unsigned char near *>(_SI); _AL = *p++; "
        "_SI = reinterpret_cast<unsigned int>(p); }"
    ),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tc4-wx-final-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def first_segdef_alignment(obj: Path) -> int:
    for record in parse_omf(obj.read_bytes()):
        if record.record_type == 0x98:
            return (record.data[0] >> 5) & 7
    raise ValueError("object has no SEGDEF")


def compile_one(
    out: Path,
    name: str,
    body: str,
    *,
    wx: bool,
    includes: str = "#include <dos.h>\n",
) -> dict[str, object]:
    work = out / name
    work.mkdir()
    source = work / "p.cpp"
    source.write_text(PREFIX + includes + body + SUFFIX)
    flags = [*BASE, *(["-WX"] if wx else [])]
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
    (work / "compile.log").write_text(done.stdout + done.stderr)
    obj = work / "p.obj"
    if done.returncode or not obj.is_file():
        raise RuntimeError(f"{name}: compile failed: {done.stdout}{done.stderr}")
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
        "first_segdef_alignment_code": first_segdef_alignment(obj),
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

    core_base = compile_one(
        out, "core-base", f"void near probe(void) {{ {CORE} }}", wx=False
    )
    core_wx = compile_one(
        out, "core-wx", f"void near probe(void) {{ {CORE} }}", wx=True
    )
    if bytes.fromhex(str(core_base["code_hex"])) != CORE_EXPECTED:
        raise ValueError("baseline register core drift")
    if bytes.fromhex(str(core_wx["code_hex"])) != CORE_EXPECTED:
        raise ValueError("-WX register core changed unexpectedly")
    if core_base["first_segdef_alignment_code"] != 1:
        raise ValueError("baseline code alignment drift")
    if core_wx["first_segdef_alignment_code"] != 2:
        raise ValueError("-WX did not activate word-aligned code SEGDEF")
    core_target_hits = {
        name: pattern.hex() in str(core_wx["code_hex"])
        for name, pattern in TARGET_CORE_FORMS.items()
    }
    if any(core_target_hits.values()):
        raise ValueError(f"-WX unexpectedly emits target register form: {core_target_hits}")

    checker = {}
    for name, body in CHECKER_VARIANTS.items():
        result = compile_one(out, f"checker-{name}", body, wx=True)
        dis = "\n".join(result["disassembly"]).lower()
        result["contains_loop_instruction"] = " loop " in f" {dis} "
        if result["contains_loop_instruction"]:
            raise ValueError(f"{name}: -WX unexpectedly emits LOOP")
        checker[name] = result

    lodsb = {}
    for name, body in LODSB_VARIANTS.items():
        result = compile_one(out, f"lodsb-{name}", body, wx=True)
        dis = "\n".join(result["disassembly"]).lower()
        result["contains_lodsb"] = "lodsb" in dis
        if result["contains_lodsb"]:
            raise ValueError(f"{name}: -WX unexpectedly emits LODSB")
        lodsb[name] = result

    ds_es = compile_one(
        out,
        "ds-es-wx",
        "void near probe(void){ _ES = _DS; }",
        wx=True,
    )
    if bytes.fromhex(str(ds_es["code_hex"])) != bytes.fromhex("8C D8 8E C0 C3"):
        raise ValueError("-WX DS-to-ES pseudoregister codegen drift")

    memcpy = compile_one(
        out,
        "memcpy-wx",
        "char a[32], b[32]; void near probe(void){ _BX=0x1234; memcpy(a,b,32); }",
        wx=True,
        includes="#include <dos.h>\n#include <string.h>\n#pragma intrinsic memcpy\n",
    )
    memcpy_code = bytes.fromhex(str(memcpy["code_hex"]))
    scalar = memcpy_code.find(bytes.fromhex("BB 34 12"))
    ds_es_pair = memcpy_code.find(bytes.fromhex("1E 07"))
    memcpy["contains_push_ds_pop_es"] = ds_es_pair >= 0
    memcpy["push_ds_pop_es_after_scalar"] = scalar >= 0 and ds_es_pair > scalar
    if not memcpy["contains_push_ds_pop_es"] or not memcpy["push_ds_pop_es_after_scalar"]:
        raise ValueError("-WX memcpy DS/ES placement drift")

    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J -WX/DPMI16 final MAIN blocker codegen surface",
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "base_flags": list(BASE),
        "wx_flag": "-WX",
        "switch_activation": {
            "baseline_first_code_segdef_alignment": core_base[
                "first_segdef_alignment_code"
            ],
            "wx_first_code_segdef_alignment": core_wx[
                "first_segdef_alignment_code"
            ],
        },
        "register_core": {
            "baseline": core_base,
            "wx": core_wx,
            "target_form_hits": core_target_hits,
        },
        "checkerboard_wx": checker,
        "lodsb_wx": lodsb,
        "ds_to_es_wx": ds_es,
        "intrinsic_memcpy_wx": memcpy,
        "conclusion": (
            "-WX is active and changes the probe CODE SEGDEF from alignment code "
            "1 to 2, but it leaves the tested final-blocker instruction selection "
            "unchanged. The register core stays byte-identical to ordinary TC4J; "
            "none of 14 natural checkerboard countdown forms emits LOOP; none of "
            "four fixed-SI byte-load forms emits LODSB; direct DS-to-ES remains "
            "MOV AX,DS / MOV ES,AX. String-intrinsic memcpy still emits PUSH DS / "
            "POP ES only at the real copy site after preceding scalar work."
        ),
        "limit": (
            "This closes -WX as a compiler-option explanation for these tested "
            "final-blocker forms. It does not prove original source language and "
            "does not authorize target-derived inline assembly."
        ),
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "receipt": str(path),
                "receipt_sha256": sha(path.read_bytes()),
                "register_core_same": (
                    core_base["code_sha256"] == core_wx["code_sha256"]
                ),
                "checker_loop_count": sum(
                    bool(v["contains_loop_instruction"]) for v in checker.values()
                ),
                "lodsb_count": sum(bool(v["contains_lodsb"]) for v in lodsb.values()),
                "switch_activation": receipt["switch_activation"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
