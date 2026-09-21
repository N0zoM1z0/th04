#!/usr/bin/env python3
"""Probe the same-media TC4J PC-98 IDE optimizer/project surface.

This diagnostic decodes the scalar option records in Borland's own TCALC.PRJ
through the pinned PRJ2MAK utility and compiles two bounded natural-C probes
with the original PC-98 TC.EXE under the pinned DOSBox-X PC-98 runtime.
It is compiler-surface evidence only and grants no TH04 exactness by itself.
"""
from __future__ import annotations

import argparse
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

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path.insert(0, str(ROOT / "scripts"))

from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import digest_file  # noqa: E402
from probe_tc4j_pc98_ide import (  # noqa: E402
    INSTALLED,
    MEDIA,
    REFERENCE_MSDOS,
    RUNTIME_CONFIG,
    RUNTIME_MANIFEST,
    public_code_bytes,
    run_checked,
    unpak,
)

TCALC_PAK_SHA256 = "dc5778ac8484d28dfd0529c5feb129e4708918cac1f758fd9d58e05094388be4"
TCPC98_PAK_SHA256 = "abdeac6cf17e76c096848ed3769c7b40cd9d535e0cf7aab937a44b4408715261"
TCALC_PRJ_SHA256 = "3f80d402a14c1124c709d261416943c0cb2986852d25d5d774c17ac54bf762de"
PRJ2MAK_SHA256 = "2149c33d49e7d91f0556e97a7619f101630b448ac479258437ea79deeddc544c"
PC98_TC_SHA256 = "91d410850da69c6ff894f902d1b5610f04b5e2b6d0097b2a11cf2fafa54f14b4"
OPTION_BLOCK_OFFSET = 0x24
EXPECTED_OPTION_RECORDS = 102
BASELINE_FLAGS = ("-ml", "-v", "-vi-", "-I$(INCLUDEPATH)", "-L$(LIBPATH)")
EXPECTED_PRODUCTION_FLAGS = {"-ml", "-3", "-O", "-Z", "-d", "-b-"}
PRODUCTION_OPTIONS = {
    0x0111: 1,  # -O
    0x00FD: 3,  # -3
    0x0112: 1,  # -Z
    0x0116: 1,  # -d
    0x011F: 0,  # -b-
    0x010E: 0,  # remove sample -v
    0x0120: 1,  # remove sample -vi-
}
PROBE_SOURCE = b"""\r\nvoid far probe_counted_loop(void)\r\n{\r\n    _CX = 6;\r\nagain:\r\n    _DI += 8;\r\n    if(--_CX) goto again;\r\n}\r\n\r\nvoid far probe_load_inc(void)\r\n{\r\n    _AL = *((unsigned char near *)_SI);\r\n    _SI++;\r\n}\r\n"""
EXPECTED_LOOP = bytes.fromhex("55 8B EC 57 B9 06 00 83 C7 08 49 8B C1 0B C0 75 F6 5F 5D CB")
EXPECTED_LOAD = bytes.fromhex("55 8B EC 56 8A 04 46 5E 5D CB")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tc4j-ide-optimizer-", dir=parent))
    result = path.resolve()
    if result.exists() or not result.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    result.mkdir(parents=True)
    return result


def parse_options(data: bytes) -> list[dict[str, int]]:
    if not data.startswith(b"Turbo C Project File \x1a"):
        raise ValueError("unexpected TCALC.PRJ signature")
    records: list[dict[str, int]] = []
    pos = OPTION_BLOCK_OFFSET
    while pos + 4 <= len(data):
        ident = int.from_bytes(data[pos:pos + 2], "little")
        size = int.from_bytes(data[pos + 2:pos + 4], "little")
        if size not in (1, 2, 4) or pos + 4 + size > len(data):
            break
        records.append({
            "offset": pos,
            "id": ident,
            "size": size,
            "value": int.from_bytes(data[pos + 4:pos + 4 + size], "little"),
        })
        pos += 4 + size
    if len(records) != EXPECTED_OPTION_RECORDS:
        raise ValueError(f"TCALC.PRJ option-record count drift: {len(records)}")
    return records


