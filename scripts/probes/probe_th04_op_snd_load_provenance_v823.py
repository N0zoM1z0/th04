#!/usr/bin/env python3
"""Bound TH04 OP SND_LOAD to one two-byte source-provenance question.

This probe deliberately does not promote SND_LOAD. It proves that replacing the
candidate decompilation's ordinary pseudo-register assignment with TC4J inline
assembly changes exactly the target's two MOV bytes, while preserving the
complete 234-byte producer extent, MAP ownership, and all ordered relocations.

It also scans the pinned v401 TC86 object corpus for the same 89 C3 encoding and
binds the sole historical hit to an explicit-asm ReC98 decompilation source.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
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
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from replay_th04_op_help_put import SNAPSHOT, loose_segment_bytes, tcc_op  # noqa: E402

TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
TARGET_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
BASE_EXE_SHA = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
DIAG_EXE_SHA = "b2785d3ed2203ef6e9f5af8b3817e3a0c7a248e5440fac731bfaea50769c3c5f"
BASE_MAP_SHA = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
RELOCATIONS = 804

START = 0xDDCA
SIZE = 0xEA
MOV_OFFSET = 0xC1
MOV_START = START + MOV_OFFSET
TARGET_SLICE_SHA = "50d62cb466990971edcfe5bdbf78ce99e815af2027cc3d21951db8e73fd6659f"
NATURAL_SLICE_SHA = "7f04ce7bae23c3805dde0bacd5e7c936797be4e2a2f1c5feb189a9c75e2d61eb"
NATURAL_CODE_SHA = "4d0e4b2577d371061f460eb53691694f4b76c23e198e88de6c9341a8a19cef40"
DIAG_CODE_SHA = "1a486ee1cde1e0766d08ce0efa316ea36002ff836644971977494920b397478e"

WRAPPER = "th04/snd_load.cpp"
INNER = "th04/snd/load.cpp"
INNER_SHA = "9777ebd973098395823bfcfbc53daa451d2c6db62500aa038873e72729c1a39a"
WRAPPER_SHA = "d955e7916647541010a8f972e270c86eb2575df4b369b18a1cfc81ce8172d945"
BASE_OBJ_SHA = "55a0f19718afc6470fc3f857b24eea4c24393eb5fe437a3fe1c8cba4140d71d2"

V401 = ROOT / ".analysis/gpt-web/v401-master-vs-object-replay-001/a/source"
V401_PLAYER_OBJ = "obj/th02/player_b.obj"
V401_PLAYER_OBJ_SHA = "b77d06ba1ca3ed6b37202d16a6a896bd1e9d2fc1cb18501dd7615d4002c40f1c"
V401_PLAYER_SOURCE = "th02/main/player/bomb.cpp"
V401_PLAYER_SOURCE_SHA = "f26f438a8886157d254006645a1d66f6ea809c932d777418c6f42a427023a95e"
V401_OBJ_FILES = 437
V401_TC86_FILES = 356
V401_UNIQUE_TC86 = 345

REC98 = ROOT / "_reference/ReC98"
REC98_HEAD = "b6ba5b0a529edbb31efdf8c0e939263804f8ee47"
TH04_DECOMP = "d9858113d8135d265b88e0325d40fc237e6b9763"
TH02_BOMB_DECOMP = "522976d6687603576278f1d925d9d8631748f1d2"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def new_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="op-snd-load-v823-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REC98), *args],
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8", errors="replace").strip()


def omf_index(data: bytes, pos: int) -> tuple[int, int]:
    first = data[pos]
    if first < 0x80:
        return first, pos + 1
    return ((first & 0x7F) << 8) | data[pos + 1], pos + 2


def pstr(data: bytes, pos: int) -> tuple[str, int]:
    n = data[pos]
    return data[pos + 1:pos + 1 + n].decode("latin-1", errors="replace"), pos + 1 + n


def scan_v401_corpus() -> dict[str, object]:
    objects = list(V401.rglob("*.obj")) + list(V401.rglob("*.OBJ"))
    tc86_files = 0
    unique: dict[str, Path] = {}
    hits: list[dict[str, object]] = []

    for path in objects:
        raw = path.read_bytes()
        if b"TC86 Borland C++ 4.02" not in raw:
            continue
        tc86_files += 1
        digest = sha(raw)
        if digest in unique:
            continue
        unique[digest] = path

        records = parse_omf(raw)
        names = [""]
        segments: list[tuple[str, str]] = []
        for record in records:
            if record.record_type == 0x96:
                pos = 0
                while pos < len(record.data):
                    name, pos = pstr(record.data, pos)
                    names.append(name)
            elif record.record_type == 0x98:
                data = record.data
                pos = 1 + (3 if (data[0] >> 5) == 0 else 2)
                name_i, pos = omf_index(data, pos)
                class_i, pos = omf_index(data, pos)
                _overlay_i, pos = omf_index(data, pos)
                segments.append((
                    names[name_i] if name_i < len(names) else "",
                    names[class_i] if class_i < len(names) else "",
                ))

        for record in records:
            if record.record_type != 0xA0:
                continue
            data = record.data
            seg_i, pos = omf_index(data, 0)
            offset = int.from_bytes(data[pos:pos + 2], "little")
            pos += 2
            if not (1 <= seg_i <= len(segments)):
                continue
            if segments[seg_i - 1][1] != "CODE":
                continue
            payload = data[pos:]
            search = 0
            while True:
                found = payload.find(bytes((0x89, 0xC3)), search)
                if found < 0:
                    break
                strings = [
                    match.group().decode("latin-1", errors="replace")
                    for match in re.finditer(rb"[ -~]{4,}", raw)
                    if b".cpp" in match.group().lower()
                ]
                hits.append({
                    "path": str(path.relative_to(V401)),
                    "object_sha256": digest,
                    "segment": segments[seg_i - 1][0],
                    "segment_offset": offset + found,
                    "source_strings": strings[:8],
                })
                search = found + 1

    if (
        len(objects) != V401_OBJ_FILES
        or tc86_files != V401_TC86_FILES
        or len(unique) != V401_UNIQUE_TC86
        or len(hits) != 1
    ):
        raise ValueError(
            f"v401 corpus drift: files={len(objects)} tc86={tc86_files} "
            f"unique={len(unique)} hits={hits}"
        )
    hit = hits[0]
    if (
        hit["path"] != V401_PLAYER_OBJ
        or hit["object_sha256"] != V401_PLAYER_OBJ_SHA
        or hit["segment"] != "PLAYER_B_TEXT"
        or hit["segment_offset"] != 0xC6
    ):
        raise ValueError(f"unexpected v401 89 C3 hit: {hit}")

    source = V401 / V401_PLAYER_SOURCE
    if sha_file(source) != V401_PLAYER_SOURCE_SHA:
        raise ValueError("v401 TH02 bomb source identity drift")
    text = source.read_text(errors="replace")
    if "asm { mov	bx, ax; }" not in text:
        raise ValueError("v401 TH02 explicit MOV BX,AX source marker drift")

    return {
        "object_files": len(objects),
        "tc86_files": tc86_files,
        "unique_tc86_objects": len(unique),
        "mov_89c3_hits": hits,
        "finding": (
            "The only 89 C3 in the pinned v401 TC86 corpus is in th02/player_b.obj, "
            "whose source explicitly spells asm { mov bx, ax; }. No natural C/C++ "
            "object in this corpus emits 89 C3."
        ),
    }


def provenance() -> dict[str, object]:
    if git_text("rev-parse", "HEAD") != REC98_HEAD:
        raise ValueError("pinned ReC98 HEAD drift")

    th04_subject = git_text("show", "-s", "--format=%s", TH04_DECOMP)
    th02_subject = git_text("show", "-s", "--format=%s", TH02_BOMB_DECOMP)
    if "[Decompilation]" not in th04_subject or "[Decompilation]" not in th02_subject:
        raise ValueError("expected ReC98 decompilation subjects drifted")

    th04_source = git_text("show", f"{TH04_DECOMP}:th04/snd/load.cpp")
    th02_source = git_text("show", f"{TH02_BOMB_DECOMP}:th02/main/player/bomb.cpp")
    if "_BX = _AX;" not in th04_source:
        raise ValueError("TH04 decompilation handle-copy marker drift")
    if "asm { mov	bx, ax; }" not in th02_source:
        raise ValueError("TH02 decompilation explicit MOV marker drift")

    return {
        "rec98_head": REC98_HEAD,
        "th04_snd_load": {
            "commit": TH04_DECOMP,
            "subject": th04_subject,
            "source_marker": "_BX = _AX;",
        },
        "th02_bomb": {
            "commit": TH02_BOMB_DECOMP,
            "subject": th02_subject,
            "source_marker": "asm { mov bx, ax; }",
        },
        "source_credit": False,
        "finding": (
            "Both the TH04 snd_load candidate line and the only historical v401 "
            "explicit-asm 89 C3 witness originate in ReC98 [Decompilation] commits. "
            "They explain code generation but do not independently attest ZUN's source."
        ),
    }


def build_round(output: Path, label: str, diagnostic: bool) -> dict[str, object]:
    work = output / ("diagnostic" if diagnostic else "natural") / label / "op/source"
    work.parent.mkdir(parents=True)
    compact = copy_compact_snapshot(SNAPSHOT, work, "op")

    inner = work / INNER
    wrapper = work / WRAPPER
    if sha_file(inner) != INNER_SHA or sha_file(wrapper) != WRAPPER_SHA:
        raise ValueError(f"{label}: pinned snd_load source identity drift")

    if diagnostic:
        text = inner.read_text()
        old = chr(9) + "_BX = _AX;" + chr(10)
        new = chr(9) + "asm { mov bx, ax; }" + chr(10)
        if text.count(old) != 1:
            raise ValueError("diagnostic handle-copy anchor drift")
        inner.write_text(text.replace(old, new, 1))

    obj = work / "obj/th04/snd_load.obj"
    obj.unlink()
    tcc_op(work, output, f"snd-load-{'diagnostic' if diagnostic else 'natural'}-{label}", WRAPPER)

    code = loose_segment_bytes(obj, "SHARED")
    expected_code_sha = DIAG_CODE_SHA if diagnostic else NATURAL_CODE_SHA
    expected_mov = bytes((0x89, 0xC3)) if diagnostic else bytes((0x8B, 0xD8))
    if len(code) != SIZE or sha(code) != expected_code_sha or code[MOV_OFFSET:MOV_OFFSET + 2] != expected_mov:
        raise ValueError(f"{label}: snd_load object codegen drift")

    exe = work / "bin/th04/op.exe"
    map_path = work / "obj/th04/op.map"
    exe.unlink()
    map_path.unlink()
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", "@obj" + chr(92) + "th04" + chr(92) + "op.@l"],
        work,
        output / f"link-{'diagnostic' if diagnostic else 'natural'}-{label}.log",
        timeout=300,
    )

    linked = parse_mz(exe.read_bytes())
    if not linked.valid or len(linked.relocations) != RELOCATIONS:
        raise ValueError(f"{label}: linked OP identity drift")
    if sha_file(map_path) != BASE_MAP_SHA:
        raise ValueError(f"{label}: OP MAP ownership drift")
    if "0DA1:03BA 00EA C=CODE   S=SHARED         G=(none)  M=th04/snd_load.cpp ACBP=28" not in map_path.read_text(encoding="cp437"):
        raise ValueError(f"{label}: snd_load MAP owner drift")

    expected_exe_sha = DIAG_EXE_SHA if diagnostic else BASE_EXE_SHA
    if sha_file(exe) != expected_exe_sha:
        raise ValueError(f"{label}: linked OP EXE drift")

    body = linked.program_image[START:START + SIZE]
    expected_slice_sha = TARGET_SLICE_SHA if diagnostic else NATURAL_SLICE_SHA
    if sha(body) != expected_slice_sha or body[MOV_OFFSET:MOV_OFFSET + 2] != expected_mov:
        raise ValueError(f"{label}: linked SND_LOAD slice drift")

    return {
        "compact_snapshot": compact,
        "object_code_sha256": sha(code),
        "object_mov_hex": code[MOV_OFFSET:MOV_OFFSET + 2].hex(),
        "linked_exe_sha256": sha_file(exe),
        "linked_map_sha256": sha_file(map_path),
        "ordered_relocations": len(linked.relocations),
        "snd_load_sha256": sha(body),
        "snd_load_mov_hex": body[MOV_OFFSET:MOV_OFFSET + 2].hex(),
        "program_image_sha256": sha(linked.program_image),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output = new_output(args.output_dir)

    if sha_file(RUNNER) != RUNNER_SHA:
        raise ValueError("pinned DOS runner drift")
    if sha_file(TARGET) != TARGET_SHA:
        raise ValueError("OP restored target identity drift")
    if sha_file(SNAPSHOT / INNER) != INNER_SHA or sha_file(SNAPSHOT / WRAPPER) != WRAPPER_SHA:
        raise ValueError("pinned OP snd_load source snapshot drift")
    if sha_file(SNAPSHOT / "obj/th04/snd_load.obj") != BASE_OBJ_SHA:
        raise ValueError("pinned natural snd_load object drift")

    target_mz = parse_mz(TARGET.read_bytes())
    if not target_mz.valid or len(target_mz.relocations) != RELOCATIONS:
        raise ValueError("OP target MZ/relocation identity drift")
    target_body = target_mz.program_image[START:START + SIZE]
    if (
        len(target_body) != SIZE
        or sha(target_body) != TARGET_SLICE_SHA
        or target_body[MOV_OFFSET:MOV_OFFSET + 2] != bytes((0x89, 0xC3))
    ):
        raise ValueError("OP target SND_LOAD identity drift")

    natural = {label: build_round(output, label, False) for label in ("a", "b")}
    diagnostic = {label: build_round(output, label, True) for label in ("a", "b")}

    def stable(round_: dict[str, object]) -> dict[str, object]:
        return {k: v for k, v in round_.items() if k != "compact_snapshot"}

    if stable(natural["a"]) != stable(natural["b"]):
        raise ValueError("natural cold rounds disagree")
    if stable(diagnostic["a"]) != stable(diagnostic["b"]):
        raise ValueError("diagnostic cold rounds disagree")

    # The diagnostic link must differ from the natural link at exactly the two
    # target MOV bytes and nowhere else in the decoded program image.
    natural_exe = output / "natural/a/op/source/bin/th04/op.exe"
    diag_exe = output / "diagnostic/a/op/source/bin/th04/op.exe"
    nimg = parse_mz(natural_exe.read_bytes()).program_image
    dimg = parse_mz(diag_exe.read_bytes()).program_image
    diffs = [i for i, (a, b) in enumerate(zip(nimg, dimg)) if a != b]
    if diffs != [MOV_START, MOV_START + 1]:
        raise ValueError(f"unexpected diagnostic program differences: {diffs[:20]}")
    if [x.linear for x in parse_mz(natural_exe.read_bytes()).relocations] != [
        x.linear for x in parse_mz(diag_exe.read_bytes()).relocations
    ]:
        raise ValueError("diagnostic changed ordered relocation topology")

    corpus = scan_v401_corpus()
    prov = provenance()

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-op",
        "function": "SND_LOAD",
        "claim_scope": "OP SND_LOAD complete-producer codegen and source-provenance bound",
        "accepted_state": "blocked",
        "source_credit": False,
        "target_restored_sha256": TARGET_SHA,
        "boundary": {
            "payload_offset": hex(START),
            "size": SIZE,
            "target_sha256": TARGET_SLICE_SHA,
            "handle_copy_offset": hex(MOV_START),
            "handle_copy_hex": "89c3",
        },
        "natural": natural,
        "diagnostic_inline_asm": {
            "rounds": diagnostic,
            "program_difference_offsets": [hex(x) for x in diffs],
            "source_credit": False,
            "finding": (
                "Changing only _BX = _AX to TC4J inline asm mov bx, ax makes the "
                "complete 234-byte SND_LOAD slice raw-identical to target in both "
                "cold rounds. MAP ownership and all 804 ordered relocations are unchanged."
            ),
        },
        "v401_tc86_corpus": corpus,
        "decompilation_provenance": prov,
        "conclusion": (
            "SND_LOAD is no longer a code-generation mystery: TC4J integrated inline "
            "assembly exactly explains the sole 89 C3 residual and changes no other "
            "decoded program byte. However, the only corroborating 89 C3 source witness "
            "in the pinned v401 TC86 corpus is itself explicit asm from a ReC98 "
            "[Decompilation] commit. Independent authored-source provenance is still absent."
        ),
        "limit": (
            "No decoded-exact, original-source-spelling, packed-file, or whole-artifact "
            "credit is granted. SND_LOAD remains blocked."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + chr(10))
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "accepted_state": "blocked",
        "natural_mov": natural["a"]["snd_load_mov_hex"],
        "diagnostic_mov": diagnostic["a"]["snd_load_mov_hex"],
        "diagnostic_snd_load_sha256": diagnostic["a"]["snd_load_sha256"],
        "v401_unique_tc86": corpus["unique_tc86_objects"],
        "v401_89c3_hits": len(corpus["mov_89c3_hits"]),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
