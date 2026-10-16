#!/usr/bin/env python3
"""Attest actual own-file stage epochs from raw trace,CPU,DGROUP and video."""

import gzip, hashlib, json, struct
from pathlib import Path

root = Path(__file__).resolve().parents[2]
from compare_th04_dos_ordinary_prefix import load
from compare_th04_dos_demos import relocated_module
from th04_demo_video import BLOCK_SIZE, OFFSETS

sha = lambda b: hashlib.sha256(b).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def parse_raw(raw, main, profile, load_segment):
    counts = {"lcg": 0, "ring": 0}
    rows = {}
    pending = []
    events = {}
    loaded = False
    for line in raw.decode("ascii").splitlines():
        c = line.split()
        kind = c[0]
        if kind == "L":
            require(
                not loaded
                and len(c) == 6
                and c[1] == "1"
                and int(c[2], 16) == load_segment
                and bytes.fromhex(c[-1]) == relocated_module(main, load_segment),
                "epoch full relocated module identity",
            )
            loaded = True
        elif kind == "R":
            require(loaded and len(c) == 9 and c[1] == "1", "epoch RNG shape")
            index = int(c[2])
            require(2 <= index < len(profile["hooks"]), "epoch RNG index")
            hook, seg, off = profile["hooks"][index]
            require(
                (int(c[3], 16), int(c[4], 16)) == (load_segment + seg, off),
                "epoch RNG own-file PC",
            )
            counts["lcg" if hook == 3 else "ring"] += 1
            pending.append([index, int(c[8], 16) if index in [4, 5, 7, 8] else None])
        else:
            require(
                kind == "I"
                and loaded
                and c[1] == "1"
                and len(c) == len(profile["fields"]) + 8,
                "epoch raw loop shape",
            )
            entry = profile["entries"]["loop"]
            require(
                [int(v, 16) for v in c[2:5]]
                == [
                    load_segment + entry["segment"],
                    entry["offset"],
                    load_segment + profile["dgroup"],
                ],
                "epoch raw loop own-file PC/DS",
            )
            require(
                [int(v) for v in c[5:7]] == [counts["lcg"], counts["ring"]],
                "epoch raw RNG count",
            )
            fields = {}
            for (name, _, size), value in zip(profile["fields"], c[7:-1], strict=True):
                require(
                    len(bytes.fromhex(value)) == size
                    and value == bytes.fromhex(value).hex(),
                    "epoch raw field width",
                )
                fields[name] = value
            stage = int(fields["stage"], 16)
            frame = int.from_bytes(bytes.fromhex(fields["frame"]), "little")
            key = (stage, frame)
            require(
                key not in rows and stage in [0, 1], "duplicate/invalid raw stage/frame"
            )
            resident = bytes.fromhex(c[-1])
            require(
                len(resident) == 80 and resident[:11] == b"HUMAConfig\0",
                "epoch raw resident identity",
            )
            rows[key] = dict(
                fields=fields,
                resident=resident.hex(),
                lcg_calls=counts["lcg"],
                ring_calls=counts["ring"],
            )
            events[key] = pending
            pending = []
    return rows, events, counts, pending


def records(capture):
    summary = json.loads((capture / "stage-boundary-summary.json").read_text())
    metadata_path = capture / "stage-boundary.jsonl"
    with metadata_path.open("rb") as metadata:
        require(sum(1 for _ in metadata) == summary["records"], "epoch record count")
    prior_group = prior_video = 0
    with (
        metadata_path.open() as metadata,
        gzip.open(capture / "stage-boundary.bin.gz", "rb") as stream,
    ):
        require(stream.read(8) == b"TH04SB1\n", "epoch wire header")
        observed = 0
        for index, line in enumerate(metadata):
            row = json.loads(line)
            header = stream.read(4)
            require(
                len(header) == 4
                and struct.unpack("<I", header)[0] == row["ordinal"] == index,
                "epoch wire order",
            )
            group = stream.read(65536)
            video = stream.read(BLOCK_SIZE)
            require(
                len(group) == 65536 and len(video) == BLOCK_SIZE,
                "epoch complete record extent",
            )
            prior_group ^= int.from_bytes(group, "little")
            prior_video ^= int.from_bytes(video, "little")
            group = prior_group.to_bytes(65536, "little")
            video = prior_video.to_bytes(BLOCK_SIZE, "little")
            require(
                (sha(group), sha(video)) == (row["dgroup_sha256"], row["video_sha256"]),
                "epoch raw wire identity",
            )
            observed += 1
            yield row, group, video
        require(observed == summary["records"], "epoch complete streamed metadata")
        require(stream.read(1) == b"", "epoch trailing wire data")


