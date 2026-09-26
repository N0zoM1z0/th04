#!/usr/bin/env python3
"""Replay TH04 OP nopoly_B_put() from a narrowed cross-game hybrid source.

TH03, TH04, and TH05 OP release targets contain the same 30-byte function
modulo only the linked _nopoly_B address word. The maintained source keeps the
segment values and copy length as ordinary TC4J pseudoregister assignments and
restricts symbolic low-level source to DS save/restore, the target XOR encoding
direction, and REP MOVSW.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from probe_th04_final_blocker_crossartifact import restore_diet  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from replay_th04_op_music_remaining import (  # noqa: E402
    SNAPSHOT, TARGET, TARGET_SHA, BASE_EXE_SHA, BASE_MAP_SHA, RELOCATIONS,
    PRODUCER_START, PRODUCER_SIZE, PRODUCER_SHA,
    BASE_WRAPPER_SHA, BASE_IMPL_SHA, BASE_CODE_SHA, tcc_op,
)

SOURCE = ROOT / "src/op/music/nopoly_put.inl"
WRAPPER = ROOT / "src/op/music/nopoly_put.cpp"
SOURCE_SHA = "c16defa51f3cec10c2aedf225b225211f2b3a5e8b244c24b44dcba8ce0d6eab9"
WRAPPER_SHA = "decaf5daa42c97c5934df28c30b61035a3cfc46f6c7263d393e6235d16fbf42c"

START = 0xBFA7
SIZE = 0x1E
TARGET_BODY_SHA = "f9af3bf25fe94b1ca89ef5ad9bdacd77a87cfc401450a378a12428ea1f409083"
PRELINK_BODY_SHA = "ec0ca0d388011a3a96e3c34b10d0f8c26e176a86de11bae5271d530f8bfac9a3"
LINK_WORD = (0x0C, 0x0E)

CROSSGAME = {
    "th03-op-smoke": {
        "offset": 0xA5F6,
        "sha256": "257c3b9373036a7c7f274c3927bfc16d081f29f4c46fa85050e0e1e099b8a23d",
        "map": ROOT / ".analysis/gpt-web/v401-master-vs-object-replay-001/a/source/obj/th03/op.map",
        "map_sha256": "d84e5b7763d6075b88decfe590c487d4ca31dab3d336a043a41c5ec387c70c2b",
        "public": "0990:0CF6 idle  nopoly_b_put()",
        "owner": "0990:0C1E 08C4 C=CODE   S=OP_MUSIC_TEXT  G=GROUP_01 M=th03/op_music.cpp ACBP=28",
    },
    "th04-op": {
        "offset": START,
        "sha256": TARGET_BODY_SHA,
        "map": ROOT / ".analysis/gpt-web/v401-master-vs-object-replay-001/a/source/obj/th04/op.map",
        "map_sha256": "08ab21543cc5e7c58e29a566538011aab3514adb5d3193216df7e44d671b0cf3",
        "public": "0A74:1867 idle  nopoly_b_put()",
        "owner": "0A74:1795 06A5 C=CODE   S=OP_MUSIC_TEXT  G=OP_01   M=th04/op_music.cpp ACBP=28",
    },
    "th05-op-smoke": {
        "offset": 0xBFF6,
        "sha256": "5471206cd4cc4e9c4707874bc9d2603c2da03687da1e466b8f8e0c1186f6cf9c",
        "map": ROOT / ".analysis/gpt-web/v401-master-vs-object-replay-001/a/source/obj/th05/op.map",
        "map_sha256": "da2598ec3f3c707fdc968d0d9dcca5cddf333beb9b8241d76d123ee0970af907",
        "public": "0A39:1C66 idle  nopoly_b_put()",
        "owner": "0A39:1AE9 095C C=CODE   S=OP_MUSIC_TEXT  G=OP_01   M=th05/op_music.cpp ACBP=28",
    },
}
TH02_OFFSET = 0xC0E4
TH02_BODY_SHA = "69deb644135a07efe9c0d54d23815bb5fd325439fc3fe0c722506eab4a1b84ee"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def mask_link_word(data: bytes) -> bytes:
    out = bytearray(data)
    out[LINK_WORD[0]:LINK_WORD[1]] = b"\0\0"
    return bytes(out)


def new_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="op-nopoly-v826-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def source_policy() -> dict[str, object]:
    if sha_file(SOURCE) != SOURCE_SHA or sha_file(WRAPPER) != WRAPPER_SHA:
        raise ValueError("maintained nopoly source identity drift")
    text = SOURCE.read_text()
    forbidden = ("__emit__", "#pragma codestring", "__memcpy__", "target_bytes", "db 0x")
    if any(token in text for token in forbidden):
        raise ValueError("maintained nopoly source contains byte-forcing/decomp helper surface")
    required = (
        "asm { push ds; }",
        "_AX = SEG_PLANE_B;",
        "_ES = _AX;",
        "_AX = (unsigned int)nopoly_B;",
        "_DS = _AX;",
        "xor di, di",
        "xor si, si",
        "_CX = (PLANE_SIZE / sizeof(unsigned short));",
        "rep movsw",
        "pop ds",
    )
    for marker in required:
        if marker not in text:
            raise ValueError(f"maintained nopoly marker drift: {marker}")
    return {
        "ordinary_tc4j": [
            "SEG_PLANE_B load and ES assignment",
            "_nopoly_B segment load and DS assignment",
            "PLANE_SIZE/2 word count",
        ],
        "symbolic_low_level": [
            "PUSH DS / POP DS around temporary source-segment selection",
            "XOR DI,DI and XOR SI,SI target encoding direction",
            "REP MOVSW segmented VRAM copy",
        ],
        "no_emit": True,
        "no_codestring": True,
        "no_decomp_memcpy_helper": True,
        "no_target_byte_arrays": True,
        "no_post_build_patch": True,
    }


def restore_target(aid: str, output: Path) -> bytes:
    manifest = load_target_manifest(ROOT / "config/targets.toml")
    artifact = find_artifact(manifest, aid)
    packed = read_verified_artifact(ROOT, artifact)
    if len(packed) >= 0x20 and packed[0x1C:0x20].lower() == b"diet":
        restored, _ = restore_diet(artifact, packed, output)
        return restored
    return packed


def unique_normalized_hits(image: bytes, normalized: bytes) -> list[int]:
    hits: list[int] = []
    for pos in range(0, len(image) - SIZE + 1):
        if mask_link_word(image[pos:pos + SIZE]) == normalized:
            hits.append(pos)
    return hits


def crossgame_evidence(output: Path) -> dict[str, object]:
    work = output / "crossgame"
    work.mkdir()
    normalized = bytes.fromhex(
        "55 8b ec 56 57 1e b8 00 a8 8e c0 a1 00 00 8e d8 "
        "31 ff 31 f6 b9 80 3e f3 a5 1f 5f 5e 5d c3"
    )
    if sha(normalized) != PRELINK_BODY_SHA:
        raise ValueError("normalized nopoly identity drift")

    results: dict[str, object] = {}
    for aid, spec in CROSSGAME.items():
        raw = restore_target(aid, work)
        mz = parse_mz(raw)
        if not mz.valid:
            raise ValueError(f"{aid}: invalid MZ")
        off = int(spec["offset"])
        body = mz.program_image[off:off + SIZE]
        if len(body) != SIZE or sha(body) != spec["sha256"]:
            raise ValueError(f"{aid}: release nopoly body drift")
        if mask_link_word(body) != normalized:
            raise ValueError(f"{aid}: normalized nopoly body drift")
        hits = unique_normalized_hits(mz.program_image, normalized)
        if hits != [off]:
            raise ValueError(f"{aid}: normalized nopoly unique-hit drift: {hits}")

        map_path = Path(spec["map"])
        if sha_file(map_path) != spec["map_sha256"]:
            raise ValueError(f"{aid}: pinned map identity drift")
        map_text = map_path.read_text(encoding="cp437", errors="replace")
        if spec["public"] not in map_text or spec["owner"] not in map_text:
            raise ValueError(f"{aid}: map public/owner drift")
        results[aid] = {
            "payload_offset": hex(off),
            "body_sha256": sha(body),
            "normalized_sha256": sha(mask_link_word(body)),
            "unique_normalized_match": True,
            "ordered_relocations": len(mz.relocations),
            "map_sha256": spec["map_sha256"],
            "map_owner": spec["owner"],
        }

    # TH02 is intentionally a negative lineage control. GAME<3 uses a loop,
    # not the GAME>=3 segment/REP-MOVSW producer.
    raw = restore_target("th02-op-smoke", work)
    mz = parse_mz(raw)
    body = mz.program_image[TH02_OFFSET:TH02_OFFSET + SIZE]
    if sha(body) != TH02_BODY_SHA or mask_link_word(body) == normalized:
        raise ValueError("TH02 negative control drift")
    results["th02-negative-control"] = {
        "payload_offset": hex(TH02_OFFSET),
        "body_sha256": sha(body),
        "matches_game3plus_shape": False,
    }

    shutil.rmtree(work)
    return {
        "normalized_body_sha256": PRELINK_BODY_SHA,
        "game3plus_targets": results,
        "classification": (
            "TH03/TH04/TH05 release-target machine-code identity modulo only "
            "the linked source-segment word; source spelling is not claimed"
        ),
    }


def find_function_end(text: str, start: int) -> int:
    brace = text.find("{", start)
    if brace < 0:
        raise ValueError("nopoly function opening brace drift")
    depth = 0
    for pos in range(brace, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return pos + 1
    raise ValueError("nopoly function end drift")


def overlay_source(work: Path) -> dict[str, str]:
    wrapper = work / "th04/op_music.cpp"
    impl = work / "th02/op/m_music.cpp"
    if sha_file(wrapper) != BASE_WRAPPER_SHA or sha_file(impl) != BASE_IMPL_SHA:
        raise ValueError("pinned op_music source drift")

    dst = work / SOURCE.relative_to(ROOT)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, dst)

    text = impl.read_text()
    marker = "void near nopoly_B_put(void)\n"
    if text.count(marker) != 1:
        raise ValueError("nopoly function marker drift")
    start = text.index(marker)
    end = find_function_end(text, start)
    text = text[:start] + '#include "src/op/music/nopoly_put.inl"' + text[end:]
    impl.write_text(text)
    return {
        str(SOURCE.relative_to(ROOT)): sha_file(SOURCE),
        "overlay_th02/op/m_music.cpp": sha_file(impl),
    }


def build_round(output: Path, label: str, target_mz) -> dict[str, object]:
    work = output / label / "op/source"
    work.parent.mkdir(parents=True)
    compact = copy_compact_snapshot(SNAPSHOT, work, "op")
    source_hashes = overlay_source(work)

    obj = work / "obj/th04/op_music.obj"
    obj.unlink()
    tcc_op(work, output, f"nopoly-hybrid-{label}", "th04/op_music.cpp")
    code = segment_bytes(obj, "OP_MUSIC_TEXT")
    if len(code) != PRODUCER_SIZE or sha(code) != BASE_CODE_SHA:
        raise ValueError(f"{label}: OP_MUSIC_TEXT object CODE drift")

    local = START - PRODUCER_START
    body = code[local:local + SIZE]
    if sha(mask_link_word(body)) != PRELINK_BODY_SHA:
        raise ValueError(f"{label}: nopoly prelink fixed bytes drift")

    exe = work / "bin/th04/op.exe"
    map_path = work / "obj/th04/op.map"
    exe.unlink()
    map_path.unlink()
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
        work, output / f"link-{label}.log", timeout=300,
    )
    linked = parse_mz(exe.read_bytes())
    if not linked.valid:
        raise ValueError(f"{label}: invalid linked OP")
    if sha_file(exe) != BASE_EXE_SHA or sha_file(map_path) != BASE_MAP_SHA:
        raise ValueError(f"{label}: linked OP EXE/MAP drift")
    if [x.linear for x in linked.relocations] != [x.linear for x in target_mz.relocations]:
        raise ValueError(f"{label}: ordered relocation drift")

    linked_body = linked.program_image[START:START + SIZE]
    linked_producer = linked.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    target_body = target_mz.program_image[START:START + SIZE]
    if linked_body != target_body or sha(linked_body) != TARGET_BODY_SHA:
        raise ValueError(f"{label}: linked nopoly raw mismatch")
    if sha(linked_producer) != PRODUCER_SHA:
        raise ValueError(f"{label}: linked OP_MUSIC_TEXT producer drift")

    return {
        "compact_snapshot": compact,
        "source_sha256": source_hashes,
        "object_code_size": len(code),
        "object_code_sha256": sha(code),
        "prelink_body_sha256": sha(body),
        "prelink_normalized_sha256": sha(mask_link_word(body)),
        "linked_body_sha256": sha(linked_body),
        "linked_body_difference_count": 0,
        "linked_producer_sha256": sha(linked_producer),
        "linked_exe_sha256": sha_file(exe),
        "linked_map_sha256": sha_file(map_path),
        "ordered_relocations": len(linked.relocations),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    output = new_output(args.output_dir)

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA:
        raise ValueError("pinned DOS runner drift")
    if sha_file(TARGET) != TARGET_SHA:
        raise ValueError("OP restored target identity drift")
    if sha_file(SOURCE) != SOURCE_SHA or sha_file(WRAPPER) != WRAPPER_SHA:
        raise ValueError("maintained nopoly source drift")
    for path, expected in (
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/op_music.cpp", BASE_WRAPPER_SHA),
        (SNAPSHOT / "th02/op/m_music.cpp", BASE_IMPL_SHA),
    ):
        if sha_file(path) != expected:
            raise ValueError(f"pinned v826 input drift: {path}")

    policy = source_policy()
    crossgame = crossgame_evidence(output)

    target_mz = parse_mz(TARGET.read_bytes())
    if not target_mz.valid or len(target_mz.relocations) != RELOCATIONS:
        raise ValueError("OP target MZ/relocation drift")
    target_body = target_mz.program_image[START:START + SIZE]
    if len(target_body) != SIZE or sha(target_body) != TARGET_BODY_SHA:
        raise ValueError("OP target nopoly body drift")

    builds = {label: build_round(output, label, target_mz) for label in ("a", "b")}
    stable = lambda x: {k: v for k, v in x.items() if k != "compact_snapshot"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise ValueError("independent nopoly cold rounds disagree")
    if sha_file(SOURCE) != SOURCE_SHA or sha_file(WRAPPER) != WRAPPER_SHA:
        raise ValueError("maintained nopoly source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP nopoly_B_put hybrid-source decoded exactness",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": SOURCE_SHA,
        "wrapper": str(WRAPPER.relative_to(ROOT)),
        "wrapper_sha256": WRAPPER_SHA,
        "boundary": {
            "payload_offset": hex(START),
            "size": SIZE,
            "target_sha256": TARGET_BODY_SHA,
            "producer_offset": hex(PRODUCER_START),
            "producer_size": PRODUCER_SIZE,
            "producer_sha256": PRODUCER_SHA,
        },
        "source_policy": policy,
        "crossgame_release_evidence": crossgame,
        "negative_controls": {
            "ordinary_intrinsic_memcpy": (
                "v670/v766: same 30-byte REP MOVSW strategy but different "
                "segment setup order and XOR opcode directions"
            ),
            "assembly_backend": (
                "v820: TC4J -B/TASM32 is byte-identical to the nonexact "
                "natural intrinsic-memcpy candidate"
            ),
            "zero_registers": (
                "ordinary TC4J _DI=0/_SI=0 emits 33 FF / 33 F6; "
                "TH03/TH04/TH05 release targets consistently use 31 FF / 31 F6"
            ),
        },
        "builds": builds,
        "conclusion": (
            "TH03, TH04, and TH05 OP release targets preserve the complete "
            "GAME>=3 30-byte nopoly_B_put producer modulo only the linked "
            "_nopoly_B word. Two cold TC4.02/TLINK rounds compile the maintained "
            "narrow hybrid into the unchanged 0x6A5 OP_MUSIC_TEXT CODE, accepted "
            "OP EXE/MAP, and all 804 ordered relocations; the linked function is raw-zero."
        ),
        "limit": (
            "Decoded-function exactness only. Cross-game identity supports the "
            "machine mechanism, not original source spelling or packed-file exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha_file(path),
        "body_sha256": TARGET_BODY_SHA,
        "crossgame_normalized_sha256": PRELINK_BODY_SHA,
        "producer_sha256": PRODUCER_SHA,
        "ordered_relocations": RELOCATIONS,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
