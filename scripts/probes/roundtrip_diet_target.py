#!/usr/bin/env python3
"""Calibrate DIET restore/repack on private copies of pinned packed targets.

This is intentionally circular for source reconstruction: the input is a
target copy. It identifies a packer/options round trip and the limitations of
DIET's restored MZ, never an accepted TH04 source or exact unit.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from replay_diet145f import NAMES, check_toolchain, private_output, sha256  # noqa: E402


def run_guest(
    work: Path, dosbox: Path, config: Path, command_text: str, log_name: str
) -> dict[str, object]:
    environment = os.environ.copy()
    environment.update({
        "SDL_VIDEODRIVER": "dummy",
        "SDL_AUDIODRIVER": "dummy",
        "XDG_CACHE_HOME": str(work / "cache"),
        "XDG_CONFIG_HOME": str(work / "config"),
        "XDG_DATA_HOME": str(work / "data"),
    })
    guest_command = f"{command_text} > {log_name}"
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
    (work / f"{log_name}.host").write_text(completed.stdout + completed.stderr)
    guest_log_path = work / log_name
    guest_log = (
        guest_log_path.read_bytes().decode("cp437", errors="replace")
        if guest_log_path.exists() else ""
    )
    if completed.returncode != 0 or "Success!" not in guest_log:
        raise RuntimeError(
            f"DIET {command_text!r} failed: emulator={completed.returncode}, "
            f"guest={guest_log!r}"
        )
    return {
        "guest_command": guest_command,
        "host_command": command,
        "guest_log_sha256": sha256(guest_log_path.read_bytes()),
        "host_log_sha256": sha256((work / f"{log_name}.host").read_bytes()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", choices=tuple(NAMES))
    parser.add_argument("--observation-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    artifact = find_artifact(
        load_target_manifest(ROOT / "config/targets.toml"), args.artifact
    )
    target = read_verified_artifact(ROOT, artifact)
    observation = args.observation_dir.resolve()
    observation_receipt = json.loads((observation / "receipt.json").read_text())
    observed_payload = (observation / "payload.bin").read_bytes()
    if (
        observation_receipt["artifact"] != args.artifact
        or observation_receipt["packed_target_sha256"] != sha256(target)
        or observation_receipt["payload_sha256"] != sha256(observed_payload)
        or not all(observation_receipt["checks"].values())
    ):
        raise ValueError("independent target-stub payload observation failed identity")
    with (observation / "relocations.csv").open(newline="") as stream:
        observed_relocations = [
            int(row["relative_linear"], 0) for row in csv.DictReader(stream)
        ]
    if len(observed_relocations) != observation_receipt["relocation_count"]:
        raise ValueError("independent target-stub relocation count failed")
    binary, dosbox, config, options, toolchain = check_toolchain(args.artifact)
    output = private_output(args.output_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    name = NAMES[args.artifact]
    builds: list[dict[str, object]] = []
    restored_outputs: list[bytes] = []
    repacked_outputs: list[bytes] = []
    for label in ("a", "b"):
        work = output / label
        work.mkdir()
        shutil.copy2(binary, work / "DIET.EXE")
        (work / name).write_bytes(target)
        restore_command = run_guest(
            work, dosbox, config, f"diet.exe -ra {name.lower()}", "RESTORE.LOG"
        )
        restored = (work / name).read_bytes()
        if args.artifact == "th04-zun":
            restored_payload = restored
            restored_sites: list[int] = []
            extra = b""
            header: dict[str, int] | None = None
        else:
            mz = parse_mz(restored)
            if not mz.valid:
                raise ValueError(f"{label}: DIET-restored MZ is invalid")
            restored_payload = mz.program_image[: len(observed_payload)]
            extra = mz.program_image[len(observed_payload) :]
            restored_sites = [item.linear for item in mz.relocations]
            header = {
                "header_paragraphs": mz.header.header_paragraphs,
                "initial_relative_ss": mz.header.initial_relative_ss,
                "initial_sp": mz.header.initial_sp,
                "minimum_extra_allocation": mz.header.minimum_extra_allocation,
                "relocation_count": len(mz.relocations),
            }
        if restored_payload != observed_payload:
            raise ValueError(f"{label}: DIET restore disagrees with target-stub payload")
        if restored_sites != observed_relocations:
            raise ValueError(f"{label}: DIET restore and target-stub relocation order disagree")
        (work / "restored.bin").write_bytes(restored)
        restored_outputs.append(restored)
        pack_command = run_guest(
            work, dosbox, config,
            " ".join(["diet.exe", *options, name.lower()]), "REPACK.LOG",
        )
        repacked = (work / name).read_bytes()
        repacked_outputs.append(repacked)
        builds.append({
            "label": label,
            "restored_size": len(restored),
            "restored_sha256": sha256(restored),
            "restored_path": str(work / "restored.bin"),
            "restored_payload_prefix_exact": True,
            "restored_extra_zero_bytes": len(extra) if all(value == 0 for value in extra) else None,
            "restored_relocation_order_equals_stub_application": True,
            "restored_header_diagnostic": header,
            "repacked_size": len(repacked),
            "repacked_sha256": sha256(repacked),
            "restore_command": restore_command,
            "pack_command": pack_command,
        })
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "target-derived-packer-roundtrip-only",
        "artifact": args.artifact,
        "target_size": len(target),
        "target_sha256": sha256(target),
        "observation_receipt_sha256": sha256((observation / "receipt.json").read_bytes()),
        "toolchain": toolchain,
        "pack_options": options,
        "builds": builds,
        "restored_outputs_identical": restored_outputs[0] == restored_outputs[1],
        "repacked_outputs_identical": repacked_outputs[0] == repacked_outputs[1],
        "repacked_raw_exact": all(item == target for item in repacked_outputs),
        "source_acceptance": "none; restore begins from target copies",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "artifact": args.artifact,
        "restored_size": builds[0]["restored_size"],
        "extra_zero_bytes": builds[0]["restored_extra_zero_bytes"],
        "repacked_raw_exact": receipt["repacked_raw_exact"],
        "receipt": str(output / "receipt.json"),
    }))
    return 0 if (
        receipt["restored_outputs_identical"]
        and receipt["repacked_outputs_identical"]
        and receipt["repacked_raw_exact"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
