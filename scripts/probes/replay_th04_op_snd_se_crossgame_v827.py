#!/usr/bin/env python3
"""Replay TH04 OP shared sound functions with TH05 release-target provenance.

v822 proved the exact 0x86 producer mechanically but left source credit blocked
because the frame-free parameter/current-index helpers were known only from a
ReC98 decompilation spelling plus same-game TH04 evidence.

v827 adds independent release-target evidence: restored TH05 OP and MAINE each
contain exactly one copy of the complete 0x86 fixed producer after masking only
the 20 legal OMF fixup operands. This corroborates the two compiler/register
primitives while leaving the surrounding selection/update logic in maintained
C++ and without claiming literal original-source spelling.
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
from probe_th04_op_snd_se_shared import (  # noqa: E402
    TARGET, TARGET_SHA, BASE_EXE_SHA, BASE_MAP_SHA, BASE_CODE_SHA, RELOCATIONS,
    PRODUCER_START, PRODUCER_SIZE, PRODUCER_SHA,
    PLAY_START, PLAY_SIZE, PLAY_SHA,
    UPDATE_START, UPDATE_SIZE, UPDATE_SHA,
    SNAPSHOT, loose_segment_bytes, tcc_op, object_fixups, mask_fixups,
)
from replay_th04_zun_source_only import source_closure  # noqa: E402

SOURCES = {
    "src/shared/sound/se_play.cpp": "7f862ee7b8850b6b12e1dd28b79d98301aa71e637803327acf564c22088ae622",
    "src/shared/sound/impl.hpp": "9b9108a07a1602451a81de44c1301961a68ba7b415e819dfdf36f668abb84405",
    "src/shared/sound/api.hpp": "4356c39a7aad86fd1da13d7b0640c93378012072a6c383d20ecbda7a0f94d877",
    "src/op/sound/se_update.cpp": "d955a0185a6b4581ea8e00c95114009be19c0f3fca569878ce6cea53d9f76ee6",
    "src/op/sound/se_update.inl": "7c1044a4527d08e7c02bdbb2c432a4c9d518e3b56fd0f556a33fccc03534e6af",
}

TH05 = {
    "th05-op-smoke": {
        "restored_sha256": "1caaa7f804146838e8771ae69487005f1ccd70cc8369dcb62e8adaf6addad71c",
        "producer_offset": 0xD602,
        "map": ROOT / ".analysis/gpt-web/v401-master-vs-object-replay-001/a/source/obj/th05/op.map",
        "map_sha256": "da2598ec3f3c707fdc968d0d9dcca5cddf333beb9b8241d76d123ee0970af907",
        "owner": "0D30:0302 0086 C=CODE   S=SHARED         G=(none)  M=th04/snd_se.cpp ACBP=28",
        "play_public": "0D30:0302       SND_SE_PLAY",
        "update_public": "0D30:033C       _snd_se_update",
    },
    "th05-maine-smoke": {
        "restored_sha256": "247a7b90bb912562999da15267fe6e98fa72c8cccdbab3f1a88eee37c82fc9a4",
        "producer_offset": 0xEAE6,
        "map": ROOT / ".analysis/gpt-web/v401-master-vs-object-replay-001/a/source/obj/th05/maine.map",
        "map_sha256": "27bece1e57bc7c11e7dc5a949baeacb10cd88391d581130c250616ecfaaa5277",
        "owner": "0E7F:02F0 0086 C=CODE   S=SHARED         G=(none)  M=th04/snd_se.cpp ACBP=28",
        "play_public": "0E7F:02F0       SND_SE_PLAY",
        "update_public": "0E7F:032A       _snd_se_update",
    },
}

FRAME_FREE = bytes.fromhex("8bdc368b5704")
CURRENT_INDEX = bytes.fromhex("8a1e000032ff")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def new_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="op-snd-se-v827-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def source_policy() -> dict[str, object]:
    for rel, digest in SOURCES.items():
        if sha_file(ROOT / rel) != digest:
            raise ValueError(f"maintained sound source identity drift: {rel}")

    play = (ROOT / "src/shared/sound/se_play.cpp").read_text()
    impl = (ROOT / "src/shared/sound/impl.hpp").read_text()
    update = (ROOT / "src/op/sound/se_update.inl").read_text()
    combined = play + "\n" + impl + "\n" + update
    for forbidden in ("__emit__", "#pragma codestring", "target_bytes", "db 0x"):
        if forbidden in combined:
            raise ValueError(f"sound function source contains byte-forcing surface: {forbidden}")
    for marker in (
        "register int se = snd_get_param(new_se);",
        "snd_se_priorities[snd_se_current_index()]",
        "_BX = _SP;",
        "return peek(_SS, (_BX + 4));",
        "_BL = snd_se_playing;",
        "_BH ^= _BH;",
        "snd_se_priority_frames[snd_se_current_index()]",
    ):
        if marker not in combined:
            raise ValueError(f"sound hybrid source marker drift: {marker}")

    return {
        "ordinary_cpp": [
            "sound-mode and SE_NONE guards",
            "priority comparisons and selected-effect writes",
            "driver dispatch, frame increment, and expiry updates",
        ],
        "crossgame_corroborated_compiler_primitives": [
            "frame-free Pascal parameter read: BX=SP; DX=SS:[BX+4]",
            "current-index construction: BL=snd_se_playing; XOR BH,BH",
        ],
        "no_emit": True,
        "no_function_codestring": True,
        "no_target_byte_arrays": True,
        "no_post_build_patch": True,
        "original_source_spelling_claimed": False,
    }


def unique_fixed_hits(image: bytes, fixed: bytes, fixups: list[tuple[int, int]]) -> list[int]:
    hits = []
    for pos in range(0, len(image) - PRODUCER_SIZE + 1):
        if mask_fixups(image[pos:pos + PRODUCER_SIZE], fixups) == fixed:
            hits.append(pos)
    return hits


def crossgame_release_targets(output: Path, fixed: bytes, fixups: list[tuple[int, int]]) -> dict[str, object]:
    manifest = load_target_manifest(ROOT / "config/targets.toml")
    cross_root = output / "crossgame"
    cross_root.mkdir()
    result: dict[str, object] = {}

    for aid, spec in TH05.items():
        artifact = find_artifact(manifest, aid)
        packed = read_verified_artifact(ROOT, artifact)
        artifact_out = cross_root / aid
        artifact_out.mkdir()
        restored, restore_meta = restore_diet(artifact, packed, artifact_out)
        if sha(restored) != spec["restored_sha256"]:
            raise ValueError(f"{aid}: restored identity drift")
        mz = parse_mz(restored)
        if not mz.valid:
            raise ValueError(f"{aid}: invalid restored MZ")
        hits = unique_fixed_hits(mz.program_image, fixed, fixups)
        expected = int(spec["producer_offset"])
        if hits != [expected]:
            raise ValueError(f"{aid}: fixed producer unique-hit drift: {hits}")

        producer = mz.program_image[expected:expected + PRODUCER_SIZE]
        masked = mask_fixups(producer, fixups)
        if masked != fixed:
            raise ValueError(f"{aid}: fixed producer bytes drift")
        if producer[PLAY_SIZE:PLAY_SIZE + 1] != bytes.fromhex("90"):
            raise ValueError(f"{aid}: inter-function NOP drift")

        map_path = Path(spec["map"])
        if sha_file(map_path) != spec["map_sha256"]:
            raise ValueError(f"{aid}: v401 MAP identity drift")
        map_text = map_path.read_text(encoding="cp437", errors="replace")
        for marker in (spec["owner"], spec["play_public"], spec["update_public"]):
            if marker not in map_text:
                raise ValueError(f"{aid}: MAP sound producer marker drift: {marker}")

        if FRAME_FREE not in masked[:PLAY_SIZE]:
            raise ValueError(f"{aid}: frame-free parameter primitive missing")
        # The linked variable operand is masked to 0000 by OMF fixup locations.
        current_hits = []
        pos = 0
        while True:
            pos = masked.find(CURRENT_INDEX, pos)
            if pos < 0:
                break
            current_hits.append(pos)
            pos += 1
        if len(current_hits) != 2:
            raise ValueError(f"{aid}: current-index primitive occurrence drift: {current_hits}")

        result[aid] = {
            "restored_sha256": sha(restored),
            "producer_payload_offset": hex(expected),
            "raw_producer_sha256": sha(producer),
            "fixed_producer_sha256": sha(masked),
            "unique_fixed_producer_match": True,
            "frame_free_parameter_primitive": FRAME_FREE.hex(),
            "current_index_primitive": CURRENT_INDEX.hex(),
            "current_index_relative_offsets": [hex(x) for x in current_hits],
            "map_sha256": spec["map_sha256"],
            "map_owner": spec["owner"],
            "ordered_relocations": len(mz.relocations),
            "restore_log_sha256": restore_meta["restore_log_sha256"],
        }

    shutil.rmtree(cross_root)
    return result


def install_sources(work: Path) -> dict[str, str]:
    closure = source_closure(
        ROOT,
        ("src/shared/sound/se_play.cpp", "src/op/sound/se_update.cpp"),
    )
    for rel in closure:
        src = ROOT / rel
        dst = work / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    wrapper = work / "th04/snd_se.cpp"
    wrapper.write_text(
        '#include "src/shared/sound/se_play.cpp"\n'
        '#pragma codestring "\\x90"\n\n'
        'static const int PMD_INTERRUPT = PMD;\n'
        'extern "C" int far pascal bgm_sound(int num);\n\n'
        '#include "src/op/sound/se_update.inl"\n'
    )
    return {rel: sha_file(ROOT / rel) for rel in SOURCES}


def build_round(output: Path, label: str, target_mz, fixed: bytes, fixups: list[tuple[int, int]]) -> dict[str, object]:
    work = output / label / "op/source"
    work.parent.mkdir(parents=True)
    compact = copy_compact_snapshot(SNAPSHOT, work, "op")
    hashes = install_sources(work)
    if hashes != SOURCES:
        raise ValueError(f"{label}: copied maintained source identity drift")

    obj = work / "obj/th04/snd_se.obj"
    obj.unlink()
    tcc_op(work, output, f"snd-se-crossgame-{label}", "th04/snd_se.cpp")
    code = loose_segment_bytes(obj, "SHARED")
    candidate_fixups = object_fixups(obj)
    if code != fixed or candidate_fixups != fixups:
        raise ValueError(f"{label}: maintained sound object/fixup drift")

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
        raise ValueError(f"{label}: invalid linked OP MZ")
    if sha_file(exe) != BASE_EXE_SHA or sha_file(map_path) != BASE_MAP_SHA:
        raise ValueError(f"{label}: linked OP EXE/MAP drift")
    if [x.linear for x in linked.relocations] != [x.linear for x in target_mz.relocations]:
        raise ValueError(f"{label}: ordered relocation drift")

    producer = linked.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    play = linked.program_image[PLAY_START:PLAY_START + PLAY_SIZE]
    update = linked.program_image[UPDATE_START:UPDATE_START + UPDATE_SIZE]
    target_producer = target_mz.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if producer != target_producer or sha(producer) != PRODUCER_SHA:
        raise ValueError(f"{label}: linked producer raw mismatch")
    if sha(play) != PLAY_SHA or sha(update) != UPDATE_SHA:
        raise ValueError(f"{label}: linked sound function raw mismatch")

    return {
        "compact_snapshot": compact,
        "source_sha256": hashes,
        "object_code_sha256": sha(code),
        "object_fixups": [list(x) for x in candidate_fixups],
        "linked_exe_sha256": sha_file(exe),
        "linked_map_sha256": sha_file(map_path),
        "ordered_relocations": len(linked.relocations),
        "producer_sha256": sha(producer),
        "SND_SE_PLAY_sha256": sha(play),
        "_snd_se_update_sha256": sha(update),
        "raw_difference_counts": {
            "producer": 0,
            "SND_SE_PLAY": 0,
            "_snd_se_update": 0,
        },
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

    policy = source_policy()
    target_mz = parse_mz(TARGET.read_bytes())
    if not target_mz.valid or len(target_mz.relocations) != RELOCATIONS:
        raise ValueError("OP target MZ/relocation drift")
    target_producer = target_mz.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(target_producer) != PRODUCER_SHA:
        raise ValueError("OP target sound producer drift")
    if sha(target_mz.program_image[PLAY_START:PLAY_START + PLAY_SIZE]) != PLAY_SHA:
        raise ValueError("OP target play body drift")
    if sha(target_mz.program_image[UPDATE_START:UPDATE_START + UPDATE_SIZE]) != UPDATE_SHA:
        raise ValueError("OP target update body drift")

    base_obj = SNAPSHOT / "obj/th04/snd_se.obj"
    fixed = loose_segment_bytes(base_obj, "SHARED")
    fixups = object_fixups(base_obj)
    if len(fixed) != PRODUCER_SIZE or sha(fixed) != BASE_CODE_SHA or len(fixups) != 20:
        raise ValueError("baseline sound object/fixup drift")
    if mask_fixups(target_producer, fixups) != fixed:
        raise ValueError("OP target fixed producer drift")

    crossgame = crossgame_release_targets(output, fixed, fixups)
    builds = {
        label: build_round(output, label, target_mz, fixed, fixups)
        for label in ("a", "b")
    }
    stable = lambda row: {k: v for k, v in row.items() if k != "compact_snapshot"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise ValueError("independent sound cold rounds disagree")
    for rel, digest in SOURCES.items():
        if sha_file(ROOT / rel) != digest:
            raise ValueError(f"maintained source changed during replay: {rel}")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP SND_SE_PLAY + snd_se_update cross-game hybrid decoded exactness",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "sources": SOURCES,
        "source_policy": policy,
        "producer": {
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_sha256": PRODUCER_SHA,
            "fixed_sha256": BASE_CODE_SHA,
            "omf_fixup_count": len(fixups),
            "inter_function_padding": {
                "relative_offset": hex(PLAY_SIZE),
                "hex": "90",
                "authored_function_credit": False,
            },
        },
        "functions": {
            "SND_SE_PLAY": {
                "payload_offset": hex(PLAY_START),
                "size": PLAY_SIZE,
                "target_sha256": PLAY_SHA,
            },
            "_snd_se_update": {
                "payload_offset": hex(UPDATE_START),
                "size": UPDATE_SIZE,
                "target_sha256": UPDATE_SHA,
            },
        },
        "crossgame_release_targets": crossgame,
        "builds": builds,
        "conclusion": (
            "Restored TH05 OP and MAINE release targets independently contain exactly one "
            "copy of the complete TH04 fixed 0x86 sound producer after only legal OMF link "
            "operands are masked. Two cold TC4.02/TLINK rounds reproduce both reviewed "
            "TH04 functions, the full producer, accepted OP EXE/MAP, and all 804 ordered "
            "relocations. Cross-game evidence supports the bounded frame-free parameter "
            "and current-index compiler/register primitives; literal original-source "
            "spelling is not claimed."
        ),
        "limit": (
            "Decoded-function exactness only. The one-byte inter-function padding is layout "
            "scaffold, and packed-file/original-source-spelling exactness is not claimed."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha_file(path),
        "fixed_producer_sha256": BASE_CODE_SHA,
        "crossgame_offsets": {
            aid: data["producer_payload_offset"] for aid, data in crossgame.items()
        },
        "functions": {
            "SND_SE_PLAY": PLAY_SHA,
            "_snd_se_update": UPDATE_SHA,
        },
        "ordered_relocations": RELOCATIONS,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
