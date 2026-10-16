#!/usr/bin/env python3
"""Attest raw elapsed time and independently predict the captured GDC clock.

The first actual master refresh supplies the display-init time origin. Its
phase/count start at the pinned constructor's zero, never a fitted later value.
Native replay inputs contain only frame numbers and elapsed nanoseconds.
"""

import argparse
import gzip
import hashlib
import json
import math
import struct
from fractions import Fraction
from pathlib import Path
from compare_th04_dos_ordinary_prefix import load
from th04_demo_video import OFFSETS, SIZES
from th04_ordinary_video import records


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def advance(phase, count, rate):
    """Pinned GDC BYTE transition, including its count-bit fallback."""
    count = (count + 1) & 255
    if count == rate:
        count = 0
        phase = (phase + 1) & 3
    elif count & 64:
        count = 0
    return phase, count


def double(raw, name):
    return struct.unpack("<d", bytes.fromhex(raw[name]))[0]


def validate_rows(rows, abi, summary, limit, frames, terminal):
    """Validate actual raw observations before using their times or verdicts."""
    kinds = {
        "initial-host",
        "master-advance-entry",
        "main-start",
        "after-actor",
        "after-score",
    }
    counts = {}
    actor = {}
    score = {}
    events = []
    last_time = None
    for ordinal, row in enumerate(rows):
        require(
            type(row["ordinal"]) is int
            and row["ordinal"] == ordinal
            and row["kind"] in kinds,
            "clock row order/kind",
        )
        require(
            row["unchanged_context"]
            and len(bytes.fromhex(row["registers"])) == 48
            and len(bytes.fromhex(row["segments"])) == 136,
            "clock raw CPU/read-only context",
        )
        raw = row["raw"]
        for name, meta in abi["symbols"].items():
            if name not in ["vga", "pc98_gdc"]:
                require(
                    len(bytes.fromhex(raw[name])) == meta["size"],
                    "clock raw symbol width",
                )
        require(
            len(bytes.fromhex(raw["master_blink"])) == 3
            and len(bytes.fromhex(raw["frame_start"]))
            == len(bytes.fromhex(raw["period"]))
            == 8,
            "clock raw device width",
        )
        maximum = int.from_bytes(
            bytes.fromhex(raw["CPU_CycleMax"]), "little", signed=True
        )
        left = int.from_bytes(
            bytes.fromhex(raw["CPU_CycleLeft"]), "little", signed=True
        )
        cycles = int.from_bytes(bytes.fromhex(raw["CPU_Cycles"]), "little", signed=True)
        ticks = int.from_bytes(bytes.fromhex(raw["PIC_Ticks"]), "little")
        numerator = ticks * maximum + maximum - left - cycles
        require(
            maximum > 0
            and row["pic_ms_denominator"] == maximum
            and row["pic_ms_numerator"] == numerator,
            "clock raw PIC rational",
        )
        time = Fraction(numerator, maximum)
        require(last_time is None or time >= last_time, "clock PIC moved backwards")
        last_time = time
        phase, count, rate = bytes.fromhex(raw["master_blink"])
        require(phase < 4, "GDC phase range")
        row["_time"] = time
        row["_state"] = (phase, count, rate)
        counts[row["kind"]] = counts.get(row["kind"], 0) + 1
        if row["kind"] == "master-advance-entry":
            require(not actor, "master watch survived first actor")
            events.append(row)
        elif row["kind"] in ["after-actor", "after-score"]:
            frame = row["frame"]
            require(type(frame) is int and 1 <= frame <= limit, "clock frame width")
            mapping = actor if row["kind"] == "after-actor" else score
            require(frame not in mapping, "duplicate clock boundary")
            mapping[frame] = row
            regs = bytes.fromhex(row["registers"])
            segs = bytes.fromhex(row["segments"])
            ip = 0x1B3 if row["kind"] == "after-actor" else 0x207
            require(
                (
                    int.from_bytes(regs[32:36], "little") & 65535,
                    int.from_bytes(segs[8:16], "little"),
                    int.from_bytes(segs[24:32], "little"),
                )
                == (ip, terminal["load_segment"] + 0xAAF, terminal["dgroup_segment"]),
                "clock actual boundary CS:IP/DS",
            )
    require(
        counts == summary["counts"]
        and rows[0]["kind"] == "initial-host"
        and counts.get("initial-host") == 1
        and counts.get("main-start") == 1
        and summary["master_watch_retired_at_frame"] == 1,
        "clock observer lifecycle/counts",
    )
    require(
        list(actor) == list(range(1, limit + 1)) and events,
        "clock complete actor/event extent",
    )
    require(list(score) == frames, "clock complete score-sample extent")
    return actor, score, events


