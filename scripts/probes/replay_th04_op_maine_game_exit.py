#!/usr/bin/env python3
"""Cold-compile maintained shared game_exit and relink OP or MAINE."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot
from lib.omf import describe_omf, parse_omf
from lib.pc98 import parse_mz
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked
from probe_th04_maine_segment_topology_v470 import tcc as tcc_maine
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from replay_th04_op_help_put import tcc_op
from replay_th04_scroll_driver_natural import fixup_locations
from replay_th04_shared_delay_measure import link_relevant_omf_sha
from replay_th04_zun_source_only import source_closure

SOURCE = ROOT / "src/shared/core/game_exit.cpp"
SIZE = 0x48
BASE_EXIT_SOURCE_SHA = "13183f846ac74026e831cc666fbf7b3cd63a18f48fe2b7747203aa408c1f278b"
BASE_EXIT_OBJECT_SHA = "52c11994e825d2c77096ad3c50501434d437b6a0870510c74f703a619d807259"
BASE_LINK_OMF_SHA = "88db48d6d032260588ecb352911fa41dae657eb36006dc6b13f2818922611297"
CODE_SHA = "233ddbd15def50fa6e18e47a868a25746fde6a30d0d63deff1dc69493d398b77"
FIXUPS = [(3,66),(3,61),(3,56),(3,51),(3,46),(3,41),(3,26),(3,15),(3,4)]

CONFIG = {
    "op": {
        "artifact": "th04-op",
        "snapshot": ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source",
        "target": ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin",
        "target_sha": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
        "exe_sha": "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274",
        "map_sha": "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee",
        "start": 0xE0AC, "fn_sha": "69aeb7ab16c1e74d4e220e8ca24a6253e4d301cdf565edf70d3f2bce1aca0745",
        "entry_segment": 0x1DA1, "entry_offset": 0x069C, "callers": 4,
        "relocs": 804, "exe": "op.exe", "map": "op.map", "rsp": r"@obj\th04\op.@l",
    },
    "maine": {
        "artifact": "th04-maine",
        "snapshot": ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/maine/source",
        "target": ROOT / ".analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin",
        "target_sha": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
        "exe_sha": "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c",
        "map_sha": "014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e",
        "start": 0xD3F4, "fn_sha": "2c230b46d1ee194419df9e016888ca58a7a684d4917313ae5735ff1abe8fadaf",
        "entry_segment": 0x1CC7, "entry_offset": 0x0784, "callers": 1,
        "relocs": 559, "exe": "maine.exe", "map": "maine.map", "rsp": r"@obj\th04\maine.@l",
    },
}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha_file(path: Path) -> str:
    return sha(path.read_bytes())

def fixups(obj: Path) -> list[tuple[int,int]]:
    return [item for rec in parse_omf(obj.read_bytes()) if rec.record_type == 0x9C
            for item in fixup_locations(rec.data)]

def boundary(cfg, body):
    start = cfg["start"]
    if len(body) != SIZE or sha(body) != cfg["fn_sha"]:
        raise RuntimeError("game_exit target identity drift")
    p = ROOT / f".analysis/ghidra/boundary-exports/{cfg['artifact']}/functions.csv"
    rows = [r for r in csv.DictReader(p.open(newline="", encoding="utf-8"))
            if int(r["entry_linear"],0) == 0x10000 + start]
    if len(rows) != 1:
        raise RuntimeError("game_exit Ghidra entry count drift")
    r = rows[0]
    if (int(r["entry_segment"],0) != cfg["entry_segment"]
        or int(r["entry_offset"],0) != cfg["entry_offset"]
        or int(r["body_addresses"]) != SIZE or int(r["body_span"]) != SIZE
        or r["contiguous"] != "true" or r["body_range_count"] != "1"
        or int(r["caller_count"]) != cfg["callers"] or int(r["callee_count"]) != 8):
        raise RuntimeError(f"game_exit Ghidra extent drift: {r!r}")
    if (body[:3] != bytes.fromhex("55 8b ec")
        or body[8:14] != bytes.fromhex("ba a6 00 b0 01 ee")
        or body[19:25] != bytes.fromhex("ba a6 00 b0 00 ee")
        or body[30:40] != bytes.fromhex("ba a6 00 b0 00 ee ba a4 00 ee")
        or body[-2:] != bytes.fromhex("5d cb")):
        raise RuntimeError("game_exit inline topology drift")
    return {
        "segment_identity": f"{cfg['entry_segment']:04X}",
        "segment_offset": f"{cfg['entry_offset']:04X}",
        "payload_offset": hex(start), "size": SIZE,
        "target_sha256": sha(body), "caller_count": cfg["callers"],
        "callee_count": 8, "terminal": "RETF",
    }

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--artifact", choices=sorted(CONFIG), required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    which = args.artifact
    cfg = CONFIG[which]
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")

    snap = cfg["snapshot"]
    target_path = cfg["target"]
    base_exe = snap / f"bin/th04/{cfg['exe']}"
    base_map = snap / f"obj/th04/{cfg['map']}"
    base_wrapper = snap / "th04/exit.cpp"
    base_obj = snap / "obj/th04/exit.obj"
    for path, expected in (
        (target_path, cfg["target_sha"]), (base_exe, cfg["exe_sha"]),
        (base_map, cfg["map_sha"]), (base_wrapper, BASE_EXIT_SOURCE_SHA),
        (base_obj, BASE_EXIT_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    base_code = segment_bytes(base_obj, "SHARED")
    if len(base_code) != SIZE or sha(base_code) != CODE_SHA:
        raise RuntimeError("baseline SHARED code drift")
    if link_relevant_omf_sha(base_obj) != BASE_LINK_OMF_SHA:
        raise RuntimeError("baseline exit.obj OMF drift")

    target = parse_mz(target_path.read_bytes())
    baseline = parse_mz(base_exe.read_bytes())
    if (not target.valid or not baseline.valid
        or len(target.relocations) != cfg["relocs"]
        or len(baseline.relocations) != cfg["relocs"]):
        raise RuntimeError("invalid target/baseline MZ")
    sites = [x.linear for x in target.relocations]
    if [x.linear for x in baseline.relocations] != sites:
        raise RuntimeError("baseline relocation order drift")

    start = cfg["start"]
    body = target.program_image[start:start + SIZE]
    if baseline.program_image[start:start + SIZE] != body:
        raise RuntimeError("baseline game_exit differs from target")
    bound = boundary(cfg, body)

    closure = source_closure(ROOT, ("src/shared/core/game_exit.cpp",))
    hashes = {name: sha_file(ROOT / name) for name in closure}
    compiler = tcc_op if which == "op" else tcc_maine

    output.mkdir(parents=True)
    builds = {}
    for label in ("a", "b"):
        work = output / label / which / "source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(snap, work, which)
        for rel in closure:
            dst = work / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)

        objdir = work / "obj/th04"
        before = {p.name for p in objdir.glob("*.obj")}
        compiler(work, output, f"standalone-{which}-{label}",
                 "src/shared/core/game_exit.cpp")
        local = [p for p in objdir.glob("*.obj") if p.name not in before]
        if len(local) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = local[0]
        local_code = segment_bytes(local_obj, "SHARED")
        local_fixups = fixups(local_obj)
        masked = bytearray(body)
        for kind, off in FIXUPS:
            width = 2 if kind == 1 else 4
            masked[off:off + width] = b"\0" * width
        local_desc = describe_omf(local_obj.read_bytes())
        if (not local_desc["valid"]
            or "TC86 Borland C++ 4.02" not in local_desc["translator_comments"]
            or len(local_code) != SIZE or sha(local_code) != CODE_SHA
            or local_fixups != FIXUPS or local_code != bytes(masked)):
            raise RuntimeError(f"{label}: standalone game_exit drift")

        wrapper = work / "th04/exit.cpp"
        if sha_file(wrapper) != BASE_EXIT_SOURCE_SHA:
            raise RuntimeError(f"{label}: exit.cpp wrapper drift")
        wrapper.write_text('#include "src/shared/core/game_exit.cpp"\n')
        wrapper_sha = sha_file(wrapper)
        group_obj = work / "obj/th04/exit.obj"
        group_obj.unlink()
        compiler(work, output, f"group-{which}-{label}", "th04/exit.cpp")
        group_desc = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "SHARED")
        if (not group_desc["valid"]
            or "TC86 Borland C++ 4.02" not in group_desc["translator_comments"]
            or group_code != base_code
            or link_relevant_omf_sha(group_obj) != BASE_LINK_OMF_SHA):
            raise RuntimeError(f"{label}: grouped exit.obj drift")

        exe = work / f"bin/th04/{cfg['exe']}"
        mp = work / f"obj/th04/{cfg['map']}"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", cfg["rsp"]],
                    work, output / f"link-{which}-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[start:start + SIZE]
        if (not image.valid or sha_file(exe) != cfg["exe_sha"]
            or sha_file(mp) != cfg["map_sha"]
            or [x.linear for x in image.relocations] != sites
            or image.program_image != baseline.program_image
            or linked != body):
            raise RuntimeError(f"{label}: linked {which} game_exit/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_wrapper_sha256": wrapper_sha,
            "standalone_object_sha256": sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": sha(local_code),
            "standalone_fixup_sites": [list(x) for x in local_fixups],
            "group_object_sha256": sha_file(group_obj),
            "group_link_relevant_omf_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": sha(group_code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_function_sha256": sha(linked),
            "raw_function_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(sites),
        }

    stable = (
        "patched_wrapper_sha256", "standalone_link_relevant_omf_sha256",
        "standalone_code_sha256", "standalone_fixup_sites",
        "group_link_relevant_omf_sha256", "group_code_sha256",
        "linked_exe_sha256", "linked_map_sha256", "linked_program_sha256",
        "linked_function_sha256", "raw_function_difference_count",
        "raw_producer_difference_count", "ordered_relocations",
    )
    if any(builds["a"][k] != builds["b"][k] for k in stable):
        raise RuntimeError(f"independent {which} game_exit cold rounds differ")
    if any(sha_file(ROOT / name) != digest for name, digest in hashes.items()):
        raise RuntimeError("maintained shared game_exit source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": cfg["artifact"],
        "source_sha256": hashes,
        "boundary": bound,
        "producer": {
            "segment": "SHARED", "payload_offset": hex(start), "size": SIZE,
            "target_linked_sha256": sha(body),
        },
        "builds": builds,
        "limit": "Decoded 72-byte game_exit only; no packed-file or whole-program exactness.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "artifact": cfg["artifact"], "receipt": str(path),
        "function_sha256": builds["a"]["linked_function_sha256"],
        "producer_sha256": builds["a"]["linked_function_sha256"],
        "relocations": builds["a"]["ordered_relocations"],
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
