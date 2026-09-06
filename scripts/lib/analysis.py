"""Pinned analysis-tool identities and private Ghidra path policy."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import subprocess
import tomllib
import zipfile

from .pc98 import digest_file
from .toolchain import ToolchainError, tree_identity


class AnalysisError(ValueError):
    """Raised when an analysis tool or private path fails closed."""


@dataclass(frozen=True)
class LinkAwareTreeIdentity:
    sha256: str
    file_count: int
    symlink_count: int
    total_size: int


def load_analysis_config(path: Path) -> dict[str, object]:
    with path.open("rb") as stream:
        config = tomllib.load(stream)
    if config.get("schema_version") != 1:
        raise AnalysisError("unsupported analysis-toolchain manifest schema")
    return config


def repository_path(root: Path, configured: object) -> Path:
    """Resolve one manifest path while rejecting lexical or resolved escapes."""

    relative = Path(str(configured))
    if relative.is_absolute() or ".." in relative.parts:
        raise AnalysisError(f"analysis manifest path must be repository-relative: {relative}")
    path = root / relative
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise AnalysisError(f"analysis manifest path resolves outside repository: {relative}") from error
    return path


def default_project_root(root: Path, config: dict[str, object]) -> Path:
    relative = Path(str(config["private_paths"]["project_root"]))
    if relative.is_absolute() or ".." in relative.parts:
        raise AnalysisError("private project path must be a safe relative path")
    return root / relative


def validate_project_root(root: Path, project_root: Path) -> Path:
    """Allow ignored ghidra-project or an external non-dot-prefixed path."""

    resolved = project_root.expanduser().resolve()
    if any(part.startswith(".") and part not in (".", "..") for part in resolved.parts):
        raise AnalysisError(
            "Ghidra rejects project paths containing a dot-prefixed path element"
        )
    allowed_internal = (root / "ghidra-project").resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return resolved
    if resolved != allowed_internal:
        raise AnalysisError(
            "the only allowed in-repository Ghidra project root is ignored ghidra-project"
        )
    return resolved


def link_aware_tree_identity(root: Path) -> LinkAwareTreeIdentity:
    """Hash regular files and safe internal symlink topology.

    JDK distributions legitimately contain relative symlinks.  The framing is
    ``F NUL path NUL size NUL digest LF`` for files and
    ``L NUL path NUL target LF`` for links.  Links escaping the installation
    are rejected.
    """

    if root.is_symlink() or not root.is_dir():
        raise AnalysisError(f"tree root is missing, invalid, or a symlink: {root}")
    root_resolved = root.resolve()
    aggregate = hashlib.sha256()
    file_count = 0
    symlink_count = 0
    total_size = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            target = os.readlink(path)
            try:
                (path.parent / target).resolve().relative_to(root_resolved)
            except ValueError as error:
                raise AnalysisError(f"symlink escapes attested tree: {path} -> {target}") from error
            aggregate.update(b"L\0")
            aggregate.update(relative.encode("utf-8"))
            aggregate.update(b"\0")
            aggregate.update(target.encode("utf-8"))
            aggregate.update(b"\n")
            symlink_count += 1
        elif path.is_file():
            size = path.stat().st_size
            aggregate.update(b"F\0")
            aggregate.update(relative.encode("utf-8"))
            aggregate.update(b"\0")
            aggregate.update(str(size).encode("ascii"))
            aggregate.update(b"\0")
            aggregate.update(digest_file(path).encode("ascii"))
            aggregate.update(b"\n")
            file_count += 1
            total_size += size
        elif not path.is_dir():
            raise AnalysisError(f"unsupported entry in attested tree: {path}")
    if not file_count:
        raise AnalysisError(f"attested tree contains no regular files: {root}")
    return LinkAwareTreeIdentity(
        sha256=aggregate.hexdigest(),
        file_count=file_count,
        symlink_count=symlink_count,
        total_size=total_size,
    )


def _file_check(
    path: Path, expected_size: object | None, expected_sha256: object
) -> dict[str, object]:
    report: dict[str, object] = {
        "path": str(path),
        "expected_sha256": str(expected_sha256),
    }
    if expected_size is not None:
        report["expected_size"] = int(expected_size)
    try:
        actual_size = path.stat().st_size
        actual_sha256 = digest_file(path)
        report.update({"size": actual_size, "sha256": actual_sha256})
        report["pass"] = actual_sha256 == str(expected_sha256) and (
            expected_size is None or actual_size == int(expected_size)
        )
    except OSError as error:
        report.update({"pass": False, "error": str(error)})
    return report


def attest_analysis_install(root: Path, config: dict[str, object]) -> dict[str, object]:
    """Return independent acquisition, installed-tree, source, and execution checks."""

    ghidra = config["ghidra"]
    jdk = config["temurin_jdk"]
    checks: dict[str, object] = {}
    ghidra_archive = repository_path(root, ghidra["archive_path"])
    jdk_archive = repository_path(root, jdk["archive_path"])
    ghidra_home = repository_path(root, ghidra["install_path"])
    jdk_home = repository_path(root, jdk["install_path"])
    for name, item, version_home in (
        ("ghidra_stable_link", ghidra, ghidra_home),
        ("jdk_stable_link", jdk, jdk_home),
    ):
        relative = Path(str(item["stable_path"]))
        link = root / relative
        try:
            target = os.readlink(link)
            checks[name] = {
                "pass": link.is_symlink()
                and target == version_home.name
                and link.resolve() == version_home.resolve(),
                "path": relative.as_posix(),
                "target": target,
                "expected_target": version_home.name,
            }
        except OSError as error:
            checks[name] = {"pass": False, "path": relative.as_posix(), "error": str(error)}
    checks["ghidra_archive"] = _file_check(
        ghidra_archive, ghidra["archive_size"], ghidra["archive_sha256"]
    )
    checks["jdk_archive"] = _file_check(
        jdk_archive, jdk["archive_size"], jdk["archive_sha256"]
    )

    try:
        identity = tree_identity(ghidra_home)
        checks["ghidra_tree"] = {
            "pass": identity.sha256 == ghidra["tree_sha256"]
            and identity.file_count == int(ghidra["tree_file_count"])
            and identity.total_size == int(ghidra["tree_total_size"]),
            "path": str(ghidra_home),
            "sha256": identity.sha256,
            "file_count": identity.file_count,
            "total_size": identity.total_size,
        }
    except (OSError, ToolchainError) as error:
        checks["ghidra_tree"] = {"pass": False, "error": str(error)}

    try:
        identity = link_aware_tree_identity(jdk_home)
        checks["jdk_tree"] = {
            "pass": identity.sha256 == jdk["tree_sha256"]
            and identity.file_count == int(jdk["tree_file_count"])
            and identity.symlink_count == int(jdk["tree_symlink_count"])
            and identity.total_size == int(jdk["tree_total_size"]),
            "path": str(jdk_home),
            "sha256": identity.sha256,
            "file_count": identity.file_count,
            "symlink_count": identity.symlink_count,
            "total_size": identity.total_size,
        }
    except (OSError, AnalysisError) as error:
        checks["jdk_tree"] = {"pass": False, "error": str(error)}

    installed_files = {
        "ghidra_properties": (
            ghidra_home / "Ghidra" / "application.properties",
            ghidra["application_properties_sha256"],
        ),
        "analyze_headless": (
            ghidra_home / "support" / "analyzeHeadless",
            ghidra["analyze_headless_sha256"],
        ),
        "base_sources": (
            ghidra_home / "Ghidra" / "Features" / "Base" / "lib" / "Base-src.zip",
            ghidra["base_sources_sha256"],
        ),
        "java": (jdk_home / "bin" / "java", jdk["java_sha256"]),
        "jdk_modules": (jdk_home / "lib" / "modules", jdk["modules_sha256"]),
        "jdk_release": (jdk_home / "release", jdk["release_sha256"]),
    }
    for name, (path, expected) in installed_files.items():
        checks[name] = _file_check(path, None, expected)

    try:
        with zipfile.ZipFile(installed_files["base_sources"][0]) as source_zip:
            source = source_zip.read(str(config["mz_loader"]["source_member"]))
        source_sha256 = hashlib.sha256(source).hexdigest()
        checks["mz_loader_source"] = {
            "pass": source_sha256 == ghidra["mz_loader_source_sha256"],
            "sha256": source_sha256,
            "member": config["mz_loader"]["source_member"],
        }
    except (KeyError, OSError, zipfile.BadZipFile) as error:
        checks["mz_loader_source"] = {"pass": False, "error": str(error)}

    identity_pass = all(bool(item.get("pass")) for item in checks.values())
    executions: dict[str, object] = {}
    commands = {
        "java_banner": [str(jdk_home / "bin" / "java"), "-version"],
        "headless_usage": [str(ghidra_home / "support" / "analyzeHeadless")],
    }
    expectations = {
        "java_banner": str(jdk["banner_substring"]),
        "headless_usage": "Headless Analyzer Usage",
    }
    if not identity_pass:
        executions["identity_gate"] = {
            "pass": False,
            "skipped": True,
            "reason": "static identity attestation failed; Java and Ghidra execution is forbidden",
        }
    else:
        environment = os.environ.copy()
        environment["JAVA_HOME"] = str(jdk_home)
        for name, command in commands.items():
            try:
                completed = subprocess.run(
                    command,
                    cwd=root,
                    env=environment,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    errors="replace",
                    timeout=60,
                )
                output = completed.stdout.replace("\r", "")
                executions[name] = {
                    "pass": expectations[name] in output,
                    "command": command,
                    "returncode": completed.returncode,
                    "expected_substring": expectations[name],
                    "output": output,
                }
            except (OSError, subprocess.SubprocessError) as error:
                executions[name] = {"pass": False, "error": str(error), "command": command}
    ready = identity_pass and all(bool(item.get("pass")) for item in executions.values())
    return {
        "ready": ready,
        "checks": checks,
        "executions": executions,
        "ghidra_home": str(ghidra_home),
        "jdk_home": str(jdk_home),
    }
