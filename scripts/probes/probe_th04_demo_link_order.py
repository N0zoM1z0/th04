#!/usr/bin/env python3
"""Relink the attested v214 MAIN snapshot with two DEMO object-order controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.pc98 import parse_mz

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001/a/source"
TARGET = ROOT / ".analysis/targets/th04/main.exe"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
INPUT_HASHES = {
    "obj/th04/main.@l": "b2ce7be007aa044e83321333bd3a0febc85496d2035cf66be37f863b6bcba2fe",
    "obj/th04/main.obj": "4ca3fdc4a7933b4da18a9cd291753fa2438506196c9fd83e7e5fdd63291a9e0a",
    "obj/th04/sess.obj": "3816b5f0aaabe5e8646243d22fbe13d40e97f53f012a398ae95ec76ae426f6ad",
    "obj/th04/demo.obj": "0e15d04274f0c8a511f562aa6e409b416e8b35d34e6db59aaa8f061a8c5b381e",
    "obj/th04/ems.obj": "17c864cdcc1f4992449dbad92119c7e874614c42dfb2e599f53d3d5bfe21023d",
    "bin/th04/main.exe": "1c1bcec509b775a6fa994d403d573ede75e74b8781ac5f0db06eb124d5fbae21",
}
TARGET_HASH = "077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b"
DEMO_START, DEMO_SIZE = 0xAED0, 0x51E


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_one(data: bytes, old: bytes, new: bytes) -> bytes:
    if data.count(old) != 1:
        raise RuntimeError(f"expected one response token {old!r}")
    return data.replace(old, new)


def map_session(map_path: Path) -> dict[str, object]:
    pattern = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+"
        r"C=CODE\s+S=DEMO_TEXT\s+.*M=th04/sess\.cpp\b", re.IGNORECASE
    )
    matches = [(line, pattern.search(line)) for line in map_path.read_text(
        encoding="cp437", errors="replace"
    ).splitlines()]
    matches = [(line, match) for line, match in matches if match]
    if len(matches) != 1:
        raise RuntimeError(f"expected one session MAP contribution, got {len(matches)}")
    line, match = matches[0]
    assert match is not None
    return {
        "line": line.strip(),
        "load_start": int(match[1], 16) * 16 + int(match[2], 16),
        "size": int(match[3], 16),
    }


def relink(label: str, response: bytes, output: Path, target: bytes) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix=f"{label}-", dir=output) as temporary:
        source = Path(temporary) / "source"
        shutil.copytree(SNAPSHOT, source, symlinks=True)
        (source / "obj/th04/main.@l").write_bytes(response)
        environment = os.environ.copy()
        environment.update(
            WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
            WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
        )
        log_path = output / f"{label}.log"
        with log_path.open("wb") as stream:
            subprocess.run(
                ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\main.@l"],
                cwd=source, env=environment, stdout=stream,
                stderr=subprocess.STDOUT, check=True,
            )
        candidate = (source / "bin/th04/main.exe").read_bytes()
        image = parse_mz(candidate)
        if not image.valid:
            raise RuntimeError(f"{label}: TLINK output is not a valid MZ")
        session = map_session(source / "obj/th04/main.map")
        start = int(session["load_start"])
        size = int(session["size"])
        session_indices = [
            index for index, relocation in enumerate(image.relocations)
            if start <= relocation.linear < start + size
        ]
        header = int.from_bytes(candidate[8:10], "little") * 16
        target_header = int.from_bytes(target[8:10], "little") * 16
        target_owner = target[target_header + DEMO_START:target_header + DEMO_START + DEMO_SIZE]
        candidate_owner = candidate[header + DEMO_START:header + DEMO_START + DEMO_SIZE]
        target_image = parse_mz(target)
        target_sites = [
            relocation.linear for relocation in target_image.relocations
            if DEMO_START <= relocation.linear < DEMO_START + DEMO_SIZE
        ]
        candidate_sites = [
            relocation.linear for relocation in image.relocations
            if DEMO_START <= relocation.linear < DEMO_START + DEMO_SIZE
        ]
        differing_offsets = [
            offset for offset, (expected, actual) in enumerate(zip(target_owner, candidate_owner))
            if expected != actual
        ]
        return {
            "label": label,
            "response_sha256": sha(response),
            "candidate_sha256": sha(candidate),
            "header_size": header,
            "session_map": session,
            "session_relocation_count": len(session_indices),
            "session_global_indices": session_indices,
            "target_owner_sha256": sha(target_owner),
            "candidate_owner_sha256": sha(candidate_owner),
            "target_owner_raw_equal": candidate_owner == target_owner,
            "target_owner_differing_byte_count": len(differing_offsets),
            "target_owner_first_differing_offsets": differing_offsets[:12],
            "owner_relocation_sites_equal_unordered": sorted(candidate_sites) == sorted(target_sites),
            "owner_relocation_order_equal": candidate_sites == target_sites,
            "link_log_sha256": sha(log_path.read_bytes()),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists():
        raise RuntimeError(f"refusing to overwrite probe output: {output}")
    if output.parent != (ROOT / ".analysis/reconstruction/probes").resolve():
        raise RuntimeError("output must be a direct child of .analysis/reconstruction/probes")
    target = TARGET.read_bytes()
    if sha(target) != TARGET_HASH or not parse_mz(target).valid:
        raise RuntimeError("pinned target identity or MZ structure changed")
    for relative, expected in INPUT_HASHES.items():
        path = SNAPSHOT / relative
        if not path.is_file() or path.is_symlink() or sha(path.read_bytes()) != expected:
            raise RuntimeError(f"v214 snapshot input changed: {relative}")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT, check=True)
    output.mkdir(parents=True)
    baseline = (SNAPSHOT / "obj/th04/main.@l").read_bytes()
    anchor = b"obj\\th04\\coanch.obj "
    session = b"obj\\th04\\sess.obj "
    pair = b"obj\\th04\\main.obj obj\\th04\\sess.obj "
    trials = {
        "session_first": replace_one(replace_one(baseline, session, b""), anchor, anchor + session),
        "main_session_first": replace_one(replace_one(baseline, pair, b""), anchor, anchor + pair),
    }
    results = [relink(label, response, output, target) for label, response in trials.items()]
    receipt = {
        "claim_scope": "MAIN DEMO_TEXT link-input order controls; diagnostic only",
        "target_sha256": TARGET_HASH,
        "snapshot_input_sha256": INPUT_HASHES,
        "target_session_global_indices": [
            index for index, relocation in enumerate(parse_mz(target).relocations)
            if DEMO_START <= relocation.linear < DEMO_START + DEMO_SIZE
        ],
        "trials": results,
        "result": "neither response-only order reproduces target owner bytes and ordered relocations",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(result["label"], "map", result["session_map"]["line"],
              "raw", result["target_owner_raw_equal"],
              "ordered", result["owner_relocation_order_equal"],
              "first-index", result["session_global_indices"][0])
    print(f"receipt: {receipt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
