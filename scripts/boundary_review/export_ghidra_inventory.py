#!/usr/bin/env python3
"""Create or check a headless Ghidra database for a private boundary-review image."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tomllib
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.analysis import (
    AnalysisError,
    default_project_root,
    load_analysis_config,
    repository_path,
    validate_project_root,
)


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_CONFIG = ROOT / "config" / "analysis_toolchain.toml"
SCRIPT_DIR = ROOT / "scripts" / "ghidra"
FUNCTION_HEADER = [
    "index", "entry_linear", "entry_segment", "entry_offset", "body_min_linear",
    "body_max_linear", "body_addresses", "body_span", "body_range_count", "contiguous",
    "name", "signature", "calling_convention", "parameter_count", "is_thunk",
    "is_external", "is_no_return", "is_varargs", "has_custom_storage", "symbol_source",
    "caller_count", "callee_count",
]


def configured_com_seeds(artifact_id: str) -> list[int]:
    config_path = ROOT / "config" / "th04_boundary_review.toml"
    parsed = tomllib.loads(config_path.read_text(encoding="utf-8"))
    seeds = [0]
    for region in parsed.get("com_regions", []):
        if region.get("artifact") != artifact_id:
            continue
        start = int(region["start"])
        seeds.extend(start + int(offset) for offset in region.get("entry_offsets", []))
    return sorted(set(seeds))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private_path(path: Path, description: str) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to((ROOT / ".analysis").resolve())
    except ValueError as error:
        raise AnalysisError(f"{description} must stay below ignored .analysis") from error
    return resolved


def safe_name(value: str, description: str) -> str:
    if not value or value.startswith(".") or any(
        not (character.isalnum() or character in "-_") for character in value
    ):
        raise AnalysisError(f"unsafe {description}: {value!r}")
    return value


def environment(config: dict[str, object]) -> dict[str, str]:
    result = os.environ.copy()
    result["GHIDRA_HOME"] = str(repository_path(ROOT, config["ghidra"]["stable_path"]))
    result["JAVA_HOME"] = str(repository_path(ROOT, config["temurin_jdk"]["stable_path"]))
    xdg_root = repository_path(ROOT, config["private_paths"]["xdg_root"])
    for variable, leaf in (
        ("XDG_CONFIG_HOME", "config"),
        ("XDG_CACHE_HOME", "cache"),
        ("XDG_DATA_HOME", "data"),
    ):
        path = xdg_root / leaf
        path.mkdir(parents=True, exist_ok=True)
        result[variable] = str(path)
    result["DISPLAY"] = ""
    result["WAYLAND_DISPLAY"] = ""
    return result


def read_properties(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if not separator or not key or key in result:
            raise AnalysisError(f"malformed inventory properties: {path}")
        result[key] = value
    return result


def attest_export(output: Path, expected_sha: str, expected_nonce: str) -> int:
    properties = read_properties(output / "inventory.properties")
    checks = {
        "schema": properties.get("schema_version") == "1",
        "nonce": properties.get("export_nonce") == expected_nonce,
        "digest": properties.get("executable_sha256") == expected_sha,
        "language": properties.get("language_id") == "x86:LE:16:Real Mode",
        "timeout": properties.get("headless_analysis_timed_out") == "false",
    }
    with (output / "functions.csv").open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FUNCTION_HEADER:
            raise AnalysisError("function inventory header mismatch")
        rows = list(reader)
    checks["row_count"] = len(rows) == int(properties.get("function_count", "-1"))
    checks["indices"] = all(int(row["index"]) == index for index, row in enumerate(rows))
    entries = [int(row["entry_linear"], 0) for row in rows]
    checks["unique_entries"] = len(entries) == len(set(entries))
    checks["sorted_entries"] = entries == sorted(entries)
    if not all(checks.values()):
        failed = ", ".join(key for key, value in checks.items() if not value)
        raise AnalysisError(f"function inventory attestation failed: {failed}")
    return len(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_id")
    parser.add_argument("image", type=Path)
    parser.add_argument("--format", choices=("mz", "com"), required=True)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--project-name")
    parser.add_argument("--export-dir", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("--analysis-timeout", type=int, default=1800)
    import_parser.add_argument("--max-cpu", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    subparsers.add_parser("check")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_analysis_config(ANALYSIS_CONFIG)
        artifact_id = safe_name(args.artifact_id, "artifact ID")
        image = private_path(args.image, "analysis image")
        if not image.is_file():
            raise AnalysisError(f"missing analysis image: {image}")
        image_sha = digest(image)
        project_root = validate_project_root(
            ROOT,
            args.project_root
            or default_project_root(ROOT, config),
        )
        project_name = args.project_name or f"TH04-boundary-{artifact_id}"
        safe_name(project_name, "project name")
        output = private_path(
            args.export_dir
            or ROOT / ".analysis" / "ghidra" / "boundary-exports" / artifact_id,
            "inventory export",
        )
        project_file = project_root / f"{project_name}.gpr"
        project_store = project_root / f"{project_name}.rep"
        analyzer = repository_path(ROOT, config["ghidra"]["stable_path"]) / "support" / "analyzeHeadless"
        env = environment(config)
        subprocess.run([sys.executable, "scripts/attest_analysis_toolchain.py"], cwd=ROOT, check=True)
        nonce = uuid.uuid4().hex
        postscript = [
            "-postScript", "ExportFunctionInventory.java", str(output), image_sha, nonce,
            "-scriptPath", str(SCRIPT_DIR),
        ]
        if args.command == "import":
            if args.analysis_timeout <= 0 or args.max_cpu <= 0:
                raise AnalysisError("analysis timeout and max CPU must be positive")
            if project_file.exists() or project_store.exists():
                raise AnalysisError(f"project already exists: {project_file}")
            project_root.mkdir(parents=True, exist_ok=True)
            loader = [
                "-loader", str(config["mz_loader"]["class"]),
                "-processor", str(config["mz_loader"]["language_id"]),
                "-cspec", str(config["mz_loader"]["compiler_spec_id"]),
            ] if args.format == "mz" else [
                "-loader", "BinaryLoader", "-loader-baseAddr", "0x10000",
                "-loader-blockName", "COM_PAYLOAD",
                "-processor", str(config["mz_loader"]["language_id"]),
                "-cspec", str(config["mz_loader"]["compiler_spec_id"]),
            ]
            seed_script: list[str] = []
            if args.format == "com":
                seed_script = [
                    "-preScript", "SeedCodeEntries.java",
                    *(f"0x{0x10000 + offset:x}" for offset in configured_com_seeds(artifact_id)),
                ]
            command = [
                str(analyzer), str(project_root), project_name,
                "-import", str(image), *loader,
                *seed_script,
                "-analysisTimeoutPerFile", str(args.analysis_timeout),
                "-max-cpu", str(args.max_cpu), *postscript,
            ]
        else:
            if not project_file.is_file() or not project_store.is_dir():
                raise AnalysisError(f"missing Ghidra project: {project_file}")
            command = [
                str(analyzer), str(project_root), project_name,
                "-process", image.name, "-readOnly", "-noanalysis", *postscript,
            ]
        print("Running:", " ".join(command), flush=True)
        subprocess.run(command, cwd=ROOT, env=env, check=True)
        count = attest_export(output, image_sha, nonce)
        print(f"attested function inventory: {count} rows in {output / 'functions.csv'}")
        return 0
    except (
        AnalysisError, KeyError, OSError, subprocess.CalledProcessError, ValueError,
    ) as error:
        print(f"error: boundary Ghidra workflow failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
