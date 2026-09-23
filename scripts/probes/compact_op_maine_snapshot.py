"""Materialize the OP/MAINE replay inputs without cloning all of ReC98.

Every output is an independent writable copy. The retained v489 snapshot is
never hardlinked or symlinked into the worktree: a compiler/linker write must
not be able to mutate an attested baseline through an alias.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil


OBJECT_REF = re.compile(rb"obj\\[A-Za-z0-9_.\\-]+\.obj", re.IGNORECASE)
ROOT_BINARY_SUFFIXES = {".obj", ".lib"}
SOURCE_SUFFIXES = {".h", ".hpp", ".inc", ".cpp", ".c", ".csp", ".inl"}
SKIP_DIRS = {".github", ".tup", "bin", "obj"}


def reject_symlinks(tree: Path) -> None:
    """Keep a copied source tree independent of paths outside the snapshot."""
    if tree.is_symlink():
        raise ValueError(f"snapshot symlink is not a replay input: {tree}")
    for parent, directories, files in os.walk(tree, followlinks=False):
        for name in (*directories, *files):
            path = Path(parent) / name
            if path.is_symlink():
                raise ValueError(f"snapshot symlink is not a replay input: {path}")


def copy_compact_snapshot(snapshot: Path, work: Path, artifact: str) -> dict[str, int]:
    """Copy compile-facing sources and only this artifact's link-input objects.

    The response file is the source of truth for required object paths. The
    compiler probes consume C/C++ sources, headers, and textual include files;
    unrelated listings, maps, executables, assets, assembly sources, other
    games' binaries, and Tup metadata are not copied into each backend round.
    """
    if artifact not in {"op", "maine"}:
        raise ValueError(f"unsupported compact snapshot artifact: {artifact}")
    if not snapshot.is_dir() or snapshot.is_symlink() or work.exists():
        raise ValueError("snapshot must exist and new worktree must not exist")

    response = snapshot / "obj/th04" / f"{artifact}.@l"
    linked_exe = snapshot / "bin/th04" / f"{artifact}.exe"
    linked_map = snapshot / "obj/th04" / f"{artifact}.map"
    if not all(path.is_file() and not path.is_symlink()
               for path in (response, linked_exe, linked_map)):
        raise ValueError("OP/MAINE compact snapshot link scaffold missing")
    response_bytes = response.read_bytes()
    object_names = {
        match.group().decode("ascii").replace("\\", "/")
        for match in OBJECT_REF.finditer(response_bytes)
    }
    if not object_names or not any(name.startswith("obj/th04/") for name in object_names):
        raise ValueError("OP/MAINE link response contains no TH04 objects")

    object_sources = []
    for relative in sorted(object_names):
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or path.parts[0] != "obj":
            raise ValueError(f"unsafe response object path: {relative}")
        source = snapshot / path
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"response object missing: {relative}")
        object_sources.append(source)

    # No selected tree may contain a link to the retained baseline or another
    # path. Check before creating the destination, so a bad input leaves no
    # partial worktree to mistake for a cold replay.
    for entry in snapshot.iterdir():
        if entry.is_symlink():
            raise ValueError(f"unexpected top-level snapshot symlink: {entry}")
        if entry.is_dir() and entry.name not in SKIP_DIRS:
            reject_symlinks(entry)
    reject_symlinks(snapshot / "bin/th04")

    work.mkdir(parents=True)
    source_files = 0
    source_bytes = 0
    for parent, directories, files in os.walk(snapshot, followlinks=False):
        source_dir = Path(parent)
        relative_dir = source_dir.relative_to(snapshot)
        if not relative_dir.parts:
            directories[:] = [name for name in directories if name not in SKIP_DIRS]
        selected = [name for name in files
                    if Path(name).suffix.lower() in SOURCE_SUFFIXES]
        if not selected:
            continue
        destination_dir = work / relative_dir
        destination_dir.mkdir(parents=True, exist_ok=True)
        for name in selected:
            source = source_dir / name
            if source.is_symlink() or not source.is_file():
                raise ValueError(f"source input is not a regular file: {source}")
            shutil.copy2(source, destination_dir / name)
            source_files += 1
            source_bytes += source.stat().st_size

    for entry in snapshot.iterdir():
        if entry.is_file() and entry.suffix.lower() in ROOT_BINARY_SUFFIXES:
            shutil.copy2(entry, work / entry.name)
            source_files += 1
            source_bytes += entry.stat().st_size

    for source in object_sources:
        destination = work / source.relative_to(snapshot)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    for source in (response, linked_map):
        destination = work / source.relative_to(snapshot)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    shutil.copytree(snapshot / "bin/th04", work / "bin/th04", symlinks=True)
    for source in (snapshot / "bin").iterdir():
        if source.is_file() and not source.is_symlink() and source.suffix.lower() in {".lib", ".obj"}:
            shutil.copy2(source, work / "bin" / source.name)

    if (work / "obj/th04" / f"{artifact}.@l").read_bytes() != response_bytes:
        raise RuntimeError("compact snapshot response copy changed")
    return {
        "source_file_count": source_files,
        "source_bytes": source_bytes,
        "linked_object_count": len(object_sources),
        "linked_object_bytes": sum(source.stat().st_size for source in object_sources),
    }