def watchpoint_resources(summary, rows, expected_slots, required=False):
    """Validate actual debugger registry observations without guest-state writes."""
    if "watchpoint_cache_limit" not in summary:
        require(not required, "epoch required bounded watchpoint observations")
        return None
    baseline = summary["baseline_registered_breakpoints"]
    require(
        type(baseline) is int
        and 0 <= baseline <= 64
        and summary["watchpoint_cache_limit"] == expected_slots,
        "epoch bounded watchpoint declaration",
    )
    previous_slots = 0
    maximum_registered = baseline
    for row in rows:
        slots = row["watchpoint_cache_slots"]
        registered = row["registered_breakpoints"]
        require(
            type(slots) is int
            and previous_slots <= slots <= expected_slots
            and type(registered) is int
            and slots <= registered <= baseline + slots
            and row["baseline_registered_breakpoints"] == baseline,
            "epoch bounded watchpoint registry",
        )
        previous_slots = slots
        maximum_registered = max(maximum_registered, registered)
    require(
        previous_slots == summary["watchpoint_cache_slots"] == expected_slots
        and maximum_registered == summary["maximum_registered_breakpoints"],
        "epoch complete watchpoint resource summary",
    )
    return dict(
        passed=True,
        cache_slots=expected_slots,
        baseline_registered=baseline,
        maximum_registered=maximum_registered,
        observations=len(rows),
    )


