#!/usr/bin/env python3
"""Verify bounded original FM86 OP startup, installation and display clocks.

Consumes read-only normal-core captures stopped at the first ordinary menu.
Checks the entire decoded load and its 804 relocations, scalar request/return
observations, raw GDC events, timer scheduling and physical resident options.
The independent GDC model must have its own closed producer receipt. Injected
load-byte and counter mutations must reject. No complete process, audio device,
physical chip, native boot-clock or historical exactness claim follows.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD_SHA = "13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74"
EVENT = struct.Struct("<BBHBIHHHHH")
CLOCK_SIZE = 540


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def equal_load(actual: bytes, expected: bytes) -> None:
    require(actual == expected, "complete decoded load/804 relocations differ")


def timer_observations(observation: dict) -> dict | None:
    if "timer_rows" not in observation:
        return None
    events = observation["timer_rows"]
    schedules = [row for row in events if row["kind"] == "timer_schedule"]
    writes = [row for row in events if row["kind"] == "timer_register"]
    callbacks = [row for row in events if row["kind"] == "timer_b_callback"]
    for index, row in enumerate(events):
        require(row["index"] == index, "timer observation order")
        cycles = row["cycles"]
        require(cycles["CPU_CycleMax"] > 0, "invalid CPU cycle budget")
        pic = cycles["pic_ticks"] + (
            cycles["CPU_CycleMax"] - cycles["CPU_CycleLeft"] - cycles["CPU_Cycles"]
        ) / cycles["CPU_CycleMax"]
        require(row["pic_ms"] == pic, "read-only PIC time arithmetic differs")
        require(len(bytes.fromhex(row["fmtimer_hex"])) == 8, "FMTIMER extent")
    for row in schedules:
        raw = bytes.fromhex(row["fmtimer_hex"])
        require(row["timer"] in (0, 1), "unknown timer")
        expected = (
            18 * (1024 - int.from_bytes(raw[:2], "little"))
            if row["timer"] == 0 else 288 * (256 - raw[2])
        ) / 1000
        require(abs(expected - row["delta_ms"]) < 1e-12, "timer period differs")
    first_b = next(row for row in schedules if row["timer"] == 1)
    require(first_b["delta_ms"] == 73.728, "first B period is not cold installation")
    require(bytes.fromhex(first_b["fmtimer_hex"])[2] == 0, "first B register differs")
    tempo = next(row for row in writes if row["register"] == 0x26 and row["value"] == 200)
    require(tempo["pic_ms"] > first_b["pic_ms"], "200 written before first enable")
    start = next(row for row in observation["rows"] if row["name"] == "measure_start")
    end = next(row for row in observation["rows"] if row["name"] == "measure_end")
    inside = [row for row in callbacks if start["pic_ms"] <= row["pic_ms"] <= end["pic_ms"]]
    require(len(inside) == 48, "measure wait lacks 48 B callbacks")
    return dict(
        rows=len(events), schedule_rows=len(schedules), callback_b_rows=len(callbacks),
        first_b_schedule=first_b, following_200_write=tempo,
        measure_timer_b_callbacks=48, measure_elapsed_ms=end["pic_ms"] - start["pic_ms"],
        first_measure_callback=inside[0], last_measure_callback=inside[-1],
        measure_schedule_histogram=dict(Counter(
            str(row["delta_ms"]) for row in schedules
            if row["timer"] == 1 and start["pic_ms"] <= row["pic_ms"] <= end["pic_ms"]
        )),
    )


def verify_capture(directory: Path, output: Path, model: Path) -> dict:
    observation = json.loads((directory / "startup-observation.json").read_text())
    wrapper = json.loads((directory / "wrapper-receipt.json").read_text())
    profile = json.loads((directory / "profile.json").read_text())
    require(observation["passed"] and wrapper["passed"], "capture incomplete")
    require(observation["controlled_host_stop"], "unrecognized completion boundary")
    require(digest(directory / "preparation.json") == wrapper["preparation_sha256"], "preparation identity")
    require(digest(directory / "execution.hdi") == wrapper["final_image_sha256"], "execution image identity")
    lines = (directory / "raw.txt").read_text().splitlines()
    loads = [line.split() for line in lines if line.startswith("L ")]
    inputs = [line.split() for line in lines if line.startswith("I ")]
    require(len(loads) == 1 and len(inputs) == 23 and len(lines) == 24, "scalar extent")
    require(int(loads[0][1]) == 1, "OP process order")
    load = int(loads[0][2], 16)
    payload_path = Path(profile["payload_path"])
    payload = bytearray(payload_path.read_bytes())
    require(hashlib.sha256(payload).hexdigest() == profile["payload_sha256"] == PAYLOAD_SHA, "decoded target identity")
    decoded_receipt = payload_path.parent / "receipt.json"
    require(digest(decoded_receipt) == profile["decoded_receipt_sha256"], "decoder receipt identity")
    decoded = json.loads(decoded_receipt.read_text())
    require(decoded["packed_target_sha256"] ==
            "8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f" and
            decoded["relocation_count"] == 804 and all(decoded["checks"].values()), "packed/decoded binding")
    relocations = payload_path.parent / "relocations.csv"
    require(digest(relocations) == "84972ed592c6ecbac79fe880db94687522a8880e558bf4b084e92b7afbcf9417", "relocation stream identity")
    with relocations.open(newline="") as stream:
        sites = [int(row["relative_linear"], 0) for row in csv.DictReader(stream)]
    require(sites == profile["relocations"], "profile relocation order differs")
    require(len(payload) == 69028 and len(profile["relocations"]) == 804, "load/relocation extent")
    for offset in profile["relocations"]:
        struct.pack_into("<H", payload, offset, (struct.unpack_from("<H", payload, offset)[0] + load) & 65535)
    loaded = bytes.fromhex(loads[0][-1])
    equal_load(loaded, payload)
    mutant = bytearray(loaded)
    mutant[0x522] ^= 1
    try:
        equal_load(mutant, payload)
    except ValueError:
        pass
    else:
        raise ValueError("loaded-byte mutation accepted")
    rows = observation["rows"]
    require(len(rows) == 24 and rows[-1]["name"] == "menu_ready", "startup request extent")
    for line, row in zip(inputs, rows[:-1], strict=True):
        require(len(line) == 11, "scalar field extent")
        require(tuple(int(value, 16) for value in line[2:5]) == (row["cs"], row["ip"], row["ds"]), "scalar caller identity")
        require(int(line[1]) == row["process"] == 1 and line[5:7] == ["0", "0"], "scalar process/counters")
        require(line[7] == row["sound_modes_hex"] and line[9] == row["resident_pointer_hex"] and line[10] == row["resident_hex"], "scalar memory differs")
    for row in rows:
        require(row["load_segment"] == load and row["ds"] == load + 0xF34, "OP load/DGROUP identity")
        require(bytes.fromhex(row["pmd_isr_prefix_hex"])[2:5] == b"PMD", "resident vector magic")
    names = ("driver_type", "resolved_modes", "logo_start", "measure_start", "measure_end",
             "after_measure", "logo_complete", "title_start", "title_complete", "menu_ready")
    selected = {}
    for name in names:
        found = [row for row in rows if row["name"] == name]
        require(len(found) == 1, "startup event count: " + name)
        selected[name] = found[0]
    require(selected["driver_type"]["ax"] == 0x4802 and selected["resolved_modes"]["ax"] == 2, "FM86 service/mode differs")
    require(all(row["sound_modes_hex"] == "010200" for row in rows[1:]), "live sound modes differ")
    resident = bytes.fromhex(selected["logo_start"]["resident_hex"])
    require(tuple(resident[index] for index in (0xF, 0x10, 0x18, 0x3A, 0x3B, 0x49)) == (2, 2, 1, 3, 2, 1), "physical options differ")
    require(resident[0x48] == 0 and bytes.fromhex(selected["title_start"]["resident_hex"])[0x48] == 1, "resident Logo ownership")
    require(struct.unpack_from("<HH", bytes.fromhex(selected["measure_start"]["stack_hex"]), 4) == (0, 2), "measure arguments")
    require(selected["measure_end"]["ax"] == 2, "returned measure differs")
    events = directory / "video-clock-events.bin.gz"
    require(digest(events) == observation["clock_file_sha256"], "clock stream identity")
    counts, verticals, boundary = Counter(), 0, 0
    expanded = output / (directory.name + "-events.bin")
    with gzip.open(events, "rb") as stream, expanded.open("xb") as destination:
        require(stream.read(8) == b"TH04EP1\n", "clock stream magic")
        while header := stream.read(EVENT.size):
            raw = stream.read(CLOCK_SIZE)
            require(len(header) == EVENT.size and len(raw) == CLOCK_SIZE, "clock record extent")
            destination.write(header + raw)
            kind, side, param, active, process, observed_load, frame, cs, ip, ds = EVENT.unpack(header)
            kind = chr(kind)
            require(kind in "CEVPF", "unknown clock event")
            counts[kind] += 1
            if kind == "V":
                verticals += 1
            if kind == "F":
                row = rows[boundary]
                require((param, frame, active, process, observed_load, cs, ip, ds) ==
                        (boundary, boundary, 1, 1, load, row["cs"], row["ip"], row["ds"]), "request/clock context")
                require(verticals == row["display_events"] and hashlib.sha256(raw).hexdigest() == row["clock_sha256"], "request/clock payload")
                boundary += 1
        require(stream.read(1) == b"", "clock complete EOF")
    require(dict(counts) == observation["event_counts"], "event counts")
    require(counts["C"] == counts["E"] == 2 and counts["P"] == 0 and boundary == 24, "clock coverage")
    result = subprocess.run([str(model), str(expanded)], capture_output=True)
    (output / (directory.name + "-model.log")).write_bytes(result.stdout + result.stderr)
    require(result.returncode == 0, "independent GDC replay rejected")
    mutant = bytearray(expanded.read_bytes())
    first_v = next(offset for offset in range(0, len(mutant), EVENT.size + CLOCK_SIZE) if mutant[offset] == ord("V"))
    mutant[first_v + EVENT.size + 197] ^= 1
    negative = output / (directory.name + "-clock-negative.bin")
    negative.write_bytes(mutant)
    result = subprocess.run([str(model), str(negative)], capture_output=True)
    (output / (directory.name + "-clock-negative.log")).write_bytes(result.stdout + result.stderr)
    require(result.returncode == 5, "GDC counter mutation accepted")
    return dict(
        capture=str(directory), raw_sha256=digest(directory / "raw.txt"),
        wrapper_sha256=digest(directory / "wrapper-receipt.json"),
        observation_sha256=digest(directory / "startup-observation.json"),
        profile_sha256=digest(directory / "profile.json"),
        whole_runtime_payload_sha256=hashlib.sha256(loaded).hexdigest(),
        load_segment=load, dgroup_segment=load + 0xF34, relocations=804,
        event_counts=dict(counts), clock_negative_rejected=True, loaded_byte_negative_rejected=True,
        measure=dict(start=selected["measure_start"]["display_events"], end=selected["measure_end"]["display_events"],
                     span=selected["measure_end"]["display_events"] - selected["measure_start"]["display_events"], returned_measure=2),
        timer=timer_observations(observation),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, action="append", required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--model-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    require(not output.exists() and output.is_relative_to(ROOT / ".analysis"), "use a fresh private output")
    parent = json.loads(args.model_receipt.read_text())
    model = args.model_dir / "model"
    require(parent["passed"] and digest(model) == parent["model_program_sha256"] and
            digest(args.model_dir / "model.cpp") == parent["model_source_sha256"], "independent model producer identity")
    require(len({path.name for path in args.capture}) == len(args.capture), "duplicate capture names")
    output.mkdir(parents=True)
    rows = [verify_capture(path.resolve(), output, model.resolve()) for path in args.capture]
    report = dict(passed=True, captures=rows, source_sha256=digest(Path(__file__)),
                  model_program_sha256=digest(model), model_source_sha256=digest(args.model_dir / "model.cpp"),
                  model_receipt_sha256=digest(args.model_receipt), scope=__doc__)
    (output / "receipt.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PASS original FM86 OP startup/installation/clock:", len(rows), "captures")


if __name__ == "__main__":
    main()
