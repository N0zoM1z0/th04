"""Deterministic identities for private toolchain files and directory trees."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Callable, Iterable


class ToolchainError(ValueError):
    """Raised when a configured toolchain surface cannot be attested."""


@dataclass(frozen=True)
class TreeIdentity:
    sha256: str
    file_count: int
    total_size: int
    files: tuple[dict[str, str | int], ...]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def tree_identity(root: Path) -> TreeIdentity:
    """Hash a tree as sorted path, size, and content-digest records.

    The digest framing is ``UTF-8 relative path NUL decimal size NUL SHA-256
    LF``.  Symlinks and non-regular files are rejected so two machines cannot
    silently attest different external content under the same tree identity.
    """

    if root.is_symlink():
        raise ToolchainError(f"symlink is not allowed as attested tree root: {root}")
    if not root.is_dir():
        raise ToolchainError(f"tree is missing or is not a directory: {root}")
    paths = sorted(root.rglob("*"), key=lambda path: path.relative_to(root).as_posix())
    for path in paths:
        if path.is_symlink():
            raise ToolchainError(f"symlink is not allowed in attested tree: {path}")
        if not path.is_dir() and not path.is_file():
            raise ToolchainError(f"non-regular entry in attested tree: {path}")
    return file_set_identity(root, (path for path in paths if path.is_file()))


def file_set_identity(
    root: Path,
    paths: Iterable[Path],
    *,
    digest_function: Callable[[Path], str] = file_sha256,
) -> TreeIdentity:
    """Hash a selected file set using the same stable framing as a full tree."""

    if root.is_symlink():
        raise ToolchainError(f"symlink is not allowed as attested tree root: {root}")
    if not root.is_dir():
        raise ToolchainError(f"tree is missing or is not a directory: {root}")
    selected: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for path in paths:
        try:
            relative_path = path.relative_to(root)
        except ValueError as error:
            raise ToolchainError(f"selected file is outside root: {path}") from error
        if ".." in relative_path.parts:
            raise ToolchainError(f"selected file escapes root: {path}")
        relative = relative_path.as_posix()
        if relative in seen:
            raise ToolchainError(f"duplicate selected file: {relative}")
        seen.add(relative)
        selected.append((relative, path))
    selected.sort(key=lambda item: item[0])
    files: list[dict[str, str | int]] = []
    aggregate = hashlib.sha256()
    total_size = 0
    for relative, path in selected:
        parent = path
        while parent != root:
            if parent.is_symlink():
                raise ToolchainError(f"symlink is not allowed in attested tree: {parent}")
            parent = parent.parent
        if not path.is_file():
            raise ToolchainError(f"selected path is not a regular file: {path}")
        size = path.stat().st_size
        digest = digest_function(path)
        if len(digest) != 64 or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise ToolchainError(f"invalid SHA-256 returned for selected file: {path}")
        aggregate.update(relative.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(str(size).encode("ascii"))
        aggregate.update(b"\0")
        aggregate.update(digest.encode("ascii"))
        aggregate.update(b"\n")
        total_size += size
        files.append({"path": relative, "size": size, "sha256": digest})
    if not files:
        raise ToolchainError(f"attested file set is empty: {root}")
    return TreeIdentity(
        sha256=aggregate.hexdigest(),
        file_count=len(files),
        total_size=total_size,
        files=tuple(files),
    )


def attest_surface(root: Path, config: dict[str, object]) -> dict[str, object]:
    relative = Path(str(config["path"]))
    path = root / relative
    kind = str(config["kind"])
    expected = str(config["sha256"])
    report: dict[str, object] = {
        "id": str(config["id"]),
        "kind": kind,
        "path": relative.as_posix(),
        "required": bool(config.get("required", True)),
        "expected_sha256": expected,
    }
    try:
        if kind == "file":
            if not path.is_file():
                raise ToolchainError(f"file is missing: {path}")
            actual = file_sha256(path)
            report.update({"size": path.stat().st_size, "actual_sha256": actual})
        elif kind == "tree":
            identity = tree_identity(path)
            actual = identity.sha256
            report.update(
                {
                    "file_count": identity.file_count,
                    "total_size": identity.total_size,
                    "actual_sha256": actual,
                    "inventory": list(identity.files),
                }
            )
            expected_count = config.get("file_count")
            if expected_count is not None and identity.file_count != int(expected_count):
                raise ToolchainError(
                    f"{config['id']} has {identity.file_count} files, expected {expected_count}"
                )
        else:
            raise ToolchainError(f"unknown surface kind {kind!r}")
        if actual != expected:
            raise ToolchainError(
                f"{config['id']} SHA-256 mismatch: got {actual}, expected {expected}"
            )
        report["pass"] = True
    except (OSError, ToolchainError) as error:
        report.update({"pass": False, "error": str(error)})
    return report
