#!/usr/bin/env python3
"""Attest a continuous bounded Stage3 route and its ordinary keyboard transport."""
import argparse
import json
from pathlib import Path

from attest_th04_stage_boundary import capture_source, require, sha
from attest_th04_stage_clear import attest_clear
from capture_th04_dos_demos import map_symbols

KEYS = [(1, "KBD_up"), (2, "KBD_down"), (4, "KBD_left"),
        (8, "KBD_right"), (16, "KBD_x"), (32, "KBD_z")]
PRIVATE = [("pattern", 0x53, 1, "a20000"),
           ("mirror", 0x5b, 1, "a20000"),
           ("patterns_done", 0x5e, 2, "c606000000")]
root = Path(__file__).resolve().parents[2]


def attest_input_rows(inputs, rows, raw, actions):
    require(len(rows) == len(inputs), "route complete input sidecar extent")
    require([(v["stage"], v["frame"], v["actual"], v["expected"]) for v in rows]
            == [(2, i, value, value) for i, value in enumerate(inputs)], "route actual sidecar inputs")
    require([int.from_bytes(bytes.fromhex(raw[(2, i)]["fields"]["input"]), "little")
             for i in range(len(inputs))] == inputs, "route independent raw inputs")
    require(all(raw[(2, i)]["fields"]["shift_raw"] == "00" for i in range(len(inputs))),
            "route unshifted actual inputs")
    expected = []
    for frame in range(1, len(inputs)):
        old, new = inputs[frame - 1:frame + 1]
        expected += [(2, frame, name, False) for bit, name in KEYS if old & bit and not new & bit]
        expected += [(2, frame, name, True) for bit, name in KEYS if not old & bit and new & bit]
    require([(v["stage"], v["next_loop_frame"], v["key"], v["pressed"]) for v in actions]
            == expected, "route ordered real keyboard edges")
    require(all(v["unchanged_guest"] is True and len(v["conventional_memory_sha256"]) == 64
                and bytes.fromhex(v["conventional_memory_sha256"]) for v in actions),
            "route keyboard CPU/tick/full RAM guards")
    require([v["tick"] for v in actions] == sorted(v["tick"] for v in actions), "route monotonic keyboard calls")
    return len(expected)


def attest_lcg(raw):
    previous = None
    transitions = draws = 0
    for row in raw.values():
        value = int.from_bytes(bytes.fromhex(row["fields"]["lcg"]), "little")
        if previous is not None:
            before, count = previous
            delta = row["lcg_calls"] - count
            require(delta >= 0, "route monotonic process LCG count")
            for _ in range(delta): before = (before * 0x015a4e35 + 1) & 0xffffffff
            require(value == before, "route every-loop process LCG recurrence")
            draws += delta
            transitions += 1
        previous = value, row["lcg_calls"]
    return dict(passed=True, transitions=transitions, draws=draws)


def attest_private(main, profile, role):
    original = role == "original"
    symbols = {} if original else map_symbols(Path(profile["map_path"]))
    function = (0x13a9, 0x09fb) if original else symbols["midboss3_update()"]
    offsets = [0x4258, 0x4259, 0x425a] if original else [
        symbols["_midboss3_" + name][1] for name, *_ in PRIVATE]
    header = int.from_bytes(main[8:10], "little") * 16
    entries = profile["stage3_private_fields"]
    require(len(entries) == 3, "route all three private owners")
    for row, (name, relative, operand, template), offset in zip(entries, PRIVATE, offsets, strict=True):
        expected = bytearray.fromhex(template)
        expected[operand:operand + 2] = offset.to_bytes(2, "little")
        segment, ip = function[0], function[1] + relative
        require(row == dict(role=role, name=name, code_segment=segment, code_offset=ip,
                            bytes=bytes(expected).hex(), dgroup_segment=profile["dgroup"], offset=offset, size=1),
                "route own private store declaration")
        at = header + segment * 16 + ip
        require(main[at:at + len(expected)] == expected, "route own MZ private store operand")
        if not original:
            require(symbols["_midboss3_" + name] == (profile["dgroup"], offset), "route own MAP private owner")
    point = profile["stage3_gameover_guard"]
    location = (0x0aaf, 0x3a51) if original else symbols["gameover_run()"]
    require((point["segment"], point["offset"]) == location, "route own GameOver guard owner")
    at = header + location[0] * 16 + location[1]
    require(main[at:at + 16].hex() == point["opcode"], "route own MZ GameOver guard bytes")
    return offsets