def patch_option(data: bytes, records: list[dict[str, int]], ident: int, value: int) -> bytes:
    matches = [row for row in records if row["id"] == ident]
    if len(matches) != 1:
        raise ValueError(f"option 0x{ident:04X}: expected one record, got {len(matches)}")
    row = matches[0]
    size = row["size"]
    if value < 0 or value >= (1 << (size * 8)):
        raise ValueError(f"option 0x{ident:04X}: value out of range")
    out = bytearray(data)
    start = row["offset"] + 4
    out[start:start + size] = value.to_bytes(size, "little")
    return bytes(out)


def make_flags(makefile: Path) -> list[str]:
    return [
        line.strip()
        for line in makefile.read_text(encoding="cp437", errors="replace").splitlines()
        if line.strip().startswith("-")
    ]


def prj2mak(prj2mak_exe: Path, project: bytes, work: Path, env: dict[str, str]) -> list[str]:
    work.mkdir(parents=True, exist_ok=True)
    (work / "P.PRJ").write_bytes(project)
    for name in ("P.MAK", "P.CFG"):
        path = work / name
        if path.exists():
            path.unlink()
    done = subprocess.run(
        ["wine", str(REFERENCE_MSDOS), "-e", "-x", str(prj2mak_exe), "P.PRJ", "P.MAK", "P.CFG"],
        cwd=work,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if done.returncode or not (work / "P.MAK").is_file():
        raise RuntimeError(f"PRJ2MAK failed: {done.stdout}{done.stderr}")
    return make_flags(work / "P.MAK")


def scan_toggle_surface(
    project: bytes,
    records: list[dict[str, int]],
    prj2mak_exe: Path,
    output: Path,
    env: dict[str, str],
) -> dict[str, object]:
    scratch = output / "project-option-scan"
    scratch.mkdir()
    baseline = prj2mak(prj2mak_exe, project, scratch / "baseline", env)
    if tuple(baseline) != BASELINE_FLAGS:
        raise ValueError(f"unexpected baseline project flags: {baseline}")
    rows: list[dict[str, object]] = []
    all_flags = set(baseline)
    for row in records:
        for value in (0, 1):
            if value == row["value"]:
                continue
            mutated = patch_option(project, records, row["id"], value)
            flags = prj2mak(
                prj2mak_exe,
                mutated,
                scratch / f"{row['id']:04X}-{value}",
                env,
            )
            added = [flag for flag in flags if flag not in baseline]
            removed = [flag for flag in baseline if flag not in flags]
            all_flags.update(flags)
            rows.append({
                "id": f"0x{row['id']:04X}",
                "size": row["size"],
                "baseline_value": row["value"],
                "test_value": value,
                "added": added,
                "removed": removed,
            })
    # Pin the option IDs required by the production-like IDE build.
    checks = {
        (0x0111, 1): ("-O",),
        (0x0112, 1): ("-Z",),
        (0x0116, 1): ("-d",),
        (0x011F, 0): ("-b-",),
    }
    keyed = {(int(item["id"], 16), int(item["test_value"])): item for item in rows}
    for key, expected in checks.items():
        if tuple(keyed[key]["added"]) != expected:
            raise ValueError(f"project option mapping drift for {key}: {keyed[key]}")
    if keyed[(0x010E, 0)]["removed"] != ["-v"]:
        raise ValueError("project -v removal mapping drift")
    if keyed[(0x0120, 1)]["removed"] != ["-vi-"]:
        raise ValueError("project -vi- removal mapping drift")
    # CPU is an enum, not a boolean toggle, so check its production value separately.
    cpu_flags = prj2mak(
        prj2mak_exe,
        patch_option(project, records, 0x00FD, 3),
        scratch / "00FD-3",
        env,
    )
    if "-3" not in cpu_flags:
        raise ValueError("project CPU option no longer maps to -3")
    all_flags.update(cpu_flags)
    optimizer_flags = sorted(flag for flag in all_flags if re.fullmatch(r"-O.*", flag))
    if optimizer_flags != ["-O"]:
        raise ValueError(f"unexpected optimizer flags from scalar project surface: {optimizer_flags}")
    return {
        "baseline_flags": baseline,
        "scalar_record_count": len(records),
        "binary_toggle_tests": len(rows),
        "optimizer_flags_observed": optimizer_flags,
        "production_option_mappings": {
            "0x0111=1": "-O",
            "0x00FD=3": "-3",
            "0x0112=1": "-Z",
            "0x0116=1": "-d",
            "0x011F=0": "-b-",
            "0x010E=0": "remove -v",
            "0x0120=1": "remove -vi-",
        },
        "tests": rows,
    }


def compile_probes(
    project: bytes,
    records: list[dict[str, int]],
    tc_exe: Path,
    sample_dir: Path,
    output: Path,
) -> dict[str, object]:
    runtime = tomllib.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))
    dosbox_text = shutil.which(str(runtime["primary"]["command"]))
    if dosbox_text is None:
        raise ValueError("pinned DOSBox-X is unavailable")
    dosbox = Path(dosbox_text).resolve()
    if digest_file(dosbox) != str(runtime["primary"]["binary_sha256"]):
        raise ValueError("DOSBox-X identity mismatch")
    if digest_file(RUNTIME_CONFIG) != str(runtime["primary"]["config_sha256"]):
        raise ValueError("DOSBox-X config identity mismatch")

    configured = project
    for ident, value in PRODUCTION_OPTIONS.items():
        configured = patch_option(configured, records, ident, value)

    drive = output / "pc98-ide" / "drive"
    project_dir = drive / "TC4" / "EXAMPLES" / "TCALC"
    project_dir.mkdir(parents=True)
    shutil.copytree(INSTALLED / "BIN", drive / "TC4" / "BIN")
    shutil.copytree(INSTALLED / "INCLUDE", drive / "TC4" / "INCLUDE")
    shutil.copytree(INSTALLED / "LIB", drive / "TC4" / "LIB")
    shutil.copy2(tc_exe, drive / "TC4" / "BIN" / "TC.EXE")
    for path in sample_dir.iterdir():
        if path.is_file():
            shutil.copy2(path, project_dir / path.name)
    (project_dir / "TCALC.PRJ").write_bytes(configured)
    source = project_dir / "TCALC.C"
    source.write_bytes(source.read_bytes() + PROBE_SOURCE)

    session = output / "pc98-ide" / "xdg"
    environment = os.environ.copy()
    environment.update(
        SDL_VIDEODRIVER=str(runtime["primary"]["execution"]["video_driver"]),
        SDL_AUDIODRIVER=str(runtime["primary"]["execution"]["audio_driver"]),
        XDG_CACHE_HOME=str(session / "cache"),
        XDG_CONFIG_HOME=str(session / "config"),
        XDG_DATA_HOME=str(session / "data"),
    )
    command = [
        str(dosbox), "-defaultconf", "-defaultmapper", "-conf", str(RUNTIME_CONFIG),
        "-fastlaunch", "-nogui", "-nomenu", "-exit", "-time-limit", "30",
        "-c", f'mount c "{drive}"', "-c", "c:",
        "-c", r"set PATH=C:\TC4\BIN", "-c", r"cd \TC4\EXAMPLES\TCALC",
        "-c", "tc /b tcalc.prj", "-c", "exit",
    ]
    done = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=50,
    )
    log = output / "pc98-ide" / "dosbox.log"
    log.write_text(done.stdout + done.stderr)
    if done.returncode:
        raise RuntimeError("PC-98 IDE compiler failed")
    for marker in runtime["primary"]["execution"]["required_log_markers"]:
        if str(marker) not in done.stdout:
            raise RuntimeError(f"missing DOSBox-X PC-98 marker: {marker}")
    obj_path = project_dir / "TCALC.OBJ"
    if not obj_path.is_file():
        raise RuntimeError("PC-98 IDE produced no TCALC.OBJ")
    obj = obj_path.read_bytes()
    desc = describe_omf(obj)
    if not desc["valid"] or desc["translator_comments"] != ["TC86 Borland C++ 4.02"]:
        raise ValueError("unexpected PC-98 IDE OMF identity")
    loop, loop_public = public_code_bytes(obj, "_probe_counted_loop", len(EXPECTED_LOOP))
    load, load_public = public_code_bytes(obj, "_probe_load_inc", len(EXPECTED_LOAD))
    if loop != EXPECTED_LOOP:
        raise ValueError(f"PC-98 IDE counted-loop code drift: {loop.hex()}")
    if load != EXPECTED_LOAD:
        raise ValueError(f"PC-98 IDE load/increment code drift: {load.hex()}")
    if b"\xE2" in loop:
        raise ValueError("unexpected x86 LOOP in PC-98 IDE counted-loop probe")
    if b"\xAC" in load:
        raise ValueError("unexpected LODSB in PC-98 IDE load/increment probe")
    return {
        "project_options": {f"0x{k:04X}": v for k, v in PRODUCTION_OPTIONS.items()},
        "source_append_sha256": sha(PROBE_SOURCE),
        "object_sha256": sha(obj),
        "object_dependency_normalized_sha256": desc["dependency_timestamp_normalized_sha256"],
        "translator_comments": desc["translator_comments"],
        "counted_loop": {
            "public": loop_public,
            "code_hex": loop.hex(),
            "contains_loop": False,
        },
        "load_increment": {
            "public": load_public,
            "code_hex": load.hex(),
            "contains_lodsb": False,
        },
        "dosbox_log_sha256": sha(log.read_bytes()),
    }



