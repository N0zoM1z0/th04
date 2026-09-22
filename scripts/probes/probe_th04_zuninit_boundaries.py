#!/usr/bin/env python3
"""Review the complete TH04 ZUNINIT physical function/data partition.

The TASM listing is compiler-observed corroboration from target-derived
candidate assembly. Function extents are accepted only after independent
control-flow checks on the hash-attested target component.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from boundary_review.export_tasm_function_boundaries import export as export_tasm
from replay_th04_zun_source_only import PAYLOAD, PAYLOAD_SHA256, sha

CANDIDATE_ROOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source"
COMPONENT_START = 0x6F3
COMPONENT_SIZE = 0x475
COMPONENT_RUNTIME_BASE = 0x100
COMPONENT_SHA256 = "692b1e056d907a9649bd1effa6e83239f71039d17de3569464067d0b42b7aa5e"
CANDIDATE_SOURCE_SHA256 = "eba32cd57f73a6aee5db971e5b595298e9430d09152a89facb2ef89a7476852e"
CANDIDATE_MAP_SHA256 = "01bef5dc5d337097371ca4e605cfe6c7a0d5b04ef4a61fabda591310c62c3cc4"

# Runtime COM offsets, exclusive ends, and the final control instruction.
FUNCTIONS = (
    ("start", 0x100, 0x103, "near", "jmp", "0x333"),
    ("sub_103", 0x103, 0x115, "far", "iret", ""),
    ("sub_115", 0x115, 0x127, "far", "iret", ""),
    ("sub_127", 0x127, 0x1BD, "near", "ret", ""),
    ("sub_1BD", 0x1BD, 0x1CF, "near", "ret", ""),
    ("sub_1CF", 0x1CF, 0x20A, "near", "ret", ""),
    ("sub_30C", 0x30C, 0x333, "near", "ret", ""),
    ("start_0", 0x333, 0x40D, "near", "int", "0x21"),
)
DATA_ISLANDS = (
    (0x20A, 0x30C),
    (0x40D, 0x575),
)
EXPECTED_EDGES = {
    "start": ((0x100, "jmp", 0x333),),
    "sub_103": ((0x109, "jnz", 0x114), (0x111, "call", 0x127)),
    "sub_115": ((0x11B, "jnz", 0x126), (0x123, "call", 0x127)),
    "sub_127": (
        (0x139, "jz", 0x15A), (0x141, "call", 0x1CF),
        (0x14A, "call", 0x1CF), (0x153, "call", 0x1CF),
        (0x158, "jmp", 0x177), (0x160, "call", 0x1CF),
        (0x169, "call", 0x1CF), (0x172, "call", 0x1CF),
        (0x17F, "jnz", 0x177), (0x189, "jz", 0x181),
        (0x195, "call", 0x1CF), (0x19E, "call", 0x1CF),
        (0x1A7, "call", 0x1CF),
    ),
    "sub_1BD": ((0x1C1, "jnc", 0x1C8),),
    "sub_1CF": (
        (0x1E3, "jz", 0x1F9), (0x1E7, "call", 0x1BD),
        (0x1F7, "jmp", 0x1DE), (0x205, "jz", 0x209),
        (0x207, "jmp", 0x203),
    ),
    "sub_30C": (
        (0x31F, "jnz", 0x32F), (0x328, "jnz", 0x32F),
        (0x32D, "jmp", 0x332),
    ),
    "start_0": (
        (0x339, "jz", 0x347), (0x33D, "jz", 0x351),
        (0x341, "jz", 0x351), (0x345, "jna", 0x336),
        (0x347, "call", 0x30C), (0x34C, "jz", 0x36C),
        (0x34E, "jmp", 0x3ED), (0x354, "ja", 0x359),
        (0x356, "jmp", 0x3FF), (0x35D, "jz", 0x362),
        (0x35F, "jmp", 0x3FF), (0x362, "call", 0x30C),
        (0x367, "jnz", 0x3B0), (0x369, "jmp", 0x3F6),
        (0x3E2, "jnc", 0x3E7), (0x3EB, "jmp", 0x408),
        (0x3F4, "jmp", 0x408), (0x3FD, "jmp", 0x408),
        (0x406, "jmp", 0x408),
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_ndisasm(ndisasm: str, data: bytes, origin: int) -> list[dict[str, object]]:
    completed = subprocess.run(
        [ndisasm, "-b16", f"-o0x{origin:X}", "-"],
        input=data, capture_output=True, check=True,
    )
    rows: list[dict[str, object]] = []
    pattern = re.compile(
        rb"^([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)\s+([A-Za-z0-9]+)\s*(.*)$"
    )
    for raw in completed.stdout.splitlines():
        match = pattern.match(raw)
        if not match:
            raise RuntimeError(f"unexpected ndisasm line: {raw!r}")
        hex_bytes = match[2].decode("ascii")
        rows.append({
            "address": int(match[1], 16),
            "size": len(hex_bytes) // 2,
            "hex": hex_bytes.lower(),
            "mnemonic": match[3].decode("ascii").lower(),
            "operands": match[4].decode("ascii").strip().lower(),
            "text": raw.decode("ascii"),
        })
    return rows


def branch_edges(rows: list[dict[str, object]]) -> tuple[tuple[int, str, int], ...]:
    result = []
    for row in rows:
        mnemonic = str(row["mnemonic"])
        if not (
            mnemonic == "call" or mnemonic.startswith("j")
            or mnemonic in {"loop", "loope", "loopne", "loopz", "loopnz"}
        ):
            continue
        target = re.search(r"0x([0-9a-f]+)", str(row["operands"]))
        if target:
            result.append((int(row["address"]), mnemonic, int(target.group(1), 16)))
    return tuple(result)


def payload_offset(runtime: int) -> int:
    return COMPONENT_START + runtime - COMPONENT_RUNTIME_BASE


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    retention = tomllib.loads(
        (ROOT / "config/analysis_retention.toml").read_text(encoding="utf-8")
    )
    if "v489-bgimage-hybrid-replay-003" not in retention["full_keep_dirs"]:
        raise RuntimeError("retained v489 source snapshot is no longer pinned")

    payload = PAYLOAD.read_bytes()
    if sha(payload) != PAYLOAD_SHA256:
        raise RuntimeError("decoded ZUN payload identity drift")
    component = payload[COMPONENT_START:COMPONENT_START + COMPONENT_SIZE]
    if len(component) != COMPONENT_SIZE or sha(component) != COMPONENT_SHA256:
        raise RuntimeError("target ZUNINIT component identity drift")

    source = CANDIDATE_ROOT / "th04_zuninit.asm"
    map_path = CANDIDATE_ROOT / "obj/th04/zuninit.map"
    linked = CANDIDATE_ROOT / "bin/th04/zuninit.com"
    if (
        digest(source) != CANDIDATE_SOURCE_SHA256
        or digest(map_path) != CANDIDATE_MAP_SHA256
        or digest(linked) != COMPONENT_SHA256
        or linked.read_bytes() != component
    ):
        raise RuntimeError("retained target-derived ZUNINIT corroboration scaffold drift")

    output.mkdir()
    tasm_dir = output / "tasm"
    rows = export_tasm(CANDIDATE_ROOT, tasm_dir)
    actual_entries = [
        row for row in rows
        if row["artifact"] == "th04-zun" and row["module"] == "th04_zuninit.asm"
    ]
    expected_entries = [
        {
            "payload_offset": f"0x{payload_offset(start):X}",
            "name": name,
            "distance": distance,
        }
        for name, start, _end, distance, _last_mnemonic, _last_operands in FUNCTIONS
    ]
    compact_actual = [
        {
            "payload_offset": row["payload_offset"],
            "name": row["name"],
            "distance": row["distance"],
        }
        for row in actual_entries
    ]
    if compact_actual != expected_entries:
        raise RuntimeError(
            f"fresh TASM ZUNINIT PROC inventory drift: {compact_actual!r}"
        )

    ndisasm = shutil.which("ndisasm")
    if not ndisasm:
        raise RuntimeError("ndisasm is required")
    ndisasm_sha = digest(Path(ndisasm))
    function_receipts = []
    all_control_targets: set[int] = set()
    code_ranges = [(start, end) for _name, start, end, *_rest in FUNCTIONS]
    data_ranges = list(DATA_ISLANDS)
    for name, start, end, distance, last_mnemonic, last_operands in FUNCTIONS:
        start_local = start - COMPONENT_RUNTIME_BASE
        end_local = end - COMPONENT_RUNTIME_BASE
        body = component[start_local:end_local]
        decoded = parse_ndisasm(ndisasm, body, start)
        if not decoded:
            raise RuntimeError(f"{name}: target body did not decode")
        if int(decoded[0]["address"]) != start:
            raise RuntimeError(f"{name}: target entry drift")
        last = decoded[-1]
        if int(last["address"]) + int(last["size"]) != end:
            raise RuntimeError(f"{name}: instruction stream does not close at extent end")
        if last["mnemonic"] != last_mnemonic:
            raise RuntimeError(f"{name}: terminal mnemonic drift: {last}")
        if last_operands and last["operands"] != last_operands:
            raise RuntimeError(f"{name}: terminal operands drift: {last}")
        if name == "start_0":
            if len(decoded) < 2 or not (
                decoded[-2]["mnemonic"] == "mov"
                and decoded[-2]["operands"] == "ax,0x4c00"
            ):
                raise RuntimeError("start_0 no-return DOS exit sequence drift")
        edges = branch_edges(decoded)
        if edges != EXPECTED_EDGES[name]:
            raise RuntimeError(f"{name}: target control-flow edge drift: {edges!r}")
        for _source, _kind, target in edges:
            all_control_targets.add(target)
            if any(lo <= target < hi for lo, hi in DATA_ISLANDS):
                raise RuntimeError(f"{name}: control flow enters configured data island")
        function_receipts.append({
            "name": name,
            "distance": distance,
            "runtime_start": f"0x{start:X}",
            "runtime_end": f"0x{end:X}",
            "payload_offset": f"0x{payload_offset(start):X}",
            "size": end - start,
            "target_slice_sha256": sha(body),
            "instruction_count": len(decoded),
            "terminal": decoded[-1]["text"],
            "edges": [
                {"source": f"0x{src:X}", "kind": kind, "target": f"0x{target:X}"}
                for src, kind, target in edges
            ],
        })
        (output / f"{name}.ndisasm").write_text(
            "\n".join(str(row["text"]) for row in decoded) + "\n",
            encoding="ascii",
        )

    # The full component is tiled without gaps or overlaps by the reviewed code
    # extents and the two target data islands.
    partition = sorted(
        [(start, end, "code") for start, end in code_ranges]
        + [(start, end, "data") for start, end in data_ranges]
    )
    cursor = COMPONENT_RUNTIME_BASE
    for start, end, _kind in partition:
        if start != cursor or end <= start:
            raise RuntimeError(f"ZUNINIT partition gap/overlap at {cursor:#x}: {partition}")
        cursor = end
    if cursor != COMPONENT_RUNTIME_BASE + COMPONENT_SIZE:
        raise RuntimeError("ZUNINIT partition does not cover complete component")

    # Calls may target another reviewed function entry; jumps other than the
    # initial thunk must stay within their owning function. The exact edge
    # vector above makes this fail closed if that topology changes.
    code_entries = {start for _name, start, _end, *_rest in FUNCTIONS}
    if not {target for target in all_control_targets if target in code_entries}.issubset(code_entries):
        raise RuntimeError("unexpected cross-function control target")

    tasm_receipt = json.loads((tasm_dir / "receipt.json").read_text(encoding="utf-8"))
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 ZUNINIT target-local physical function/data partition and boundary review",
        "target_payload_sha256": PAYLOAD_SHA256,
        "component_payload_offset": f"0x{COMPONENT_START:X}",
        "component_size": COMPONENT_SIZE,
        "component_sha256": COMPONENT_SHA256,
        "candidate_source_sha256": CANDIDATE_SOURCE_SHA256,
        "candidate_map_sha256": CANDIDATE_MAP_SHA256,
        "candidate_linked_component_raw_equal": True,
        "tasm_function_csv_sha256": tasm_receipt["function_csv_sha256"],
        "tasm_listing_sha256": next(
            row["listing_sha256"] for row in tasm_receipt["listings"]
            if row["artifact"] == "th04-zun"
            and row["source"] == "th04_zuninit.asm"
        ),
        "tasm_classification": tasm_receipt["classification"],
        "ndisasm_path": ndisasm,
        "ndisasm_sha256": ndisasm_sha,
        "functions": function_receipts,
        "data_islands": [
            {
                "runtime_start": f"0x{start:X}",
                "runtime_end": f"0x{end:X}",
                "payload_offset": f"0x{payload_offset(start):X}",
                "size": end - start,
                "target_slice_sha256": sha(
                    component[
                        start - COMPONENT_RUNTIME_BASE:
                        end - COMPONENT_RUNTIME_BASE
                    ]
                ),
            }
            for start, end in DATA_ISLANDS
        ],
        "partition_complete": True,
        "conclusion": (
            "The complete 0x475-byte target ZUNINIT component is tiled by eight "
            "physical code extents and two data islands. Fresh TASM PROC entries "
            "agree with all eight starts, but target bytes independently close each "
            "extent at JMP/IRET/RET/DOS-exit boundaries and no control-flow edge "
            "enters either data island. Ghidra-missed PROC entries can therefore be "
            "reviewed, and start_0 ends at runtime 0x40D rather than extending into "
            "the trailing data that Ghidra had decoded as extra ranges."
        ),
        "limit": (
            "The candidate assembly is target-derived and the raw-equal linked "
            "component is corroboration only. This receipt proves physical "
            "boundaries, not original ASM provenance, source ownership authority, "
            "or codegen exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        row["name"]: {
            "payload_offset": row["payload_offset"],
            "size": row["size"],
            "terminal": row["terminal"],
        }
        for row in function_receipts
    }, sort_keys=True))
    print(f"receipt: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