def attest(
    capture,
    target,
    source_snapshot=None,
    stage2_updates=600,
    require_bounded_watchpoints=False,
):
    require(
        type(stage2_updates) is int and 0 < stage2_updates <= 65535,
        "epoch configured Stage2 extent",
    )
    prefix = load(capture, target, source_snapshot)
    receipt = prefix["receipt"]
    require(
        receipt["complete"] and receipt["end_after"] == 9836,
        "epoch complete first-stage prefix",
    )
    summary_bytes = (capture / "stage-boundary-summary.json").read_bytes()
    summary = json.loads(summary_bytes)
    profile = summary["profile"]
    profile_path = capture_source(receipt, "boundary-profiles.json")
    profiles = json.loads(profile_path.read_text())
    require(profile == profiles[receipt["role"]], "epoch executed profile binding")
    ordinary = json.loads((capture / "profile.json").read_text())
    require(
        all(profile[k] == v for k, v in ordinary.items()),
        "epoch baseline profile binding",
    )
    layout_path = Path(profile["layout_path"])
    require(
        sha(layout_path.read_bytes()) == profile["layout_sha256"],
        "epoch pinned video ABI receipt",
    )
    require(
        receipt["emulator_sha256"]
        == "6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1",
        "epoch pinned runtime observer binary",
    )
    require(
        receipt["emulator_receipt_sha256"]
        == "43af0cfd0ce27474b088d6564325a1cc6f0c9f91cd14a9247ac7f62a92e7e86b",
        "epoch pinned runtime observer receipt",
    )
    command = receipt["command"]
    emulator = Path(command[command.index("--args") + 1])
    require(
        sha(emulator.read_bytes()) == receipt["emulator_sha256"],
        "epoch runtime observer executable identity",
    )
    emulator_receipt = emulator.parents[3] / "receipt.json"
    require(
        sha(emulator_receipt.read_bytes()) == receipt["emulator_receipt_sha256"],
        "epoch runtime observer build receipt identity",
    )
    built_emulator = json.loads(emulator_receipt.read_text())
    require(
        Path(built_emulator["binary"]) == emulator
        and built_emulator["binary_sha256"] == receipt["emulator_sha256"],
        "epoch runtime observer producer binding",
    )
    main = Path(profile["main_path"]).read_bytes()
    require(
        sha(main) == profile["main_sha256"] == receipt["main_sha256"],
        "epoch own MZ identity",
    )
    require(
        profile["map_path"] == receipt["map_path"]
        and profile["map_sha256"] == receipt["map_sha256"],
        "epoch own MAP identity",
    )
    require(
        summary["complete"]
        and summary["stage2_complete_updates"] == stage2_updates
        and profile["stage2_updates"] == stage2_updates,
        "epoch complete next-stage fixture",
    )
    require(
        summary["trace_sha256"] == sha((capture / "stage-boundary.jsonl").read_bytes())
        and summary["wire_sha256"]
        == sha((capture / "stage-boundary.bin.gz").read_bytes()),
        "epoch trace/wire summary identity",
    )
    require(
        summary["reader_sha256"]
        == receipt["source_files"][
            str(capture_source(receipt, "stage_boundary_gdb.py"))
        ],
        "epoch active reader identity",
    )
    raw = (capture / "stage-all-raw.txt").read_bytes()
    bounded = (capture / "raw.txt").read_bytes()
    require(
        raw.startswith(bounded)
        and len(bounded) == summary["first_stage_prefix_bytes"]
        and sha(bounded) == summary["first_stage_prefix_sha256"]
        and sha(raw) == summary["extended_raw_sha256"]
        and raw[len(bounded) :] == (capture / "stage2-raw-suffix.txt").read_bytes(),
        "epoch immutable prefix/extended trace split",
    )
    load_segment = prefix["bounded_terminal"]["load_segment"]
    raw_rows, events, counts, pending = parse_raw(raw, main, profile, load_segment)
    require(not pending, "epoch unconsumed trailing RNG events")
    require(
        [key for key in raw_rows if key[0] == 0] == [(0, f) for f in range(9837)]
        and [key for key in raw_rows if key[0] == 1]
        == [(1, f) for f in range(stage2_updates + 1)],
        "epoch complete raw stage/frame ranges",
    )
    module = relocated_module(main, load_segment)
    bridge = [
        "stage1-actor",
        "stage1-score",
        "gameplay_return",
        "stage_free",
        "stage_init",
        "init_return",
    ]
    rows = []
    fields = profile["fields"]
    full_mem = 0
    for row, group, video in records(capture):
        ordinal = row["ordinal"]
        label = row["label"]
        expected_label = (
            bridge[ordinal]
            if ordinal < 6
            else ["stage2-loop", "stage2-actor", "stage2-score"][(ordinal - 6) % 3]
        )
        require(label == expected_label, "epoch bridge/stage2 boundary order")
        if ordinal >= 6:
            require(
                row["stage"] == 1
                and row["frame"] == (ordinal - 6) // 3 + (label != "stage2-loop"),
                "epoch sequential Stage2 frames",
            )
        regs = bytes.fromhex(row["cpu_regs"])
        segs = bytes.fromhex(row["segments"])
        require(
            row["unchanged_context"] and len(regs) == 48 and len(segs) == 136,
            "epoch raw CPU/read-only assertion",
        )
        cs = int.from_bytes(segs[8:16], "little")
        ip = int.from_bytes(regs[32:36], "little") & 65535
        ds = int.from_bytes(segs[24:32], "little")
        require(
            (cs, ip, ds) == (row["cs"], row["ip"], row["dgroup_segment"])
            and ds == load_segment + profile["dgroup"],
            "epoch actual CPU/DS",
        )
        point_key = (
            "score"
            if label in ["stage1-score", "stage2-score"]
            else "loop"
            if label == "stage2-loop"
            else "actor"
            if label == "stage2-actor"
            else label
        )
        if label == "stage1-actor":
            require(
                (cs, ip)
                == (prefix["bounded_terminal"]["cs"], prefix["bounded_terminal"]["ip"]),
                "epoch actual first-stage store context",
            )
        else:
            point = profile["entries"][point_key]
            require(
                (cs, ip) == (load_segment + point["segment"], point["offset"]),
                "epoch own entry PC",
            )
        start = (cs - load_segment) * 16 + ip
        require(
            bytes.fromhex(row["opcode"]) == module[start : start + 16],
            "epoch relocated own-file code readback",
        )
        require(
            all(
                group[at : at + size].hex() == row["fields"][name]
                for name, at, size in fields
            ),
            "epoch complete DGROUP/fields",
        )
        frame = int.from_bytes(bytes.fromhex(row["fields"]["frame"]), "little")
        stage = int(row["fields"]["stage"], 16)
        require(
            (frame, stage) == (row["frame"], row["stage"])
            and video[OFFSETS["stage"]] == stage,
            "epoch stage/frame/video identity",
        )
        resident = bytes.fromhex(row["resident"])
        require(
            len(resident) == 256 and resident[:11] == b"HUMAConfig\0",
            "epoch complete resident owner",
        )
        pointer = bytes.fromhex(row["fields"]["resident_pointer"])
        require(
            row["resident_linear"]
            == int.from_bytes(pointer[:2], "little")
            + int.from_bytes(pointer[2:], "little") * 16,
            "epoch resident pointer ownership",
        )
        if stage == 1:
            require(
                (row["lcg_calls"], row["ring_calls"])
                == (
                    raw_rows[(stage, frame)]["lcg_calls"],
                    raw_rows[(stage, frame)]["ring_calls"],
                ),
                "epoch boundary RNG counters",
            )
        if label == "stage2-loop":
            saved = raw_rows[(stage, frame)]
            require(
                saved["fields"] == row["fields"]
                and saved["resident"] == resident[:80].hex()
                and (saved["lcg_calls"], saved["ring_calls"])
                == (row["lcg_calls"], row["ring_calls"]),
                "epoch independent C++/GDB loop identity",
            )
        if row["memory"]:
            memory = gzip.decompress(
                (capture / "stage-boundary" / row["memory"]).read_bytes()
            )
            require(
                len(memory) == 655360
                and sha(memory) == row["memory_sha256"]
                and memory[ds * 16 : ds * 16 + 65536] == group
                and memory[row["resident_linear"] : row["resident_linear"] + 256]
                == resident,
                "epoch complete conventional memory ownership",
            )
            ss = int.from_bytes(segs[16:24], "little")
            sp = int.from_bytes(regs[16:20], "little") & 65535
            require(
                (ss, sp) == (row["ss"], row["sp"])
                and memory[ss * 16 + sp : ss * 16 + sp + 64].hex() == row["stack"],
                "epoch raw stack ownership",
            )
            full_mem += 1
        rows.append(row)
    require(len(rows) == 3 * stage2_updates + 7, "epoch full boundary extent")
    b = rows[:6]
    require(
        [v["frame"] for v in b] == [9836, 9836, 9837, 9837, 9837, 0]
        and [v["stage"] for v in b] == [0, 0, 0, 0, 0, 1]
        and b[1]["quit"] == 0
        and b[2]["quit"] == 2,
        "observed final loop and actual stage reset",
    )
    require(
        b[5]["lcg_calls"] - b[2]["lcg_calls"] == 353
        and b[5]["ring_calls"] == b[2]["ring_calls"],
        "observed persistent LCG and ring refill ownership",
    )
    report = dict(
        passed=True,
        video_layout_sha256=profile["layout_sha256"],
        executed_profile_sha256=sha(profile_path.read_bytes()),
        emulator_sha256=receipt["emulator_sha256"],
        role=receipt["role"],
        artifact_sha256=profile["main_sha256"],
        map_sha256=profile["map_sha256"],
        capture_receipt_sha256=sha((capture / "receipt.json").read_bytes()),
        boundary_summary_sha256=sha(summary_bytes),
        reader_sha256=sha(Path(__file__).read_bytes()),
        rows=len(rows),
        stage1_final_complete_frame=9837,
        stage2_complete_updates=stage2_updates,
        full_conventional_snapshots=full_mem,
        bridge=[
            {
                k: v[k]
                for k in [
                    "label",
                    "frame",
                    "stage",
                    "quit",
                    "lcg_calls",
                    "ring_calls",
                    "cs",
                    "ip",
                    "dgroup_segment",
                    "resident",
                ]
            }
            for v in b
        ],
        raw_loop_samples=len(raw_rows),
        raw_rng_counts=counts,
        stage_init_lcg_draws=353,
        loop_contexts_bound=stage2_updates + 1,
        scope=__doc__
        + f" Source/capture/MZ/MAP/profile/ABI identity, complete relocated module, CPU/opcode/DGROUP/video/resident and selected conventional memory are checked. Independent C++ loop samples bind every Stage2 frame. This DOSBox-X fixture observes Stage1 return at9837 and{stage2_updates} complete Stage2 updates, with353 initialization LCG calls and no process reseed. It does not accept a campaign, physical timing, NP2, Windows or historical exactness.",
    )
    resources = watchpoint_resources(
        summary, rows, len(profile["entries"]), require_bounded_watchpoints
    )
    if resources is not None:
        report["watchpoint_resources"] = resources
    require(
        ("stage2_waits" in profile) == ("stage2_waits_sha256" in summary),
        "epoch blocking observation declaration",
    )
    if "stage2_waits" in profile:
        from th04_stage_waits import attest_waits

        report["stage2_waits"] = attest_waits(
            capture, main, target, profile, load_segment, raw_rows
        )
    return report, rows, raw_rows, events


def capture_source(receipt, name):
    matches = [Path(p) for p in receipt["source_files"] if Path(p).name == name]
    require(len(matches) == 1, "unique epoch reader source")
    return matches[0]


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--source-snapshot", type=Path)
    p.add_argument("--stage2-updates", type=int, default=600)
    p.add_argument("--require-bounded-watchpoints", action="store_true")
    p.add_argument("--require-stage2-waits", action="store_true")
    args = p.parse_args()
    report, *_ = attest(
        args.capture.resolve(),
        (root / ".analysis/targets/th04/main.exe").read_bytes(),
        args.source_snapshot,
        args.stage2_updates,
        args.require_bounded_watchpoints,
    )
    require(
        not args.require_stage2_waits or "stage2_waits" in report,
        "required Stage2 wait observations",
    )
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(
        "ACTUAL OWN-FILE STAGE EPOCH ATTESTATION PASS",
        report["role"],
        report["rows"],
        report["stage2_complete_updates"],
        flush=True,
    )
