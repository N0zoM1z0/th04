#!/usr/bin/env python3
"""Cold-replay maintained TH04 MAIN authored units against the pinned target.

The replay starts from the pinned ReC98 commit only as build scaffolding, overlays
repository-maintained natural source, performs two isolated serial cold builds,
and validates each reviewed extent independently. ReC98 source/status is never
accepted as exact evidence by itself.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib
import uuid

from lib.omf import describe_omf
from lib.pc98 import digest_bytes, digest_file, parse_mz

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "_reference" / "ReC98"
MANIFEST = ROOT / "config" / "th04_main_exact_units.toml"
TARGET = ROOT / ".analysis" / "targets" / "th04" / "main.exe"
REC98_COMPAT = ROOT / "compat" / "rec98"


def run_checked(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=cwd, env=env, check=True)


def read_units() -> dict[str, dict[str, str]]:
    with (ROOT / "config" / "units.csv").open(newline="", encoding="utf-8") as stream:
        return {row["id"]: row for row in csv.DictReader(stream)}


def integer(value: str) -> int:
    return int(value, 0)


def map_contribution(map_path: Path, module: str) -> tuple[int, int, str]:
    pattern = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE\s+.*\bM="
        + re.escape(module)
        + r"(?:\s|$)",
        re.IGNORECASE,
    )
    matches: list[tuple[int, int, str]] = []
    for line in map_path.read_text(encoding="cp437", errors="replace").splitlines():
        match = pattern.search(line)
        if match:
            start = int(match.group(1), 16) * 16 + int(match.group(2), 16)
            size = int(match.group(3), 16)
            if size:
                matches.append((start, size, line.strip()))
    if len(matches) != 1:
        raise RuntimeError(f"expected one map contribution for {module}, got {len(matches)}")
    return matches[0]


def overlapping_relocations(image, start: int, size: int) -> list[int]:
    end = start + size
    return [r.linear for r in image.relocations if r.linear < end and r.linear + 2 > start]


def materialize(revision: str, destination: Path) -> None:
    destination.mkdir(parents=True)
    archive = destination.parent / "source.tar"
    run_checked(["git", "archive", "--format=tar", f"--output={archive}", revision], REFERENCE)
    run_checked(["tar", "-xf", archive, "-C", destination], ROOT)


def materialize_rec98_compat(source_root: Path) -> list[dict[str, object]]:
    """Copy and attest the repository-owned ReC98 forwarding layer."""

    if not REC98_COMPAT.is_dir():
        raise FileNotFoundError(REC98_COMPAT)
    destination_root = source_root / "compat" / "rec98"
    receipt: list[dict[str, object]] = []
    for path in sorted(REC98_COMPAT.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"ReC98 compatibility layer contains a symlink: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(REC98_COMPAT)
        destination = destination_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        receipt.append(
            {
                "path": str(relative),
                "size": path.stat().st_size,
                "sha256": digest_file(path),
            }
        )
    if not receipt:
        raise RuntimeError("ReC98 compatibility layer is empty")
    return receipt


def resolve_rec98_forwarders(source: bytes) -> tuple[bytes, list[str]]:
    """Resolve only attested one-line compat/rec98 includes for scaffold matching."""

    used: list[str] = []
    pattern = re.compile(
        rb'(^\s*#include\s+")compat/rec98/([^"\r\n]+)(")', re.MULTILINE
    )

    def replace(match: re.Match[bytes]) -> bytes:
        relative_text = match.group(2).decode("ascii")
        relative = Path(relative_text)
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"invalid ReC98 forwarding path: {relative_text}")
        forwarder = REC98_COMPAT / relative
        expected = f'#include "{relative.as_posix()}"\n'.encode("ascii")
        if (
            not forwarder.is_file()
            or forwarder.is_symlink()
            or forwarder.read_bytes() != expected
        ):
            raise RuntimeError(f"invalid ReC98 forwarding header: {forwarder}")
        used.append(relative.as_posix())
        return match.group(1) + match.group(2) + match.group(3)

    resolved = pattern.sub(replace, source)
    if not used:
        raise RuntimeError("forwarded fragment does not include compat/rec98")
    return resolved, sorted(set(used))


def overlay_sources(source_root: Path, entries: list[dict[str, object]]) -> list[dict[str, object]]:
    overlays: list[dict[str, object]] = []
    for entry in entries:
        repo_source = ROOT / str(entry["repo_source"])
        if not repo_source.is_file():
            raise FileNotFoundError(repo_source)
        mode = str(entry.get("source_mode", "overlay"))
        if mode == "overlay":
            destination = source_root / str(entry["overlay_path"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(repo_source, destination)
            overlays.append({"unit_id": entry["id"], "mode": mode, "repo_source": entry["repo_source"], "source_path": entry["overlay_path"], "sha256": digest_file(repo_source)})
        elif mode in {"fragment", "forwarded-fragment"}:
            destination = source_root / str(entry["patch_path"])
            maintained_fragment = repo_source.read_bytes()
            forwarded_headers: list[str] = []
            if mode == "forwarded-fragment":
                fragment, forwarded_headers = resolve_rec98_forwarders(
                    maintained_fragment
                )
            else:
                fragment = maintained_fragment
            original = destination.read_bytes()
            if original.count(fragment) != 1:
                raise RuntimeError(f"{entry['id']}: maintained fragment must occur exactly once in {entry['patch_path']}")
            offset = original.index(fragment)
            stat = destination.stat()
            patched = original[:offset] + fragment + original[offset + len(fragment):]
            destination.write_bytes(patched)
            os.utime(destination, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            if patched != original:
                raise RuntimeError(f"{entry['id']}: identity fragment unexpectedly changed scaffold bytes")
            overlays.append({"unit_id": entry["id"], "mode": mode, "repo_source": entry["repo_source"], "source_path": entry["patch_path"], "fragment_offset": offset, "fragment_size": len(fragment), "maintained_fragment_size": len(maintained_fragment), "sha256": digest_file(repo_source), "resolved_fragment_sha256": digest_bytes(fragment), "forwarded_headers": forwarded_headers, "scaffold_sha256": digest_bytes(original)})
        elif mode == "replace":
            destination = source_root / str(entry["patch_path"])
            replacement = repo_source.read_bytes()
            original = destination.read_bytes()
            expected_scaffold = str(entry["scaffold_sha256"])
            if digest_bytes(original) != expected_scaffold:
                raise RuntimeError(
                    f"{entry['id']}: scaffold SHA-256 drift in {entry['patch_path']}"
                )
            offset = int(entry["replace_offset"])
            match_size = int(entry["replace_size"])
            if offset < 0 or match_size <= 0 or offset + match_size > len(original):
                raise RuntimeError(f"{entry['id']}: replacement extent escapes scaffold")
            matched = original[offset:offset + match_size]
            expected_match = str(entry["replace_sha256"])
            if digest_bytes(matched) != expected_match:
                raise RuntimeError(f"{entry['id']}: replacement source span SHA-256 mismatch")
            stat = destination.stat()
            patched = original[:offset] + replacement + original[offset + match_size:]
            destination.write_bytes(patched)
            os.utime(destination, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            overlays.append(
                {
                    "unit_id": entry["id"],
                    "mode": mode,
                    "repo_source": entry["repo_source"],
                    "source_path": entry["patch_path"],
                    "replace_offset": offset,
                    "replace_size": match_size,
                    "replace_sha256": expected_match,
                    "replacement_size": len(replacement),
                    "replacement_sha256": digest_file(repo_source),
                    "scaffold_sha256": expected_scaffold,
                    "patched_scaffold_sha256": digest_bytes(patched),
                }
            )
        else:
            raise RuntimeError(f"{entry['id']}: unknown source_mode {mode!r}")
    return overlays


def apply_source_splits(
    source_root: Path,
    splits: list[dict[str, object]],
    selected_ids: set[str],
) -> list[dict[str, object]]:
    """Apply exact source/TU splits that are triggered by selected units.

    Every split removes one checked-in fragment from one pinned scaffold source,
    materializes that exact fragment as an extra translation-unit dependency,
    copies a checked-in wrapper, and inserts the wrapper immediately after a
    unique build-graph anchor.  The source removal must be unique; `suffix`
    mode additionally requires the fragment to end the scaffold file.
    """

    receipts: list[dict[str, object]] = []
    for split in splits:
        triggers = {str(value) for value in split.get("trigger_units", [])}
        if not (triggers & selected_ids):
            continue
        split_id = str(split["id"])
        fragment_path = ROOT / str(split["repo_fragment"])
        wrapper_path = ROOT / str(split["repo_wrapper"])
        if not fragment_path.is_file() or not wrapper_path.is_file():
            raise FileNotFoundError(
                fragment_path if not fragment_path.is_file() else wrapper_path
            )

        scaffold = source_root / str(split["scaffold_path"])
        original = scaffold.read_bytes()
        fragment = fragment_path.read_bytes()
        if original.count(fragment) != 1:
            raise RuntimeError(
                f"{split_id}: split fragment must occur exactly once in "
                f"{split['scaffold_path']}"
            )
        offset = original.index(fragment)
        remove_mode = str(split.get("remove_mode", "unique"))
        if remove_mode == "suffix":
            if offset + len(fragment) != len(original):
                raise RuntimeError(f"{split_id}: split fragment is not the scaffold suffix")
        elif remove_mode != "unique":
            raise RuntimeError(f"{split_id}: unknown remove_mode {remove_mode!r}")
        stat = scaffold.stat()
        truncated = original[:offset] + original[offset + len(fragment):]
        scaffold.write_bytes(truncated)
        os.utime(scaffold, ns=(stat.st_atime_ns, stat.st_mtime_ns))

        fragment_overlay = source_root / str(split["fragment_overlay_path"])
        fragment_overlay.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fragment_path, fragment_overlay)
        wrapper_overlay = source_root / str(split["wrapper_overlay_path"])
        wrapper_overlay.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wrapper_path, wrapper_overlay)

        build_file = source_root / str(split["build_file"])
        build_text = build_file.read_text(encoding="utf-8")
        build_anchor = str(split["build_anchor"])
        build_insert = str(split["build_insert"])
        if build_text.count(build_anchor) != 1:
            raise RuntimeError(
                f"{split_id}: expected one build anchor in {split['build_file']}, "
                f"got {build_text.count(build_anchor)}"
            )
        patched_build = build_text.replace(
            build_anchor, build_anchor + build_insert, 1
        )
        build_file.write_text(patched_build, encoding="utf-8")
        receipts.append(
            {
                "id": split_id,
                "trigger_units": sorted(triggers & selected_ids),
                "scaffold_path": str(split["scaffold_path"]),
                "scaffold_original_sha256": digest_bytes(original),
                "scaffold_truncated_sha256": digest_bytes(truncated),
                "fragment_offset": offset,
                "fragment_size": len(fragment),
                "repo_fragment": str(split["repo_fragment"]),
                "fragment_sha256": digest_file(fragment_path),
                "fragment_overlay_path": str(split["fragment_overlay_path"]),
                "repo_wrapper": str(split["repo_wrapper"]),
                "wrapper_sha256": digest_file(wrapper_path),
                "wrapper_overlay_path": str(split["wrapper_overlay_path"]),
                "build_file": str(split["build_file"]),
                "build_anchor": build_anchor,
                "build_insert": build_insert,
                "build_file_sha256": digest_file(build_file),
            }
        )
    return receipts


def apply_build_inserts(
    source_root: Path,
    inserts: list[dict[str, object]],
    selected_ids: set[str],
) -> list[dict[str, object]]:
    """Materialize checked-in build inputs at one fail-closed build anchor."""

    receipts: list[dict[str, object]] = []
    for entry in inserts:
        triggers = {str(value) for value in entry.get("trigger_units", [])}
        if not (triggers & selected_ids):
            continue
        insert_id = str(entry["id"])
        repo_source = ROOT / str(entry["repo_source"])
        if not repo_source.is_file() or repo_source.is_symlink():
            raise FileNotFoundError(repo_source)
        overlay = source_root / str(entry["overlay_path"])
        overlay.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo_source, overlay)
        build_file = source_root / str(entry["build_file"])
        original = build_file.read_text(encoding="utf-8")
        anchor = str(entry["build_anchor"])
        insertion = str(entry["build_insert"])
        count = original.count(anchor)
        if count != 1:
            raise RuntimeError(
                f"{insert_id}: expected one build anchor in {entry['build_file']}, got {count}"
            )
        if insertion in original:
            raise RuntimeError(f"{insert_id}: build insertion already exists in scaffold")
        patched = original.replace(anchor, anchor + insertion, 1)
        build_file.write_text(patched, encoding="utf-8")
        receipts.append({
            "id": insert_id,
            "trigger_units": sorted(triggers & selected_ids),
            "repo_source": str(entry["repo_source"]),
            "source_sha256": digest_file(repo_source),
            "overlay_path": str(entry["overlay_path"]),
            "build_file": str(entry["build_file"]),
            "build_file_original_sha256": digest_bytes(original.encode("utf-8")),
            "build_file_patched_sha256": digest_file(build_file),
            "build_anchor": anchor,
            "build_insert": insertion,
        })
    return receipts


def build(source: Path, log: Path) -> None:
    prefix = ROOT / ".analysis" / "toolchain" / "wineprefix"
    environment = os.environ.copy()
    environment.update(
        {
            "WINEPREFIX": str(prefix),
            "WINEDEBUG": "-all",
            "MSDOS_PATH": r"C:\TC4\BIN",
        }
    )
    windows_command = (
        r"set PATH=C:\TASM50\BIN;C:\TC4\BIN;%PATH%"
        r"&&set PROCESSOR_ARCHITECTURE=AMD64"
        r"&&set PROCESSOR_ARCHITEW6432=AMD64"
        r"&&build.bat"
    )
    with log.open("wb") as stream:
        subprocess.run(
            ["wine", "cmd", "/d", "/c", windows_command],
            cwd=source,
            env=environment,
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
        )


def inspect_build(source: Path, entries: list[dict[str, str]], ledger: dict[str, dict[str, str]], target_mz):
    candidate_path = source / "bin" / "th04" / "main.exe"
    candidate_mz = parse_mz(candidate_path.read_bytes())
    if not candidate_mz.valid:
        raise RuntimeError("candidate MAIN.EXE failed MZ integrity")
    map_path = source / "obj" / "th04" / "main.map"
    results = {}
    for entry in entries:
        row = ledger[entry["id"]]
        file_start = integer(row["file_offset"])
        size = integer(row["compare_size"])
        program_start = file_start - target_mz.header.header_size
        if program_start < 0:
            raise RuntimeError(f"{entry['id']}: extent is inside MZ header")
        target_slice = target_mz.program_image[program_start : program_start + size]
        candidate_slice = candidate_mz.program_image[program_start : program_start + size]
        if len(target_slice) != size or len(candidate_slice) != size:
            raise RuntimeError(f"{entry['id']}: candidate/target slice is truncated")
        map_start, map_size, map_line = map_contribution(map_path, entry["map_module"])
        map_mode = entry.get("map_mode", "exact")
        if map_mode == "exact":
            map_exact = map_start == program_start and map_size == size
        elif map_mode == "contains":
            map_exact = map_start <= program_start and (program_start + size) <= (map_start + map_size)
        else:
            raise RuntimeError(f"{entry['id']}: unknown map_mode {map_mode!r}")
        obj_path = source / entry["object_path"]
        omf = describe_omf(obj_path.read_bytes())
        target_relocs = overlapping_relocations(target_mz, program_start, size)
        candidate_relocs = overlapping_relocations(candidate_mz, program_start, size)
        results[entry["id"]] = {
            "file_start": file_start,
            "program_start": program_start,
            "size": size,
            "target_slice_sha256": digest_bytes(target_slice),
            "candidate_slice_sha256": digest_bytes(candidate_slice),
            "raw_exact": target_slice == candidate_slice,
            "map_start": map_start,
            "map_size": map_size,
            "map_mode": map_mode,
            "map_exact": map_exact,
            "map_line": map_line,
            "target_overlapping_relocations": target_relocs,
            "candidate_overlapping_relocations": candidate_relocs,
            "relocations_exact": target_relocs == candidate_relocs,
            "object_path": entry["object_path"],
            "object_sha256": omf["sha256"],
            "object_normalized_sha256": omf["dependency_timestamp_normalized_sha256"],
            "object_valid": bool(omf["valid"]),
            "object_module_name": omf["module_name"],
            "object_translators": omf["translator_comments"],
            "object_dependencies": omf["dependency_paths"],
        }
    return candidate_path, results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", action="append", default=[], help="unit id; repeatable")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--list-selected", action="store_true", help="print selected unit ids without building")
    args = parser.parse_args()

    config = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    revision = config["reference_revision"]
    entries = list(config["units"])
    splits = list(config.get("splits", []))
    build_inserts = list(config.get("build_inserts", []))
    if args.unit:
        wanted = set(args.unit)
        entries = [entry for entry in entries if entry["id"] in wanted]
        missing = wanted - {entry["id"] for entry in entries}
        if missing:
            parser.error(f"unknown manifest unit(s): {', '.join(sorted(missing))}")
    else:
        entries = [entry for entry in entries if entry.get("default_enabled", True)]
    if not entries:
        parser.error("no units selected")
    if args.list_selected:
        for entry in entries:
            print(entry["id"])
        return 0
    ledger = read_units()
    for entry in entries:
        if entry["id"] not in ledger:
            raise RuntimeError(f"manifest unit missing from units.csv: {entry['id']}")

    resolved = subprocess.check_output(["git", "rev-parse", revision], cwd=REFERENCE, text=True).strip()
    if resolved != revision:
        raise RuntimeError("pinned ReC98 revision is unavailable")
    if not TARGET.is_file():
        raise FileNotFoundError(TARGET)

    # Identity/execution attestation is always replayed immediately before builds.
    run_checked([sys.executable, "scripts/attest_toolchain.py"], ROOT)
    toolchain_receipt = ROOT / ".analysis" / "toolchain" / "attestation.json"
    run_id = args.run_id or (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    root = ROOT / ".analysis" / "reconstruction" / "exact-unit-replay" / run_id
    if root.exists():
        raise RuntimeError(f"refusing to overwrite replay: {root}")
    target_mz = parse_mz(TARGET.read_bytes())
    if not target_mz.valid:
        raise RuntimeError("pinned target failed MZ integrity")

    build_results = []
    for label in ("a", "b"):
        run_root = root / label
        source = run_root / "source"
        materialize(revision, source)
        compat_headers = materialize_rec98_compat(source)
        overlays = overlay_sources(source, entries)
        selected_ids = {entry["id"] for entry in entries}
        split_receipts = apply_source_splits(source, splits, selected_ids)
        build_insert_receipts = apply_build_inserts(
            source, build_inserts, selected_ids
        )
        log = run_root / "build.log"
        build(source, log)
        candidate_path, units = inspect_build(source, entries, ledger, target_mz)
        build_results.append(
            {
                "label": label,
                "source": str(source.relative_to(ROOT)),
                "rec98_compat": compat_headers,
                "overlays": overlays,
                "source_splits": split_receipts,
                "build_inserts": build_insert_receipts,
                "build_log_sha256": digest_file(log),
                "candidate_main_sha256": digest_file(candidate_path),
                "units": units,
            }
        )

    failures = []
    for entry in entries:
        unit_id = entry["id"]
        a = build_results[0]["units"][unit_id]
        b = build_results[1]["units"][unit_id]
        checks = {
            "raw_exact_a": a["raw_exact"],
            "raw_exact_b": b["raw_exact"],
            "map_exact_a": a["map_exact"],
            "map_exact_b": b["map_exact"],
            "relocations_exact_a": a["relocations_exact"],
            "relocations_exact_b": b["relocations_exact"],
            "object_valid_a": a["object_valid"],
            "object_valid_b": b["object_valid"],
            "slice_deterministic": a["candidate_slice_sha256"] == b["candidate_slice_sha256"],
            "object_normalized_deterministic": a["object_normalized_sha256"] == b["object_normalized_sha256"],
        }
        if not all(checks.values()):
            failures.append({"unit_id": unit_id, "checks": checks})

    receipt = {
        "schema_version": 1,
        "kind": "th04-main-exact-unit-cold-replay",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reference_revision": revision,
        "reference_tree": subprocess.check_output(["git", "rev-parse", f"{revision}^{{tree}}"], cwd=REFERENCE, text=True).strip(),
        "target_sha256": digest_file(TARGET),
        "target_header_size": target_mz.header.header_size,
        "toolchain_attestation_sha256": digest_file(toolchain_receipt),
        "manifest_sha256": digest_file(MANIFEST),
        "selected_units": [entry["id"] for entry in entries],
        "builds": build_results,
        "failures": failures,
        "pass": not failures,
        "policy": "Natural repository source plus two isolated cold builds; exact unit bytes require zero differences and matching map/relocation/OMF surfaces.",
    }
    root.mkdir(parents=True, exist_ok=True)
    receipt_path = root / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"receipt: {receipt_path}")
    for unit_id in receipt["selected_units"]:
        a = build_results[0]["units"][unit_id]
        print(
            f"{unit_id}: raw={a['raw_exact']} map={a['map_exact']} "
            f"relocs={a['relocations_exact']} size={a['size']} "
            f"sha256={a['candidate_slice_sha256']}"
        )
    if failures:
        print(json.dumps(failures, indent=2), file=sys.stderr)
        return 1
    print("exact-unit cold replay: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
