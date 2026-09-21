#!/usr/bin/env python3
"""Test whether historical MASTER.LIB BGM BSS explains the v228 restored MZ tail.

The v228 DIET -RA views add zero bytes through exactly the current `_snd_load_fn`
address in both OP and MAINE.  In the maintained topology that address is the
end of `libs/master.lib/bgm[bss].asm`.  This probe extracts the independent
historical `b_data` member from the pinned MASTER.LIB and inspects its OMF
segment/data records.  It never changes product source or executable bytes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_master_bgm_archive_order import (  # noqa: E402
    ARCHIVE,
    ARCHIVE_SHA,
    RUNNER,
    RUNNER_SHA,
    TLIB,
    TLIB_SHA,
    run_tlib,
)

BDATA_SHA256 = "e85c6d60229b3137b3c9c32228e3744577c74fd28e36f53712018a2d9007e688"
BDATA_SIZE = 425
EXPECTED_BDATA = {
    "_TEXT": {"length": 0x0000, "ledata_bytes": 0},
    "_DATA": {"length": 0x011C, "ledata_bytes": 0x00B0},
    "_BSS": {"length": 0x00C6, "ledata_bytes": 0},
}
EXPECTED_BSS_PUBLICS = {
    "timerorg": 0x0000,
    "part": 0x0004,
    "_bgm_part": 0x0004,
    "esound": 0x0046,
    "_bgm_esound": 0x0046,
}
EXPECTED_INPUTS = {
    "th04-op": {
        "candidate_sha256": "78468a2ae389ba9c97fb7b391355e4eda2cb750f84f3cc4abf3e34802bceafbd",
        "map_sha256": "cd2e0a35b1d1262dca398db0302ab68243179cf18edfac2e1ec0810acf2ef334",
        "target_restored_sha256": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
        "extra_zero_bytes": 0xC9C,
        "candidate_minalloc": 612,
        "target_restored_minalloc": 410,
        "timerorg_linear": 0x1197A,
        "snd_load_fn_linear": 0x11A40,
    },
    "th04-maine": {
        "candidate_sha256": "9b14cad4fc3bbd079890cd15d64de03d3c7159fb2b4ae38dab111bdfc8a0df60",
        "map_sha256": "1dd895faa6c7fbfc537c2d56a95ff5ea693aa923b7f5701bb922f170dbfae4e0",
        "target_restored_sha256": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
        "extra_zero_bytes": 0xC94,
        "candidate_minalloc": 817,
        "target_restored_minalloc": 615,
        "timerorg_linear": 0x0FF9C,
        "snd_load_fn_linear": 0x10062,
    },
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def omf_index(data: bytes, pos: int) -> tuple[int, int]:
    first = data[pos]
    if first < 0x80:
        return first, pos + 1
    return ((first & 0x7F) << 8) | data[pos + 1], pos + 2


def parse_names(records: tuple) -> list[str]:
    names = [""]
    for record in records:
        if record.record_type != 0x96:
            continue
        pos = 0
        while pos < len(record.data):
            length = record.data[pos]
            names.append(record.data[pos + 1 : pos + 1 + length].decode("latin-1"))
            pos += length + 1
    return names


def segment_table(records: tuple) -> list[dict[str, object]]:
    names = parse_names(records)
    segments = []
    for record in records:
        if record.record_type != 0x98:
            continue
        data = record.data
        align = data[0] >> 5
        pos = 1
        if align == 0:
            pos += 3
        length = int.from_bytes(data[pos : pos + 2], "little")
        pos += 2
        name_index, pos = omf_index(data, pos)
        class_index, pos = omf_index(data, pos)
        overlay_index, pos = omf_index(data, pos)
        segments.append({
            "index": len(segments) + 1,
            "name": names[name_index],
            "class": names[class_index],
            "overlay": names[overlay_index],
            "length": length,
        })
    return segments


def data_records(records: tuple, segments: list[dict[str, object]]) -> dict[str, list[dict[str, int]]]:
    result = {str(segment["name"]): [] for segment in segments}
    for record in records:
        if record.record_type not in {0xA0, 0xA2}:
            continue
        segment_index, pos = omf_index(record.data, 0)
        offset = int.from_bytes(record.data[pos : pos + 2], "little")
        payload = record.data[pos + 2 :]
        name = str(segments[segment_index - 1]["name"])
        result[name].append({
            "record_type": record.record_type,
            "offset": offset,
            "encoded_payload_bytes": len(payload),
        })
    return result


def pubdefs(records: tuple, segments: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for record in records:
        if record.record_type != 0x90:
            continue
        data = record.data
        group_index, pos = omf_index(data, 0)
        segment_index, pos = omf_index(data, pos)
        if segment_index == 0:
            pos += 2
        while pos < len(data):
            length = data[pos]
            pos += 1
            name = data[pos : pos + length].decode("latin-1")
            pos += length
            offset = int.from_bytes(data[pos : pos + 2], "little")
            pos += 2
            type_index, pos = omf_index(data, pos)
            result[name] = {
                "group_index": group_index,
                "segment_index": segment_index,
                "segment": str(segments[segment_index - 1]["name"]) if segment_index else None,
                "offset": offset,
                "type_index": type_index,
            }
    return result


def map_public_linear(map_bytes: bytes, symbol: str) -> int:
    text = map_bytes.decode("cp437", errors="replace")
    pattern = re.compile(rf"^\s*([0-9A-F]{{4}}):([0-9A-F]{{4}})\s+(?:idle\s+)?{re.escape(symbol)}\s*$", re.M)
    values = {int(seg, 16) * 16 + int(off, 16) for seg, off in pattern.findall(text)}
    if len(values) != 1:
        raise ValueError(f"MAP public {symbol}: expected one address, got {sorted(values)}")
    return next(iter(values))


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="master-bgm-bss-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def inspect_artifact(artifact: str, candidate_path: Path, map_path: Path, target_restored_path: Path) -> dict[str, object]:
    expected = EXPECTED_INPUTS[artifact]
    candidate_bytes = candidate_path.read_bytes()
    map_bytes = map_path.read_bytes()
    restored_bytes = target_restored_path.read_bytes()
    identities = {
        "candidate_sha256": sha_bytes(candidate_bytes),
        "map_sha256": sha_bytes(map_bytes),
        "target_restored_sha256": sha_bytes(restored_bytes),
    }
    for key, value in identities.items():
        if value != expected[key]:
            raise ValueError(f"{artifact}: {key} drift: {value}")
    candidate = parse_mz(candidate_bytes)
    restored = parse_mz(restored_bytes)
    if not candidate.valid or not restored.valid:
        raise ValueError(f"{artifact}: invalid MZ")
    if candidate.header.header_size != restored.header.header_size:
        raise ValueError(f"{artifact}: header-size drift")
    extra = len(restored_bytes) - len(candidate_bytes)
    if extra != expected["extra_zero_bytes"] or set(restored_bytes[len(candidate_bytes):]) - {0}:
        raise ValueError(f"{artifact}: restored zero-tail drift")
    if candidate.header.minimum_extra_allocation != expected["candidate_minalloc"]:
        raise ValueError(f"{artifact}: candidate minalloc drift")
    if restored.header.minimum_extra_allocation != expected["target_restored_minalloc"]:
        raise ValueError(f"{artifact}: target-restored minalloc drift")
    timerorg = map_public_linear(map_bytes, "timerorg")
    snd_load_fn = map_public_linear(map_bytes, "_snd_load_fn")
    if timerorg != expected["timerorg_linear"] or snd_load_fn != expected["snd_load_fn_linear"]:
        raise ValueError(f"{artifact}: MAP boundary drift")
    restored_program_size = len(restored_bytes) - restored.header.header_size
    candidate_program_size = len(candidate_bytes) - candidate.header.header_size
    if restored_program_size != snd_load_fn:
        raise ValueError(f"{artifact}: restored EOF no longer equals _snd_load_fn")
    if snd_load_fn - timerorg != 0xC6:
        raise ValueError(f"{artifact}: BGM BSS public span no longer 0xC6")
    return {
        **identities,
        "candidate_file_size": len(candidate_bytes),
        "target_restored_file_size": len(restored_bytes),
        "candidate_program_size": candidate_program_size,
        "target_restored_program_size": restored_program_size,
        "extra_zero_bytes": extra,
        "candidate_minalloc": candidate.header.minimum_extra_allocation,
        "target_restored_minalloc": restored.header.minimum_extra_allocation,
        "minalloc_delta_paragraphs": candidate.header.minimum_extra_allocation - restored.header.minimum_extra_allocation,
        "timerorg_linear": timerorg,
        "snd_load_fn_linear": snd_load_fn,
        "timerorg_to_snd_load_fn": snd_load_fn - timerorg,
        "target_restored_eof_equals_snd_load_fn": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for prefix in ("op", "maine"):
        parser.add_argument(f"--{prefix}-candidate", type=Path, required=True)
        parser.add_argument(f"--{prefix}-map", type=Path, required=True)
        parser.add_argument(f"--{prefix}-target-restored", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    out = output_dir(args.output_dir)

    for path, expected in ((ARCHIVE, ARCHIVE_SHA), (RUNNER, RUNNER_SHA), (TLIB, TLIB_SHA)):
        if not path.is_file() or sha_path(path) != expected:
            raise ValueError(f"identity drift: {path}")

    # Extract only into private scratch; the archive itself remains untouched.
    archive_copy = out / "masters.lib"
    archive_copy.write_bytes(ARCHIVE.read_bytes())
    rsp = out / "BD.RSP"
    rsp.write_text("*b_data\n")
    done = run_tlib(out, "masters.lib", f"@{rsp.name}")
    (out / "extract-b_data.log").write_text(done.stdout + done.stderr)
    obj = out / "b_data.OBJ"
    if done.returncode or not obj.is_file():
        raise RuntimeError("TLIB b_data extraction failed")
    if obj.stat().st_size != BDATA_SIZE or sha_path(obj) != BDATA_SHA256:
        raise ValueError("historical b_data object identity drift")

    records = parse_omf(obj.read_bytes())
    segments = segment_table(records)
    by_name = {str(segment["name"]): segment for segment in segments}
    records_by_segment = data_records(records, segments)
    publics = pubdefs(records, segments)
    summary: dict[str, dict[str, int]] = {}
    for name, expected in EXPECTED_BDATA.items():
        if name not in by_name:
            raise ValueError(f"b_data missing segment {name}")
        ledata_bytes = sum(
            row["encoded_payload_bytes"]
            for row in records_by_segment[name]
            if row["record_type"] == 0xA0
        )
        summary[name] = {
            "length": int(by_name[name]["length"]),
            "ledata_bytes": ledata_bytes,
            "ledata_records": sum(row["record_type"] == 0xA0 for row in records_by_segment[name]),
            "lidata_records": sum(row["record_type"] == 0xA2 for row in records_by_segment[name]),
        }
        if summary[name]["length"] != expected["length"] or summary[name]["ledata_bytes"] != expected["ledata_bytes"]:
            raise ValueError(f"b_data {name} segment drift: {summary[name]}")
    if summary["_BSS"]["ledata_records"] or summary["_BSS"]["lidata_records"]:
        raise ValueError("historical b_data unexpectedly materializes _BSS")
    bss_publics = {}
    for name, offset in EXPECTED_BSS_PUBLICS.items():
        row = publics.get(name)
        if not row or row["segment"] != "_BSS" or row["offset"] != offset:
            raise ValueError(f"historical b_data public drift: {name}: {row}")
        bss_publics[name] = row

    artifacts = {
        "th04-op": inspect_artifact("th04-op", args.op_candidate.resolve(), args.op_map.resolve(), args.op_target_restored.resolve()),
        "th04-maine": inspect_artifact("th04-maine", args.maine_candidate.resolve(), args.maine_map.resolve(), args.maine_target_restored.resolve()),
    }
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "historical MASTER.LIB b_data BSS versus v228 target-derived restore tail; negative provenance/routing evidence only",
        "archive_sha256": ARCHIVE_SHA,
        "tlib_sha256": TLIB_SHA,
        "historical_b_data": {
            "size": BDATA_SIZE,
            "sha256": BDATA_SHA256,
            "segments": summary,
            "bss_publics": bss_publics,
        },
        "artifacts": artifacts,
        "conclusion": (
            "In both current OP and MAINE candidates the v228 DIET-restored program image ends exactly at _snd_load_fn, 0xC6 bytes after timerorg, i.e. exactly after the BGM BSS public span. However, the independent historical MASTER.LIB b_data member defines that same 0xC6 _BSS span with timerorg/part/esound at matching offsets and contains no _BSS LEDATA or LIDATA. Historical b_data therefore gives no support for materializing the restored zero tail as authored initialized BSS."
        ),
        "limit": (
            "This does not prove the original pre-DIET TH04 MZ length or minalloc. DIET -RA produces a target-derived repackable preimage, not an independently observed historical TLINK file. The result is evidence against treating the v228 zero tail as a source requirement, not proof that every equivalent preimage must omit it."
        ),
    }
    rp = out / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha_path(rp),
        "historical_b_data_sha256": BDATA_SHA256,
        "historical_bss_length": summary["_BSS"]["length"],
        "historical_bss_data_records": summary["_BSS"]["ledata_records"] + summary["_BSS"]["lidata_records"],
        "op_restored_eof": artifacts["th04-op"]["target_restored_program_size"],
        "maine_restored_eof": artifacts["th04-maine"]["target_restored_program_size"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
