#!/usr/bin/env python3
"""Cold A/B replay of the pinned DIET 1.45f packaging step.

The verdict concerns the supplied candidates and the packed target file only.
It grants no authored-source or unit exactness credit.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402

NAMES = {"th04-op": "OP.EXE", "th04-maine": "MAINE.EXE", "th04-zun": "ZUN.COM"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def private_output(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to((ROOT / ".analysis").resolve())
    except ValueError as error:
        raise ValueError("output must be below ignored .analysis") from error
    return resolved


def check_toolchain(artifact_id: str) -> tuple[Path, Path, Path, list[str], dict[str, str]]:
    diet = tomllib.loads((ROOT / "config/diet145f.toml").read_text())
    tool = diet["tool"]
    archive = ROOT / tool["archive_path"]
    binary = ROOT / tool["binary_path"]
    if sha256(archive.read_bytes()) != tool["archive_sha256"]:
        raise ValueError("DIET archive SHA-256 differs from pinned identity")
    with zipfile.ZipFile(archive) as bundle:
        extracted = bundle.read(tool["binary_member"])
    if sha256(extracted) != tool["binary_sha256"]:
        raise ValueError("DIET archive member SHA-256 differs from pinned identity")
    if binary.read_bytes() != extracted:
        raise ValueError("installed DIET.EXE differs from pinned archive member")
    runtime = tomllib.loads((ROOT / diet["runtime"]["identity_manifest"]).read_text())
    profile = runtime[diet["runtime"]["profile"]]
    executable_name = profile["command"]
    executable_str = shutil.which(executable_name)
    if executable_str is None:
        raise ValueError(f"{executable_name} is unavailable")
    executable = Path(executable_str).resolve()
    if sha256(executable.read_bytes()) != profile["binary_sha256"]:
        raise ValueError("DOSBox-X binary SHA-256 differs from pinned identity")
    config = ROOT / profile["config"]
    if sha256(config.read_bytes()) != profile["config_sha256"]:
        raise ValueError("DOSBox-X config SHA-256 differs from pinned identity")
    options = list(diet["pack_options"][artifact_id])
    expected = ["-B"] if artifact_id == "th04-zun" else ["-B", "-G"]
    if options != expected:
        raise ValueError(f"{artifact_id}: unexpected DIET pack options {options!r}")
    return binary, executable, config, options, {
        "archive_url": tool["archive_url"],
        "archive_sha256": tool["archive_sha256"],
        "diet_binary_sha256": tool["binary_sha256"],
        "dosbox_binary_sha256": profile["binary_sha256"],
        "dosbox_config_sha256": profile["config_sha256"],
        "diet_version": tool["version"],
        "dosbox_banner": profile["banner"],
    }


def run_once(
    label: str,
    candidate: Path,
    output: Path,
    name: str,
    diet_binary: Path,
    dosbox: Path,
    config: Path,
    options: list[str],
) -> dict[str, object]:
    work = output / label
    work.mkdir()
    shutil.copy2(diet_binary, work / "DIET.EXE")
    shutil.copy2(candidate, work / name)
    environment = os.environ.copy()
    environment.update({
        "SDL_VIDEODRIVER": "dummy",
        "SDL_AUDIODRIVER": "dummy",
        "XDG_CACHE_HOME": str(work / "cache"),
        "XDG_CONFIG_HOME": str(work / "config"),
        "XDG_DATA_HOME": str(work / "data"),
    })
    guest_command = " ".join(["diet.exe", *options, name.lower(), ">", "DIET.LOG"])
    command = [
        str(dosbox), "-defaultconf", "-defaultmapper", "-conf", str(config),
        "-fastlaunch", "-nogui", "-nomenu", "-exit", "-time-limit", "30",
        "-c", f'mount c "{work}"', "-c", "c:", "-c", guest_command,
        "-c", "exit",
    ]
    completed = subprocess.run(
        command, cwd=ROOT, env=environment, capture_output=True,
        text=True, timeout=40, check=False,
    )
    (work / "dosbox.log").write_text(completed.stdout + completed.stderr)
    guest_log_path = work / "DIET.LOG"
    guest_log = guest_log_path.read_bytes().decode("cp437", errors="replace") if guest_log_path.exists() else ""
    if completed.returncode != 0 or "Success!" not in guest_log:
        raise RuntimeError(
            f"{label}: DIET did not report success; DOSBox exit={completed.returncode}; "
            f"guest log={guest_log!r}"
        )
    result = (work / name).read_bytes()
    if not parse_mz(result).valid:
        raise ValueError(f"{label}: DIET output is not a valid MZ")
    return {
        "label": label,
        "candidate_path": str(candidate),
        "candidate_size": candidate.stat().st_size,
        "candidate_sha256": sha256(candidate.read_bytes()),
        "packed_path": str(work / name),
        "packed_size": len(result),
        "packed_sha256": sha256(result),
        "guest_command": guest_command,
        "host_command": command,
        "environment": {
            key: environment[key] for key in (
                "SDL_VIDEODRIVER", "SDL_AUDIODRIVER", "XDG_CACHE_HOME",
                "XDG_CONFIG_HOME", "XDG_DATA_HOME",
            )
        },
        "guest_log_sha256": sha256(guest_log_path.read_bytes()),
        "dosbox_log_sha256": sha256((work / "dosbox.log").read_bytes()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", choices=tuple(NAMES))
    parser.add_argument("--candidate-a", type=Path, required=True)
    parser.add_argument("--candidate-b", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--require-exact", action="store_true")
    args = parser.parse_args()
    artifact = find_artifact(
        load_target_manifest(ROOT / "config/targets.toml"), args.artifact
    )
    target = read_verified_artifact(ROOT, artifact)
    name = NAMES[args.artifact]
    candidates = [args.candidate_a.resolve(), args.candidate_b.resolve()]
    for candidate in candidates:
        data = candidate.read_bytes()
        if args.artifact == "th04-zun":
            if data[:2] == b"MZ":
                raise ValueError("ZUN input must be the pre-DIET flat COM composite")
        elif not parse_mz(data).valid:
            raise ValueError(f"candidate MZ integrity failed: {candidate}")
    diet_binary, dosbox, config, options, toolchain = check_toolchain(args.artifact)
    output = private_output(args.output_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    builds = [
        run_once(label, candidate, output, name, diet_binary, dosbox, config, options)
        for label, candidate in zip(("a", "b"), candidates)
    ]
    packed = [(output / label / name).read_bytes() for label in ("a", "b")]
    common_prefix = 0
    while (
        common_prefix < min(len(target), len(packed[0]))
        and target[common_prefix] == packed[0][common_prefix]
    ):
        common_prefix += 1
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "packed-file-toolchain-diagnostic-only",
        "artifact": args.artifact,
        "target_size": len(target),
        "target_sha256": sha256(target),
        "toolchain": toolchain,
        "options": options,
        "builds": builds,
        "candidate_inputs_identical": builds[0]["candidate_sha256"] == builds[1]["candidate_sha256"],
        "packed_outputs_identical": packed[0] == packed[1],
        "packed_raw_exact": packed[0] == target and packed[1] == target,
        "common_raw_prefix_bytes": common_prefix,
        "source_acceptance": "none",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "artifact": args.artifact,
        "candidate_inputs_identical": receipt["candidate_inputs_identical"],
        "packed_outputs_identical": receipt["packed_outputs_identical"],
        "packed_raw_exact": receipt["packed_raw_exact"],
        "target_size": len(target),
        "candidate_packed_size": len(packed[0]),
        "receipt": str(output / "receipt.json"),
    }))
    if not receipt["candidate_inputs_identical"] or not receipt["packed_outputs_identical"]:
        return 1
    if args.require_exact and not receipt["packed_raw_exact"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
