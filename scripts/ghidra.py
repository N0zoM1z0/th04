#!/usr/bin/env python3
"""Run the pinned, target-attested TH04 Ghidra workflow."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import uuid

from lib.analysis import (
    AnalysisError,
    default_project_root,
    load_analysis_config,
    repository_path,
    validate_project_root,
)
from lib.pc98 import parse_mz
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_CONFIG = ROOT / "config" / "analysis_toolchain.toml"
TARGET_CONFIG = ROOT / "config" / "targets.toml"
SCRIPT_DIR = ROOT / "scripts" / "ghidra"


def private_export(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to((ROOT / ".analysis").resolve())
    except ValueError as error:
        raise AnalysisError("Ghidra exports must stay below ignored .analysis") from error
    return resolved


def project_name(artifact_id: str) -> str:
    if not artifact_id or any(not (character.isalnum() or character in "-_") for character in artifact_id):
        raise AnalysisError(f"unsafe artifact ID for Ghidra project: {artifact_id!r}")
    return f"TH04-{artifact_id}"


def environment(config: dict[str, object]) -> dict[str, str]:
    result = os.environ.copy()
    ghidra_home = repository_path(ROOT, config["ghidra"]["stable_path"])
    jdk_home = repository_path(ROOT, config["temurin_jdk"]["stable_path"])
    xdg_root = repository_path(ROOT, config["private_paths"]["xdg_root"])
    for variable, leaf in (
        ("XDG_CONFIG_HOME", "config"),
        ("XDG_CACHE_HOME", "cache"),
        ("XDG_DATA_HOME", "data"),
    ):
        path = xdg_root / leaf
        path.mkdir(parents=True, exist_ok=True)
        result[variable] = str(path)
    result["GHIDRA_HOME"] = str(ghidra_home)
    result["JAVA_HOME"] = str(jdk_home)
    return result


def run_checked(command: list[str], *, env: dict[str, str] | None = None) -> None:
    print("Running:", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_id", help="MZ artifact ID from config/targets.toml")
    parser.add_argument(
        "--project-root",
        type=Path,
        help="ignored non-dot-prefixed project directory (default: ghidra-project)",
    )
    parser.add_argument("--project-name", help="override the per-artifact project name")
    parser.add_argument("--export-dir", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    import_parser = subparsers.add_parser("import", help="clean import, analyze, export, and attest")
    import_parser.add_argument("--no-analysis", action="store_true", help="loader-only calibration import")
    import_parser.add_argument("--analysis-timeout", type=int, default=1800)
    import_parser.add_argument("--max-cpu", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    subparsers.add_parser("check", help="read-only export and independent database attestation")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        analysis_config = load_analysis_config(ANALYSIS_CONFIG)
        target_manifest = load_target_manifest(TARGET_CONFIG)
        artifact = find_artifact(target_manifest, args.artifact_id)
        if artifact["format"] != "mz":
            raise AnalysisError("the current Ghidra workflow requires a DOS MZ target")
        target = read_verified_artifact(ROOT, artifact)
        image = parse_mz(target)

        configured_project_root = args.project_root
        if configured_project_root is None and os.environ.get("TH04_GHIDRA_PROJECT_ROOT"):
            configured_project_root = Path(os.environ["TH04_GHIDRA_PROJECT_ROOT"])
        project_root = validate_project_root(
            ROOT,
            configured_project_root
            if configured_project_root is not None
            else default_project_root(ROOT, analysis_config),
        )
        name = args.project_name or project_name(args.artifact_id)
        if not name or any(character in "/\\" for character in name) or name.startswith("."):
            raise AnalysisError(f"unsafe Ghidra project name: {name!r}")
        export_dir = private_export(
            args.export_dir or ROOT / ".analysis" / "ghidra" / "exports" / args.artifact_id
        )
        project_file = project_root / f"{name}.gpr"
        project_store = project_root / f"{name}.rep"

        run_checked([sys.executable, "scripts/attest_analysis_toolchain.py"])
        env = environment(analysis_config)
        analyzer = repository_path(
            ROOT, analysis_config["ghidra"]["stable_path"]
        ) / "support" / "analyzeHeadless"
        export_nonce = uuid.uuid4().hex
        postscript = [
            "-postScript",
            "ExportMzAttestation.java",
            str(export_dir),
            str(len(target)),
            str(image.header.header_size),
            str(image.header.declared_file_size),
            export_nonce,
        ]
        common = [
            "-scriptPath",
            str(SCRIPT_DIR),
        ]

        if args.command == "import":
            if project_file.exists() or project_store.exists():
                raise AnalysisError(
                    f"project already exists: {project_file}; use check or choose a clean name"
                )
            project_root.mkdir(parents=True, exist_ok=True)
            import_options = [
                "-import",
                str((ROOT / artifact["private_path"]).resolve()),
                "-loader",
                str(analysis_config["mz_loader"]["class"]),
                "-processor",
                str(analysis_config["mz_loader"]["language_id"]),
                "-cspec",
                str(analysis_config["mz_loader"]["compiler_spec_id"]),
            ]
            if args.no_analysis:
                import_options.append("-noanalysis")
            else:
                if args.analysis_timeout <= 0 or args.max_cpu <= 0:
                    raise AnalysisError("analysis timeout and max CPU must be positive")
                import_options.extend(
                    [
                        "-analysisTimeoutPerFile",
                        str(args.analysis_timeout),
                        "-max-cpu",
                        str(args.max_cpu),
                    ]
                )
            run_checked(
                [str(analyzer), str(project_root), name, *import_options, *postscript, *common],
                env=env,
            )
        else:
            if not project_file.is_file() or not project_store.is_dir():
                raise AnalysisError(f"missing Ghidra project: {project_file}; run import first")
            run_checked(
                [
                    str(analyzer),
                    str(project_root),
                    name,
                    "-process",
                    Path(str(artifact["private_path"])).name,
                    "-readOnly",
                    "-noanalysis",
                    *postscript,
                    *common,
                ],
                env=env,
            )

        run_checked(
            [
                sys.executable,
                "scripts/attest_ghidra_database.py",
                args.artifact_id,
                str(export_dir),
                "--expected-nonce",
                export_nonce,
            ]
        )
        return 0
    except (
        AnalysisError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"error: Ghidra workflow failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
