#!/usr/bin/env python3
"""Build TH04 ZUN's flat COM payload from maintained source components."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PROBES = (ROOT / ".analysis/reconstruction/probes").resolve()
USAGE = ROOT / "src/zun/launcher/usage.txt"
sys.path.insert(0, str(ROOT / "scripts"))
from build_zun_composite import flat_payload  # noqa: E402
from probes.replay_th04_zun_source_composite import BUILDERS, OUTPUTS  # noqa: E402


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def invoke(script: str, directory: Path, output: Path, *arguments: str) -> dict[str, object]:
    command = [sys.executable, str(ROOT / "scripts/probes" / script),
               "--output-dir", str(directory), *arguments]
    done = subprocess.run(command, cwd=ROOT, capture_output=True,
                          text=True, timeout=1200)
    log = output / (directory.name + ".log")
    log.write_text(json.dumps(command) + f"\nexit={done.returncode}\n"
                   + done.stdout + done.stderr, encoding="utf-8")
    if done.returncode:
        raise RuntimeError(f"component build failed: {log}")
    receipt = directory / "receipt.json"
    if not receipt.is_file():
        raise RuntimeError(f"component receipt missing: {directory}")
    return {"script": script, "receipt": str(receipt.relative_to(ROOT)),
            "receipt_sha256": sha(receipt.read_bytes())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(PROBES):
        parser.error("use a new private probe directory")
    children = {
        name: output.with_name(output.name + "-" + name)
        for name, _script in BUILDERS
    }
    children.update({
        label: output.with_name(output.name + "-resident-" + label)
        for label in ("a", "b")
    })
    if any(directory.exists() for directory in children.values()):
        parser.error("a component output directory already exists")
    usage_source = USAGE.read_text(encoding="utf-8")
    if not usage_source.endswith("\n") or "\r" in usage_source:
        raise ValueError("usage source needs LF lines and final newline")
    usage = usage_source.replace("\n", "\r\n").encode("cp932")

    output.mkdir(parents=True)
    builds = {}
    for name, _script in BUILDERS:
        builds[name] = invoke("probe_th04_native_zun_parts.py", children[name], output,
                              "--component", name)
    for label in ("a", "b"):
        builds["resident_" + label] = invoke(
            "probe_th04_native_zun_resident.py", children[label], output
        )

    rounds = {}
    for label in ("a", "b"):
        parts = {}
        provenance = {}
        for name, (child, relative) in OUTPUTS.items():
            source = children[child] / label / relative
            parts[name] = source.read_bytes()
            provenance[name] = {"path": str(source.relative_to(ROOT)),
                                "size": len(parts[name]), "sha256": sha(parts[name])}
        resident_receipt = json.loads((children[label] / "receipt.json").read_text())
        if not resident_receipt["link_complete"] or resident_receipt["problems"]:
            raise ValueError(f"resident {label} is not a source-only complete link")
        resident_path = children[label] / "source/bin/res_huma.com"
        resident = resident_path.read_bytes()
        if sha(resident) != resident_receipt["com_sha256"]:
            raise ValueError(f"resident {label} identity drift")
        provenance["resident"] = {"path": str(resident_path.relative_to(ROOT)),
                                   "size": len(resident), "sha256": sha(resident)}
        flat, generated = flat_payload(
            usage, parts["selector"],
            (parts["ongchk"], parts["zuninit"], resident, parts["memchk"]),
            parts["moveup"], parts["customization"],
        )
        flat_path = output / f"{label}.flat.bin"
        flat_path.write_bytes(flat)
        rounds[label] = {"flat_size": len(flat), "flat_sha256": sha(flat),
                         "directory_sha256": sha(generated["directory"]),
                         "inputs": provenance}
    if rounds["a"]["flat_sha256"] != rounds["b"]["flat_sha256"]:
        raise ValueError("two cold source-only flat ZUN builds differ")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "TH04-only source-composed flat ZUN payload before DIET packing",
        "artifact": "th04-zun",
        "usage_source": str(USAGE.relative_to(ROOT)),
        "usage_source_sha256": sha(USAGE.read_bytes()),
        "usage_encoded_sha256": sha(usage),
        "source_builds": builds,
        "rounds": rounds,
        "cold_equal": True,
        "packed_mz_claim": False,
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n",
                                          encoding="utf-8")
    print(json.dumps({"cold_equal": True, "flat_size": rounds["a"]["flat_size"],
                      "flat_sha256": rounds["a"]["flat_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
