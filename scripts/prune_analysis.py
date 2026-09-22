#!/usr/bin/env python3
"""Safely prune unreferenced private `.analysis/gpt-web` experiment trees.

The default mode is a dry run. `--apply` removes only top-level directories
that satisfy all of the following:

* they are below the configured `.analysis/gpt-web` root;
* no tracked repository text file mentions that top-level directory;
* they are not listed in `config/analysis_retention.toml::full_keep_dirs`.

This intentionally does *not* collapse referenced directories to receipt-only
form. That stronger cleanup requires a human review of replay dependencies.
Targets, toolchains, runtime images, Ghidra data, and every other `.analysis`
subtree are outside this script's deletion scope.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/analysis_retention.toml"
REFERENCE_RE = re.compile(r"\.analysis/gpt-web/([^/\s;,)`\"']+)")


def tracked_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item.decode() for item in raw.split(b"\0") if item]


def referenced_top_dirs() -> set[str]:
    result: set[str] = set()
    for path in tracked_files():
        try:
            text = path.read_text(errors="replace")
        except (OSError, UnicodeError):
            continue
        result.update(match.group(1) for match in REFERENCE_RE.finditer(text))
    return result


def tree_bytes(path: Path) -> int:
    total = 0
    for child in path.rglob("*"):
        try:
            if child.is_file() and not child.is_symlink():
                total += child.stat().st_size
        except OSError:
            pass
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="perform deletions; default is dry-run")
    args = parser.parse_args()

    cfg = tomllib.loads(CONFIG.read_text())
    root = (ROOT / cfg["gpt_web_root"]).resolve()
    analysis = (ROOT / ".analysis").resolve()
    if not root.is_relative_to(analysis) or root == analysis:
        raise SystemExit(f"unsafe configured prune root: {root}")
    if not root.is_dir():
        print(f"analysis prune: nothing to do; missing {root.relative_to(ROOT)}")
        return 0

    protected = set(cfg.get("full_keep_dirs", []))
    refs = referenced_top_dirs()
    candidates: list[tuple[Path, int]] = []
    for path in sorted(root.iterdir(), key=lambda p: p.name):
        if not path.is_dir() or path.is_symlink():
            continue
        if path.name in protected or path.name in refs:
            continue
        resolved = path.resolve()
        if resolved.parent != root:
            raise SystemExit(f"refusing non-child prune candidate: {resolved}")
        candidates.append((path, tree_bytes(path)))

    total = sum(size for _, size in candidates)
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(
        f"analysis prune [{mode}]: {len(candidates)} unreferenced top-level dirs, "
        f"{total / (1024 ** 3):.2f} GiB"
    )
    for path, size in sorted(candidates, key=lambda item: item[1], reverse=True):
        print(f"  {size / (1024 ** 2):8.1f} MiB  {path.relative_to(ROOT)}")

    if args.apply:
        for path, _ in candidates:
            shutil.rmtree(path)
        print(f"analysis prune: removed {len(candidates)} directories")
    else:
        print("analysis prune: no files deleted; rerun with --apply after review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