def attest_route(capture, target, stage3_updates=4000, stage2_budget=11000):
    report, metadata, raw, events = attest_clear(capture, target, stage2_updates=stage2_budget,
        require_bounded_watchpoints=True, stage3_updates=stage3_updates, extra_registered_watchpoints=1)
    receipt = json.loads((capture / "receipt.json").read_text())
    summary = json.loads((capture / "stage-boundary-summary.json").read_text())
    profile = summary["profile"]
    helper = capture_source(receipt, "stage_input_gdb.py")
    require(sha(helper.read_bytes()) == receipt["source_files"][str(helper)], "route actual keyboard helper identity")
    plan = capture_source(receipt, "stage-inputs.txt")
    require(str(plan) == profile["stage3_input_path"] and sha(plan.read_bytes()) == profile["stage3_input_sha256"],
            "route actual input plan binding")
    lines = plan.read_text().splitlines()
    require(lines[0] == f"TH04_STAGE_INPUT 1 2 {stage3_updates}" and len(lines) == stage3_updates + 1,
            "route complete declared input plan")
    inputs = []
    for frame, line in enumerate(lines[1:]):
        row = list(map(int, line.split()))
        require(len(row) == 3 and row[0] == frame and 0 <= row[1] <= 63 and row[2] == 0,
                "route explicit input plan row")
        inputs.append(row[1])
    doc = json.loads((capture / "stage-input.json").read_text())
    require(doc["complete"] is True and doc["stage"] == 2
            and doc["extent"] == doc["observed_loops"] == stage3_updates
            and doc["plan_path"] == str(plan) and doc["plan_sha256"] == sha(plan.read_bytes())
            and doc["external_loop_owner"] is True and doc["gameover_guard_registered"] == 1
            and doc["gameover_guard_fired"] is False, "route complete input/guard registry")
    rows = [json.loads(line) for line in (capture / "stage-input-loops.jsonl").open()]
    edges = attest_input_rows(inputs, rows, raw, doc["actions"])
    require(all(m["baseline_registered_breakpoints"] == 9 and m["registered_breakpoints"] == 9 + m["watchpoint_cache_slots"]
                and 0 <= m["watchpoint_cache_slots"] <= 7 for m in metadata), "route bounded nine-plus-seven observer registry")
    require(max(m["watchpoint_cache_slots"] for m in metadata) == 7, "route complete bounded observer cache")
    require(not (capture / "stage-input-gameover.json").exists() and not (capture / "stage-input-error.json").exists(),
            "route no hidden input or GameOver failure")
    offsets = attest_private(Path(profile["main_path"]).read_bytes(), profile, receipt["role"])
    report.update(route_reader_sha256=sha(Path(__file__).read_bytes()), stage3_input=dict(passed=True, loops=len(rows), physical_edges=edges,
        helper_sha256=sha(helper.read_bytes()), plan_sha256=sha(plan.read_bytes()),
        report_sha256=sha((capture / "stage-input.json").read_bytes()),
        loops_sha256=sha((capture / "stage-input-loops.jsonl").read_bytes()),
        gameover_guard_registered=1, gameover_guard_fired=False),
        stage3_private_offsets=offsets, process_lcg=attest_lcg(raw),
        scope="Actual complete two-stage prefix and bounded Stage3 route, with every loop's declared ordinary hardware input, real keyboard edges and all conventional RAM/CPU/tick guards. Private Midboss3 bytes and the GameOver watch bind to own MZ/MAP. This is an observation attestation; paired state, native pictures, timing, campaign and exactness are separate claims.")
    return report, metadata, raw, events


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dos-root", type=Path, default=root)
    p.add_argument("--capture", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--stage3-updates", type=int, default=4000)
    p.add_argument("--stage2-budget", type=int, default=11000)
    args = p.parse_args()
    report, *_ = attest_route(args.capture.resolve(), (args.dos_root.resolve() / ".analysis/targets/th04/main.exe").read_bytes(),
                             args.stage3_updates, args.stage2_budget)
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print("ACTUAL BOUNDED STAGE3 ROUTE ATTESTATION PASS", report["role"], report["rows"], flush=True)
