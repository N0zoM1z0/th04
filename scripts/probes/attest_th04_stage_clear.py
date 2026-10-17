#!/usr/bin/env python3
"""Attest actual Stage2 score exit and the first complete Stage3 update."""
import gzip, hashlib, json, struct
from pathlib import Path
from attest_th04_stage_boundary import capture_source, parse_raw, records, require, sha, watchpoint_resources
from compare_th04_dos_ordinary_prefix import load
from compare_th04_dos_demos import relocated_module
from capture_th04_dos_demos import map_symbols
from th04_demo_video import BLOCK_SIZE, OFFSETS

root = Path(__file__).resolve().parents[2]


def attest_exit_cfg(main, original, profile):
    entries = profile["entries"]
    segment = entries["score"]["segment"]
    score = entries["score"]["offset"]
    header = int.from_bytes(main[8:10], "little") * 16
    code = main[header + segment * 16 : header + segment * 16 + 65536]
    raw = code[score : score + 12]
    require(raw[:2] == b"\x80\x3e" and int.from_bytes(raw[2:4], "little") == profile["quit_offset"]
            and raw[4:7] == b"\0\x0f\x84" and raw[9:] == b"\x5e\x5d\xc3", "clear own post-score quit/JE/RET")
    loop_start = (score + 9 + struct.unpack_from("<h", raw, 7)[0]) & 65535
    hook = entries["loop"]["offset"]
    require(hook == loop_start + 9 and code[loop_start] == 0x9a
            and code[loop_start + 5 : hook - 2] == b"\xff\x16", "clear loop input/callback prefix")
    returned = entries["gameplay_return"]["offset"]
    require(code[returned - 3] == 0xe8 and code[score - 3] == 0xe8, "clear own caller/score near calls")
    function = (returned + struct.unpack_from("<h", code, returned - 2)[0]) & 65535
    callee = (score + struct.unpack_from("<h", code, score - 2)[0]) & 65535
    require(function < loop_start < hook < score and code[function : function + 4] == b"\x55\x8b\xec\x56", "clear bounded gameplay function")
    if profile["map_path"] is None:
        require(main == original and (segment, score, callee) == (0x0aaf, 0x207, 0x6bd4), "clear original bounded owner")
    else:
        symbols = map_symbols(Path(profile["map_path"]))
        require(symbols["gameplay_loop()"] == (segment, function)
                and symbols["score_update_and_render()"] == (segment, callee)
                and symbols["_quit"] == (profile["dgroup"], profile["quit_offset"]), "clear source own MAP owners")
    return dict(segment=segment, score=score, function=function, loop_start=loop_start, loop_hook=hook, score_callee=callee, quit_offset=profile["quit_offset"], raw=raw.hex())


def attest_clear_tail(rows, raw, events, updates, profile):
    regular = 3 * updates + 6
    last_actor, last_score = rows[regular - 2 : regular]
    tail = rows[regular:]
    require(last_actor["label"] == "stage2-actor" and last_score["label"] == "stage2-score"
            and last_actor["frame"] == last_score["frame"] == updates
            and last_score["quit"] == 2 and all(v["quit"] == 2 for v in tail[:3]), "clear actual final score/return quit")
    names = lambda m: (m["lcg_calls"], m["ring_calls"])
    before = raw[(1, updates - 1)]
    limit = raw[(2, 0)]
    event_list = events[(2, 0)]
    counts = [before["lcg_calls"], before["ring_calls"]]
    prefixes = {tuple(counts)}
    for index, value in event_list:
        counts[0 if profile["hooks"][index][0] == 3 else 1] += 1
        prefixes.add(tuple(counts))
    require(tuple(counts) == names(limit), "clear ordered raw RNG suffix extent")
    for m in [last_actor, last_score, *tail[:4]]:
        require(names(m) in prefixes, "clear intermediate counts are real raw RNG prefixes")
    require(all(names(v) == names(last_score) for v in tail[:3]), "clear return/free/pre-init RNG stability")
    require(all(v["fields"]["lcg"] == last_score["fields"]["lcg"] for v in tail[:3]), "clear retained process LCG before initialization")
    for left, right in [(before, last_score), (last_score, tail[3])]:
        delta = right["lcg_calls"] - left["lcg_calls"]
        require(delta >= 0, "clear monotonic LCG count")
        value = int.from_bytes(bytes.fromhex(left["fields"]["lcg"]), "little")
        for _ in range(delta): value = (value * 0x015a4e35 + 1) & 0xffffffff
        require(value == int.from_bytes(bytes.fromhex(right["fields"]["lcg"]), "little"), "clear process LCG continuity")
    require(tail[3]["lcg_calls"] == limit["lcg_calls"] and tail[3]["ring_calls"] == limit["ring_calls"], "clear Stage3 init/first-loop RNG identity")


