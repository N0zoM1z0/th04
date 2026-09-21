#!/usr/bin/env python3
"""Probe TC4J register-register opcode selection across attested front ends.

The probe compares the pinned TCC driver under every already-relevant optimizer
/register profile with the same-media PC-98 TC.EXE integrated compiler under a
production-like project. It is compiler-surface evidence only; it does not
promote snd_load or carpet and never injects target bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import digest_file  # noqa: E402
from probe_tc4_mov_bx_ax_encoding import code_bytes  # noqa: E402
from probe_tc4j_pc98_ide import (  # noqa: E402
    INSTALLED,
    MEDIA,
    RUNTIME_CONFIG,
    RUNTIME_MANIFEST,
    public_code_bytes,
    run_checked,
    unpak,
)
from probe_tc4j_pc98_ide_optimizer_surface import (  # noqa: E402
    PC98_TC_SHA256,
    PRODUCTION_OPTIONS,
    TCALC_PAK_SHA256,
    TCALC_PRJ_SHA256,
    TCPC98_PAK_SHA256,
    parse_options,
    patch_option,
)

CLI_FLAGS = ("-c", "-ml", "-b-", "-3", "-Z", "-d")
CLI_PROFILES = {
    "O": ("-O",),
    "noO": (),
    "Ominus": ("-O-",),
    "OG": ("-O", "-G"),
    "OGminus": ("-O", "-G-"),
    "Or": ("-O", "-r"),
    "OGminusr": ("-O", "-G-", "-r"),
}
CORE = (
    "_BX=_AX; _SI=_AX; _DI=_DX; _DX=0; _BX+=_BX; _DI<<=1; "
    "_AX=(_AX*_BX);"
)
CLI_EXPECTED = bytes.fromhex("56 57 8B D8 8B F0 8B FA 33 D2 03 DB 03 FF F7 EB 5F 5E C3")
IDE_PROBES = {
    "_probe_mov_bx_ax": bytes.fromhex("55 8B EC 8B D8 5D CB"),
    "_probe_mov_si_ax": bytes.fromhex("55 8B EC 56 8B F0 5E 5D CB"),
    "_probe_mov_di_dx": bytes.fromhex("55 8B EC 57 8B FA 5F 5D CB"),
    "_probe_zero_dx": bytes.fromhex("55 8B EC 33 D2 5D CB"),
    "_probe_add_bx": bytes.fromhex("55 8B EC 03 DB 5D CB"),
    "_probe_shl_di": bytes.fromhex("55 8B EC 57 03 FF 5F 5D CB"),
    "_probe_mul_bx": bytes.fromhex("55 8B EC F7 EB 5D CB"),
}
IDE_SOURCE = b"""\r\nvoid far probe_mov_bx_ax(void) { _BX = _AX; }\r\nvoid far probe_mov_si_ax(void) { _SI = _AX; }\r\nvoid far probe_mov_di_dx(void) { _DI = _DX; }\r\nvoid far probe_zero_dx(void) { _DX = 0; }\r\nvoid far probe_add_bx(void) { _BX += _BX; }\r\nvoid far probe_shl_di(void) { _DI <<= 1; }\r\nvoid far probe_mul_bx(void) { _AX = (_AX * _BX); }\r\n"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tc4-reg-encoding-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def cli_matrix(output: Path) -> dict[str, object]:
    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(item for item in surfaces if item["id"] == "active-tcc")
    tcc_path = ROOT / tcc["path"]
    if digest_file(tcc_path) != tcc["sha256"]:
        raise ValueError("active TCC identity drift")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    result = {}
    for name, extra in CLI_PROFILES.items():
        work = output / f"cli-{name}"
        work.mkdir()
        source = work / "p.cpp"
        source.write_text(
            "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n"
            "#include <dos.h>\n"
            f"void near probe(void) {{ {CORE} }}\n"
            "#pragma option -k.\n"
        )
        command = [
            "wine", str(runner), "-e", "-x", "tcc", *CLI_FLAGS, *extra,
            f"-I{ROOT / '_reference/ReC98'}", source.name,
        ]
        done = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=120)
        (work / "compile.log").write_text(done.stdout + done.stderr)
        obj = work / "p.obj"
        if done.returncode or not obj.is_file():
            raise RuntimeError(f"CLI profile {name} failed")
        code = code_bytes(obj)
        if code != CLI_EXPECTED:
            raise ValueError(f"CLI profile {name} code drift: {code.hex()}")
        result[name] = {
            "flags": list(CLI_FLAGS + extra),
            "source_sha256": sha(source.read_bytes()),
            "object_sha256": sha(obj.read_bytes()),
            "code_hex": code.hex(),
        }
    if len({item["code_hex"] for item in result.values()}) != 1:
        raise ValueError("CLI register encoding changes across profiles")
    return {
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": digest_file(runner),
        "profiles": result,
    }


