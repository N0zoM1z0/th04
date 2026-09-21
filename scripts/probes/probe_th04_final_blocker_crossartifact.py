#!/usr/bin/env python3
"""Scan every registered TH01-TH05 target image for final TH04 blocker motifs.

DIET-wrapped targets are restored only inside ignored .analysis output with the
pinned DIET/DOSBox-X toolchain. This is provenance evidence only: no restored
target bytes are treated as source and no exactness is granted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import load_target_manifest, read_verified_artifact  # noqa: E402
from replay_diet145f import check_toolchain  # noqa: E402

CARPET_PROLOGUE = bytes.fromhex("55 8b ec 56 57 1e 07")
CARPET_REQUIRED = tuple(bytes.fromhex(x) for x in ("f7 e3", "ac", "d1 e7", "e2"))
CHECKER_CORE = bytes.fromhex("8e c2 b9 06 00 66 26 89 05 83 c7 08 e2")
EXPECTED_CARPET = {"th04-main": [0xEA8A]}
EXPECTED_CHECKER = {"th04-main": [0x120AF]}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def new_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="final-crossartifact-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def restore_diet(artifact: dict[str, object], packed: bytes, output: Path) -> tuple[bytes, dict[str, object]]:
    diet, dosbox, cfg, _options, toolchain = check_toolchain("th04-op")
    work = output / str(artifact["id"])
    work.mkdir()
    filename = Path(str(artifact["private_path"])).name.upper()
    shutil.copy2(diet, work / "DIET.EXE")
    (work / filename).write_bytes(packed)
    env = os.environ.copy()
    env.update(
        SDL_VIDEODRIVER="dummy",
        SDL_AUDIODRIVER="dummy",
        XDG_CACHE_HOME=str(work / "cache"),
        XDG_CONFIG_HOME=str(work / "config"),
        XDG_DATA_HOME=str(work / "data"),
    )
    cmd = [
        str(dosbox), "-defaultconf", "-defaultmapper", "-conf", str(cfg),
        "-fastlaunch", "-nogui", "-nomenu", "-exit", "-time-limit", "30",
        "-c", f'mount c "{work}"', "-c", "c:",
        "-c", f"diet.exe -ra {filename.lower()} > restore.log", "-c", "exit",
    ]
    done = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=40)
    (work / "host.log").write_text(done.stdout + done.stderr)
    guest = work / "RESTORE.LOG"
    guest_text = guest.read_bytes().decode("cp437", errors="replace") if guest.exists() else ""
    if done.returncode or "Success!" not in guest_text:
        raise RuntimeError(f"{artifact['id']}: DIET restore failed")
    restored = (work / filename).read_bytes()
    return restored, {
        "restored_size": len(restored),
        "restored_sha256": sha(restored),
        "restore_log_sha256": sha(guest.read_bytes()),
        "toolchain": toolchain,
    }


def program_image(raw: bytes) -> tuple[bytes, str, int]:
    if raw[:2] == b"MZ":
        mz = parse_mz(raw)
        if not mz.valid:
            raise ValueError("invalid restored/direct MZ")
        return mz.program_image, "mz", len(mz.relocations)
    return raw, "flat", 0


def carpet_hits(image: bytes) -> list[int]:
    hits: list[int] = []
    pos = 0
    while True:
        start = image.find(CARPET_PROLOGUE, pos)
        if start < 0:
            break
        window = image[start:start + 96]
        if (
            window.count(CARPET_REQUIRED[0]) >= 2
            and all(motif in window for motif in CARPET_REQUIRED[1:])
        ):
            hits.append(start)
        pos = start + 1
    return hits


def checker_hits(image: bytes) -> list[int]:
    hits: list[int] = []
    pos = 0
    while True:
        start = image.find(CHECKER_CORE, pos)
        if start < 0:
            break
        hits.append(start)
        pos = start + 1
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    output = new_output(args.output_dir)
    artifacts = load_target_manifest(ROOT / "config/targets.toml")["artifacts"]
    scans: dict[str, dict[str, object]] = {}
    carpet: dict[str, list[int]] = {}
    checker: dict[str, list[int]] = {}
    restored_ids: list[str] = []

    for artifact in artifacts:
        aid = str(artifact["id"])
        packed = read_verified_artifact(ROOT, artifact)
        raw = packed
        restore_meta: dict[str, object] | None = None
        if len(raw) >= 0x20 and raw[0x1C:0x20].lower() == b"diet":
            raw, restore_meta = restore_diet(artifact, packed, output)
            restored_ids.append(aid)
        image, fmt, reloc_count = program_image(raw)
        ch = carpet_hits(image)
        kh = checker_hits(image)
        if ch:
            carpet[aid] = ch
        if kh:
            checker[aid] = kh
        scans[aid] = {
            "packed_sha256": str(artifact["sha256"]),
            "container_was_diet": restore_meta is not None,
            "restored": restore_meta,
            "program_format": fmt,
            "program_image_size": len(image),
            "program_image_sha256": sha(image),
            "relocation_count": reloc_count,
            "carpet_signature_offsets": [hex(x) for x in ch],
            "checker_core_offsets": [hex(x) for x in kh],
        }

    carpet_expected = {k: [int(x) for x in v] for k, v in EXPECTED_CARPET.items()}
    checker_expected = {k: [int(x) for x in v] for k, v in EXPECTED_CHECKER.items()}
    if carpet != carpet_expected:
        raise ValueError(f"carpet cross-artifact result drift: {carpet}")
    if checker != checker_expected:
        raise ValueError(f"checkerboard cross-artifact result drift: {checker}")
    if len(scans) != 20 or len(restored_ids) != 8:
        raise ValueError("registered target corpus size/DIET partition drift")

    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04 final blocker cross-artifact provenance negative",
        "registered_artifact_count": len(scans),
        "diet_restored_artifact_count": len(restored_ids),
        "diet_restored_artifacts": restored_ids,
        "carpet_signature": {
            "definition": "near prologue PUSH DS/POP ES plus >=2 MUL BX, LODSB, SHL DI,1, and LOOP within 96 bytes",
            "hits": {k: [hex(x) for x in v] for k, v in carpet.items()},
            "conclusion": "Only TH04 MAIN carpet_lighting_put_new matches across all registered TH01-TH05 artifact images.",
        },
        "checkerboard_signature": {
            "hex_prefix": CHECKER_CORE.hex(),
            "hits": {k: [hex(x) for x in v] for k, v in checker.items()},
            "conclusion": "Only TH04 MAIN contains the exact MOV ES,DX / CX=6 / ES dword store / ADD DI,8 / LOOP core.",
        },
        "artifacts": scans,
        "limit": "This broadens prior MAIN-only provenance scans to every registered executable image. It remains negative evidence and does not prove original source language or authorize target-derived inline assembly.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "carpet_hits": receipt["carpet_signature"]["hits"],
        "checkerboard_hits": receipt["checkerboard_signature"]["hits"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