def attest_clear(
    capture,
    target,
    source_snapshot=None,
    stage2_updates=11000,
    require_bounded_watchpoints=False,
    stage3_updates=1,
    extra_registered_watchpoints=0,
):
    require(
        type(stage2_updates) is int and 0 < stage2_updates <= 65535,
        "epoch configured Stage2 extent",
    )
    require(type(stage3_updates) is int and 0 < stage3_updates <= 65535, "clear configured Stage3 extent")
    require(type(extra_registered_watchpoints) is int and extra_registered_watchpoints in [0, 1],
            "clear explicit additional observer registry")
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
    budget = stage2_updates
    require(
        summary["complete"] and summary["stage2_until_clear"] is True
        and profile["stage2_until_clear"] is True
        and summary["stage2_clear_checkpoint"] == profile["stage2_clear_checkpoint"] == "score"
        and summary["stage2_update_budget"] == profile["stage2_updates"] == budget
        and type(summary["stage2_complete_updates"]) is int
        and 9905 < summary["stage2_complete_updates"] <= budget
        and summary["stage3_complete_updates"] == profile["stage3_updates"] == stage3_updates
        and summary["stage2_final_score_quit"] == 2,
        "clear observed post-score exit/budget/followup",
    )
    stage2_updates = summary["stage2_complete_updates"]
    require(summary["stage2_last_raw_loop_frame"] == stage2_updates - 1,
            "clear terminal update has no following Stage2 loop")
    exit_cfg = attest_exit_cfg(main, target, profile)
    require(
        summary["trace_sha256"] == sha((capture / "stage-boundary.jsonl").read_bytes())
        and summary["wire_sha256"]
        == sha((capture / "stage-boundary.bin.gz").read_bytes()),
        "epoch trace/wire summary identity",
    )
    require(
        summary["reader_sha256"]
        == receipt["source_files"][
            str(capture_source(receipt, "stage_clear_score_gdb.py"))
        ],
        "epoch active reader identity",
    )
    require(summary["base_reader_sha256"] == receipt["source_files"][
        str(capture_source(receipt, "stage_boundary_gdb.py"))], "clear complete base reader identity")
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
    raw_rows, events, counts, pending = parse_raw(raw, main, profile, load_segment, allowed_stages=(0, 1, 2))
    require(not pending, "epoch unconsumed trailing RNG events")
    require(
        [key for key in raw_rows if key[0] == 0] == [(0, f) for f in range(9837)]
        and [key for key in raw_rows if key[0] == 1]
        == [(1, f) for f in range(stage2_updates)]
        and [key for key in raw_rows if key[0] == 2] == [(2, f) for f in range(stage3_updates + 1)],
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
    tail_labels = ["stage2-return", "stage2-free", "stage3-init", "stage3-init-return", "stage3-loop"]
    tail_labels += [label for _ in range(stage3_updates)
                    for label in ["stage3-actor", "stage3-score", "stage3-loop"]]
    tail_frames = [stage2_updates] * 3 + [0, 0]
    tail_frames += [frame for frame in range(1, stage3_updates + 1) for _ in range(3)]
    tail_stages = [1] * 3 + [2] * (3 * stage3_updates + 2)
    regular_extent = 3 * stage2_updates + 6
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
            if ordinal < regular_extent
            else tail_labels[ordinal - regular_extent]
        )
        require(label == expected_label, "epoch bridge/stage2 boundary order")
        if 6 <= ordinal < regular_extent:
            require(
                row["stage"] == 1
                and row["frame"] == (ordinal - 6) // 3 + (label != "stage2-loop"),
                "epoch sequential Stage2 frames",
            )
        if ordinal >= regular_extent:
            ti = ordinal - regular_extent
            require((row["stage"], row["frame"]) == (tail_stages[ti], tail_frames[ti]),
                    "clear actual return/init/first-update frame order")
            if ti < 8 or ti >= len(tail_labels) - 3:
                require(bool(row["memory"]), "clear mandatory complete tail memory")
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
            if label in ["stage1-score", "stage2-score", "stage3-score"]
            else "loop"
            if label in ["stage2-loop", "stage3-loop"]
            else "actor"
            if label in ["stage2-actor", "stage3-actor"]
            else {"stage2-return": "gameplay_return", "stage2-free": "stage_free",
                  "stage3-init": "stage_init", "stage3-init-return": "init_return"}.get(label, label)
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
        require(row["quit"] == group[profile["quit_offset"]], "clear actual DGROUP quit owner")
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
        if stage in [1, 2] and (stage, frame) in raw_rows:
            require(
                (row["lcg_calls"], row["ring_calls"])
                == (
                    raw_rows[(stage, frame)]["lcg_calls"],
                    raw_rows[(stage, frame)]["ring_calls"],
                ),
                "epoch boundary RNG counters",
            )
        if label in ["stage2-loop", "stage3-loop"]:
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
    require(len(rows) == 3 * stage2_updates + 3 * stage3_updates + 11, "clear complete boundary extent")
    attest_clear_tail(rows, raw_rows, events, stage2_updates, profile)
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
        stage2_update_budget=budget,
        stage2_until_clear=True,
        stage3_init_lcg_draws=rows[regular_extent + 3]["lcg_calls"] - rows[regular_extent]["lcg_calls"],
        stage3_init_ring_draws=rows[regular_extent + 3]["ring_calls"] - rows[regular_extent]["ring_calls"],
        stage2_clear_checkpoint="score",
        stage3_complete_updates=stage3_updates,
        exit_cfg=exit_cfg,
        clear_bridge=[{k: v[k] for k in ["label", "frame", "stage", "quit", "lcg_calls", "ring_calls", "cs", "ip", "dgroup_segment", "resident"]}
                      for v in (rows[regular_extent:] if stage3_updates == 1
                                else rows[regular_extent:regular_extent + 8] + rows[-3:])],
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
        loop_contexts_bound=stage2_updates + stage3_updates + 1,
        scope=__doc__
        + f" Own-MZ/MAP/raw/CPU/DGROUP/video/full-memory/CFG attest {stage2_updates} complete Stage2 updates and {'one' if stage3_updates == 1 else stage3_updates} complete Stage3 update{'s' if stage3_updates != 1 else ''}. Post-score quit2 returns without another loop. Raw RNG suffixes independently bind the final update and next initialization; LCG continuity is checked. Native fidelity, physical timing, NP2, Windows, campaigns and historical exactness remain separate.",
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
            capture, main, target, profile, load_segment, raw_rows, extra_registered_watchpoints
        )
    return report, rows, raw_rows, events


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dos-root", type=Path, default=root)
    p.add_argument("--source-snapshot", type=Path)
    p.add_argument("--capture", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--stage2-budget", type=int, default=11000)
    args = p.parse_args()
    report, *_ = attest_clear(args.capture.resolve(), (args.dos_root.resolve() / ".analysis/targets/th04/main.exe").read_bytes(), source_snapshot=args.source_snapshot, stage2_updates=args.stage2_budget, require_bounded_watchpoints=True)
    with args.output.open("x") as stream: json.dump(report, stream, indent=2);stream.write("\n")
    print("ACTUAL OWN-FILE STAGE CLEAR ATTESTATION PASS",report["role"],report["stage2_complete_updates"],report["stage3_complete_updates"],flush=True)
