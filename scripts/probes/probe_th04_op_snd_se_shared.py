#!/usr/bin/env python3
"""Bound the TH04 OP sound blockers with same-game producer evidence.

This is a diagnostic/provenance replay only. It proves that MAIN and OP share
one fixed 0x86 snd_se producer and that the decompilation-shaped helper form can
reproduce OP exactly. It deliberately grants no authored-source or decoded-exact
credit because the required low-level helper spelling first appears in a
ReC98 decompilation commit and is explicitly marked as modder-facing bloat.
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
from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from replay_th04_op_help_put import SNAPSHOT, loose_segment_bytes, tcc_op  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_zun_source_only import source_closure  # noqa: E402

TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
TARGET_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
BASE_EXE_SHA = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
BASE_MAP_SHA = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
BASE_CODE_SHA = "2300d500c2b4d9701f49ffec4647cb4e199296543253796ddb1f6804603dae9f"
RELOCATIONS = 804

PRODUCER_START = 0xE2F2
PRODUCER_SIZE = 0x86
PRODUCER_SHA = "83a91c2784779561c19afb76b307a99ab0d92974be0b2004354d5116c27bb297"
PLAY_START = 0xE2F2
PLAY_SIZE = 0x39
PLAY_SHA = "fea779b877971c519c0729a6f0546e60f37225a2a675cd3fa4dc0975eef884b8"
UPDATE_START = 0xE32C
UPDATE_SIZE = 0x4C
UPDATE_SHA = "a9e451577270f1d448bd39c71b2c4e69570357b1090111740df0b440931cf5f5"

NATURAL_PLAY_SIZE = 0x3C
NATURAL_PLAY_SHA = "4519e45ef064d7af3fb2d4be6d870277e558dfc3bb940cbe8fa5b70a7653e624"
NATURAL_UPDATE_SIZE = 0x4D
NATURAL_UPDATE_SHA = "4e317f24d1f54c95e37ce43450bb187bdec40909a30c3898e0ec3e55959106a1"

MAIN_PRODUCER_FILE_OFFSET = 0x150B2
MAIN_PLAY_SHA = "0a8e69ea753b8b0229d0eef5b225d7f4482c8f1bbc6b2792c47a5b85650cf6b5"
MAIN_UPDATE_SHA = "6ae4c660afc2e80fa2982cde8c02cb8c754ed0e161d4760f147acadc32acf561"
MAIN_MAP = ROOT / ".analysis/gpt-web/v401-master-vs-object-replay-001/a/source/obj/th04/main.map"

REC98 = ROOT / "_reference/ReC98"
DECOMP_COMMIT = "c85f444b07debfdf02d842ad51d7b4d918198f94"
DECOMP_PATH = "th02/snd/se.cpp"

NATURAL_SOURCES = {
    "SND_SE_PLAY": "src/shared/sound/se_play.cpp",
    "_snd_se_update": "src/op/sound/se_update.cpp",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def new_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="op-snd-se-shared-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def object_fixups(path: Path) -> list[tuple[int, int]]:
    return [
        item
        for record in parse_omf(path.read_bytes())
        if record.record_type == 0x9C
        for item in fixup_locations(record.data)
    ]


def mask_fixups(data: bytes, fixups: list[tuple[int, int]]) -> bytes:
    out = bytearray(data)
    for kind, offset in fixups:
        width = 2 if kind == 1 else 4
        if offset + width > len(out):
            raise ValueError(f"fixup outside producer: {kind=} {offset=:#x}")
        out[offset:offset + width] = b"\0" * width
    return bytes(out)


def compile_natural(name: str, source: str, output: Path) -> dict[str, object]:
    expected = {
        "SND_SE_PLAY": (NATURAL_PLAY_SIZE, NATURAL_PLAY_SHA),
        "_snd_se_update": (NATURAL_UPDATE_SIZE, NATURAL_UPDATE_SHA),
    }[name]
    work = output / "natural" / name / "op/source"
    work.parent.mkdir(parents=True)
    copy_compact_snapshot(SNAPSHOT, work, "op")
    closure = source_closure(ROOT, (source,))
    hashes = {}
    for rel in closure:
        src = ROOT / rel
        dst = work / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        hashes[rel] = sha_file(src)
    before = {p.name for p in (work / "obj/th04").glob("*.obj")}
    tcc_op(work, output, f"natural-{name}", source)
    objects = [p for p in (work / "obj/th04").glob("*.obj") if p.name not in before]
    if len(objects) != 1:
        raise ValueError(f"{name}: expected one natural object, got {objects}")
    code = loose_segment_bytes(objects[0], "SHARED")
    if len(code) != expected[0] or sha(code) != expected[1]:
        raise ValueError(f"{name}: natural codegen drift")
    return {
        "source": source,
        "source_sha256": hashes,
        "code_size": len(code),
        "code_sha256": sha(code),
        "target_size": PLAY_SIZE if name == "SND_SE_PLAY" else UPDATE_SIZE,
        "decoded_exact": False,
    }


def same_game_shared_producer(op_target: bytes, fixups: list[tuple[int, int]]) -> dict[str, object]:
    manifest = load_target_manifest(ROOT / "config/targets.toml")
    main_raw = read_verified_artifact(ROOT, find_artifact(manifest, "th04-main"))
    main = main_raw[MAIN_PRODUCER_FILE_OFFSET:MAIN_PRODUCER_FILE_OFFSET + PRODUCER_SIZE]
    op = op_target[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if len(main) != PRODUCER_SIZE or len(op) != PRODUCER_SIZE:
        raise ValueError("MAIN/OP producer extent drift")
    if sha(main[:PLAY_SIZE]) != MAIN_PLAY_SHA:
        raise ValueError("MAIN SND_SE_PLAY identity drift")
    if sha(main[PLAY_SIZE + 1:]) != MAIN_UPDATE_SHA:
        raise ValueError("MAIN snd_se_update identity drift")
    if sha(op) != PRODUCER_SHA:
        raise ValueError("OP producer identity drift")
    masked_main = mask_fixups(main, fixups)
    masked_op = mask_fixups(op, fixups)
    if masked_main != masked_op or sha(masked_op) != BASE_CODE_SHA:
        raise ValueError("MAIN/OP fixed producer bytes diverged")

    main_map = MAIN_MAP.read_text(encoding="cp437", errors="replace")
    op_map = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437", errors="replace")
    main_owner = "130E:07D2 0086 C=CODE   S=SHARED         G=(none)  M=th04/snd_se.cpp"
    op_owner = "0DA1:08E2 0086 C=CODE   S=SHARED         G=(none)  M=th04/snd_se.cpp"
    if main_owner not in main_map or op_owner not in op_map:
        raise ValueError("MAIN/OP map ownership drift")
    return {
        "main_owner": main_owner,
        "op_owner": op_owner,
        "producer_size": PRODUCER_SIZE,
        "fixup_count": len(fixups),
        "masked_fixed_sha256": sha(masked_op),
        "masked_main_op_equal": True,
        "raw_difference_count": sum(a != b for a, b in zip(main, op)),
        "source_credit": False,
        "finding": (
            "MAIN and OP independently map the same 0x86 th04/snd_se.cpp "
            "contribution and have identical fixed bytes after legal fixups "
            "are masked. This proves shared binary production, not original "
            "source spelling."
        ),
    }


def decompilation_provenance() -> dict[str, object]:
    subject = subprocess.run(
        ["git", "-C", str(REC98), "show", "-s", "--format=%s", DECOMP_COMMIT],
        check=True, capture_output=True,
    ).stdout.decode("utf-8", errors="replace").strip()
    source = subprocess.run(
        ["git", "-C", str(REC98), "show", f"{DECOMP_COMMIT}:{DECOMP_PATH}"],
        check=True, capture_output=True,
    ).stdout.decode("shift_jis", errors="replace")
    markers = [
        "MODDERS: Just use [new_se] directly.",
        "_BX = _SP;",
        "MODDERS: Just replace with [snd_se_playing].",
        "_BL = snd_se_playing;",
        "_BH ^= _BH;",
    ]
    if "[Decompilation]" not in subject:
        raise ValueError("expected decompilation provenance marker missing")
    missing = [marker for marker in markers if marker not in source]
    if missing:
        raise ValueError(f"decompilation helper markers drifted: {missing}")
    return {
        "repository": "_reference/ReC98",
        "commit": DECOMP_COMMIT,
        "path": DECOMP_PATH,
        "subject": subject,
        "markers": markers,
        "source_credit": False,
        "finding": (
            "The exact helper spelling first appears in a ReC98 decompilation "
            "commit and is explicitly labeled as bloat to replace for modders. "
            "It is therefore target-derived provenance, not independent "
            "authored-source evidence."
        ),
    }


def install_diagnostic_sources(work: Path) -> dict[str, str]:
    closure = source_closure(ROOT, (*NATURAL_SOURCES.values(), "src/shared/sound/impl.hpp", "src/shared/sound/api.hpp"))
    source_hashes = {}
    for rel in closure:
        src = ROOT / rel
        dst = work / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        source_hashes[rel] = sha_file(src)

    impl = work / "src/shared/sound/impl.hpp"
    text = impl.read_text()
    anchor = "extern unsigned char snd_se_frame;\n\n"
    helper = (
        "extern unsigned char snd_se_frame;\n\n"
        "inline uint16_t snd_se_current_index() {\n"
        "\t_BL = snd_se_playing;\n"
        "\t_BH ^= _BH;\n"
        "\treturn _BX;\n"
        "}\n\n"
    )
    if anchor not in text:
        raise ValueError("diagnostic impl anchor drift")
    impl.write_text(text.replace(anchor, helper, 1))

    play = work / "src/shared/sound/se_play.cpp"
    play.write_text(
        '#pragma option -zCSHARED -k-\n\n'
        '#include "src/shared/sound/api.hpp"\n'
        '#include "src/shared/sound/impl.hpp"\n\n'
        'extern unsigned char snd_se_mode;\n\n'
        'void far pascal snd_se_play(int new_se)\n'
        '{\n'
        '\tregister int se = snd_get_param(new_se);\n'
        '\tif(!snd_se_mode) {\n\t\treturn;\n\t}\n'
        '\tif(snd_se_playing == SE_NONE) {\n'
        '\t\tsnd_se_playing = se;\n'
        '\t} else if(snd_se_priorities[snd_se_current_index()] <= snd_se_priorities[se]) {\n'
        '\t\tsnd_se_playing = se;\n'
        '\t\tsnd_se_frame = 0;\n'
        '\t}\n'
        '}\n'
    )

    update_cpp = work / "src/op/sound/se_update.cpp"
    text = update_cpp.read_text()
    old = '#include "src/shared/platform/x86.hpp"\n'
    if old not in text:
        raise ValueError("diagnostic update include anchor drift")
    update_cpp.write_text(text.replace(old, '#include "src/shared/sound/impl.hpp"\n', 1))

    update_inl = work / "src/op/sound/se_update.inl"
    text = update_inl.read_text()
    old = "snd_se_priority_frames[(unsigned int)snd_se_playing]"
    if old not in text:
        raise ValueError("diagnostic update index anchor drift")
    update_inl.write_text(text.replace(old, "snd_se_priority_frames[snd_se_current_index()]", 1))

    wrapper = work / "th04/snd_se.cpp"
    wrapper.write_text(
        '#include "src/shared/sound/se_play.cpp"\n'
        '#pragma codestring "\\x90"\n\n'
        'static const int PMD_INTERRUPT = PMD;\n'
        'extern "C" int far pascal bgm_sound(int num);\n\n'
        '#include "src/op/sound/se_update.inl"\n'
    )
    return source_hashes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    output = new_output(args.output_dir)

    if sha_file(RUNNER) != RUNNER_SHA:
        raise ValueError("pinned DOS runner drift")
    if sha_file(TARGET) != TARGET_SHA:
        raise ValueError("OP restored target identity drift")

    target_mz = parse_mz(TARGET.read_bytes())
    if not target_mz.valid or len(target_mz.relocations) != RELOCATIONS:
        raise ValueError("OP target MZ/relocation drift")
    target = target_mz.program_image
    if sha(target[PLAY_START:PLAY_START + PLAY_SIZE]) != PLAY_SHA:
        raise ValueError("OP SND_SE_PLAY target drift")
    if sha(target[UPDATE_START:UPDATE_START + UPDATE_SIZE]) != UPDATE_SHA:
        raise ValueError("OP snd_se_update target drift")

    base_obj = SNAPSHOT / "obj/th04/snd_se.obj"
    base_code = loose_segment_bytes(base_obj, "SHARED")
    fixups = object_fixups(base_obj)
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_CODE_SHA:
        raise ValueError("baseline snd_se object drift")
    if len(fixups) != 20:
        raise ValueError("baseline snd_se fixup count drift")
    if mask_fixups(target[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE], fixups) != base_code:
        raise ValueError("target fixed bytes no longer match baseline producer")

    natural = {
        name: compile_natural(name, source, output)
        for name, source in NATURAL_SOURCES.items()
    }
    provenance = decompilation_provenance()
    same_game = same_game_shared_producer(target, fixups)

    rounds = {}
    for label in ("a", "b"):
        work = output / "diagnostic" / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        source_hashes = install_diagnostic_sources(work)

        obj = work / "obj/th04/snd_se.obj"
        obj.unlink()
        tcc_op(work, output, f"diagnostic-{label}", "th04/snd_se.cpp")
        code = loose_segment_bytes(obj, "SHARED")
        candidate_fixups = object_fixups(obj)
        if code != base_code or candidate_fixups != fixups:
            raise ValueError(f"{label}: diagnostic object producer drift")

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
        if [x.linear for x in linked.relocations] != [x.linear for x in target_mz.relocations]:
            raise ValueError(f"{label}: ordered relocation drift")
        if sha_file(exe) != BASE_EXE_SHA or sha_file(map_path) != BASE_MAP_SHA:
            raise ValueError(f"{label}: final OP EXE/MAP drift")

        producer = linked.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        play = linked.program_image[PLAY_START:PLAY_START + PLAY_SIZE]
        update = linked.program_image[UPDATE_START:UPDATE_START + UPDATE_SIZE]
        if producer != target[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]:
            raise ValueError(f"{label}: diagnostic producer raw mismatch")
        if sha(play) != PLAY_SHA or sha(update) != UPDATE_SHA:
            raise ValueError(f"{label}: diagnostic function raw mismatch")

        rounds[label] = {
            "compact_snapshot": compact,
            "source_sha256": source_hashes,
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

    stable_a = {k: v for k, v in rounds["a"].items() if k != "compact_snapshot"}
    stable_b = {k: v for k, v in rounds["b"].items() if k != "compact_snapshot"}
    if stable_a != stable_b:
        raise ValueError("diagnostic cold rounds disagree")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-op",
        "claim_scope": "OP shared sound producer diagnostic and source-provenance bound",
        "accepted_state": "blocked",
        "source_credit": False,
        "target_restored_sha256": TARGET_SHA,
        "natural": natural,
        "same_game_shared_producer": same_game,
        "decompilation_provenance": provenance,
        "diagnostic_exact_candidate": {
            "source_credit": False,
            "reason": (
                "The exact low-level parameter/current-index helpers are "
                "target-derived decompilation constructs. Exact diagnostic "
                "code generation cannot promote authored-source acceptance."
            ),
            "rounds": rounds,
        },
        "conclusion": (
            "The two OP sound blockers are now bounded to source provenance: "
            "their same-game 0x86 producer is shared with MAIN and an exact "
            "decompilation-shaped candidate is reproducible, but the helper "
            "spelling has no independent authored-source provenance. Both "
            "functions remain blocked."
        ),
        "limit": (
            "No decoded-exact, packed-file, original-source-spelling, or "
            "whole-artifact exactness credit is granted."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "accepted_state": receipt["accepted_state"],
        "natural_sizes": {k: v["code_size"] for k, v in natural.items()},
        "diagnostic_exact": True,
        "source_credit": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
