#!/usr/bin/env python3
"""Test whether DIET 1.45f preserves arbitrary MZ relocation-table order.

The controls modify only relocation-table entry order inside ignored private MZ
copies. No relocation site is added/removed and no product/source file is
modified. Each control is packed with the pinned TH04 DIET options and then
restored with `DIET -RA`; byte-exact roundtrip demonstrates whether the packer
canonicalizes or preserves input relocation order.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.pc98 import parse_mz  # noqa: E402
from replay_diet145f import check_toolchain, run_once  # noqa: E402
from roundtrip_diet_target import run_guest  # noqa: E402

EXPECTED = {
    "th04-op": {
        "name": "OP.EXE",
        "candidate_sha256": "78468a2ae389ba9c97fb7b391355e4eda2cb750f84f3cc4abf3e34802bceafbd",
        "target_restored_sha256": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
        "relocations": 804,
        "variant_input_sha256": {
            "baseline": "78468a2ae389ba9c97fb7b391355e4eda2cb750f84f3cc4abf3e34802bceafbd",
            "rotate1": "10e1cc1236c1b7ca5fa73dc7f77a3fce5827b69b4895741b607138602e4a9087",
            "reverse": "220de5ea8c9c02baf725be432dd6bf6d834d05a06b29376dd1821b134d33cd0c",
            "swap01": "ee6eb077ee60fc8d614a49e0f8b4c04071a01336de9cfeefdcbb4037637d05f8",
            "target_order": "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274",
        },
        "packed_size": {
            "baseline": 42256,
            "rotate1": 42255,
            "reverse": 42258,
            "swap01": 42257,
            "target_order": 42242,
        },
        "baseline_packed_sha256": "901cd032a87d1a3c96b64792c903d52d970ce33ac04d4d839b5e60b51a7282eb",
        "target_order_packed_sha256": "0f0b8b7bc1a56042beeb50540757c69b18df76b3edc429423120425aa99f96bb",
    },
    "th04-maine": {
        "name": "MAINE.EXE",
        "candidate_sha256": "9b14cad4fc3bbd079890cd15d64de03d3c7159fb2b4ae38dab111bdfc8a0df60",
        "target_restored_sha256": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
        "relocations": 559,
        "variant_input_sha256": {
            "baseline": "9b14cad4fc3bbd079890cd15d64de03d3c7159fb2b4ae38dab111bdfc8a0df60",
            "rotate1": "1de1bea223e27c9dae92c193f434c9fdcb05b1a025fb0651349d76767190b269",
            "reverse": "a659cf180da0e1e20fc8ddeaef889c58507daee170910ec5c489a099d3417ab4",
            "swap01": "4daace7860155329f13d386ae1f3a17109e690f194db3fb5fbcea6376729a342",
            "target_order": "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c",
        },
        "packed_size": {
            "baseline": 37989,
            "rotate1": 37989,
            "reverse": 37987,
            "swap01": 37989,
            "target_order": 37935,
        },
        "baseline_packed_sha256": "c893e94928eb690a005fa4f46d5a618451cee949d433f097f3ddd212c158234c",
        "target_order_packed_sha256": "07b8154440b8b10c93ad70c970f2863cf53063370e410a6d0c169442a7de5973",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def outdir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="diet-reloc-order-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def relocation_entries(data: bytes) -> tuple[int, int, list[bytes]]:
    mz = parse_mz(data)
    if not mz.valid:
        raise ValueError("invalid MZ")
    begin = mz.header.relocation_table_offset
    end = begin + 4 * len(mz.relocations)
    entries = [data[begin + 4 * i : begin + 4 * i + 4] for i in range(len(mz.relocations))]
    return begin, end, entries


def make_variants(candidate: bytes, target_restored: bytes) -> dict[str, bytes]:
    begin, end, entries = relocation_entries(candidate)
    t_begin, t_end, target_entries = relocation_entries(target_restored)
    if (begin, end) != (t_begin, t_end):
        raise ValueError("candidate/target-restored relocation table extent drift")
    if Counter(entries) != Counter(target_entries):
        raise ValueError("candidate/target-restored raw relocation-entry multiset differs")
    if len(set(entries)) != len(entries):
        raise ValueError("candidate relocation entries are not unique")
    orders = {
        "baseline": entries,
        "rotate1": entries[1:] + entries[:1],
        "reverse": entries[::-1],
        "swap01": [entries[1], entries[0], *entries[2:]],
        "target_order": target_entries,
    }
    result = {}
    for label, ordered in orders.items():
        mutated = bytearray(candidate)
        mutated[begin:end] = b"".join(ordered)
        data = bytes(mutated)
        mz = parse_mz(data)
        if not mz.valid:
            raise ValueError(f"{label}: reordered MZ became invalid")
        _, _, observed = relocation_entries(data)
        if observed != ordered or Counter(observed) != Counter(entries):
            raise ValueError(f"{label}: relocation order/multiset mutation drift")
        result[label] = data
    return result


def pack_restore(
    artifact: str,
    label: str,
    source: bytes,
    output: Path,
) -> dict[str, object]:
    expected = EXPECTED[artifact]
    diet, dosbox, config, options, toolchain = check_toolchain(artifact)
    input_path = output / "inputs" / f"{artifact}-{label}.exe"
    input_path.parent.mkdir(exist_ok=True)
    input_path.write_bytes(source)
    pack = run_once(
        f"{artifact}-{label}", input_path, output / "roundtrip",
        expected["name"], diet, dosbox, config, options,
    )
    packed_path = Path(str(pack["packed_path"]))
    packed = packed_path.read_bytes()
    work = packed_path.parent
    restore = run_guest(
        work, dosbox, config,
        f"diet.exe -ra {expected['name'].lower()}", "RESTORE.LOG",
    )
    restored = (work / expected["name"]).read_bytes()
    return {
        "input_size": len(source),
        "input_sha256": sha(source),
        "packed_size": len(packed),
        "packed_sha256": sha(packed),
        "restored_size": len(restored),
        "restored_sha256": sha(restored),
        "restored_raw_exact": restored == source,
        "pack_guest_log_sha256": pack["guest_log_sha256"],
        "restore_guest_log_sha256": restore["guest_log_sha256"],
        "toolchain": toolchain,
        "pack_options": options,
    }


def inspect_artifact(artifact: str, candidate_path: Path, target_path: Path, output: Path) -> dict[str, object]:
    expected = EXPECTED[artifact]
    candidate = candidate_path.read_bytes()
    target_restored = target_path.read_bytes()
    if sha(candidate) != expected["candidate_sha256"]:
        raise ValueError(f"{artifact}: candidate identity drift")
    if sha(target_restored) != expected["target_restored_sha256"]:
        raise ValueError(f"{artifact}: target-restored identity drift")
    candidate_mz = parse_mz(candidate)
    target_mz = parse_mz(target_restored)
    if len(candidate_mz.relocations) != expected["relocations"] or len(target_mz.relocations) != expected["relocations"]:
        raise ValueError(f"{artifact}: relocation count drift")

    variants = make_variants(candidate, target_restored)
    results = {}
    for label, data in variants.items():
        digest = sha(data)
        if digest != expected["variant_input_sha256"][label]:
            raise ValueError(f"{artifact}/{label}: input variant identity drift: {digest}")
        row = pack_restore(artifact, label, data, output)
        if not row["restored_raw_exact"] or row["restored_sha256"] != digest:
            raise ValueError(f"{artifact}/{label}: DIET pack/-RA did not preserve relocation order")
        if row["packed_size"] != expected["packed_size"][label]:
            raise ValueError(f"{artifact}/{label}: packed size drift")
        results[label] = row

    if results["baseline"]["packed_sha256"] != expected["baseline_packed_sha256"]:
        raise ValueError(f"{artifact}: baseline packed identity drift")
    if results["target_order"]["packed_sha256"] != expected["target_order_packed_sha256"]:
        raise ValueError(f"{artifact}: target-order packed identity drift")
    packed_hashes = {row["packed_sha256"] for row in results.values()}
    if len(packed_hashes) != len(results):
        raise ValueError(f"{artifact}: distinct relocation orders collapsed to identical packed bytes")

    return {
        "candidate_sha256": sha(candidate),
        "target_restored_sha256": sha(target_restored),
        "relocation_count": expected["relocations"],
        "raw_relocation_entry_multiset_exact": True,
        "relocation_entries_unique": True,
        "all_pack_restore_roundtrips_raw_exact": True,
        "all_tested_orders_pack_to_distinct_bytes": True,
        "results": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--op-candidate", type=Path, required=True)
    ap.add_argument("--op-target-restored", type=Path, required=True)
    ap.add_argument("--maine-candidate", type=Path, required=True)
    ap.add_argument("--maine-target-restored", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    output = outdir(args.output_dir)
    (output / "roundtrip").mkdir()
    artifacts = {
        "th04-op": inspect_artifact("th04-op", args.op_candidate.resolve(), args.op_target_restored.resolve(), output),
        "th04-maine": inspect_artifact("th04-maine", args.maine_candidate.resolve(), args.maine_target_restored.resolve(), output),
    }
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "DIET 1.45f relocation-table order preservation under private TH04-compatible permutations; no source/exact promotion",
        "artifacts": artifacts,
        "conclusion": (
            "For OP and MAINE, five legal MZs differing only in relocation-table entry order (baseline, rotate-one, reverse, first-pair swap, and the v228 target-restored order) all pack to distinct bytes, and DIET -RA restores every MZ byte-for-byte including its chosen relocation order. Pinned DIET 1.45f therefore does not canonicalize/sort these relocation tables before packing. The v228 target-restored relocation order is consequently a packed-container reconstruction constraint under this toolchain, although the historical linker/object cause of that order remains unresolved."
        ),
        "limit": (
            "All non-baseline permutations are ignored private controls. This does not authorize editing a product relocation table, and it does not establish which historical TLINK/object topology produced the target order."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "op_unique_packed_orders": len({x["packed_sha256"] for x in artifacts["th04-op"]["results"].values()}),
        "maine_unique_packed_orders": len({x["packed_sha256"] for x in artifacts["th04-maine"]["results"].values()}),
        "all_roundtrips_exact": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