def surface_from_existing(records: list[dict[str, int]], output: Path) -> dict[str, object]:
    """Revalidate a previously generated exhaustive PRJ2MAK scalar scan."""
    scratch = output / "project-option-scan"
    baseline = make_flags(scratch / "baseline" / "P.MAK")
    if tuple(baseline) != BASELINE_FLAGS:
        raise ValueError(f"unexpected baseline project flags: {baseline}")
    rows: list[dict[str, object]] = []
    all_flags = set(baseline)
    for row in records:
        for value in (0, 1):
            if value == row["value"]:
                continue
            makefile = scratch / f"{row['id']:04X}-{value}" / "P.MAK"
            if not makefile.is_file():
                raise ValueError(f"missing staged project scan: {makefile}")
            flags = make_flags(makefile)
            added = [flag for flag in flags if flag not in baseline]
            removed = [flag for flag in baseline if flag not in flags]
            all_flags.update(flags)
            rows.append({
                "id": f"0x{row['id']:04X}",
                "size": row["size"],
                "baseline_value": row["value"],
                "test_value": value,
                "added": added,
                "removed": removed,
            })
    checks = {
        (0x0111, 1): ("-O",),
        (0x0112, 1): ("-Z",),
        (0x0116, 1): ("-d",),
        (0x011F, 0): ("-b-",),
    }
    keyed = {(int(item["id"], 16), int(item["test_value"])): item for item in rows}
    for key, expected in checks.items():
        if tuple(keyed[key]["added"]) != expected:
            raise ValueError(f"staged project option mapping drift for {key}: {keyed[key]}")
    if keyed[(0x010E, 0)]["removed"] != ["-v"]:
        raise ValueError("staged project -v removal mapping drift")
    if keyed[(0x0120, 1)]["removed"] != ["-vi-"]:
        raise ValueError("staged project -vi- removal mapping drift")
    cpu_makefile = scratch / "00FD-3" / "P.MAK"
    if not cpu_makefile.is_file():
        raise ValueError("missing staged CPU=386 project scan")
    cpu_flags = make_flags(cpu_makefile)
    if "-3" not in cpu_flags:
        raise ValueError("staged project CPU option no longer maps to -3")
    all_flags.update(cpu_flags)
    optimizer_flags = sorted(flag for flag in all_flags if re.fullmatch(r"-O.*", flag))
    if optimizer_flags != ["-O"]:
        raise ValueError(f"unexpected optimizer flags from staged scalar project surface: {optimizer_flags}")
    return {
        "baseline_flags": baseline,
        "scalar_record_count": len(records),
        "binary_toggle_tests": len(rows),
        "optimizer_flags_observed": optimizer_flags,
        "production_option_mappings": {
            "0x0111=1": "-O",
            "0x00FD=3": "-3",
            "0x0112=1": "-Z",
            "0x0116=1": "-d",
            "0x011F=0": "-b-",
            "0x010E=0": "remove -v",
            "0x0120=1": "remove -vi-",
        },
        "tests": rows,
    }


