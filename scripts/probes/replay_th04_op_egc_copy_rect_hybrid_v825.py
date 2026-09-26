#!/usr/bin/env python3
"""Replay TH04 OP egc_copy_rect_1_to_0_16() from a narrowed hybrid source.

The maintained source keeps rectangle arithmetic and register allocation in
C++/TC4J pseudoregister expressions. Symbolic low-level source is restricted to
CLD, two SHL-by-one instructions, immediate-port VRAM page selection, and the
STOSW/LOOP string-loop primitive. Cross-game release targets independently
corroborate the shared TH05 rectangle producer, page-switch/read architecture,
and the string-store primitive family.
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
from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from probe_th04_final_blocker_crossartifact import restore_diet  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from replay_th04_op_egc_start_copy_hybrid_v824 import (  # noqa: E402
    SNAPSHOT, TARGET, TARGET_SHA, BASE_EXE_SHA, BASE_MAP_SHA, RELOCATIONS,
    BASE_WRAPPER_SHA, BASE_IMPL_SHA, BASE_CODE_SHA,
    PRODUCER_START, PRODUCER_SIZE, PRODUCER_SHA,
    SOURCE as HELPER_SOURCE, SOURCE_SHA as HELPER_SOURCE_SHA,
    START as HELPER_START, SIZE as HELPER_SIZE, TARGET_SHA256 as HELPER_SHA,
    TH05, tcc_op,
)

SOURCE = ROOT / "src/op/hardware/egc_copy_rect_1_to_0_16.inl"
SOURCE_SHA = "0e7c0a177bfe5ee5459dfb7f8725ab2472f170317923a99c259e601f9b3a6a3e"

START = 0xE378
SIZE = 0x6F
TARGET_BODY_SHA = "3a4dfb3ccd7e3c021dd3548f4f338e221a682ccafa6e012575f6e5864bc68e22"
PRELINK_BODY_SHA = "87f4693659f367cdc6a10c1ab4c82c58a614167b85990902819c2c89720f13a1"
PRELINK_LINK_FIELDS = ((0x39, 0x3B), (0x4E, 0x50), (0x66, 0x68))

TH05_OUTER = {
    "th05-op-smoke": {
        "offset": 0xE2D8,
        "size": 0x7B,
        "sha256": "bd5300759a8d6360f9bfcf2df8c0025289903e749039642ed78fc992a0d1be1a",
    },
    "th05-maine-smoke": {
        "offset": 0xF402,
        "size": 0x7B,
        "sha256": "7f22580f40ff81745c5e2e31b37479e9404718eecc2fdcf7c46c5166de6bf2ea",
    },
}
TH05_LINK_FIELDS = ((0x38, 0x3A), (0x4D, 0x4F), (0x72, 0x76))
TH05_NORMALIZED_SHA = "04f8b7e735d9d01a18d7032ebd8b99ea63b085b0dae3c132f27c0e9aa8a87682"

# Release-target machine-code lineage for the low-level operations retained
# symbolically. These are not treated as original-source spelling.
TH03_OP_RESTORED_SHA = "efd858aef69a240af3a27c747a5beae150f55f0b41b8afdd1eda1760a759ecc0"
TH03_PAGE_READ_OFFSET = 0xB11F
PAGE_READ_PREFIX = bytes.fromhex("b001e6a6268b")
PAGE0_STOSW = bytes.fromhex("33c0e6a68bc2ab")
MOV_AX_DX_STOSW = bytes.fromhex("8bc2ab")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def new_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="op-egc-copy-v825-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def mask(data: bytes, spans: tuple[tuple[int, int], ...]) -> bytes:
    out = bytearray(data)
    for lo, hi in spans:
        out[lo:hi] = b"\0" * (hi - lo)
    return bytes(out)


def source_policy() -> dict[str, object]:
    if sha_file(SOURCE) != SOURCE_SHA:
        raise ValueError("maintained EGC copy source identity drift")
    text = SOURCE.read_text()
    forbidden = (
        "__emit__", "#pragma codestring", "_outportb_", "target_bytes",
        "unsigned char target", "db 0x", "candidate_slice",
    )
    if any(token in text for token in forbidden):
        raise ValueError("maintained EGC copy source contains byte-forcing surface")
    required = (
        "asm { cld; }",
        "_AX = left;",
        "_DX = top;",
        "asm { shl bx, 1; }",
        "asm { shl cx, 1; }",
        "_AL = 1;",
        "asm { out 0xA6, al; }",
        "_AX ^= _AX;",
        "_AX = dots;",
        "asm { stosw; loop put_loop; }",
    )
    for marker in required:
        if marker not in text:
            raise ValueError(f"maintained EGC copy marker drift: {marker}")
    if "asm { mov ax, left" in text or "asm { mov dx, top" in text:
        raise ValueError("parameter-load assembly reintroduced")
    return {
        "symbolic_low_level_operations": [
            "CLD before the TH04 forward string-store loop",
            "SHL BX,1 and SHL CX,1 (ordinary <<=1 lowers to ADD reg,reg)",
            "two immediate-port OUT 0xA6,AL page switches",
            "STOSW plus LOOP for the TH04 forward copy loop",
        ],
        "ordinary_codegen": [
            "BP-relative parameter loads",
            "rectangle-to-VRAM offset arithmetic",
            "width/stride arithmetic and loop state",
            "EGC mode word write and EGC-off call",
        ],
        "no_emit": True,
        "no_codestring_in_function_source": True,
        "no_target_byte_arrays": True,
        "no_post_build_patch": True,
    }


def restore_target(aid: str, output: Path) -> tuple[bytes, dict[str, object]]:
    manifest = load_target_manifest(ROOT / "config/targets.toml")
    artifact = find_artifact(manifest, aid)
    packed = read_verified_artifact(ROOT, artifact)
    if len(packed) >= 0x20 and packed[0x1C:0x20].lower() == b"diet":
        return restore_diet(artifact, packed, output)
    return packed, {"restore_log_sha256": None}


def crossgame_evidence(output: Path, th04_body: bytes) -> dict[str, object]:
    work = output / "crossgame"
    work.mkdir()
    results: dict[str, object] = {}

    th05_bodies: dict[str, bytes] = {}
    for aid, spec in TH05_OUTER.items():
        raw, meta = restore_target(aid, work)
        mz = parse_mz(raw)
        if not mz.valid:
            raise ValueError(f"{aid}: invalid restored MZ")
        # Reuse v824's independently pinned packed/restored identities.
        v824 = TH05[aid]
        if sha(raw) != v824["restored_sha256"]:
            raise ValueError(f"{aid}: restored identity drift")
        off = int(spec["offset"])
        body = mz.program_image[off:off + int(spec["size"])]
        if len(body) != spec["size"] or sha(body) != spec["sha256"]:
            raise ValueError(f"{aid}: outer EGC body drift")
        helper_off = int(v824["offset"])
        helper = mz.program_image[helper_off:helper_off + HELPER_SIZE]
        if sha(helper) != HELPER_SHA:
            raise ValueError(f"{aid}: helper drift")
        th05_bodies[aid] = body
        results[aid] = {
            "outer_payload_offset": hex(off),
            "outer_size": len(body),
            "outer_sha256": sha(body),
            "helper_payload_offset": hex(helper_off),
            "helper_sha256": sha(helper),
            "ordered_relocations": len(mz.relocations),
            "restore_log_sha256": meta["restore_log_sha256"],
        }

    normalized = {
        aid: mask(body, TH05_LINK_FIELDS)
        for aid, body in th05_bodies.items()
    }
    if normalized["th05-op-smoke"] != normalized["th05-maine-smoke"]:
        raise ValueError("TH05 OP/MAINE outer fixed bytes diverged")
    if sha(normalized["th05-op-smoke"]) != TH05_NORMALIZED_SHA:
        raise ValueError("TH05 normalized outer identity drift")

    # The common TH04/TH05 front half establishes the same TC4J register
    # allocation and rectangle arithmetic. TH04 inserts CLD before the helper;
    # TH05 adds a loop-body VRAM bounds guard instead.
    common_markers = (
        bytes.fromhex("baa404b8f029ef8b460c8b560a8bd8c1fb04d1e3c1e20603dac1ea0203da8bfb250f008bc8"),
        bytes.fromhex("b928002bc8d1e18b5e068be9b800a88ec0"),
        PAGE_READ_PREFIX,
    )
    for marker in common_markers:
        if marker not in th04_body:
            raise ValueError("TH04 shared outer marker drift")
        if marker not in th05_bodies["th05-op-smoke"] or marker not in th05_bodies["th05-maine-smoke"]:
            raise ValueError("TH05 shared outer marker drift")

    # Earlier TH03 release code independently uses the same immediate page-1
    # select followed by an ES:[DI] read.
    th03_raw, _ = restore_target("th03-op-smoke", work)
    if sha(th03_raw) != TH03_OP_RESTORED_SHA:
        raise ValueError("TH03 OP restored identity drift")
    th03 = parse_mz(th03_raw)
    if not th03.valid or th03.program_image[TH03_PAGE_READ_OFFSET:TH03_PAGE_READ_OFFSET + len(PAGE_READ_PREFIX)] != PAGE_READ_PREFIX:
        raise ValueError("TH03 page-read lineage drift")

    # Broader registered release-target corpus for MOV AX,DX / STOSW.
    manifest = load_target_manifest(ROOT / "config/targets.toml")
    corpus_work = work / "corpus"
    corpus_work.mkdir()
    stosw_hits: dict[str, list[str]] = {}
    for artifact in manifest["artifacts"]:
        packed = read_verified_artifact(ROOT, artifact)
        raw = packed
        if len(raw) >= 0x20 and raw[0x1C:0x20].lower() == b"diet":
            raw, _ = restore_diet(artifact, packed, corpus_work)
        mz = parse_mz(raw) if raw[:2] == b"MZ" else None
        image = mz.program_image if mz and mz.valid else raw
        hits = []
        pos = 0
        while True:
            pos = image.find(MOV_AX_DX_STOSW, pos)
            if pos < 0:
                break
            hits.append(hex(pos))
            pos += 1
        if hits:
            stosw_hits[str(artifact["id"])] = hits

    for required in ("th02-op-smoke", "th03-op-smoke", "th04-op", "th05-main-smoke"):
        if required not in stosw_hits:
            raise ValueError(f"cross-game MOV AX,DX/STOSW lineage drift: {required}")

    shutil.rmtree(work)
    return {
        "th05": results,
        "th05_normalized_fixed_sha256": TH05_NORMALIZED_SHA,
        "th05_outer_fixed_equal": True,
        "th03_op_page_read_offset": hex(TH03_PAGE_READ_OFFSET),
        "th03_op_page_read_prefix": PAGE_READ_PREFIX.hex(),
        "mov_ax_dx_stosw_release_hits": stosw_hits,
        "classification": (
            "independent release-target machine-code corroboration of the shared "
            "rectangle arithmetic and retained low-level primitives; not original-source spelling"
        ),
    }


def overlay_sources(work: Path) -> dict[str, str]:
    for src in (SOURCE, HELPER_SOURCE):
        dst = work / src.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    impl = work / "th04/hardware/egcrect.cpp"
    if sha_file(impl) != BASE_IMPL_SHA:
        raise ValueError("pinned egcrect implementation identity drift")
    text = impl.read_text()

    outer = re.compile(
        r"void DEFCONV egc_copy_rect_1_to_0_16\(.*?\n\}\n\n"
        r'(#pragma codestring "\\x90")',
        re.S,
    )
    matches = list(outer.finditer(text))
    if len(matches) != 1:
        raise ValueError("outer definition replacement anchor drift")
    text = (
        text[:matches[0].start()]
        + '#include "src/op/hardware/egc_copy_rect_1_to_0_16.inl"\n\n'
        + matches[0].group(1)
        + text[matches[0].end():]
    )

    helper = re.compile(
        r"static void near egc_start_copy\(void\)\n\{.*?\n\}\n\n"
        r'(#pragma codestring "\\x90")',
        re.S,
    )
    matches = list(helper.finditer(text))
    if len(matches) != 1:
        raise ValueError("helper definition replacement anchor drift")
    text = (
        text[:matches[0].start()]
        + '#include "src/op/hardware/egc_start_copy.inl"\n\n'
        + matches[0].group(1)
        + text[matches[0].end():]
    )
    impl.write_text(text)
    return {
        str(SOURCE.relative_to(ROOT)): sha_file(SOURCE),
        str(HELPER_SOURCE.relative_to(ROOT)): sha_file(HELPER_SOURCE),
        "overlay_th04/hardware/egcrect.cpp": sha_file(impl),
    }


def build_round(output: Path, label: str, target_mz) -> dict[str, object]:
    work = output / label / "op/source"
    work.parent.mkdir(parents=True)
    compact = copy_compact_snapshot(SNAPSHOT, work, "op")
    source_hashes = overlay_sources(work)

    obj = work / "obj/th04/egcrect.obj"
    obj.unlink()
    tcc_op(work, output, f"egc-copy-hybrid-{label}", "th04/egcrect.cpp")
    desc = describe_omf(obj.read_bytes())
    code = segment_bytes(obj, "SHARED")
    if (
        not desc["valid"]
        or "TC86 Borland C++ 4.02" not in desc["translator_comments"]
        or len(code) != PRODUCER_SIZE
        or sha(code) != BASE_CODE_SHA
    ):
        raise ValueError(f"{label}: EGC producer object drift")

    outer = code[:SIZE]
    if sha(outer) != PRELINK_BODY_SHA:
        raise ValueError(f"{label}: prelink outer identity drift")
    target_outer = target_mz.program_image[START:START + SIZE]
    if mask(outer, PRELINK_LINK_FIELDS) != mask(target_outer, PRELINK_LINK_FIELDS):
        raise ValueError(f"{label}: non-link outer bytes differ from target")

    helper = code[HELPER_START - PRODUCER_START:HELPER_START - PRODUCER_START + HELPER_SIZE]
    if sha(helper) != HELPER_SHA:
        raise ValueError(f"{label}: accepted helper drift")

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
        raise ValueError(f"{label}: accepted OP EXE/MAP drift")

    linked_outer = linked.program_image[START:START + SIZE]
    linked_producer = linked.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(linked_outer) != TARGET_BODY_SHA or linked_outer != target_mz.program_image[START:START + SIZE]:
        raise ValueError(f"{label}: linked outer raw mismatch")
    if sha(linked_producer) != PRODUCER_SHA:
        raise ValueError(f"{label}: complete EGC producer drift")

    return {
        "compact_snapshot": compact,
        "source_sha256": source_hashes,
        "object_code_size": len(code),
        "object_code_sha256": sha(code),
        "prelink_outer_sha256": sha(outer),
        "prelink_link_fields": [[lo, hi] for lo, hi in PRELINK_LINK_FIELDS],
        "nonlink_outer_difference_count": 0,
        "linked_outer_sha256": sha(linked_outer),
        "linked_outer_difference_count": 0,
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
    for path, expected in (
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/egcrect.cpp", BASE_WRAPPER_SHA),
        (SNAPSHOT / "th04/hardware/egcrect.cpp", BASE_IMPL_SHA),
        (HELPER_SOURCE, HELPER_SOURCE_SHA),
    ):
        if sha_file(path) != expected:
            raise ValueError(f"pinned v825 input drift: {path}")

    policy = source_policy()
    target_mz = parse_mz(TARGET.read_bytes())
    if not target_mz.valid or len(target_mz.relocations) != RELOCATIONS:
        raise ValueError("OP target MZ/relocation drift")
    target_body = target_mz.program_image[START:START + SIZE]
    if len(target_body) != SIZE or sha(target_body) != TARGET_BODY_SHA:
        raise ValueError("OP EGC outer target drift")

    crossgame = crossgame_evidence(output, target_body)
    source_hash = sha_file(SOURCE)
    builds = {label: build_round(output, label, target_mz) for label in ("a", "b")}
    stable = lambda x: {k: v for k, v in x.items() if k != "compact_snapshot"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise ValueError("independent v825 cold rounds disagree")
    if sha_file(SOURCE) != source_hash:
        raise ValueError("maintained EGC copy source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP egc_copy_rect_1_to_0_16 hybrid-source decoded exactness",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "boundary": {
            "payload_offset": hex(START),
            "size": SIZE,
            "target_sha256": TARGET_BODY_SHA,
            "complete_translation_unit_offset": hex(PRODUCER_START),
            "complete_translation_unit_size": PRODUCER_SIZE,
            "complete_translation_unit_sha256": PRODUCER_SHA,
        },
        "source_policy": policy,
        "crossgame_release_evidence": crossgame,
        "negative_controls": {
            "parameter_loads": (
                "Replacing decompilation asm MOV AX,left / MOV DX,top with ordinary "
                "TC4J pseudoregister assignments preserves the target parameter-load bytes."
            ),
            "shift_by_one": (
                "Ordinary _BX<<=1 and _CX<<=1 lower to ADD BX,BX / ADD CX,CX; "
                "multiplication/expression forms disturb allocation. Target SHL forms remain symbolic."
            ),
            "page_out": (
                "Ordinary outportb(0xA6,value) uses the DX-port form; target immediate OUT 0xA6,AL "
                "therefore remains symbolic."
            ),
        },
        "builds": builds,
        "conclusion": (
            "Two cold TC4.02/TLINK rounds reproduce the complete 111-byte outer function raw-zero, "
            "the accepted 63-byte helper, the full 0xB0 egcrect producer, accepted OP EXE/MAP, and "
            "all 804 ordered relocations. The maintained outer removes decompilation-only parameter-load "
            "assembly and byte-emitting helper macros; symbolic source is limited to irreducible x86/PC-98 "
            "primitives with independent release-target machine-code lineage."
        ),
        "limit": (
            "Decoded-function exactness only. This does not prove original source spelling or packed-file exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha_file(path),
        "outer_sha256": TARGET_BODY_SHA,
        "producer_sha256": PRODUCER_SHA,
        "ordered_relocations": RELOCATIONS,
        "th05_normalized_outer_sha256": TH05_NORMALIZED_SHA,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
