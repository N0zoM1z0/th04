#!/usr/bin/env python3
"""Check the local flat ZUN builder with mixed maintained and external inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_zun_composite import flat_payload  # noqa: E402

TARGET = ROOT / ".analysis/reconstruction/v218-th04-zun-diet/payload.bin"
TARGET_SHA256 = "baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e"
DIET_DIR = ROOT / ".analysis/reconstruction/probes"
SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003"

INPUTS = {
    "usage": ("external-asset", "{snapshot}/th04/zun.txt", 264,
              "46a342303388a468c5d13c3c00f800d85aa98f84a9ed11b45e03d87a32737498"),
    "selector": ("maintained", "{probes}/v786-zun-selector-focused-001/{round}/selector.bin", 223,
                 "cda3d3f38031f14988d236cc6725109d2f162e65224509101ca55c6dcb05fcfc"),
    "ongchk": ("external-library", "{snapshot}/libs/kaja/ongchk.com", 926,
                "4f9a9451f19bdd8d3ea8949a5ea75df6c2f92a9a84dcf39e1d7cf13421acc8a0"),
    "zuninit": ("maintained", "{probes}/v785-zuninit-symbolic-final-001/{round}/zuninit.com", 1141,
                "692b1e056d907a9649bd1effa6e83239f71039d17de3569464067d0b42b7aa5e"),
    "resident": ("external-candidate", "{snapshot}/bin/th04/res_huma.com", 6360,
                 "cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110"),
    "memchk": ("maintained", "{probes}/v773-zun-memchk-natural-focused-002/{round}/work/bin/th04/memchk.com", 4066,
               "2531795670b5cafb65bf261f499d5d77b71aeaf26015f8481000cdbb96272dfc"),
    "moveup": ("maintained", "{probes}/v787-zun-launcher-tails-001/{round}/moveup.bin", 8,
               "a580939da3b518b3001c1a4ff48fd9860511eddc239d702c6e13e41ac9125b00"),
    "customization": ("maintained", "{probes}/v787-zun-launcher-tails-001/{round}/custom.bin", 68,
                      "0982f4fa42c53b1df727fd10f64ef5ae2515bbdc90fb1a595209b8dc943d95fd"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_inputs(round_label: str) -> tuple[dict[str, bytes], dict[str, object]]:
    snapshot = SNAPSHOT / round_label / "op/source"
    data = {}
    provenance = {}
    for name, (origin, template, size, digest) in INPUTS.items():
        path = Path(template.format(snapshot=snapshot, probes=DIET_DIR, round=round_label))
        blob = path.read_bytes()
        if len(blob) != size or sha(blob) != digest:
            raise RuntimeError(f"{name}: source input identity drift: {path}")
        data[name] = blob
        provenance[name] = {"origin": origin, "path": str(path.relative_to(ROOT)),
                            "size": size, "sha256": digest}
    return data, provenance


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or output.parent != DIET_DIR.resolve():
        parser.error("output must be a new direct child of .analysis/reconstruction/probes")
    target = TARGET.read_bytes()
    if sha(target) != TARGET_SHA256:
        raise RuntimeError("attested decoded target identity drift")
    output.mkdir()
    rounds = {}
    for label in ("a", "b"):
        inputs, provenance = load_inputs(label)
        flat, parts = flat_payload(
            inputs["usage"], inputs["selector"],
            tuple(inputs[name] for name in ("ongchk", "zuninit", "resident", "memchk")),
            inputs["moveup"], inputs["customization"],
        )
        if flat != target or parts["directory"] != target[0x20E:0x355]:
            raise RuntimeError(f"{label}: mixed-input flat or generated directory differs")
        (output / f"{label}.flat.bin").write_bytes(flat)
        rounds[label] = {
            "inputs": provenance,
            "flat_size": len(flat),
            "flat_sha256": sha(flat),
            "directory_size": len(parts["directory"]),
            "directory_sha256": sha(parts["directory"]),
            "header_sha256": sha(parts["header"]),
        }
    if rounds["a"]["flat_sha256"] != rounds["b"]["flat_sha256"]:
        raise RuntimeError("A/B flat identity drift")
    mutated, mutated_parts = flat_payload(
        inputs["usage"], inputs["selector"],
        (inputs["ongchk"], inputs["zuninit"] + b"\0", inputs["resident"], inputs["memchk"]),
        inputs["moveup"], inputs["customization"],
    )
    if mutated == target or mutated_parts["directory"] == target[0x20E:0x355]:
        raise RuntimeError("component-length mutation failed to invalidate the directory and flat comparator")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "mixed-input integration Oracle for checked-in flat ZUN builder",
        "target_payload_sha256": TARGET_SHA256,
        "builder_sha256": sha((ROOT / "scripts/build_zun_composite.py").read_bytes()),
        "rounds": rounds,
        "generated_directory_raw_equal": True,
        "mixed_flat_raw_equal": True,
        "component_length_mutation_rejected": True,
        "limit": (
            "This is diagnostic integration, not a product-source or packed-file exact claim. "
            "Usage text and ONGCHK are external; the resident component comes from a ReC98 "
            "candidate with optimizer barriers, not maintained natural TH04 source."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "receipt_sha256": sha(path.read_bytes()),
                      "directory_sha256": rounds["a"]["directory_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
