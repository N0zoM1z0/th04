#!/usr/bin/env python3
"""Fast repository checks using Python 3.11 and Git; no private inputs required."""

from __future__ import annotations

import argparse
import ast
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIRS = {".analysis", ".tools", "ghidra-project", "_reference"}
PRIVATE_SUFFIXES = {
    ".exe", ".com", ".dll", ".obj", ".o", ".lib", ".a", ".pdb",
    ".hdi", ".hdd", ".fdi", ".img", ".iso", ".idb", ".i64", ".gpr",
    ".zip", ".7z", ".rar", ".tar", ".gz", ".zst",
}


def git(*args: str) -> list[str]:
    return subprocess.check_output(["git", *args], cwd=ROOT).decode().split("\0")


def check_file(name: str) -> None:
    path = ROOT / name
    if not path.exists() and not path.is_symlink():
        return
    if PRIVATE_DIRS.intersection(path.relative_to(ROOT).parts) or path.suffix.lower() in PRIVATE_SUFFIXES:
        raise ValueError(f"{name}: private input or generated binary must not be committed")
    if not path.is_file() or path.is_symlink():
        return
    with path.open("rb") as stream:
        magic = stream.read(4)
    if magic[:2] == b"MZ" or magic in {b"\x7fELF", b"PK\x03\x04"}:
        raise ValueError(f"{name}: executable or archive content must not be committed")
    suffix = path.suffix.lower()
    if suffix == ".py":
        ast.parse(path.read_text(encoding="utf-8"), filename=name)
    elif suffix == ".json":
        json.loads(path.read_text(encoding="utf-8"))
    elif suffix == ".toml":
        tomllib.loads(path.read_text(encoding="utf-8"))
    elif suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as stream:
            rows = csv.reader(stream, strict=True)
            header = next(rows)
            if not header or len(set(header)) != len(header):
                raise ValueError(f"{name}: empty or duplicate CSV header")
            for row in rows:
                if len(row) != len(header):
                    raise ValueError(f"{name}:{rows.line_num}: CSV column count mismatch")
    elif suffix == ".sh":
        subprocess.run(["bash", "-n", str(path)], check=True)


def check_build_sources() -> None:
    for path in sorted((ROOT / "config").glob("native_*_sources.toml")):
        pending = [tomllib.loads(path.read_text(encoding="utf-8"))]
        while pending:
            value = pending.pop()
            if isinstance(value, dict):
                pending.extend(value.values())
            elif isinstance(value, list):
                pending.extend(value)
            elif isinstance(value, str) and value.startswith(("src/", "compat/rec98/")):
                if not (ROOT / value).is_file():
                    raise ValueError(f"{path.relative_to(ROOT)}: missing source {value}")
    cmake = ROOT / "port64/CMakeLists.txt"
    if cmake.is_file():
        text = re.sub(r"#[^\n]*", "", cmake.read_text(encoding="utf-8"))
        for name in re.findall(r'(?<![\w/$])([\w./+-]+\.(?:cpp|c|cc|cxx))(?=[\s)"])', text):
            if not (cmake.parent / name).is_file():
                raise ValueError(f"port64/CMakeLists.txt: missing source {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.environ.get("CI_BASE_REF"),
                        help="also check whitespace over the complete change from this commit")
    args = parser.parse_args(argv)
    try:
        # Inspect the complete current tree, including staged and untracked inputs.
        # Clean checkouts and changes from earlier PR commits are checked too.
        names = set(git("ls-files", "-z", "--cached", "--others", "--exclude-standard")) - {""}
        for name in sorted(names):
            check_file(name)
        check_build_sources()
        for script in ("validate_tracking.py", "boundary_review/validate_function_boundary_ledger.py",
                       "decoded_function_acceptance.py"):
            subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=True)
        base = args.base if args.base and set(args.base) != {"0"} else "HEAD"
        subprocess.run(["git", "diff", "--check", base], cwd=ROOT, check=True)
    except (OSError, ValueError, SyntaxError, StopIteration, csv.Error, subprocess.CalledProcessError) as error:
        print(f"CI: FAIL: {error}", file=sys.stderr)
        return 1
    print(f"CI: PASS ({len(names)} files; syntax, ledgers, build sources, private files, whitespace)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