def compiler_from_existing(output: Path) -> dict[str, object]:
    """Revalidate the staged PC-98 IDE object without recompiling it."""
    runtime = tomllib.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))
    log = output / "pc98-ide" / "dosbox.log"
    log_text = log.read_text(errors="replace")
    for marker in runtime["primary"]["execution"]["required_log_markers"]:
        if str(marker) not in log_text:
            raise RuntimeError(f"missing staged DOSBox-X PC-98 marker: {marker}")
    obj_path = output / "pc98-ide" / "drive" / "TC4" / "EXAMPLES" / "TCALC" / "TCALC.OBJ"
    if not obj_path.is_file():
        raise RuntimeError("staged PC-98 IDE object is missing")
    obj = obj_path.read_bytes()
    desc = describe_omf(obj)
    if not desc["valid"] or desc["translator_comments"] != ["TC86 Borland C++ 4.02"]:
        raise ValueError("unexpected staged PC-98 IDE OMF identity")
    loop, loop_public = public_code_bytes(obj, "_probe_counted_loop", len(EXPECTED_LOOP))
    load, load_public = public_code_bytes(obj, "_probe_load_inc", len(EXPECTED_LOAD))
    if loop != EXPECTED_LOOP or load != EXPECTED_LOAD:
        raise ValueError("staged PC-98 IDE probe code drift")
    return {
        "project_options": {f"0x{k:04X}": v for k, v in PRODUCTION_OPTIONS.items()},
        "source_append_sha256": sha(PROBE_SOURCE),
        "object_sha256": sha(obj),
        "object_dependency_normalized_sha256": desc["dependency_timestamp_normalized_sha256"],
        "translator_comments": desc["translator_comments"],
        "counted_loop": {"public": loop_public, "code_hex": loop.hex(), "contains_loop": False},
        "load_increment": {"public": load_public, "code_hex": load.hex(), "contains_lodsb": False},
        "dosbox_log_sha256": sha(log.read_bytes()),
    }

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--resume-existing", action="store_true",
                    help="validate and finalize a staged output tree produced by an interrupted identical run")
    args = ap.parse_args()
    if args.resume_existing:
        if args.output_dir is None:
            ap.error("--resume-existing requires --output-dir")
        output = args.output_dir.resolve()
        if not output.is_dir() or not output.is_relative_to(PRIVATE):
            ap.error("resume output must already exist below .analysis")
    else:
        output = output_dir(args.output_dir)

    run_checked(
        [
            sys.executable,
            "scripts/attest_toolchain.py",
            "--identity-only",
            "--surface", "tc40j-media",
            "--surface", "msdos-player-p0281",
        ],
        ROOT,
    )
    if digest_file(MEDIA / "TCALC.PAK") != TCALC_PAK_SHA256:
        raise ValueError("TCALC.PAK identity mismatch")
    if digest_file(MEDIA / "TCPC98.PAK") != TCPC98_PAK_SHA256:
        raise ValueError("TCPC98.PAK identity mismatch")
    prj2mak_exe = INSTALLED / "BIN" / "PRJ2MAK.EXE"
    if digest_file(prj2mak_exe) != PRJ2MAK_SHA256:
        raise ValueError("PRJ2MAK identity mismatch")

    extract = output / "extract"
    wine_env = os.environ.copy()
    wine_env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN",
    )
    pc98_dir = extract / "pc98"
    sample_dir = extract / "tcalc"
    if not args.resume_existing:
        extract.mkdir()
        unpak(MEDIA / "TCPC98.PAK", pc98_dir, extract, wine_env)
        unpak(MEDIA / "TCALC.PAK", sample_dir, extract, wine_env)
    tc_exe = pc98_dir / "TC.EXE"
    project_path = sample_dir / "TCALC.PRJ"
    if digest_file(tc_exe) != PC98_TC_SHA256:
        raise ValueError("same-media PC-98 TC.EXE identity mismatch")
    project = project_path.read_bytes()
    if sha(project) != TCALC_PRJ_SHA256:
        raise ValueError("same-media TCALC.PRJ identity mismatch")
    records = parse_options(project)

    if args.resume_existing:
        surface = surface_from_existing(records, output)
        production_flags = make_flags(output / "production-project-flags" / "P.MAK")
    else:
        surface = scan_toggle_surface(project, records, prj2mak_exe, output, wine_env)
        production_project = project
        for ident, value in PRODUCTION_OPTIONS.items():
            production_project = patch_option(production_project, records, ident, value)
        production_flags = prj2mak(
            prj2mak_exe,
            production_project,
            output / "production-project-flags",
            wine_env,
        )
    if not EXPECTED_PRODUCTION_FLAGS.issubset(set(production_flags)):
        raise ValueError(f"production-like project flags incomplete: {production_flags}")
    if "-v" in production_flags or "-vi-" in production_flags:
        raise ValueError("production-like project unexpectedly retained debug flags")

    compiler = (
        compiler_from_existing(output)
        if args.resume_existing
        else compile_probes(project, records, tc_exe, sample_dir, output)
    )
    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J same-media PC-98 IDE optimizer/project surface negative",
        "staged_finalize": bool(args.resume_existing),
        "inputs": {
            "tcpc98_pak_sha256": TCPC98_PAK_SHA256,
            "tcalc_pak_sha256": TCALC_PAK_SHA256,
            "tcalc_prj_sha256": TCALC_PRJ_SHA256,
            "prj2mak_sha256": PRJ2MAK_SHA256,
            "pc98_tc_exe_sha256": PC98_TC_SHA256,
            "msdos_runner_sha256": digest_file(REFERENCE_MSDOS),
        },
        "project_surface": surface,
        "production_project_flags": production_flags,
        "compiler_probe": compiler,
        "conclusion": "Same-media PRJ2MAK exposes -O but no -Ol/-O1/-O2 optimizer suboption on binary scalar toggles. The same-media PC-98 IDE compiler under a production-like -O -3 -Z -d -b- project emits DEC/MOV/OR/JNZ rather than LOOP and MOV AL,[SI]; INC SI rather than LODSB.",
        "limit": "This closes the tested same-media IDE project/optimizer mechanism only. It does not prove original source language and does not authorize target-derived inline assembly for checkerboard or carpet.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(receipt_path),
        "receipt_sha256": sha(receipt_path.read_bytes()),
        "scalar_records": surface["scalar_record_count"],
        "toggle_tests": surface["binary_toggle_tests"],
        "optimizer_flags": surface["optimizer_flags_observed"],
        "loop_hex": compiler["counted_loop"]["code_hex"],
        "load_hex": compiler["load_increment"]["code_hex"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
