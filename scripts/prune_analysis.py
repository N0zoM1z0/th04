#!/usr/bin/env python3
"""Safely prune rebuildable private analysis and repository cache output.

Default mode is a dry run.

- Existing `.analysis/gpt-web` retention behavior is always reviewed. With
  `--compact-referenced`, referenced replay trees that are safe to compact are
  reduced to `receipt.json` plus configured keep files.
- `--prune-probes` removes direct children of the configured
  `.analysis/reconstruction/probes` root except explicit keep directories.
- `--prune-exact-replays` removes expanded MAIN exact-unit replay worktrees
  after their receipts have been archived.
- `--prune-caches` removes only explicit repository-local cache/build
  directories listed in `config/analysis_retention.toml`.

Before applying probe or exact-replay deletion, the configured private archive
must contain every top-level result and receipt with matching SHA-256 bytes.

Pinned targets, toolchains, runtime images, Ghidra data, retained source
snapshots, and configured probe dependencies are never generic prune targets.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import io
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
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
    superseded: set[str],
) -> list[tuple[Path, int, set[str], bool]]:
    plan: list[tuple[Path, int, set[str], bool]] = []
    for path in sorted(root.iterdir(), key=lambda p: p.name):
        if not path.is_dir() or path.is_symlink() or path.name in protected:
            continue
        if path.name not in refs:
            continue
        receipt = path / "receipt.json"
        if not receipt.is_file():
            continue
        keep = {"receipt.json", *extra_keep.get(path.name, [])}
        referenced = refs[path.name]
        allowed_refs = {"", *keep}
        forced = path.name in superseded
        if not forced and not referenced.issubset(allowed_refs):
            continue
        missing = [rel for rel in keep if not (path / rel).is_file()]
        if missing:
            raise SystemExit(
                f"refusing to compact {path}: configured keep files missing: {missing}"
            )
        current = tree_bytes(path)
        kept = sum((path / rel).stat().st_size for rel in keep)
        if current > kept:
            plan.append((path, current - kept, keep, forced))
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


def direct_child_delete_plan(root: Path, keep: set[str]) -> list[tuple[Path, int]]:
    result: list[tuple[Path, int]] = []
    if not root.is_dir():
        return result
    for path in sorted(root.iterdir(), key=lambda p: p.name):
        if not path.is_dir() or path.is_symlink() or path.name in keep:
            continue
        resolved = path.resolve()
        if resolved.parent != root:
            raise SystemExit(f"refusing non-child prune candidate: {resolved}")
        result.append((path, tree_bytes(path)))
    return result


def verify_replay_archive(
    directories: list[Path], archive: Path, manifest: Path
) -> None:
    """Require recoverable small results before deleting expanded replay trees."""

    if not directories:
        return
    receipt_root = (ROOT / ".analysis/reconstruction/receipt-archive").resolve()
    for path in (archive, manifest):
        if not path.is_file() or not path.resolve().is_relative_to(receipt_root):
            raise SystemExit(f"missing or unsafe replay archive input: {path}")
    checksum = archive.with_name(archive.name + ".sha256")
    if not checksum.is_file() or not checksum.resolve().is_relative_to(receipt_root):
        raise SystemExit(f"missing or unsafe replay archive checksum: {checksum}")
    match = re.fullmatch(
        r"([0-9a-f]{64})  (.+)", checksum.read_text().strip()
    )
    if not match or match.group(2) != archive.relative_to(ROOT).as_posix():
        raise SystemExit(f"invalid replay archive checksum record: {checksum}")
    if hashlib.sha256(archive.read_bytes()).hexdigest() != match.group(1):
        raise SystemExit(f"replay archive checksum mismatch: {archive}")

    recorded: dict[str, str] = {}
    for line in manifest.read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match or match.group(2) in recorded:
            raise SystemExit(f"invalid or duplicate replay manifest entry: {line}")
        recorded[match.group(2)] = match.group(1)

    required: dict[str, str] = {}
    for directory in directories:
        top_level = [
            path for path in directory.iterdir()
            if path.is_file() and not path.is_symlink()
        ]
        receipts = [
            path for path in directory.rglob("receipt.json")
            if path.is_file() and not path.is_symlink()
        ]
        if not top_level and not receipts and any(directory.rglob("*")):
            raise SystemExit(
                f"refusing unrecorded nested replay output: {directory}"
            )
        for path in {*top_level, *receipts}:
            relative = path.relative_to(ROOT).as_posix()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if recorded.get(relative) != digest:
                raise SystemExit(f"unarchived or changed replay result: {path}")
            required[relative] = digest

    decompressed = subprocess.run(
        ["zstd", "-dc", str(archive)], capture_output=True, check=True
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(decompressed), mode="r:") as bundle:
        for relative, digest in required.items():
            try:
                member = bundle.getmember(relative)
            except KeyError as error:
                raise SystemExit(f"replay archive missing {relative}") from error
            if not member.isfile():
                raise SystemExit(f"replay archive member is not a file: {relative}")
            stream = bundle.extractfile(member)
            if stream is None or hashlib.sha256(stream.read()).hexdigest() != digest:
                raise SystemExit(f"replay archive member checksum mismatch: {relative}")
    print(f"replay archive coverage: PASS ({len(required)} result files)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform deletions; default is dry-run",
    )
    parser.add_argument(
        "--compact-referenced",
        action="store_true",
        help="shrink safe referenced gpt-web replay dirs to configured keep files",
    )
    parser.add_argument(
        "--prune-probes",
        action="store_true",
        help="remove rebuildable probe worktrees except configured keep directories",
    )
    parser.add_argument(
        "--prune-exact-replays",
        action="store_true",
        help="remove expanded exact-unit replay worktrees after receipt archival",
    )
    parser.add_argument(
        "--prune-caches",
        action="store_true",
        help="remove only configured repository-local cache/build directories",
    )
    args = parser.parse_args()

    cfg = tomllib.loads(CONFIG.read_text())
    analysis = (ROOT / ".analysis").resolve()
    if not analysis.is_dir():
        print("analysis prune: nothing to do; missing .analysis")
        return 0

    # .analysis/gpt-web retention.
    gpt_root = (ROOT / cfg["gpt_web_root"]).resolve()
    if not gpt_root.is_relative_to(analysis) or gpt_root == analysis:
        raise SystemExit(f"unsafe configured prune root: {gpt_root}")
    protected = set(cfg.get("full_keep_dirs", []))
    extra_keep = {
        str(k): list(v) for k, v in cfg.get("compact_keep_files", {}).items()
    }
    superseded = set(cfg.get("superseded_compact_dirs", []))
    overlap = protected & superseded
    if overlap:
        raise SystemExit(
            f"retention config conflict: protected and superseded: {sorted(overlap)}"
        )
    refs = tracked_reference_map()

    gpt_delete: list[tuple[Path, int]] = []
    gpt_compact: list[tuple[Path, int, set[str], bool]] = []
    if gpt_root.is_dir():
        for path in sorted(gpt_root.iterdir(), key=lambda p: p.name):
            if not path.is_dir() or path.is_symlink():
                continue
            if path.name in protected or path.name in refs:
                continue
            resolved = path.resolve()
            if resolved.parent != gpt_root:
                raise SystemExit(f"refusing non-child prune candidate: {resolved}")
            gpt_delete.append((path, tree_bytes(path)))
        if args.compact_referenced:
            gpt_compact = compact_plan(
                gpt_root, refs, protected, extra_keep, superseded
            )

    # Rebuildable focused probe worktrees.
    probe_delete: list[tuple[Path, int]] = []
    if args.prune_probes:
        probe_root = (ROOT / cfg.get(
            "probe_root", ".analysis/reconstruction/probes"
        )).resolve()
        if not probe_root.is_relative_to(analysis) or probe_root == analysis:
            raise SystemExit(f"unsafe configured probe root: {probe_root}")
        probe_delete = direct_child_delete_plan(
            probe_root, set(cfg.get("probe_keep_dirs", []))
        )

    exact_replay_delete: list[tuple[Path, int]] = []
    if args.prune_exact_replays:
        exact_replay_root = (ROOT / cfg.get(
            "exact_replay_root", ".analysis/reconstruction/exact-unit-replay"
        )).resolve()
        if not exact_replay_root.is_relative_to(analysis) or exact_replay_root == analysis:
            raise SystemExit(f"unsafe configured exact replay root: {exact_replay_root}")
        exact_replay_delete = direct_child_delete_plan(
            exact_replay_root, set(cfg.get("exact_replay_keep_dirs", []))
        )

    # Explicit repository-local caches/build outputs only.
    cache_delete: list[tuple[Path, int]] = []
    if args.prune_caches:
        repo = ROOT.resolve()
        for rel in cfg.get("cache_dirs", []):
            path = (ROOT / rel).resolve()
            if not path.is_relative_to(repo):
                raise SystemExit(f"unsafe configured cache path: {path}")
            if path.is_dir() and not path.is_symlink():
                cache_delete.append((path, tree_bytes(path)))

    gpt_delete_total = sum(size for _, size in gpt_delete)
    gpt_compact_total = sum(size for _, size, _, _ in gpt_compact)
    probe_total = sum(size for _, size in probe_delete)
    exact_replay_total = sum(size for _, size in exact_replay_delete)
    cache_total = sum(size for _, size in cache_delete)
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(
        f"analysis prune [{mode}]: "
        f"gpt-web delete {len(gpt_delete)} dirs / "
        f"{gpt_delete_total / (1024 ** 3):.2f} GiB; "
        f"compact {len(gpt_compact)} dirs / "
        f"{gpt_compact_total / (1024 ** 3):.2f} GiB; "
        f"probes {len(probe_delete)} dirs / {probe_total / (1024 ** 3):.2f} GiB; "
        f"exact replays {len(exact_replay_delete)} dirs / "
        f"{exact_replay_total / (1024 ** 3):.2f} GiB; "
        f"caches {len(cache_delete)} dirs / {cache_total / (1024 ** 3):.2f} GiB"
    )

    for path, size in sorted(gpt_delete, key=lambda item: item[1], reverse=True):
        print(f"  DELETE   {size / (1024 ** 2):8.1f} MiB  {path.relative_to(ROOT)}")
    for path, size, keep, forced in sorted(
        gpt_compact, key=lambda item: item[1], reverse=True
    ):
        kept = ", ".join(sorted(keep))
        label = "SUPERSEDED" if forced else "COMPACT"
        print(
            f"  {label:10s} {size / (1024 ** 2):8.1f} MiB  "
            f"{path.relative_to(ROOT)}  keep=[{kept}]"
        )
    for path, size in sorted(probe_delete, key=lambda item: item[1], reverse=True):
        print(f"  PROBE    {size / (1024 ** 2):8.1f} MiB  {path.relative_to(ROOT)}")
    for path, size in sorted(exact_replay_delete, key=lambda item: item[1], reverse=True):
        print(f"  EXACT    {size / (1024 ** 2):8.1f} MiB  {path.relative_to(ROOT)}")
    for path, size in sorted(cache_delete, key=lambda item: item[1], reverse=True):
        print(f"  CACHE    {size / (1024 ** 2):8.1f} MiB  {path.relative_to(ROOT)}")

    if args.apply:
        replay_dirs = [path for path, _ in (*probe_delete, *exact_replay_delete)]
        if replay_dirs:
            archive = ROOT / cfg["prune_archive"]
            manifest = ROOT / cfg["prune_archive_manifest"]
            verify_replay_archive(replay_dirs, archive, manifest)
        for path, _ in gpt_delete:
            shutil.rmtree(path)
        for path, _, keep, _ in gpt_compact:
            compact_directory(path, keep)
        for path, _ in probe_delete:
            shutil.rmtree(path)
        for path, _ in exact_replay_delete:
            shutil.rmtree(path)
        for path, _ in cache_delete:
            shutil.rmtree(path)
        print(
            f"analysis prune: removed {len(gpt_delete)} gpt-web dirs; "
            f"compacted {len(gpt_compact)} dirs; "
            f"removed {len(probe_delete)} probe dirs, "
            f"{len(exact_replay_delete)} exact replay dirs, and "
            f"{len(cache_delete)} cache dirs"
        )
    else:
        print("analysis prune: no files deleted; rerun with --apply after review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