def ide_probe(output: Path) -> dict[str, object]:
    run_checked(
        [sys.executable, "scripts/attest_toolchain.py", "--identity-only",
         "--surface", "tc40j-media", "--surface", "msdos-player-p0281"],
        ROOT,
    )
    if digest_file(MEDIA / "TCALC.PAK") != TCALC_PAK_SHA256:
        raise ValueError("TCALC.PAK identity drift")
    if digest_file(MEDIA / "TCPC98.PAK") != TCPC98_PAK_SHA256:
        raise ValueError("TCPC98.PAK identity drift")
    runtime = tomllib.loads(RUNTIME_MANIFEST.read_text())
    dosbox_text = shutil.which(str(runtime["primary"]["command"]))
    if dosbox_text is None:
        raise ValueError("pinned DOSBox-X unavailable")
    dosbox = Path(dosbox_text).resolve()
    if digest_file(dosbox) != str(runtime["primary"]["binary_sha256"]):
        raise ValueError("DOSBox-X identity drift")
    if digest_file(RUNTIME_CONFIG) != str(runtime["primary"]["config_sha256"]):
        raise ValueError("DOSBox-X config identity drift")

    work = output / "pc98-ide"
    extract = work / "extract"
    extract.mkdir(parents=True)
    wine_env = os.environ.copy()
    wine_env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"), WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN")
    pc98 = extract / "pc98"
    sample = extract / "tcalc"
    unpak(MEDIA / "TCPC98.PAK", pc98, extract, wine_env)
    unpak(MEDIA / "TCALC.PAK", sample, extract, wine_env)
    tc = pc98 / "TC.EXE"
    project = sample / "TCALC.PRJ"
    if digest_file(tc) != PC98_TC_SHA256 or sha(project.read_bytes()) != TCALC_PRJ_SHA256:
        raise ValueError("same-media IDE input identity drift")
    records = parse_options(project.read_bytes())
    configured = project.read_bytes()
    for ident, value in PRODUCTION_OPTIONS.items():
        configured = patch_option(configured, records, ident, value)

    drive = work / "drive"
    shutil.copytree(INSTALLED / "BIN", drive / "TC4" / "BIN")
    shutil.copytree(INSTALLED / "INCLUDE", drive / "TC4" / "INCLUDE")
    shutil.copytree(INSTALLED / "LIB", drive / "TC4" / "LIB")
    shutil.copy2(tc, drive / "TC4" / "BIN" / "TC.EXE")
    project_dir = drive / "TC4" / "EXAMPLES" / "TCALC"
    project_dir.mkdir(parents=True)
    for path in sample.iterdir():
        if path.is_file():
            shutil.copy2(path, project_dir / path.name)
    (project_dir / "TCALC.PRJ").write_bytes(configured)
    source = project_dir / "TCALC.C"
    source.write_bytes(source.read_bytes() + IDE_SOURCE)

    session = work / "xdg"
    env = os.environ.copy()
    env.update(
        SDL_VIDEODRIVER=str(runtime["primary"]["execution"]["video_driver"]),
        SDL_AUDIODRIVER=str(runtime["primary"]["execution"]["audio_driver"]),
        XDG_CACHE_HOME=str(session / "cache"),
        XDG_CONFIG_HOME=str(session / "config"),
        XDG_DATA_HOME=str(session / "data"),
    )
    command = [
        str(dosbox), "-defaultconf", "-defaultmapper", "-conf", str(RUNTIME_CONFIG),
        "-fastlaunch", "-nogui", "-nomenu", "-exit", "-time-limit", "30",
        "-c", f'mount c "{drive}"', "-c", "c:", "-c", r"set PATH=C:\TC4\BIN",
        "-c", r"cd \TC4\EXAMPLES\TCALC", "-c", "tc /b tcalc.prj", "-c", "exit",
    ]
    done = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=50)
    log = work / "dosbox.log"
    combined_log = done.stdout + done.stderr
    log.write_text(combined_log)
    if done.returncode:
        raise RuntimeError("PC-98 IDE compile failed")
    for marker in runtime["primary"]["execution"]["required_log_markers"]:
        if str(marker) not in combined_log:
            raise RuntimeError(f"missing DOSBox-X marker {marker}")
    obj_path = project_dir / "TCALC.OBJ"
    if not obj_path.is_file():
        raise RuntimeError("PC-98 IDE produced no object")
    obj = obj_path.read_bytes()
    desc = describe_omf(obj)
    if not desc["valid"] or desc["translator_comments"] != ["TC86 Borland C++ 4.02"]:
        raise ValueError("unexpected IDE object identity")
    bodies = {}
    for public, expected in IDE_PROBES.items():
        body, meta = public_code_bytes(obj, public, len(expected))
        if body != expected:
            raise ValueError(f"IDE {public} drift: {body.hex()}")
        bodies[public] = {"code_hex": body.hex(), "public": meta}
    return {
        "pc98_tc_exe_sha256": PC98_TC_SHA256,
        "dosbox_sha256": digest_file(dosbox),
        "project_options": {f"0x{k:04X}": v for k, v in PRODUCTION_OPTIONS.items()},
        "source_append_sha256": sha(IDE_SOURCE),
        "object_sha256": sha(obj),
        "object_dependency_normalized_sha256": desc["dependency_timestamp_normalized_sha256"],
        "bodies": bodies,
        "dosbox_log_sha256": sha(log.read_bytes()),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    output = make_output(args.output_dir)
    cli = cli_matrix(output)
    ide = ide_probe(output)
    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J register-encoding surface for final TH04 blockers; no exact promotion",
        "cli": cli,
        "pc98_ide": ide,
        "target_forms_not_emitted": [
            "89 C3 MOV BX,AX", "89 C6 MOV SI,AX", "89 D7 MOV DI,DX",
            "31 D2 XOR DX,DX", "01 DB ADD BX,BX", "D1 E7 SHL DI,1", "F7 E3 MUL BX",
        ],
        "conclusion": "Pinned TCC produces identical register-opcode choices under -O/no -O/-O-/-G/-G-/-r variants, and the same-media PC-98 TC.EXE production-like project selects the same 8B/33/03/IMUL forms. Neither attested front end naturally selects the remaining TH04 snd_load/carpet register encodings.",
        "limit": "This closes only the tested legal compiler/front-end/register-strategy surface. It does not prove original source language or authorize target-derived inline assembly.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "receipt_sha256": sha(path.read_bytes()), "conclusion": receipt["conclusion"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
