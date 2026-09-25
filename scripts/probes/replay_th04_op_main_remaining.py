#!/usr/bin/env python3
"""Cold-replay six maintained natural-C++ OP_MAIN_TEXT bodies with TC86 -S boundary evidence."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot
from lib.omf import describe_omf
from lib.pc98 import parse_mz
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from replay_th04_op_playchar_menu_initial import (
    SNAPSHOT, TARGET, TARGET_SHA, BASE_EXE_SHA, BASE_MAP_SHA, RELOCATIONS,
    sha, sha_file, tcc_op,
)

PRODUCER_START = 0xA74C
PRODUCER_SIZE = 0xD53
PRODUCER_SHA = "02ba00a11483ba325fc88687232ee277e8525047372a9d0c722c92cb4ffb1659"
BASE_WRAPPER_SHA = "5cf36e94fc4d72672edd5a225f73d4ac3ae9c551f67dfd249715c8c7a7484efd"
BASE_M_MAIN_SHA = "ee74c5c1d0a2328630c8f8453cf864a49640a0d59ca9b181ae11cef0400cb233"
BASE_START_SHA = "b2d57d857e5fff08960ef1338af7174ec7309ab1eaa39762881323924a543349"
BASE_OBJECT_SHA = "6706f32fba2b8753716a66d22a2cc64539d5e96051e0ba2dbca8405b22687481"
BASE_CODE_SHA = "926ac58cb1ac3225d93ac70122377ee8ae10a35cee069aa9e5da9b76ce4b41b7"
BASE_ASM_SHA = "1c9956e4b7d1218e17cce6ec9f0410c89116e8c68d1cd993b5b2345cd52bd95f"

FUNCTIONS = (
    {
        "key": "start_demo",
        "source": "src/op/main/start_demo.inl",
        "upstream": "th04/op/start.cpp",
        "marker": "void near start_demo(void)\n",
        "start": 0xA9C9, "body_size": 0xE4, "aux_size": 0x08,
        "body_sha": "df1fffafb9bc0464440d7c64b700049357ea928aa5cb15dd4788da9f4e9d7905",
        "aux_sha": "38370b0346676e215014051b7221f3e9bec3b968da7cfe30cb9dd471d52ca7d2",
        "entry_offset": 0x0289, "callers": 1, "callees": 9,
        "map_public": "0A74:0289 idle  start_demo()",
        "ghidra_addresses": 514, "ghidra_span": 19127, "ghidra_ranges": 4,
        "terminal": bytes.fromhex("5d c3"),
    },
    {
        "key": "main_unput_and_put",
        "source": "src/op/main/main_unput_and_put.inl",
        "upstream": "th04/op/m_main.cpp",
        "marker": "void pascal near main_unput_and_put(int sel, vc2 col)\n",
        "start": 0xAAB5, "body_size": 0x115, "aux_size": 0x0D,
        "body_sha": "38c3090c75bda7226603c1c2ef905d45357ccc13d7edfdb106d378d3ddfe1aec",
        "aux_sha": "fe2c26af8cd6cb58ac7a134eb4961dd1a9388d36ae32fa3536710ccc419e17d6",
        "entry_offset": 0x0375, "callers": 1, "callees": 5,
        "map_public": "0A74:0375 idle  main_unput_and_put(int,unsigned int)",
        "ghidra_addresses": 175, "ghidra_span": 277, "ghidra_ranges": 2,
        "terminal": bytes.fromhex("5f 5e c9 c2 04 00"),
    },
    {
        "key": "option_unput_and_put",
        "source": "src/op/main/option_unput_and_put.inl",
        "upstream": "th04/op/m_main.cpp",
        "marker": "void pascal near option_unput_and_put(int sel, vc2 col)\n",
        "start": 0xABD7, "body_size": 0x240, "aux_size": 0x11,
        "body_sha": "48250e073e77dbe5fb37735f8e94c855c47a405861c5df1f6c16857cdc92949a",
        "aux_sha": "4d67210c9dbc20cf4fd3448305da2aeb95157ed00cbdbb984ac94efb977f8509",
        "entry_offset": 0x0497, "callers": 1, "callees": 7,
        "map_public": "0A74:0497 idle  option_unput_and_put(int,unsigned int)",
        "ghidra_addresses": 257, "ghidra_span": 7869, "ghidra_ranges": 3,
        "terminal": bytes.fromhex("5f 5e c9 c2 04 00"),
    },
    {
        "key": "main_update_and_render",
        "source": "src/op/main/main_update_and_render.inl",
        "upstream": "th04/op/m_main.cpp",
        "marker": "void near main_update_and_render(void)\n",
        "start": 0xAE96, "body_size": 0x1B0, "aux_size": 0x0C,
        "body_sha": "043353f7bbecb98e3ba0480889fa615512f9f68c15de8cdd3775d195cdcaaf4a",
        "aux_sha": "bfe8f9c51eec26162bbec6fa898326323be1afef06bc09e50a06447b06dcac64",
        "entry_offset": 0x0756, "callers": 1, "callees": 7,
        "map_public": "0A74:0756 idle  main_update_and_render()",
        "ghidra_addresses": 282, "ghidra_span": 43589, "ghidra_ranges": 5,
        "terminal": bytes.fromhex("5e 5d c3"),
    },
    {
        "key": "option_update_and_render",
        "source": "src/op/main/option_update_and_render.inl",
        "upstream": "th04/op/m_main.cpp",
        "marker": "void near option_update_and_render(void)\n",
        "start": 0xB052, "body_size": 0x30C, "aux_size": 0x19,
        "body_sha": "d0bc8b7619d7536075831eeff20870017b2f0b6ee1c074c9956fb39e760ddfd9",
        "aux_sha": "83c2c02d8e43c36ac7f449e684d208be5b68eda3760d65dc50df49443383755a",
        "entry_offset": 0x0912, "callers": 1, "callees": 9,
        "map_public": "0A74:0912 idle  option_update_and_render()",
        "ghidra_addresses": 611, "ghidra_span": 19775, "ghidra_ranges": 6,
        "terminal": bytes.fromhex("5e 5d c3"),
    },
    {
        "key": "_main",
        "source": "src/op/main/main.inl",
        "upstream": "th04/op/m_main.cpp",
        "marker": "void main(void)\n",
        "start": 0xB377, "body_size": 0x128, "aux_size": 0,
        "body_sha": "c61aada736581b626286e125b90faca31ecac4738dc50fc23fe4d3754deed4bd",
        "aux_sha": None,
        "entry_offset": 0x0C37, "callers": 1, "callees": 26,
        "map_public": "0A74:0C37       _main",
        "ghidra_addresses": 296, "ghidra_span": 296, "ghidra_ranges": 1,
        "terminal": bytes.fromhex("5e 5d cb"),
    },
)


def find_function_end(text: str, start: int) -> int:
    brace = text.find("{", start)
    if brace < 0:
        raise RuntimeError("function opening brace drift")
    depth = 0
    for pos in range(brace, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return pos + 1
    raise RuntimeError("unterminated function")


def overlay_sources(work: Path) -> dict[str, str]:
    upstreams = {
        "th04/op/start.cpp": BASE_START_SHA,
        "th04/op/m_main.cpp": BASE_M_MAIN_SHA,
    }
    for rel, expected in upstreams.items():
        if sha_file(work / rel) != expected:
            raise RuntimeError(f"pinned source drift: {rel}")

    for spec in FUNCTIONS:
        src = ROOT / spec["source"]
        dst = work / spec["source"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    grouped: dict[str, list[tuple[int, dict[str, object]]]] = {}
    for spec in FUNCTIONS:
        rel = str(spec["upstream"])
        text = (work / rel).read_text(encoding="utf-8")
        marker = str(spec["marker"])
        if text.count(marker) != 1:
            raise RuntimeError(f"{spec['key']}: source marker drift")
        grouped.setdefault(rel, []).append((text.index(marker), spec))

    patched: dict[str, str] = {}
    for rel, positions in grouped.items():
        path = work / rel
        text = path.read_text(encoding="utf-8")
        for start, spec in sorted(positions, reverse=True):
            end = find_function_end(text, start)
            text = text[:start] + f'#include "{spec["source"]}"' + text[end:]
        path.write_text(text, encoding="utf-8")
        patched[rel] = sha_file(path)
    return patched


def run_tcc_asm(work: Path, output: Path, label: str) -> Path:
    asm = work / "obj/th04/op_main.asm"
    if asm.exists():
        asm.unlink()
    run_checked(
        [
            "wine", str(RUNNER), "-e", "-x", "tcc", "-S", "-I.", "-O", "-b-", "-3",
            "-Z", "-d", "-DGAME=4", "-ml", "-DBINARY='O'", "-nobj/th04/",
            "th04/op_main.cpp",
        ],
        work, output / f"compile-asm-{label}.log",
    )
    if not asm.is_file():
        raise RuntimeError(f"{label}: missing TC86 generated assembly")
    return asm


def generated_asm_layout(path: Path) -> dict[str, dict[str, object]]:
    text = path.read_text(encoding="cp437", errors="replace")
    specs = (
        ("start_demo", "@start_demo$qv", 4),
        ("main_unput_and_put", "@MAIN_UNPUT_AND_PUT$QIUI", 6),
        ("option_unput_and_put", "@OPTION_UNPUT_AND_PUT$QIUI", 8),
        ("main_update_and_render", "@main_update_and_render$qv", 6),
        ("option_update_and_render", "@option_update_and_render$qv", 12),
        ("_main", "_main", 0),
    )
    summary: dict[str, dict[str, object]] = {}
    for key, symbol, table_words in specs:
        proc = f"{symbol}\tproc"
        endp = f"{symbol}\tendp"
        if text.count(proc) != 1 or text.count(endp) != 1:
            raise RuntimeError(f"{key}: TC86 generated PROC/ENDP drift")
        start = text.index(proc)
        end = text.index(endp, start) + len(endp)
        next_proc = text.find("\tproc", end)
        seg_end = text.find("OP_MAIN_TEXT\tends", end)
        stops = [x for x in (next_proc, seg_end) if x >= 0]
        stop = min(stops) if stops else len(text)
        tail = text[end:stop]
        words = sum(1 for line in tail.splitlines() if line.lstrip().startswith("dw\t"))
        if words != table_words:
            raise RuntimeError(
                f"{key}: expected {table_words} compiler switch-table words, got {words}"
            )
        summary[key] = {
            "proc_symbol": symbol,
            "switch_table_words_after_endp": words,
            "has_uninitialized_pad_directive": "db\t1 dup (?)" in tail,
        }
    return summary


def validate_target(image: bytes, map_text: str) -> list[dict[str, object]]:
    contribution = "0A74:000C 0D53 C=CODE   S=OP_MAIN_TEXT   G=OP_01   M=th04/op_main.cpp"
    if contribution not in map_text:
        raise RuntimeError("OP_MAIN_TEXT MAP contribution drift")

    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    out: list[dict[str, object]] = []
    for spec in FUNCTIONS:
        start = int(spec["start"])
        body_size = int(spec["body_size"])
        aux_size = int(spec["aux_size"])
        body = image[start:start + body_size]
        aux = image[start + body_size:start + body_size + aux_size]
        if len(body) != body_size or sha(body) != spec["body_sha"]:
            raise RuntimeError(f"{spec['key']}: target body identity drift")
        if not body.endswith(spec["terminal"]):
            raise RuntimeError(f"{spec['key']}: target terminal drift")
        if aux_size and (len(aux) != aux_size or sha(aux) != spec["aux_sha"]):
            raise RuntimeError(f"{spec['key']}: target auxiliary identity drift")

        matched = [r for r in rows if int(r["entry_linear"], 0) == 0x10000 + start]
        if len(matched) != 1:
            raise RuntimeError(f"{spec['key']}: Ghidra entry count drift")
        row = matched[0]
        if (
            int(row["entry_segment"], 0) != 0x1A74
            or int(row["entry_offset"], 0) != int(spec["entry_offset"])
            or int(row["body_addresses"]) != int(spec["ghidra_addresses"])
            or int(row["body_span"]) != int(spec["ghidra_span"])
            or int(row["body_range_count"]) != int(spec["ghidra_ranges"])
            or int(row["caller_count"]) != int(spec["callers"])
            or int(row["callee_count"]) != int(spec["callees"])
        ):
            raise RuntimeError(f"{spec['key']}: Ghidra observation drift: {row!r}")
        if spec["map_public"] not in map_text:
            raise RuntimeError(f"{spec['key']}: MAP public drift")

        out.append({
            "name": spec["key"],
            "payload_offset": hex(start),
            "reviewed_body_size": body_size,
            "target_sha256": sha(body),
            "auxiliary_size": aux_size,
            "auxiliary_sha256": sha(aux) if aux_size else None,
            "segment_identity": "1A74",
            "segment_offset": f"{int(spec['entry_offset']):04X}",
            "ghidra_auto_body_addresses": int(spec["ghidra_addresses"]),
            "ghidra_auto_body_span": int(spec["ghidra_span"]),
            "ghidra_auto_range_count": int(spec["ghidra_ranges"]),
            "caller_count": int(spec["callers"]),
            "callee_count": int(spec["callees"]),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/op_main.cpp", BASE_WRAPPER_SHA),
        (SNAPSHOT / "th04/op/m_main.cpp", BASE_M_MAIN_SHA),
        (SNAPSHOT / "th04/op/start.cpp", BASE_START_SHA),
        (SNAPSHOT / "obj/th04/op_main.obj", BASE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    source_hashes = {
        str(spec["source"]): sha_file(ROOT / spec["source"]) for spec in FUNCTIONS
    }

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 OP candidate")
    target_sites = [r.linear for r in target.relocations]
    if [r.linear for r in baseline.relocations] != target_sites:
        raise RuntimeError("v489 OP ordered relocations differ from target")

    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    boundaries = validate_target(target.program_image, map_text)

    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(producer) != PRODUCER_SHA:
        raise RuntimeError("target OP_MAIN_TEXT producer identity drift")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 OP_MAIN_TEXT producer differs from target")

    base_obj = SNAPSHOT / "obj/th04/op_main.obj"
    base_omf = describe_omf(base_obj.read_bytes())
    base_code = segment_bytes(base_obj, "OP_MAIN_TEXT")
    if (
        not base_omf["valid"]
        or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
        or len(base_code) != PRODUCER_SIZE
        or sha(base_code) != BASE_CODE_SHA
    ):
        raise RuntimeError("pinned op_main object/code drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        patched_sources = overlay_sources(work)

        asm = run_tcc_asm(work, output, label)
        asm_layout = generated_asm_layout(asm)

        obj = work / "obj/th04/op_main.obj"
        obj.unlink()
        tcc_op(work, output, f"v742-op-main-remaining-{label}", "th04/op_main.cpp")
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "OP_MAIN_TEXT")
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or code != base_code
        ):
            raise RuntimeError(f"{label}: maintained OP main bodies changed producer CODE")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [r.linear for r in image.relocations] != target_sites
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: linked OP main identity/layout drift")

        linked: dict[str, dict[str, object]] = {}
        for spec in FUNCTIONS:
            start = int(spec["start"])
            body_size = int(spec["body_size"])
            aux_size = int(spec["aux_size"])
            body = image.program_image[start:start + body_size]
            aux = image.program_image[start + body_size:start + body_size + aux_size]
            target_body = target.program_image[start:start + body_size]
            target_aux = target.program_image[start + body_size:start + body_size + aux_size]
            if body != target_body or aux != target_aux:
                raise RuntimeError(f"{label}/{spec['key']}: linked body/aux drift")
            linked[str(spec["key"])] = {
                "body_sha256": sha(body),
                "auxiliary_sha256": sha(aux) if aux_size else None,
                "raw_body_difference_count": 0,
                "raw_auxiliary_difference_count": 0 if aux_size else None,
            }

        builds[label] = {
            "compact_snapshot": compact,
            "patched_source_sha256": patched_sources,
            "generated_asm_sha256": sha_file(asm),
            "generated_asm_layout": asm_layout,
            "object_sha256": sha_file(obj),
            "group_code_sha256": sha(code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_producer_sha256": sha(linked_producer),
            "linked": linked,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    def stable(build: dict[str, object]) -> dict[str, object]:
        clean = json.loads(json.dumps(build))
        clean.pop("object_sha256", None)
        clean.pop("generated_asm_sha256", None)
        return clean

    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent OP main cold rounds differ")
    if any(sha_file(ROOT / path) != digest for path, digest in source_hashes.items()):
        raise RuntimeError("maintained OP main source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP six remaining op_main.cpp maintained natural-C++ cold replay with TC86 generated-ASM physical boundary evidence",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": sha_file(Path(__file__).resolve()),
        "generated_asm_reference_sha256": BASE_ASM_SHA,
        "generated_asm_reference_note": "Reference text SHA is recorded only; maintained includes legitimately change debug records/private static symbol names. PROC/ENDP and table structure are checked semantically, while OMF CODE/link equality is the machine-code oracle.",
        "boundaries": boundaries,
        "producer": {
            "segment": "OP_MAIN_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
            "raw_target_difference_count": 0,
        },
        "builds": builds,
        "limit": (
            "Exactness claims are limited to the six maintained OP main/menu bodies and "
            "their explicitly recorded adjacent compiler switch-table extents. Existing "
            "accepted functions in the same 0xD53 producer remain scaffold. No packed-file "
            "or whole-OP exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha_file(path),
        "function_count": len(FUNCTIONS),
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