def evaluate_model(rows, events):
    """Test the constructor and existing nominal clock without phase fitting."""
    phase = count = 0
    transition_bad = []
    for index, row in enumerate(events):
        if row["_state"][:2] != (phase, count):
            transition_bad.append(
                dict(
                    event=index, expected=[phase, count], actual=list(row["_state"][:2])
                )
            )
        phase, count = advance(phase, count, row["_state"][2])
    origin = Fraction.from_float(double(events[0]["raw"], "frame_start"))
    require(
        events[0]["_time"] == origin
        and double(events[0]["raw"], "vga_mode_time_base") == float(origin)
        and int.from_bytes(
            bytes.fromhex(events[0]["raw"]["vga_mode_frames_since_time_base"]),
            "little",
            signed=True,
        )
        == 0,
        "actual first display initialization epoch",
    )
    period_ms = double(events[0]["raw"], "period")
    require(
        math.isfinite(period_ms) and period_ms > 0, "positive configured display period"
    )
    period_ns = round(period_ms * 1000000)
    require(period_ns == 17723227, "supported existing native display period")
    eligible = [
        row
        for row in rows
        if row["kind"] in ["main-start", "after-actor", "after-score"]
    ]
    nominal_bad = []
    for row in eligible:
        require(
            row["_state"][2] == 32
            and double(row["raw"], "period") == period_ms
            and double(row["raw"], "vga_mode_time_base") == float(origin),
            "stable configured rate/geometry/reset epoch",
        )
        elapsed = round((row["_time"] - origin) * 1000000)
        require(elapsed >= 0, "elapsed before display initialization")
        require(elapsed < 2**63, "elapsed native signed width")
        refreshes = 1 + elapsed // period_ns
        expected = (refreshes // 32 % 4, refreshes % 32)
        if expected != row["_state"][:2]:
            nominal_bad.append(
                dict(
                    kind=row["kind"],
                    frame=row["frame"],
                    elapsed_ns=elapsed,
                    expected=list(expected),
                    actual=list(row["_state"][:2]),
                )
            )
        row["_elapsed_ns"] = elapsed
    return origin, period_ns, transition_bad, nominal_bad, len(eligible)


def analyze(capture, target):
    original = load(capture, target)
    receipt = original["receipt"]
    require(
        receipt["role"] == "original" and receipt["complete"],
        "complete original clock capture",
    )
    limit = receipt["end_after"]
    summary_bytes = (capture / "display-clock-summary.json").read_bytes()
    summary = json.loads(summary_bytes)
    trace_bytes = (capture / "display-clock.jsonl").read_bytes()
    require(
        summary["complete"] and summary["trace_sha256"] == sha(trace_bytes),
        "clock summary/trace identity",
    )
    abis = [
        Path(name)
        for name in receipt["source_files"]
        if Path(name).name == "clock-abi.json"
    ]
    readers = [
        Path(name)
        for name in receipt["source_files"]
        if Path(name).name == "clock_gdb.py"
    ]
    plans = [
        Path(name)
        for name in receipt["source_files"]
        if Path(name).name == "font-plan.json"
    ]
    require(
        len(abis) == len(readers) == len(plans) == 1,
        "unique clock ABI/reader/picture plan",
    )
    for p in abis + readers + plans:
        require(
            sha(p.read_bytes()) == receipt["source_files"][str(p)],
            "clock source identity",
        )
    abi = json.loads(abis[0].read_text())
    require(
        abi["passed"]
        and abi["emulator_sha256"]
        == receipt["emulator_sha256"]
        == "6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1",
        "clock emulator ABI identity",
    )
    require(
        summary["abi_sha256"] == sha(abis[0].read_bytes())
        and summary["reader_sha256"] == sha(readers[0].read_bytes()),
        "active clock ABI/reader identity",
    )
    require(
        abi["layout"]["gdc_size"] == 232
        and abi["layout"]["blink_offset"] == 196
        and abi["layout"]["blink_count_offset"] == 197
        and abi["layout"]["blink_rate_offset"] == 198
        and abi["layout"]["pic_ticks_size"] == abi["layout"]["cycle_size"] == 8,
        "supported raw clock ABI",
    )
    for name, digest in abi["source_inputs"].items():
        require(sha(Path(name).read_bytes()) == digest, "clock ABI source: " + name)
    require(
        set(summary["symbols"]) == set(abi["symbols"])
        and len(
            {
                summary["symbols"][name] - row["address"]
                for name, row in abi["symbols"].items()
            }
        )
        == 1,
        "clock ELF symbol mapping",
    )
    rows = [json.loads(line) for line in trace_bytes.splitlines()]
    frames = json.loads(plans[0].read_text())["frames"]
    require(
        frames == sorted(set(frames))
        and all(type(f) is int and 0 < f < limit for f in frames),
        "clock picture plan extent/order",
    )
    terminal = json.loads((capture / "ordinary-terminal.json").read_text())
    actor, score, events = validate_rows(rows, abi, summary, limit, frames, terminal)
    for frame, block in records(
        capture / "ordinary-video.bin.gz",
        terminal["load_segment"],
        terminal["dgroup_segment"],
        terminal["cr0"],
        terminal["cr3"],
        limit,
    ):
        gdc = block[OFFSETS["gdc"] : OFFSETS["gdc"] + SIZES["gdc"]]
        row = actor[frame]
        require(
            sha(gdc) == row["raw"]["gdc_sha256"]
            and gdc[196:199].hex() == row["raw"]["master_blink"],
            "clock actor/full-video identity",
        )
    for frame, row in score.items():
        stem = capture / "post-score-checkpoints" / str(frame)
        metadata = json.loads(Path(str(stem) + ".json").read_text())
        video = gzip.decompress(Path(str(stem) + "-video.bin.gz").read_bytes())
        require(
            sha(video) == metadata["video_sha256"]
            and metadata["registers"] == row["registers"]
            and metadata["segments"] == row["segments"],
            "clock score checkpoint identity",
        )
        gdc = video[OFFSETS["gdc"] : OFFSETS["gdc"] + SIZES["gdc"]]
        require(
            sha(gdc) == row["raw"]["gdc_sha256"]
            and gdc[196:199].hex() == row["raw"]["master_blink"],
            "clock score/full-video identity",
        )
    origin, period_ns, transition_bad, nominal_bad, observations = evaluate_model(
        rows, events
    )
    plan = ["TH04_DISPLAY_NS 1 " + str(limit - 1) + " " + str(period_ns)]
    previous = -1
    for frame in range(1, limit):
        selected = score.get(frame, actor[frame])
        elapsed = selected["_elapsed_ns"]
        require(elapsed > previous, "complete-update display time order")
        previous = elapsed
        plan.append(str(frame) + " " + str(elapsed))
    text = "\n".join(plan) + "\n"
    report = dict(
        passed=not transition_bad and not nominal_bad,
        capture_receipt_sha256=sha((capture / "receipt.json").read_bytes()),
        clock_summary_sha256=sha(summary_bytes),
        clock_trace_sha256=sha(trace_bytes),
        clock_abi_sha256=sha(abis[0].read_bytes()),
        clock_reader_sha256=sha(readers[0].read_bytes()),
        attester_sha256=sha(Path(__file__).read_bytes()),
        origin_ms_numerator=origin.numerator,
        origin_ms_denominator=origin.denominator,
        period_ns=period_ns,
        prefix_actual_master_entries=len(events),
        prefix_transition_differences=len(transition_bad),
        prefix_first_differences=transition_bad[:8],
        nominal_clock_observations=observations,
        nominal_clock_differences=len(nominal_bad),
        nominal_first_differences=nominal_bad[:8],
        after_actor_frames=limit,
        after_score_frames=frames,
        updates=limit - 1,
        times_sha256=sha(text.encode()),
        scope=__doc__
        + " Raw PIC uses the exact ticks/cycle rational. Source ABI, ELF mapping and "
        "complete original video/CPU bind every actor and sampled score clock. "
        "Constructor zero and the actual first display initialization define the "
        "prefix transitions and origin. The existing rounded 17723227 ns native "
        "period is tested against every independent raw phase/count. Exported "
        "inputs contain elapsed ns only: actor boundaries, with actual score "
        "returns for sampled pictures. Frame 0 display, UI interiors, natural "
        "OP/loader and CPU/I/O timing, scanout, campaigns, NP2 and Windows remain "
        "outside this bounded fixture.",
    )
    return report, text


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["capture", "main", "output"]:
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--times-output", type=Path)
    args = p.parse_args()
    report, text = analyze(args.capture.resolve(), args.main.read_bytes())
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    if args.times_output:
        require(report["passed"], "clock attestation rejected timing export")
        with args.times_output.open("x") as stream:
            stream.write(text)
    print(
        json.dumps(
            {
                k: report[k]
                for k in [
                    "passed",
                    "prefix_actual_master_entries",
                    "prefix_transition_differences",
                    "nominal_clock_observations",
                    "nominal_clock_differences",
                    "updates",
                ]
            }
        )
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
