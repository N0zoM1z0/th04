#!/usr/bin/env python3
"""Validate and cold-replay artifact-local decoded TH04 function acceptance.

This is deliberately separate from units.csv raw packed-file exactness. The
OP/MAINE backend relinks both artifacts; the ZUN backend links its resident
component. A diagnostic source-present row never gains acceptance from a
successful compile or a normalized/shifted comparison.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib

from lib.pc98 import parse_mz


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "config/th04_decoded_function_acceptance.csv"
HEADER = [
    "boundary_id", "artifact", "segment_identity", "payload_offset", "size",
    "producer_offset", "producer_size", "source", "decoded_state",
    "target_sha256", "replay_backend", "replay_evidence_id", "raw_evidence_id", "notes",
]
ARTIFACTS = {"th04-op", "th04-maine", "th04-zun"}
REQUIRED_PRODUCER_ORACLES = {
    "boundary-ownership", "toolchain-replay", "object-format-integrity",
    "cold-build-determinism", "layout-relocations",
    "cold-aggregate-replay",
}
RESTORED = {
    "th04-op": ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin",
    "th04-maine": ROOT / ".analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin",
}
RESTORED_SHA256 = {
    "th04-op": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
    "th04-maine": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
}
ZUN_PAYLOAD = ROOT / ".analysis/reconstruction/v218-th04-zun-diet/payload.bin"
ZUN_PAYLOAD_SHA256 = "baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e"
ZUN_COMPONENT_OFFSET = 0xB68
ZUN_COMPONENT_SHA256 = "cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110"
BGIMAGE_PRODUCERS = {"th04-op": 0xE428, "th04-maine": 0xD626}
VRAM_PRODUCERS = {"th04-op": 0xDA12, "th04-maine": 0xCC7A}
FRAME_DELAY_PRODUCERS = {"th04-op": 0xDA3B, "th04-maine": 0xCCA3}
PI_PUT_PRODUCERS = {"th04-op": 0xDA50, "th04-maine": 0xCCB8}
PI_LOAD_PRODUCERS = {"th04-op": 0xDAFD, "th04-maine": 0xCD65}
ZUN_LINKED_SOURCES = {
    "src/zun/config/cfg_init.cpp", "src/zun/resident/main.cpp",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def valid_digest(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def rows(path: Path, expected_header: list[str] | None = None) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if expected_header is not None and reader.fieldnames != expected_header:
            raise ValueError(f"{path.name}: invalid column schema")
        result = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in result):
        raise ValueError(f"{path.name}: malformed CSV row")
    return result


def number(value: str, label: str) -> int:
    try:
        result = int(value, 0)
    except ValueError as error:
        raise ValueError(f"{label}: invalid integer {value!r}") from error
    if result < 0:
        raise ValueError(f"{label}: negative extent")
    return result


def validate(
    entries: list[dict[str, str]],
    boundaries: list[dict[str, str]],
    units: list[dict[str, str]],
    evidence: list[dict[str, str]],
    *,
    root: Path = ROOT,
) -> None:
    """Fail closed on false cross-artifact or packed-file acceptance."""

    boundary_by_id = {row["id"]: row for row in boundaries}
    evidence_by_id = {row["id"]: row for row in evidence}
    exact_boundaries = {
        row["id"] for row in boundaries
        if row["artifact"] in ARTIFACTS
        and row["work_queue"] == "reconstruct"
        and row["accepted_state"] == "exact"
    }
    seen: set[str] = set()
    ranges: dict[str, list[tuple[int, int]]] = {artifact: [] for artifact in ARTIFACTS}
    for entry in entries:
        ident = entry["boundary_id"]
        if ident in seen or ident not in boundary_by_id:
            raise ValueError(f"duplicate or unknown decoded boundary: {ident}")
        seen.add(ident)
        boundary = boundary_by_id[ident]
        artifact = entry["artifact"]
        if artifact not in ARTIFACTS or artifact != boundary["artifact"]:
            raise ValueError(f"{ident}: artifact identity mismatch")
        expected_segment = "com-payload" if artifact == "th04-zun" else "mz-load-module"
        start = number(entry["payload_offset"], ident)
        size = number(entry["size"], ident)
        producer_start = number(entry["producer_offset"], ident)
        producer_size = number(entry["producer_size"], ident)
        if (
            not size or not producer_size
            or entry["segment_identity"] != expected_segment
            or boundary["segment_identity"] != expected_segment
            or start != number(boundary["payload_offset"], ident)
            or size != number(boundary["body_size"], ident)
            or size != number(boundary["body_span"], ident)
            or start < producer_start or start + size > producer_start + producer_size
            or boundary["boundary_state"] != "reviewed"
            or boundary["origin"] != "authored"
            or boundary["work_queue"] != "reconstruct"
        ):
            raise ValueError(f"{ident}: physical decoded ownership mismatch")
        if any(start < end and previous < start + size for previous, end in ranges[artifact]):
            raise ValueError(f"{ident}: overlapping decoded function extent")
        ranges[artifact].append((start, start + size))
        source_name = entry["source"]
        source_path = root / source_name
        if (
            not source_name.startswith("src/")
            or ".." in Path(source_name).parts
            or source_path.is_symlink()
            or not source_path.is_file()
            or not source_path.resolve().is_relative_to((root / "src").resolve())
            or source_name != boundary["source_ref"]
        ):
            raise ValueError(f"{ident}: missing or mismatched maintained source")
        owners = [
            unit for unit in units
            if unit["artifact"] == artifact
            and unit["offset"] and number(unit["offset"], ident) == start
            and number(unit["size"], ident) == size
            and unit["source"] == source_name
        ]
        if len(owners) != 1 or owners[0]["origin"] != "authored":
            raise ValueError(f"{ident}: expected one matching authored unit")
        owner = owners[0]
        if (owner["segment"] != f"{expected_segment}/{boundary['map_segment']}"):
            raise ValueError(f"{ident}: unit segment disagrees with physical boundary")
        if owner["file_offset"] or owner["state"] != "source-present":
            raise ValueError(f"{ident}: decoded owner must not claim packed-file exactness")
        digest = entry["target_sha256"]
        if not valid_digest(digest):
            raise ValueError(f"{ident}: invalid target slice SHA-256")
        backend = entry["replay_backend"]
        allowed_backend = ({"zun-resident-link"} if artifact == "th04-zun"
                           else {"op-maine-bgimage-v489", "op-maine-vram-v509", "op-maine-frame-delay-v510",
                                 "op-maine-pi-put-v511", "op-maine-pi-load-v511"})
        if backend not in allowed_backend:
            raise ValueError(f"{ident}: wrong artifact replay backend")
        if artifact == "th04-zun":
            if (source_name not in ZUN_LINKED_SOURCES
                    or producer_start != ZUN_COMPONENT_OFFSET or producer_size != 0x18D8):
                raise ValueError(f"{ident}: ZUN backend does not compile this producer")
        elif backend == "op-maine-bgimage-v489":
            if (source_name != "src/shared/hardware/bgimage.cpp"
                    or producer_start != BGIMAGE_PRODUCERS[artifact] or producer_size != 0xD0):
                raise ValueError(f"{ident}: BGIMAGE backend does not compile this producer")
        elif backend == "op-maine-vram-v509":
            if (source_name != "src/shared/hardware/vram_planes.cpp"
                    or producer_start != VRAM_PRODUCERS[artifact] or producer_size != 0x29):
                raise ValueError(f"{ident}: VRAM backend does not compile this producer")
        elif backend == "op-maine-frame-delay-v510":
            if (source_name != "src/shared/hardware/frame_delay.cpp"
                    or producer_start != FRAME_DELAY_PRODUCERS[artifact] or producer_size != 0x15):
                raise ValueError(f"{ident}: frame-delay backend does not compile this producer")
        elif backend == "op-maine-pi-put-v511":
            if (source_name != "src/shared/formats/pi_put.cpp"
                    or producer_start != PI_PUT_PRODUCERS[artifact] or producer_size != 0xAD):
                raise ValueError(f"{ident}: PI put backend does not compile this producer")
        elif (source_name != "src/shared/formats/pi_load.cpp"
              or producer_start != PI_LOAD_PRODUCERS[artifact] or producer_size != 0x46):
            raise ValueError(f"{ident}: PI load backend does not compile this producer")
        evidence_id = entry["replay_evidence_id"]
        if evidence_id not in evidence_by_id or evidence_by_id[evidence_id]["artifact"] != artifact:
            raise ValueError(f"{ident}: missing artifact-local replay evidence")
        state = entry["decoded_state"]
        if state not in {"decoded-exact", "source-present"}:
            raise ValueError(f"{ident}: invalid decoded acceptance state")
        if state == "decoded-exact":
            if boundary["accepted_state"] != "exact" or evidence_id not in owner["evidence_ids"].split(";"):
                raise ValueError(f"{ident}: decoded exact conflicts with existing ledgers")
            raw_id = entry["raw_evidence_id"]
            raw = evidence_by_id.get(raw_id)
            if (
                raw is None or raw["oracle"] != "raw-bytes"
                or raw["artifact"] != artifact or raw["unit_id"] != owner["id"]
                or raw["result"] != "pass" or raw["evidence_class"] != "binary"
                or not raw["extent_start"] or not raw["extent_size"]
                or number(raw["extent_start"], raw_id) != start
                or number(raw["extent_size"], raw_id) != size
                or raw["input_sha256"] != digest or raw["output_sha256"] != digest
                or not all(raw[field] for field in ("location", "tool", "command", "observed_utc"))
            ):
                raise ValueError(f"{ident}: missing exact function-scoped raw evidence")
            supporting = {
                ev["oracle"] for eid in owner["evidence_ids"].split(";")
                if (ev := evidence_by_id.get(eid)) is not None
                and ev["artifact"] == artifact and ev["result"] == "pass"
                and valid_digest(ev["input_sha256"])
                and valid_digest(ev["output_sha256"])
                and ev["extent_start"] and ev["extent_size"]
                and number(ev["extent_start"], eid) == producer_start
                and number(ev["extent_size"], eid) == producer_size
            }
            if not REQUIRED_PRODUCER_ORACLES.issubset(supporting):
                raise ValueError(f"{ident}: missing producer-scoped exact evidence")
        elif boundary["accepted_state"] == "exact":
            raise ValueError(f"{ident}: exact boundary cannot be diagnostic")
        elif entry["raw_evidence_id"]:
            raise ValueError(f"{ident}: diagnostic row cannot claim raw equality")
    if seen & exact_boundaries != exact_boundaries:
        raise ValueError(f"missing decoded-exact boundary rows: {sorted(exact_boundaries - seen)}")


def compare_extent(
    entry: dict[str, str], target: bytes, candidate: bytes, *, candidate_origin: int = 0
) -> dict[str, object]:
    """Compare the complete physical function slice without normalization."""

    ident = entry["boundary_id"]
    offset = number(entry["payload_offset"], ident)
    size = number(entry["size"], ident)
    local = offset - candidate_origin
    if offset + size > len(target) or local < 0 or local + size > len(candidate):
        raise ValueError(f"{ident}: truncated target or candidate extent")
    expected = target[offset:offset + size]
    actual = candidate[local:local + size]
    if sha(expected) != entry["target_sha256"]:
        raise ValueError(f"{ident}: attested target slice changed")
    differences = [index for index, pair in enumerate(zip(expected, actual)) if pair[0] != pair[1]]
    return {
        "boundary_id": ident,
        "segment_identity": entry["segment_identity"],
        "payload_offset": entry["payload_offset"],
        "size": size,
        "source": entry["source"],
        "source_sha256": sha((ROOT / entry["source"]).read_bytes()),
        "decoded_state": entry["decoded_state"],
        "target_slice_sha256": sha(expected),
        "candidate_slice_sha256": sha(actual),
        "raw_difference_count": len(differences),
        "first_difference_offsets": differences[:16],
    }


def require_exact_zero(results: list[dict[str, object]]) -> None:
    failed = [row["boundary_id"] for row in results
              if row["decoded_state"] == "decoded-exact" and row["raw_difference_count"]]
    if failed:
        raise RuntimeError(f"decoded-exact rows no longer raw-match: {failed}")


def output_directory(requested: Path | None) -> Path:
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    private.mkdir(parents=True, exist_ok=True)
    if requested is None:
        return Path(tempfile.mkdtemp(prefix="decoded-acceptance-", dir=private))
    output = requested.resolve()
    if output.exists() or output.parent != private:
        raise ValueError("output must be a new direct child of .analysis/reconstruction/probes")
    output.mkdir()
    return output


def verified_target(artifact: str) -> tuple[bytes, str, str]:
    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text(encoding="utf-8"))
    info = next(row for row in manifest["artifacts"] if row["id"] == artifact)
    packed = (ROOT / info["private_path"]).read_bytes()
    if len(packed) != info["size"] or sha(packed) != info["sha256"]:
        raise ValueError(f"{artifact}: packed target identity drift")
    if not parse_mz(packed).valid:
        raise ValueError(f"{artifact}: packed target MZ integrity failure")
    if artifact == "th04-zun":
        decoded = ZUN_PAYLOAD.read_bytes()
        expected = ZUN_PAYLOAD_SHA256
    else:
        restored = RESTORED[artifact].read_bytes()
        if sha(restored) != RESTORED_SHA256[artifact]:
            raise ValueError(f"{artifact}: target-derived DIET restore drift")
        mz = parse_mz(restored)
        if not mz.valid:
            raise ValueError(f"{artifact}: invalid restored MZ")
        decoded = mz.program_image
        expected = sha(decoded)
    if sha(decoded) != expected:
        raise ValueError(f"{artifact}: decoded target identity drift")
    return decoded, info["sha256"], expected


def backend(artifact: str, backend_id: str, output: Path) -> tuple[list[bytes], int, dict[str, object]]:
    saved = output / backend_id
    if backend_id == "zun-resident-link":
        command = [sys.executable, "scripts/probes/replay_th04_zun_separate_link.py",
                   "--output-dir", str(saved)]
    elif backend_id == "op-maine-vram-v509":
        command = [sys.executable, "scripts/probes/replay_th04_shared_vram.py",
                   "--output-dir", str(saved)]
    elif backend_id == "op-maine-frame-delay-v510":
        command = [sys.executable, "scripts/probes/replay_th04_shared_frame_delay.py",
                   "--output-dir", str(saved)]
    else:
        snapshot = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a"
        command = [
            sys.executable, "scripts/probes/probe_th04_bgimage_hybrid_v489.py",
            "--current-snapshot",
            "--op-source-dir", str(snapshot / "op/source"),
            "--maine-source-dir", str(snapshot / "maine/source"),
            "--op-target-restored", str(RESTORED["th04-op"]),
            "--maine-target-restored", str(RESTORED["th04-maine"]),
            "--output-dir", str(saved),
        ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=600)
    (output / f"{backend_id}.log").write_text(
        json.dumps(command) + f"\nexit={completed.returncode}\n"
        + completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.returncode:
        raise RuntimeError(f"{artifact}: cold backend failed; see {output / f'{backend_id}.log'}")
    receipt = saved / "receipt.json"
    if not receipt.is_file():
        raise RuntimeError(f"{artifact}: cold backend omitted receipt")
    if backend_id == "zun-resident-link":
        candidate = [(saved / label / "res_huma.com").read_bytes() for label in ("a", "b")]
        if sha(candidate[0]) != sha(candidate[1]):
            raise RuntimeError("ZUN cold component links disagree")
        if len(candidate[0]) != 0x18D8:
            raise RuntimeError("ZUN component size drift")
        target = ZUN_PAYLOAD.read_bytes()[ZUN_COMPONENT_OFFSET:ZUN_COMPONENT_OFFSET + 0x18D8]
        if sha(target) != ZUN_COMPONENT_SHA256:
            raise RuntimeError("ZUN target component identity drift")
        origin = ZUN_COMPONENT_OFFSET
        layout = {"component_size": len(candidate[0]), "component_sha256": sha(candidate[0]),
                  "target_component_sha256": sha(target)}
    else:
        name = "op" if artifact == "th04-op" else "maine"
        target_mz = parse_mz(RESTORED[artifact].read_bytes())
        images = []
        for label in ("a", "b"):
            path = (saved / label / name / "source/bin/th04" / f"{name}.exe")
            images.append(parse_mz(path.read_bytes()))
        if any(not image.valid for image in images):
            raise RuntimeError(f"{artifact}: invalid cold linked MZ")
        target_relocs = [item.linear for item in target_mz.relocations]
        if any([item.linear for item in image.relocations] != target_relocs for image in images):
            raise RuntimeError(f"{artifact}: ordered relocation mismatch")
        candidate = [image.program_image for image in images]
        if candidate[0] != candidate[1]:
            raise RuntimeError(f"{artifact}: cold linked program images disagree")
        origin = 0
        layout = {"ordered_relocations": len(target_relocs),
                  "candidate_program_size": len(candidate[0]),
                  "target_program_size": len(target_mz.program_image)}
    return candidate, origin, {
        "command": command, "receipt_sha256": sha(receipt.read_bytes()), "layout": layout,
    }


def replay(artifact: str, entries: list[dict[str, str]], output: Path) -> dict[str, object]:
    target, packed_sha, decoded_sha = verified_target(artifact)
    selected = [entry for entry in entries if entry["artifact"] == artifact]
    if not selected:
        raise ValueError(f"{artifact}: no decoded acceptance entries")
    source_hashes = {entry["source"]: sha((ROOT / entry["source"]).read_bytes())
                     for entry in selected}
    groups: dict[str, list[dict[str, str]]] = {}
    for entry in selected:
        groups.setdefault(entry["replay_backend"], []).append(entry)
    compared: list[dict[str, object]] = []
    builds: dict[str, dict[str, object]] = {}
    candidates: dict[str, list[str]] = {}
    for backend_id, group in groups.items():
        candidate_rounds, origin, build = backend(artifact, backend_id, output)
        rounds = [
            [compare_extent(entry, target, candidate, candidate_origin=origin) for entry in group]
            for candidate in candidate_rounds
        ]
        if rounds[0] != rounds[1]:
            raise RuntimeError(f"{artifact}/{backend_id}: cold function comparisons disagree")
        require_exact_zero(rounds[0])
        compared.extend(rounds[0])
        builds[backend_id] = build
        candidates[backend_id] = [sha(candidate) for candidate in candidate_rounds]
    if any(sha((ROOT / source).read_bytes()) != digest
           for source, digest in source_hashes.items()):
        raise RuntimeError(f"{artifact}: maintained source changed during cold replay")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": artifact,
        "packed_target_sha256": packed_sha,
        "decoded_target_sha256": decoded_sha,
        "candidate_round_sha256": candidates,
        "backends": builds,
        "functions": compared,
        "limit": "Decoded artifact-local function comparison only; no raw packed-file byte or standalone product acceptance.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", choices=sorted(ARTIFACTS), help="run the cold artifact backend")
    parser.add_argument("--output-dir", type=Path, help="new private receipt directory")
    args = parser.parse_args()
    entries = rows(LEDGER, HEADER)
    validate(
        entries,
        rows(ROOT / "config/th04_function_boundaries.csv"),
        rows(ROOT / "config/units.csv"),
        rows(ROOT / "config/evidence.csv"),
    )
    print(f"decoded function ledger: PASS ({len(entries)} rows; 3 artifacts)")
    if args.artifact:
        output = output_directory(args.output_dir)
        receipt = replay(args.artifact, entries, output)
        print(f"{args.artifact}: {len(receipt['functions'])} slices checked; receipt: {output / 'receipt.json'}")
    elif args.output_dir:
        parser.error("--output-dir requires --artifact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
