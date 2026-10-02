#!/usr/bin/env python3
"""Decode private MAIN exception frames without claiming normal gameplay."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from inspect_th04_handoff_trace import game_file, prepared_baseline

ROOT = Path(__file__).resolve().parents[2]
FIELDS = ("vector", "cs", "ip", "ss", "frame_sp", "ds", "ax", "dx",
          "bx", "cx", "si", "es", "flags")
STATE_FIELDS = ("ds", "stage_id", "rank", "stage_frame", "boss_phase",
                "boss_phase_frame", "boss_statebyte0", "boss_statebyte13",
                "boss_statebyte14", "boss_statebyte15")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_lines(log: str, names: list[str]) -> dict:
    arm = None
    last_call = None
    last_bullet = None
    faults = []
    for line in log.splitlines():
        prefix = "Bochs port E9h: "
        if prefix not in line:
            continue
        payload = line.split(prefix, 1)[1].strip()
        if payload.startswith("A") and re.fullmatch(r"A[0-9A-F]{4}(?: [0-9A-F]{4}){2}", payload):
            values = [int(word, 16) for word in payload[1:].split()]
            arm = dict(cs=values[0], previous_divide_cs=values[1], previous_divide_ip=values[2])
        elif payload.startswith("GP "):
            frame, tag, stack, ds = payload.split()[1:]
            tag = int(tag, 16)
            if tag >= len(names):
                raise ValueError("unknown gameplay call checkpoint")
            ss, sp = (int(word, 16) for word in stack.split(":"))
            last_call = dict(stage_frame=int(frame, 16), tag=tag, name=names[tag],
                             ss=ss, sp=sp, ds=int(ds, 16))
        elif payload.startswith("BV "):
            values = [int(word, 16) for word in payload.split()[1:]]
            if len(values) != 7:
                raise ValueError("malformed bullet checkpoint")
            last_bullet = dict(zip(("stage_frame", "step", "index", "pointer", "ss", "sp", "ds"), values))
        elif re.match(r"F[0-9A-F]{4} ", payload):
            values = [int(word, 16) for word in payload[1:].split()]
            if len(values) != 37 or arm is None:
                raise ValueError("malformed or unarmed exception frame")
            record = dict(zip(FIELDS, values[:13]))
            record.update(stack_words=values[13:29], code_words=values[29:],
                          last_call=last_call, last_bullet=last_bullet, arm=arm)
            faults.append(record)
        elif re.match(r"M[0-9A-F]{4}(?: |$)", payload):
            if not faults or "state" in faults[-1]:
                raise ValueError("unpaired CPU state snapshot")
            values = [int(word, 16) for word in payload[1:].split()]
            if len(values) != len(STATE_FIELDS) or values[0] != faults[-1]["ds"]:
                raise ValueError("malformed or inconsistent CPU state snapshot")
            faults[-1]["state"] = dict(zip(STATE_FIELDS, values))
    return dict(arm=arm, last_call=last_call, last_bullet=last_bullet, faults=faults)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--require-fault", action="store_true")
    args = parser.parse_args()
    run = args.run_dir.resolve()
    if not run.is_relative_to(ROOT / ".analysis/runtime/candidates"):
        parser.error("run must be a private runtime candidate")
    runtime = json.loads((run / "receipt.json").read_text())
    image = (run / "execution.hdi").read_bytes()
    if sha(image) != runtime["executed_hdi_sha256"]:
        raise ValueError("executed image identity drift")
    prepared_baseline(run, runtime)
    prepared = json.loads((run.parent / "receipt.json").read_text())
    product = prepared["products"]["main"]
    if sha(game_file(image, b"MAIN    EXE")) != product["sha256"]:
        raise ValueError("executed MAIN identity drift")
    link_path = Path(product["private_link_receipt"]).resolve()
    if not link_path.is_relative_to(ROOT / ".analysis/reconstruction/probes"):
        raise ValueError("link receipt is not private")
    link_data = link_path.read_bytes()
    if sha(link_data) != product["private_link_receipt_sha256"]:
        raise ValueError("link receipt identity drift")
    link = json.loads(link_data)
    if link["link"]["exit"] or link["link"]["mz"]["sha256"] != product["sha256"]:
        raise ValueError("MAIN does not belong to the complete diagnostic link")
    log = (run / "boot.log").read_bytes()
    if sha(log) != runtime["boot_log_sha256"]:
        raise ValueError("runtime log identity drift")
    result = decode_lines(log.decode("utf-8"), link["fault_trace"]["calls"])
    map_path = link_path.parent / "source" / link["link"]["map"]
    map_data = map_path.read_bytes()
    if sha(map_data) != link["link"]["map_sha256"]:
        raise ValueError("link MAP identity drift")
    entries = set(re.findall(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+FAULT_TRACE_SETUP\s*$",
                             map_data.decode("ascii")))
    if len(entries) != 1 or result["arm"] is None:
        raise ValueError("CPU observer has no unique linked frame or runtime arm")
    setup_segment = int(next(iter(entries))[0], 16)
    load_segment = (result["arm"]["cs"] - setup_segment) & 0xFFFF
    state_symbols = {}
    if any("state" in fault for fault in result["faults"]):
        for name in ("_stage_id", "_rank", "_stage_frame", "_boss", "_boss_statebyte"):
            locations = set(re.findall(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+"
                                       + re.escape(name) + r"\s*$", map_data.decode("ascii")))
            if len(locations) != 1:
                raise ValueError(f"CPU state has no unique MAP owner: {name}")
            segment, offset = next(iter(locations))
            state_symbols[name] = dict(segment=int(segment, 16), offset=int(offset, 16))
    for fault in result["faults"]:
        fault["main_load_segment"] = load_segment
        fault["relative_load_address"] = ((fault["cs"] - load_segment) & 0xFFFF) * 16 + fault["ip"]
        if "state" in fault:
            fault["state"]["ds_matches_owners"] = all(
                fault["state"]["ds"] == ((load_segment + owner["segment"]) & 0xFFFF)
                for owner in state_symbols.values())
    result.update(scope="private linked MAIN exception observations; no normal-game acceptance",
                  executed_main_sha256=product["sha256"], log_sha256=sha(log),
                  map_sha256=sha(map_data), main_load_segment=load_segment,
                  state_symbols=state_symbols)
    output = run / "cpu-fault.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(report=str(output), fault_count=len(result["faults"]),
                          main_load_segment=load_segment, last_call=result["last_call"],
                          last_bullet=result["last_bullet"])))
    if args.require_fault and not result["faults"]:
        raise ValueError("no guest CPU exception was recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
