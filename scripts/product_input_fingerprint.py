"""Conservative source/input identity for incremental TH04 product builds."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source_fingerprint() -> str:
    """Hash product inputs, including all native probes used by ZUN composition."""
    paths: set[Path] = set()
    for directory in ("src", "compat"):
        paths.update(path for path in (ROOT / directory).rglob("*") if path.is_file())
    paths.update((ROOT / "config").rglob("*.toml"))
    paths.update(path for path in (ROOT / "config/replay").rglob("*")
                 if path.is_file())
    for directory in ("scripts/probes", "scripts/lib"):
        paths.update((ROOT / directory).rglob("*.py"))
    paths.add(ROOT / "scripts/build_zun_composite.py")
    digest = hashlib.sha256()
    for path in sorted(paths):
        relative = path.relative_to(ROOT).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "little"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "little"))
        digest.update(data)
    return digest.hexdigest()
