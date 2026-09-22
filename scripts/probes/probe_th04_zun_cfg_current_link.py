#!/usr/bin/env python3
"""Revalidate TH04 ZUN cfg_init against the current reduced-runtime resident link."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

PROBE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROBE_DIR))

import probe_th04_zun_cfg_function_local as local
import replay_th04_zun_runtime_inventory as runtime

ROOT = local.ROOT
TARGET_START = local.TARGET_START
TARGET_SIZE = local.TARGET_SIZE
TARGET_SHA256 = local.TARGET_SHA256
EXPECTED_LINKED_DIFFS = local.EXPECTED_LINKED_DIFFS
SHIFTED_FIXUPS = (
    0x15, 0x19, 0x21, 0x2B, 0x37, 0x3A,
    0x6A, 0x73, 0x7D, 0x86, 0x90, 0x93,
)
UNCHANGED_FIXUPS = (0x06, 0x0F, 0x81)
EXPECTED_DELTA = -6


def word(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 2], "little")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error(
            "output directory must be new directly below .analysis/reconstruction/probes"
        )

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = local.PAYLOAD.read_bytes()
    if local.sha(payload) != local.PAYLOAD_SHA256:
        raise RuntimeError("decoded ZUN payload identity drift")
    target = payload[TARGET_START:TARGET_START + TARGET_SIZE]
    if len(target) != TARGET_SIZE or local.sha(target) != TARGET_SHA256:
        raise RuntimeError("target cfg_init identity drift")

    output.mkdir()
    source_inputs = local.source_closure(ROOT, (local.SOURCE,))
    input_hashes = {
        relative: local.sha((ROOT / relative).read_bytes())
        for relative in source_inputs
    }
    standalone_root = output / "standalone"
    standalone_root.mkdir()
    a = local.compile_round("a", standalone_root, source_inputs)
    b = local.compile_round("b", standalone_root, source_inputs)
    stable_keys = ("code_sha256", "code_size", "fixups", "masked_code_sha256")
    if any(a[key] != b[key] for key in stable_keys):
        raise RuntimeError("cold standalone cfg_init rounds disagree")

    fixups = [(int(kind), int(offset)) for kind, offset in a["fixups"]]
    if tuple(offset for kind, offset in fixups if kind == 1) != local.EXPECTED_FIXUPS:
        raise RuntimeError("cfg_init FIXUPP locations drift")
    candidate_object_code = (standalone_root / "a/cfg_init.code").read_bytes()
    target_masked = local.masked(target, fixups)
    candidate_masked = local.masked(candidate_object_code, fixups)
    if target_masked != candidate_masked:
        raise RuntimeError("standalone cfg_init non-FIXUPP bytes differ")

    current_link = output.parent / f"{output.name}-runtime"
    if current_link.exists():
        raise RuntimeError(f"runtime sibling output already exists: {current_link}")
    command = [
        sys.executable,
        "scripts/probes/replay_th04_zun_runtime_inventory.py",
        "--output-dir",
        str(current_link),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=900,
    )
    (output / "current-link.log").write_text(
        json.dumps(command) + f"\nexit={completed.returncode}\n"
        + completed.stdout + completed.stderr,
        encoding="utf-8",
    )
    if completed.returncode:
        raise RuntimeError("current reduced-runtime resident replay failed")
    runtime_receipt_path = current_link / "receipt.json"
    if not runtime_receipt_path.is_file():
        raise RuntimeError("current runtime replay omitted receipt")
    runtime_receipt = json.loads(runtime_receipt_path.read_text(encoding="utf-8"))
    if (
        runtime_receipt["removed_link_inputs"] != ["emu.lib", "maths.lib"]
        or runtime_receipt["remaining_external_link_inputs"] != ["c0t.obj", "ct.lib"]
        or runtime_receipt["component_raw_difference_count"] != 4241
    ):
        raise RuntimeError("current runtime surface drift")

    linked_component = (current_link / "a/res_huma.com").read_bytes()
    linked = linked_component[0x267:0x2FF]
    if len(linked) != TARGET_SIZE:
        raise RuntimeError("current linked cfg_init extent drift")
    linked_differences = [
        i for i, (expected, actual) in enumerate(zip(target, linked))
        if expected != actual
    ]
    if tuple(linked_differences) != EXPECTED_LINKED_DIFFS:
        raise RuntimeError(
            f"current linked cfg_init difference set drift: {linked_differences}"
        )

    fixup_rows = []
    for kind, offset in sorted(fixups, key=lambda item: item[1]):
        if kind != 1:
            raise RuntimeError(f"unexpected cfg_init FIXUPP kind: {kind}")
        target_word = word(target, offset)
        linked_word = word(linked, offset)
        delta = linked_word - target_word
        changed_bytes = [
            pos for pos in (offset, offset + 1)
            if target[pos] != linked[pos]
        ]
        fixup_rows.append({
            "offset": offset,
            "target_word": target_word,
            "linked_word": linked_word,
            "delta": delta,
            "changed_byte_offsets": changed_bytes,
        })
        if offset in SHIFTED_FIXUPS:
            if delta != EXPECTED_DELTA:
                raise RuntimeError(
                    f"cfg_init shifted FIXUPP delta drift at {offset:#x}: {delta}"
                )
        elif offset in UNCHANGED_FIXUPS:
            if delta != 0:
                raise RuntimeError(
                    f"cfg_init stable FIXUPP unexpectedly shifted at {offset:#x}: {delta}"
                )
        else:
            raise RuntimeError(f"unclassified cfg_init FIXUPP at {offset:#x}")

    shifted_bytes = sorted(
        byte
        for row in fixup_rows
        if row["offset"] in SHIFTED_FIXUPS
        for byte in row["changed_byte_offsets"]
    )
    if shifted_bytes != linked_differences:
        raise RuntimeError(
            f"linked differences do not equal shifted FIXUPP bytes: {shifted_bytes}"
        )

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": (
            "TH04 ZUN cfg_init natural codegen revalidated against current compact-"
            "MASTER reduced-runtime resident link"
        ),
        "target_payload_sha256": local.PAYLOAD_SHA256,
        "target_cfg_sha256": TARGET_SHA256,
        "target_cfg_size": TARGET_SIZE,
        "source_input_sha256": input_hashes,
        "standalone_cold_builds": {"a": a, "b": b},
        "non_fixup_bytes_equal": True,
        "current_link_command": command,
        "current_link_receipt_sha256": local.sha(
            runtime_receipt_path.read_bytes()
        ),
        "current_link_component_sha256": runtime_receipt["link"]["a"][
            "component_sha256"
        ],
        "current_link_map_sha256": runtime_receipt["link"]["a"]["map_sha256"],
        "removed_runtime_inputs": runtime_receipt["removed_link_inputs"],
        "remaining_runtime_inputs": runtime_receipt[
            "remaining_external_link_inputs"
        ],
        "linked_cfg_sha256": local.sha(linked),
        "linked_raw_difference_count": len(linked_differences),
        "linked_raw_difference_offsets": linked_differences,
        "fixup_rows": fixup_rows,
        "shifted_fixup_offsets": list(SHIFTED_FIXUPS),
        "unchanged_fixup_offsets": list(UNCHANGED_FIXUPS),
        "shifted_fixup_word_delta": EXPECTED_DELTA,
        "linked_differences_equal_shifted_fixup_bytes": True,
        "conclusion": (
            "Under the current source-local support, compact MASTER archive, and "
            "reduced c0t+CT runtime link, cfg_init still differs from target only "
            "inside OMF FIXUPP words. Three fixup words are already equal; the other "
            "twelve linked words are each exactly target-6, accounting for all 13 "
            "raw byte differences. This directly matches the six-byte short _main "
            "layout downstream of cfg_init and leaves no independent cfg_init source "
            "mismatch."
        ),
        "limit": (
            "cfg_init is still not raw-equal in the current artifact-local link, so "
            "it remains source-present/blocked and receives no decoded-exact or "
            "packed-file credit. The -6 causal relation is link-layout evidence, "
            "not permission to patch relocation values."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "linked_raw_differences": len(linked_differences),
        "shifted_fixup_words": len(SHIFTED_FIXUPS),
        "unchanged_fixup_words": len(UNCHANGED_FIXUPS),
        "delta": EXPECTED_DELTA,
        "runtime_inputs": receipt["remaining_runtime_inputs"],
    }, sort_keys=True))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
