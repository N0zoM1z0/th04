#!/usr/bin/env python3
"""Safely prune private `.analysis/gpt-web` experiment trees.

The default mode is a dry run. `--apply` removes only unreferenced top-level
experiment directories. With `--compact-referenced`, the script additionally
shrinks referenced expanded replay trees when every tracked path reference is
only the directory itself, `receipt.json`, or an explicitly configured small
keep-file.

Full source snapshots listed in `config/analysis_retention.toml` are never
removed or compacted. Targets, toolchains, runtime images, Ghidra data, and all
other `.analysis` subtrees are outside this script's deletion scope.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import re
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/analysis_retention.toml"
TOP_REFERENCE_RE = re.compile(r"\.analysis/gpt-web/([^/\s;,)`\"']+)")
FULL_REFERENCE_RE = re.compile(r"\.analysis/gpt-web/[A-Za-z0-9_./+\-\[\]]+")


def tracked_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item.decode() for item in raw.split(b"\0") if item]


def tracked_reference_map() -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    prefix = ".analysis/gpt-web/"
    for path in tracked_files():
        try:
            text = path.read_text(errors="replace")
        except (OSError, UnicodeError):
            continue
        for match in FULL_REFERENCE_RE.finditer(text):
            full = match.group(0).rstrip(".")
            tail = full[len(prefix):]
            top, sep, rest = tail.partition("/")
            if top:
                result[top].add(rest if sep else "")
        # Keep the simpler top-level scan as a guard for unusual punctuation
        # that terminates FULL_REFERENCE_RE early.
        for match in TOP_REFERENCE_RE.finditer(text):
            result.setdefault(match.group(1), set())
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


def compact_plan(
    root: Path,
    refs: dict[str, set[str]],
    protected: set[str],
    extra_keep: dict[str, list[str]],
) -> list[tuple[Path, int, set[str]]]:
    plan: list[tuple[Path, int, set[str]]] = []
    for path in sorted(root.iterdir(), key=lambda p: p.name):
        if not path.is_dir() or path.is_symlink() or path.name in protected:
            continue
        if path.name not in refs:
            continue  # unreferenced deletion is handled separately
        receipt = path / "receipt.json"
        if not receipt.is_file():
            continue
        keep = {"receipt.json", *extra_keep.get(path.name, [])}
        referenced = refs[path.name]
        allowed_refs = {"", *keep}
        if not referenced.issubset(allowed_refs):
            continue
        missing = [rel for rel in keep if not (path / rel).is_file()]
        if missing:
            raise SystemExit(f"refusing to compact {path}: configured keep files missing: {missing}")
        current = tree_bytes(path)
        kept = sum((path / rel).stat().st_size for rel in keep)
        if current > kept:
            plan.append((path, current - kept, keep))
    return plan


def compact_directory(path: Path, keep: set[str]) -> None:
    keep_abs = {(path / rel).resolve() for rel in keep}
    for child in sorted(path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if child.is_symlink():
            child.unlink()
        elif child.is_file():
            if child.resolve() not in keep_abs:
                child.unlink()
        elif child.is_dir():
            try:
                child.rmdir()
            except OSError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="perform deletions; default is dry-run")
    parser.add_argument(
        "--compact-referenced",
        action="store_true",
        help="also shrink safe referenced replay dirs to receipt/configured keep files",
    )
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
    extra_keep = {str(k): list(v) for k, v in cfg.get("compact_keep_files", {}).items()}
    refs = tracked_reference_map()

    delete_candidates: list[tuple[Path, int]] = []
    for path in sorted(root.iterdir(), key=lambda p: p.name):
        if not path.is_dir() or path.is_symlink():
            continue
        if path.name in protected or path.name in refs:
            continue
        resolved = path.resolve()
        if resolved.parent != root:
            raise SystemExit(f"refusing non-child prune candidate: {resolved}")
        delete_candidates.append((path, tree_bytes(path)))

    compact_candidates = (
        compact_plan(root, refs, protected, extra_keep) if args.compact_referenced else []
    )
    delete_total = sum(size for _, size in delete_candidates)
    compact_total = sum(size for _, size, _ in compact_candidates)
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(
        f"analysis prune [{mode}]: delete {len(delete_candidates)} dirs / "
        f"{delete_total / (1024 ** 3):.2f} GiB; compact "
        f"{len(compact_candidates)} dirs / {compact_total / (1024 ** 3):.2f} GiB"
    )
    for path, size in sorted(delete_candidates, key=lambda item: item[1], reverse=True):
        print(f"  DELETE  {size / (1024 ** 2):8.1f} MiB  {path.relative_to(ROOT)}")
    for path, size, keep in sorted(compact_candidates, key=lambda item: item[1], reverse=True):
        kept = ", ".join(sorted(keep))
        print(f"  COMPACT {size / (1024 ** 2):8.1f} MiB  {path.relative_to(ROOT)}  keep=[{kept}]")

    if args.apply:
        for path, _ in delete_candidates:
            shutil.rmtree(path)
        for path, _, keep in compact_candidates:
            compact_directory(path, keep)
        print(
            f"analysis prune: removed {len(delete_candidates)} dirs; "
            f"compacted {len(compact_candidates)} dirs"
        )
    else:
        print("analysis prune: no files deleted; rerun with --apply after review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
