#!/usr/bin/env python3
"""Cold-build maintained ZUN COM parts and verify their mixed flat composite."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PROBES = ROOT / ".analysis/reconstruction/probes"
sys.path.insert(0, str(ROOT / "scripts"))

from build_zun_composite import flat_payload  # noqa: E402
from probes.replay_th04_zun_mixed_composite import (  # noqa: E402
    INPUTS, SNAPSHOT, TARGET, TARGET_SHA256,
)

BUILDERS = (
    ("selector", "replay_th04_zun_selector.py"),
    ("launcher_tails", "replay_th04_zun_launcher_tails.py"),
    ("ongchk", "replay_th04_zun_ongchk.py"),
    ("zuninit", "replay_th04_zuninit_symbolic.py"),
    ("memchk", "replay_th04_zun_memchk_natural.py"),
)
OUTPUTS = {
    "selector": ("selector", "selector.bin"),
    "moveup": ("launcher_tails", "moveup.bin"),
    "customization": ("launcher_tails", "custom.bin"),
    "ongchk": ("ongchk", "ongchk.com"),
    "zuninit": ("zuninit", "zuninit.com"),
    "memchk": ("memchk", "work/bin/th04/memchk.com"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_checked(name: str, path: Path) -> tuple[bytes, dict[str, object]]:
    _origin, _template, size, digest = INPUTS[name]
    data = path.read_bytes()
    if len(data) != size or sha(data) != digest:
        raise RuntimeError(f"{name}: input identity drift: {path}")
    reported = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    return data, {"path": str(reported), "size": size, "sha256": digest}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    for name in ("usage", "resident"):
        for label in ("a", "b"):
            default = SNAPSHOT / label / "op/source" / (
                "th04/zun.txt" if name == "usage" else "bin/th04/res_huma.com"
            )
            parser.add_argument(f"--{name}-{label}", type=Path, default=default)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or output.parent != PROBES.resolve():
        parser.error("output must be a new direct child of .analysis/reconstruction/probes")
    child_dirs = {name: output.with_name(output.name + "-" + name)
                  for name, _script in BUILDERS}
    if any(path.exists() for path in child_dirs.values()):
        parser.error("a cold component output directory already exists")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   capture_output=True, text=True, check=True)
    target = TARGET.read_bytes()
    if sha(target) != TARGET_SHA256:
        raise RuntimeError("decoded ZUN target identity drift")

    external = {}
    for label in ("a", "b"):
        external[label] = {}
        for name in ("usage", "resident"):
            path = getattr(args, f"{name}_{label}").resolve()
            external[label][name] = load_checked(name, path)

    output.mkdir()
    builds = {}
    for name, script in BUILDERS:
        command = [sys.executable, str(ROOT / "scripts/probes" / script),
                   "--output-dir", str(child_dirs[name])]
        done = subprocess.run(command, cwd=ROOT, capture_output=True,
                              text=True, timeout=900)
        log = output / f"{name}.log"
        log.write_text(json.dumps(command) + f"\nexit={done.returncode}\n"
                       + done.stdout + done.stderr)
        if done.returncode:
            raise RuntimeError(f"{name}: cold source build failed; inspect {log}")
        receipt = child_dirs[name] / "receipt.json"
        builds[name] = {
            "probe": script,
            "probe_sha256": sha((ROOT / "scripts/probes" / script).read_bytes()),
            "receipt": str(receipt.relative_to(ROOT)),
            "receipt_sha256": sha(receipt.read_bytes()),
        }

    rounds = {}
    last_inputs = None
    for label in ("a", "b"):
        inputs = {}
        provenance = {}
        for name, (directory, relative) in OUTPUTS.items():
            inputs[name], provenance[name] = load_checked(
                name, child_dirs[directory] / label / relative
            )
            provenance[name]["origin"] = "maintained-source"
        for name in ("usage", "resident"):
            inputs[name], provenance[name] = external[label][name]
            provenance[name]["origin"] = (
                "external-asset" if name == "usage" else "external-diagnostic-candidate"
            )
        flat, parts = flat_payload(
            inputs["usage"], inputs["selector"],
            tuple(inputs[name] for name in ("ongchk", "zuninit", "resident", "memchk")),
            inputs["moveup"], inputs["customization"],
        )
        if flat != target or parts["directory"] != target[0x20E:0x355]:
            raise RuntimeError(f"{label}: complete flat or directory differs")
        (output / f"{label}.flat.bin").write_bytes(flat)
        rounds[label] = {"inputs": provenance, "flat_size": len(flat),
                         "flat_sha256": sha(flat),
                         "directory_sha256": sha(parts["directory"])}
        last_inputs = inputs
    if rounds["a"]["flat_sha256"] != rounds["b"]["flat_sha256"]:
        raise RuntimeError("cold A/B flat payloads differ")
    assert last_inputs is not None
    mutated, mutated_parts = flat_payload(
        last_inputs["usage"], last_inputs["selector"],
        (last_inputs["ongchk"], last_inputs["zuninit"] + b"\0",
         last_inputs["resident"], last_inputs["memchk"]),
        last_inputs["moveup"], last_inputs["customization"],
    )
    if mutated == target or mutated_parts["directory"] == target[0x20E:0x355]:
        raise RuntimeError("component-length mutation did not invalidate comparison")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "fresh maintained-source ZUN components in mixed-input flat build",
        "target_payload_sha256": TARGET_SHA256,
        "builder_sha256": sha((ROOT / "scripts/build_zun_composite.py").read_bytes()),
        "source_builds": builds, "rounds": rounds,
        "complete_flat_raw_equal": True,
        "component_length_mutation_rejected": True,
        "limit": (
            "Usage text is an external asset and RES_HUMA is a diagnostic ReC98 "
            "candidate with inert optimizer barriers. This grants no complete "
            "ZUN source or packed-MZ exact acceptance."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "receipt_sha256": sha(path.read_bytes()),
                      "flat_sha256": rounds["a"]["flat_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
