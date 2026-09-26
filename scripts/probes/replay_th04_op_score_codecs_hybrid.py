#!/usr/bin/env python3
"""Cold-replay OP SCORE codecs with the cross-game-corroborated byte-ROR primitive.

The maintained C++ remains responsible for the codec loops, data flow, calls,
checksums, and return behavior. Only the 8-bit rotate operation uses Borland
inline assembly, matching the older TH03 compiler workaround and the independent
TH03 OP/MAINL target bodies. This is a decoded-function replay, not a packed
OP.EXE exactness claim.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from replay_diet145f import check_toolchain  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402
from replay_th04_zun_source_only import source_closure  # noqa: E402
import replay_th04_op_stage_put as prior  # noqa: E402

VERSION = "v821"
SCORE_START = 0xC57A
SCORE_SIZE = 0x71D
GROUP_CODE_SHA256 = "1792cb712472c9bebb41e53da7720535202722a9f17ec347d84d99ea558e08b5"
BASE_EXE_SHA256 = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
BASE_MAP_SHA256 = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
TH03_SCORECRY = ROOT / "_reference/ReC98/th03/formats/scorecry.hpp"
TH03_SCORECRY_SHA256 = "f4c5265b445636c9a8d5e1df22b975b87153709fe4936297cd9d25bb497d5dfe"
TH03_DECODE_INTRO_COMMIT = "79aeb8dc"
TH03_DECODE_INTRO_SUBJECT = "[Decompilation] [th03] YUME.NEM: Decryption"
TH03_ENCODE_INTRO_COMMIT = "6d591888"
TH03_ENCODE_INTRO_SUBJECT = "[Decompilation] [th03] YUME.NEM: Encryption and saving"

CODECS = {
    "decode": {
        "source": "src/op/score/scoredec.cpp",
        "body": "src/op/score/scoredec.inl",
        "object": "scoredec.obj",
        "offset": 0xC57A,
        "size": 0xAD,
        "target_sha256": "5efe0d5065947fa7bc698dba06267ca16d3b34b3e90369907e14451fc9d0e2a5",
        "candidate_file": "th04/formats/scoredat/decode.cpp",
        "signature": "uint8_t pascal near scoredat_decode(void)\n",
        "primitive_markers": (
            "_AL = (section).key2;",
            "asm { ror tmp, 3; }",
            "tmp ^= _AL;",
        ),
    },
    "encode": {
        "source": "src/op/score/scoreenc.cpp",
        "body": "src/op/score/scoreenc.inl",
        "object": "scoreenc.obj",
        "offset": 0xC627,
        "size": 0x65,
        "target_sha256": "737bdcca37820fb3848004e60f12b6e8121470668ea058fb233be1bac7e3b69f",
        "candidate_file": "th04/formats/scoredat/encode.cpp",
        "signature": "void pascal near scoredat_encode(void)\n",
        "primitive_markers": (
            "_AL = hi.key2;",
            "asm { ror feedback, 3; }",
            "feedback ^= _AL;",
        ),
    },
}

CROSSGAME_TARGETS = {
    "th03-op-smoke": {
        "filename": "OP.EXE",
        "restored_sha256": "efd858aef69a240af3a27c747a5beae150f55f0b41b8afdd1eda1760a759ecc0",
        "program_size": 59770,
        "relocations": 607,
        "ror_offsets": (0xB1CB, 0xB222),
        "codec_bindings": {
            "encode_and_save": (0xB168, (0x63,)),
            "decode": (0xB20D, (0x15,)),
        },
    },
    "th03-mainl-smoke": {
        "filename": "MAINL.EXE",
        "restored_sha256": "92600c8858bb407516cac6a9d77538ebdf0c33522c4f6bd9194d569eb927134a",
        "program_size": 63276,
        "relocations": 677,
        "ror_offsets": (0xADBE, 0xAF6A),
        "codec_bindings": {
            "decode": (0xADA9, (0x15,)),
            "encode_and_save": (0xAEF0, (0x7A,)),
        },
    },
}
ROR_LOCAL = bytes.fromhex("C0 4E FF 03")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def output_dir(path: Path) -> Path:
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    out = path.resolve()
    if out.exists() or out == private or not out.is_relative_to(private):
        raise ValueError("output must be new below .analysis/reconstruction/probes")
    out.mkdir(parents=True)
    return out


def restore_crossgame_targets(output: Path) -> dict[str, object]:
    """Re-attest the byte-local ROR pattern in independent TH03 products."""
    manifest = load_target_manifest(ROOT / "config/targets.toml")
    diet, dosbox, config, _options, toolchain = check_toolchain("th04-op")
    results: dict[str, object] = {}
    cross = output / "crossgame"
    cross.mkdir()
    for artifact_id, spec in CROSSGAME_TARGETS.items():
        art = find_artifact(manifest, artifact_id)
        packed = read_verified_artifact(ROOT, art)
        work = cross / artifact_id
        work.mkdir()
        shutil.copy2(diet, work / "DIET.EXE")
        target_path = work / spec["filename"]
        target_path.write_bytes(packed)
        env = os.environ.copy()
        env.update(
            SDL_VIDEODRIVER="dummy",
            SDL_AUDIODRIVER="dummy",
            XDG_CACHE_HOME=str(work / "cache"),
            XDG_CONFIG_HOME=str(work / "config"),
            XDG_DATA_HOME=str(work / "data"),
        )
        command = [
            str(dosbox), "-defaultconf", "-defaultmapper", "-conf", str(config),
            "-fastlaunch", "-nogui", "-nomenu", "-exit", "-time-limit", "30",
            "-c", f'mount c "{work}"', "-c", "c:",
            "-c", f"diet.exe -ra {spec['filename'].lower()} > restore.log",
            "-c", "exit",
        ]
        completed = subprocess.run(
            command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=40
        )
        guest_log = work / "RESTORE.LOG"
        guest_text = (
            guest_log.read_bytes().decode("cp437", errors="replace")
            if guest_log.is_file() else ""
        )
        if completed.returncode or "Success!" not in guest_text:
            raise RuntimeError(f"{artifact_id}: pinned DIET restore failed")
        restored = target_path.read_bytes()
        mz = parse_mz(restored)
        if (
            not mz.valid
            or sha(restored) != spec["restored_sha256"]
            or len(mz.program_image) != spec["program_size"]
            or len(mz.relocations) != spec["relocations"]
        ):
            raise RuntimeError(f"{artifact_id}: restored target identity drift")

        hits: list[int] = []
        start = 0
        while True:
            found = mz.program_image.find(ROR_LOCAL, start)
            if found < 0:
                break
            hits.append(found)
            start = found + 1
        if tuple(hits) != spec["ror_offsets"]:
            raise RuntimeError(f"{artifact_id}: byte-ROR occurrence set drift")
        bound_hits = sorted(
            start + relative
            for _name, (start, relatives) in spec["codec_bindings"].items()
            for relative in relatives
        )
        if bound_hits != hits:
            raise RuntimeError(f"{artifact_id}: SCORE codec ROR/function binding drift")
        windows = []
        for found in hits:
            # Each homologous codec site stores the feedback byte at BP-1,
            # loads key2 into AL, rotates that byte, then XORs it with AL.
            if (
                found < 6
                or mz.program_image[found - 6:found - 3] != bytes.fromhex("88 46 FF")
                or mz.program_image[found - 3] != 0xA0
                or mz.program_image[found + 4:found + 7] != bytes.fromhex("30 46 FF")
            ):
                raise RuntimeError(f"{artifact_id}: byte-ROR surrounding mechanism drift")
            windows.append({
                "ror_offset": hex(found),
                "mechanism_hex": mz.program_image[found - 6:found + 7].hex(),
            })
        results[artifact_id] = {
            "packed_sha256": art["sha256"],
            "restored_sha256": sha(restored),
            "program_size": len(mz.program_image),
            "relocation_count": len(mz.relocations),
            "ror_offsets": [hex(x) for x in hits],
            "codec_bindings": {
                name: {
                    "target_function_start": hex(start),
                    "ror_relative_offsets": [hex(x) for x in relatives],
                }
                for name, (start, relatives) in spec["codec_bindings"].items()
            },
            "mechanism_windows": windows,
            "restore_log_sha256": sha_file(guest_log),
        }
    shutil.rmtree(cross)
    return {"toolchain": toolchain, "targets": results}


TH03_HISTORICAL_PROCS = {
    "th03-op-smoke": {
        "asm": "th03_op.asm",
        "decode": (TH03_DECODE_INTRO_COMMIT, "sub_B20D"),
        "encode_and_save": (TH03_ENCODE_INTRO_COMMIT, "sub_B168"),
    },
    "th03-mainl-smoke": {
        "asm": "th03_mainl.asm",
        "decode": (TH03_DECODE_INTRO_COMMIT, "sub_ADA9"),
        "encode_and_save": (TH03_ENCODE_INTRO_COMMIT, "sub_AEF0"),
    },
}


def historical_proc_block(commit: str, asm_path: str, proc: str) -> str:
    text = subprocess.check_output(
        [
            "git", "-C", str(ROOT / "_reference/ReC98"), "show",
            f"{commit}^:{asm_path}",
        ],
        text=True,
        encoding="cp932",
        errors="replace",
    )
    start = text.find(f"{proc}\tproc near")
    if start < 0:
        raise RuntimeError(f"missing historical proc {proc} in {asm_path} before {commit}")
    end = text.find(f"{proc}\tendp", start)
    if end < 0:
        raise RuntimeError(f"unterminated historical proc {proc} in {asm_path} before {commit}")
    return text[start:end]


def historical_codec_bindings() -> dict[str, object]:
    out: dict[str, object] = {}
    for artifact_id, funcs in TH03_HISTORICAL_PROCS.items():
        spec = CROSSGAME_TARGETS[artifact_id]
        bound: dict[str, object] = {}
        for name in ("decode", "encode_and_save"):
            commit, proc = funcs[name]
            block = historical_proc_block(commit, funcs["asm"], proc)
            normalized = block.lower().replace(" ", "")
            if "ror\t[bp+var_1],3" not in normalized:
                raise RuntimeError(f"historical {artifact_id}/{name} lost byte-memory ROR")
            start = int(proc.split("_")[1], 16)
            expected_start, relatives = spec["codec_bindings"][name]
            if start != expected_start:
                raise RuntimeError(f"historical {artifact_id}/{name} function-start drift")
            bound[name] = {
                "assembly": funcs["asm"],
                "pre_decompilation_commit": f"{commit}^",
                "historical_proc": proc,
                "target_function_start": hex(expected_start),
                "target_ror_offsets": [hex(expected_start + x) for x in relatives],
            }
        out[artifact_id] = bound
    return out

def th03_reference() -> dict[str, object]:
    if sha_file(TH03_SCORECRY) != TH03_SCORECRY_SHA256:
        raise RuntimeError("TH03 scorecry reference identity drift")
    text = TH03_SCORECRY.read_text(encoding="utf-8")
    markers = (
        "_AL = key2;",
        "_asm { ror feedback, 3 }",
        "feedback ^= _AL;",
        "_asm { ror tmp, 3 }",
        "tmp ^= _AL;",
    )
    if any(marker not in text for marker in markers):
        raise RuntimeError("TH03 single-byte rotate mechanism drift")
    introductions = {}
    for kind, commit, expected_subject in (
        ("decode", TH03_DECODE_INTRO_COMMIT, TH03_DECODE_INTRO_SUBJECT),
        ("encode", TH03_ENCODE_INTRO_COMMIT, TH03_ENCODE_INTRO_SUBJECT),
    ):
        subject = subprocess.check_output(
            ["git", "-C", str(ROOT / "_reference/ReC98"), "show", "-s", "--format=%s",
             commit],
            text=True,
        ).strip()
        if subject != expected_subject:
            raise RuntimeError(f"TH03 scorecry {kind} provenance commit drift")
        introductions[kind] = {"commit": commit, "subject": subject}
    return {
        "path": str(TH03_SCORECRY.relative_to(ROOT)),
        "sha256": TH03_SCORECRY_SHA256,
        "introductions": introductions,
        "historical_target_bindings": historical_codec_bindings(),
        "classification": "independent decompilation provenance; not original-source proof",
        "compiler_rationale": (
            "TH03 independently needed inline assembly only for the 8-bit ROR in both "
            "decode and encode; the decode introduction explicitly records that TC4.0J "
            "offers only 16-bit rotate intrinsics. The pre-decompilation OP/MAINL assembly "
            "binds the same byte-memory ROR to the historical codec functions rather than "
            "to unrelated coincidental instruction windows."
        ),
    }


def mask_fixups(code: bytes, target: bytes, obj: Path) -> tuple[list[tuple[int, int]], int]:
    fixups = [
        item
        for record in parse_omf(obj.read_bytes())
        if record.record_type == 0x9C
        for item in fixup_locations(record.data)
    ]
    left = bytearray(code)
    right = bytearray(target)
    for _kind, offset in fixups:
        if offset + 2 > len(left):
            raise RuntimeError("standalone codec FIXUPP escapes CODE")
        left[offset:offset + 2] = b"\0\0"
        right[offset:offset + 2] = b"\0\0"
    differences = sum(a != b for a, b in zip(left, right)) + abs(len(left) - len(right))
    return fixups, differences


def materialize_sources(work: Path) -> dict[str, str]:
    roots = tuple(spec["source"] for spec in CODECS.values())
    closure = source_closure(ROOT, roots)
    hashes = {relative: sha_file(ROOT / relative) for relative in closure}
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/op/score", work / "src/op/score", dirs_exist_ok=True)
    return hashes


def overlay_grouped_bodies(work: Path) -> None:
    """Keep the known SCORE ABI/layout scaffold and replace only maintained bodies."""
    for spec in CODECS.values():
        path = work / spec["candidate_file"]
        text = path.read_text(encoding="utf-8")
        signature = spec["signature"]
        if text.count(signature) != 1:
            raise RuntimeError(f"grouped codec signature drift: {path}")
        prefix = text[:text.index(signature)]
        replacement = (
            prefix
            + "typedef scoredat_section_t op_scoredat_section_t;\n\n"
            + signature
            + f'#include "{spec["body"]}"\n'
        )
        path.write_text(replacement, encoding="utf-8")


def verify_source_mechanism() -> None:
    for spec in CODECS.values():
        text = (ROOT / spec["body"]).read_text(encoding="utf-8")
        if any(marker not in text for marker in spec["primitive_markers"]):
            raise RuntimeError(f"maintained codec low-level primitive drift: {spec['body']}")
        forbidden = ("__emit__", "codestring", "db 0x", "#pragma codestring")
        if any(token in text.lower() for token in forbidden):
            raise RuntimeError(f"maintained codec contains byte-forcing surface: {spec['body']}")


def build_round(label: str, output: Path, target_program: bytes,
                target_relocs: list[int]) -> dict[str, object]:
    work = output / label / "op/source"
    work.parent.mkdir(parents=True)
    copy_compact_snapshot(prior.SNAPSHOT, work, "op")
    source_hashes = materialize_sources(work)

    standalone: dict[str, object] = {}
    for name, spec in CODECS.items():
        obj = work / "obj/th04" / spec["object"]
        obj.unlink(missing_ok=True)
        prior.tcc(work, output, f"{VERSION}-{name}-standalone-{label}", spec["source"])
        if not obj.is_file():
            raise RuntimeError(f"{label}/{name}: standalone object missing")
        desc = describe_omf(obj.read_bytes())
        if not desc["valid"] or "TC86 Borland C++ 4.02" not in desc["translator_comments"]:
            raise RuntimeError(f"{label}/{name}: standalone OMF identity drift")
        code = prior.segment_bytes(obj, "SCORE_TEXT")
        start = spec["offset"]
        target = target_program[start:start + spec["size"]]
        if len(code) != spec["size"] or sha(target) != spec["target_sha256"]:
            raise RuntimeError(f"{label}/{name}: standalone/target extent drift")
        fixups, nonfixup_differences = mask_fixups(code, target, obj)
        if nonfixup_differences:
            raise RuntimeError(f"{label}/{name}: standalone non-FIXUPP bytes differ")
        standalone[name] = {
            "code_size": len(code),
            "code_sha256": sha(code),
            "link_relevant_omf_sha256": link_relevant_omf_sha(obj),
            "fixups": [list(item) for item in fixups],
            "nonfixup_difference_count": 0,
        }

    overlay_grouped_bodies(work)
    group_obj = work / "obj/th04/scall.obj"
    group_obj.unlink(missing_ok=True)
    prior.tcc(work, output, f"{VERSION}-group-{label}", "th04/scall.cpp")
    desc = describe_omf(group_obj.read_bytes())
    if not desc["valid"] or "TC86 Borland C++ 4.02" not in desc["translator_comments"]:
        raise RuntimeError(f"{label}: grouped SCORE OMF identity drift")
    group_code = prior.segment_bytes(group_obj, "SCORE_TEXT")
    baseline_group = prior.segment_bytes(prior.SNAPSHOT / "obj/th04/scall.obj", "SCORE_TEXT")
    if (
        len(group_code) != SCORE_SIZE
        or sha(group_code) != GROUP_CODE_SHA256
        or group_code != baseline_group
    ):
        raise RuntimeError(f"{label}: grouped SCORE producer changed")

    exe = work / "bin/th04/op.exe"
    map_path = work / "obj/th04/op.map"
    exe.unlink()
    map_path.unlink()
    prior.run_checked(
        ["wine", str(prior.RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
        work, output / f"link-{label}.log",
    )
    raw = exe.read_bytes()
    image = parse_mz(raw)
    if (
        not image.valid
        or sha(raw) != BASE_EXE_SHA256
        or sha_file(map_path) != BASE_MAP_SHA256
        or [item.linear for item in image.relocations] != target_relocs
    ):
        raise RuntimeError(f"{label}: grouped OP link/layout drift")

    linked: dict[str, object] = {}
    for name, spec in CODECS.items():
        start = spec["offset"]
        body = image.program_image[start:start + spec["size"]]
        target = target_program[start:start + spec["size"]]
        if body != target or sha(body) != spec["target_sha256"]:
            raise RuntimeError(f"{label}/{name}: linked codec is not target exact")
        linked[name] = {
            "payload_offset": hex(start),
            "size": spec["size"],
            "sha256": sha(body),
            "raw_difference_count": 0,
        }

    if any(sha_file(ROOT / relative) != digest for relative, digest in source_hashes.items()):
        raise RuntimeError(f"{label}: maintained codec source changed during build")

    return {
        "source_sha256": source_hashes,
        "standalone": standalone,
        "group_code_size": len(group_code),
        "group_code_sha256": sha(group_code),
        "group_link_relevant_omf_sha256": link_relevant_omf_sha(group_obj),
        "linked_exe_sha256": sha(raw),
        "linked_map_sha256": sha_file(map_path),
        "ordered_relocations": len(image.relocations),
        "linked_functions": linked,
    }


def stable_round(round_: dict[str, object]) -> dict[str, object]:
    return round_


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = output_dir(args.output_dir)

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    if sha_file(prior.RUNNER) != prior.RUNNER_SHA:
        raise RuntimeError("pinned DOS runner identity drift")
    for path, expected in prior.INPUTS.items():
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned OP replay input drift: {path}")
    if sha_file(prior.SNAPSHOT / "bin/th04/op.exe") != BASE_EXE_SHA256:
        raise RuntimeError("baseline OP candidate identity drift")
    if sha_file(prior.SNAPSHOT / "obj/th04/op.map") != BASE_MAP_SHA256:
        raise RuntimeError("baseline OP MAP identity drift")

    verify_source_mechanism()
    th03 = th03_reference()
    crossgame = restore_crossgame_targets(output)

    target_mz = parse_mz(prior.TARGET.read_bytes())
    if not target_mz.valid or len(target_mz.relocations) != prior.EXPECTED_RELOCATIONS:
        raise RuntimeError("restored TH04 OP target identity/layout drift")
    target_relocs = [item.linear for item in target_mz.relocations]

    rounds = {
        label: build_round(label, output, target_mz.program_image, target_relocs)
        for label in ("a", "b")
    }
    if stable_round(rounds["a"]) != stable_round(rounds["b"]):
        raise RuntimeError("OP score-codec cold rounds differ")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": (
            "TH04 OP SCORE codec decoded-exact replay using maintained C++ plus a "
            "cross-game-corroborated symbolic 8-bit ROR primitive"
        ),
        "artifact": "th04-op",
        "target_restored_sha256": prior.INPUTS[prior.TARGET],
        "target_program_sha256": sha(target_mz.program_image),
        "th03_reference": th03,
        "crossgame_target_corroboration": crossgame,
        "mechanism": (
            "Only key2-to-AL, byte-local ROR by 3, and XOR with AL are low-level. "
            "All codec loops, checksums, far calls, memory accesses, and control flow remain C++."
        ),
        "builds": rounds,
        "exact_functions": {
            name: {
                "payload_offset": hex(spec["offset"]),
                "size": spec["size"],
                "target_sha256": spec["target_sha256"],
            }
            for name, spec in CODECS.items()
        },
        "limit": (
            "Decoded SCORE functions and producer only. The linked OP candidate retains "
            "unrelated artifact differences and this does not establish packed-file exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha_file(path),
        "decode_raw_difference_count": 0,
        "encode_raw_difference_count": 0,
        "group_code_sha256": GROUP_CODE_SHA256,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
