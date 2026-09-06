"""Read hash-pinned private target artifacts without weakening provenance checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import tomllib

from .pc98 import classify_format, digest_bytes, parse_mz


class TargetError(ValueError):
    """Raised when a target is missing, ambiguous, or fails its manifest."""


def load_target_manifest(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def find_artifact(manifest: dict[str, Any], artifact_id: str) -> dict[str, Any]:
    matches = [
        artifact
        for artifact in manifest.get("artifacts", [])
        if artifact.get("id") == artifact_id
    ]
    if len(matches) != 1:
        raise TargetError(
            f"expected one manifest artifact named {artifact_id!r}; found {len(matches)}"
        )
    return matches[0]


def read_verified_artifact(root: Path, artifact: dict[str, Any]) -> bytes:
    path = root / artifact["private_path"]
    if not path.is_file():
        raise TargetError(
            f"private artifact is missing: {path}; run scripts/import_targets.py"
        )
    data = path.read_bytes()
    checks = {
        "size": (len(data), int(artifact["size"])),
        "sha256": (digest_bytes(data), artifact["sha256"]),
        "md5": (digest_bytes(data, "md5"), artifact["md5"]),
        "format": (classify_format(data), artifact["format"]),
    }
    failures = [
        f"{name}: {actual!r} != {expected!r}"
        for name, (actual, expected) in checks.items()
        if actual != expected
    ]
    if failures:
        raise TargetError(
            f"{artifact['id']} failed its public manifest: " + "; ".join(failures)
        )
    if artifact["format"] == "mz":
        image = parse_mz(data)
        if not image.valid:
            raise TargetError(
                f"{artifact['id']} is structurally invalid: "
                + "; ".join(image.errors)
            )
    return data
