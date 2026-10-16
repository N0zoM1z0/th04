"""Attest Stage2 blocking input owners from own-file CPU and full-memory records."""

import gzip
import hashlib
import json
import re
import struct
from pathlib import Path

from capture_th04_dos_demos import map_symbols
from compare_th04_dos_demos import relocated_module, require
from th04_demo_video import BLOCK_SIZE, OFFSETS
from th04_ordinary_continue import attest_continue, validate_release_resume


def sha(data):
    return hashlib.sha256(data).hexdigest()


def calls_to(main, segment, target, start=0, size=65536):
    base = int.from_bytes(main[8:10], "little") * 16 + segment * 16
    code = main[base : base + 65536]
    return [
        off + 3
        for off in range(start, min(start + size, len(code)) - 2)
        if code[off] == 0xE8
        and (off + 3 + struct.unpack_from("<h", code, off + 1)[0]) & 65535 == target
    ]


def own_entries(main, original, profile):
    if profile["map_path"] is None:
        require(main == original, "wait original artifact identity")
        segment, run, animate, player = 0x0AAF, 0x2A7C, 0x2BFB, 0x5FCF
    else:
        symbols = map_symbols(Path(profile["map_path"]))
        segment, run = symbols["dialog_run()"]
        require(
            symbols["dialog_animate()"][0] == symbols["player_update()"][0] == segment,
            "wait own MAP near code owners",
        )
        animate, player = symbols["dialog_animate()"][1], symbols["player_update()"][1]
    menu = attest_continue(
        main,
        original,
        None if profile["map_path"] is None else Path(profile["map_path"]),
        profile,
    )
    require(menu["segment"] == segment, "wait own near Continue segment")
    dialog_return = calls_to(main, segment, run, animate, 150)
    continue_return = calls_to(main, segment, menu["offset"])
    require(
        len(dialog_return) == len(continue_return) == 1,
        "wait own unique near call sites",
    )
    return {
        name: dict(segment=segment, offset=offset)
        for name, offset in dict(
            dialog_run=run,
            dialog_return=dialog_return[0],
            player_update=player,
            continue_menu=menu["offset"],
            continue_return=continue_return[0],
        ).items()
    }


def attest_waits(capture, main, original, profile, load_segment, raw_rows):
    """Validate extra records without changing or weakening the first-stage receipt."""
    data = (capture / "stage2-waits.json").read_bytes()
    summary = json.loads((capture / "stage-boundary-summary.json").read_text())
    require(summary["stage2_waits_sha256"] == sha(data), "wait summary identity")
    doc = json.loads(data)
    declared = profile["stage2_waits"]
    require(doc["complete"] and doc["profile"] == declared, "wait executed profile")
    entries = own_entries(main, original, profile)
    require(set(declared["entries"]) == set(entries), "wait exact own entry set")
    header = int.from_bytes(main[8:10], "little") * 16
    for name, point in entries.items():
        actual = declared["entries"][name]
        start = header + point["segment"] * 16 + point["offset"]
        require(
            all(actual[k] == v for k, v in point.items())
            and bytes.fromhex(actual["opcode"]) == main[start : start + 16],
            "wait own MZ/MAP code entry",
        )
    cues = declared["cues"]
    require(
        cues
        and [v["frame"] for v in cues] == sorted(set(v["frame"] for v in cues))
        and all(
            type(v["frame"]) is int
            and 0 < v["frame"] < profile["stage2_updates"]
            and v["kind"] in ["dialogue", "continue"]
            for v in cues
        ),
        "wait ordered cue extent/kind",
    )
    prefix_bytes = (capture / "clock-input.json").read_bytes()
    prefix = json.loads(prefix_bytes)
    require(
        doc["prefix_clock_sha256"] == sha(prefix_bytes)
        and doc["prefix_action_count"] == len(prefix["actions"])
        and doc["prefix_wait_count"] == len(prefix["waits"]),
        "wait immutable prefix keyboard owner",
    )
    keyboard = dict(actions=prefix["actions"] + doc["actions"])
    previous_tick = keyboard["actions"][len(prefix["actions"]) - 1]["tick"]
    for action in doc["actions"]:
        guard = action["unchanged_guest"]
        require(
            action["key"] in ["KBD_z", "KBD_enter"]
            and type(action["pressed"]) is bool
            and previous_tick <= action["tick"]
            and action["due"] <= action["tick"]
            and action["resident_seed"] == 64
            and re.fullmatch("[0-9a-f]{64}", guard["conventional_sha256"]) is not None
            and len(bytes.fromhex(guard["cpu_regs"])) == 48
            and len(bytes.fromhex(guard["segments"])) == 136,
            "wait real keyboard action/read-only context",
        )
        previous_tick = action["tick"]
    require(len(doc["waits"]) == len(cues), "wait actual keyboard cue count")
    previous_end = len(prefix["actions"])
    for cue, wait in zip(cues, doc["waits"], strict=True):
        previous_end = validate_release_resume(
            keyboard, wait, cue["kind"], cue["frame"], previous_end
        )
    require(
        previous_end == len(keyboard["actions"]) and not doc["remaining"],
        "wait complete key release/resume extent",
    )
    require(
        doc["auxiliary_registered_watchpoints"] == len(entries)
        and summary["baseline_registered_breakpoints"] == len(entries) + 3
        and len(doc["rows"]) == 3 * len(cues),
        "wait bounded auxiliary registry/record extent",
    )
    module = relocated_module(main, load_segment)
    observations = []
    owners = {}
    for ci, cue in enumerate(cues):
        frame = cue["frame"]
        labels = (
            ["player_update", "continue_menu", "continue_return"]
            if cue["kind"] == "continue"
            else ["dialog_run", "dialog_return", "player_update"]
        )
        prior_counts = (
            raw_rows[(1, frame)]["lcg_calls"],
            raw_rows[(1, frame)]["ring_calls"],
        )
        limit = (
            raw_rows[(1, frame + 1)]["lcg_calls"],
            raw_rows[(1, frame + 1)]["ring_calls"],
        )
        for index, label in enumerate(labels):
            row = doc["rows"][3 * ci + index]
            require(
                (
                    row["ordinal"],
                    row["cue_index"],
                    row["cue_kind"],
                    row["cue_ordinal"],
                    row["label"],
                    row["frame"],
                    row["stage"],
                )
                == (3 * ci + index, ci, cue["kind"], index, label, frame, 1),
                "wait actual call/return/player order",
            )
            blobs = {}
            for kind, size in [
                ("memory", 655360),
                ("dgroup", 65536),
                ("video", BLOCK_SIZE),
            ]:
                blob = gzip.decompress(
                    (capture / "stage2-waits" / row[kind]).read_bytes()
                )
                require(
                    len(blob) == size and sha(blob) == row[kind + "_sha256"],
                    "wait complete raw blob identity",
                )
                blobs[kind] = blob
            memory, group = blobs["memory"], blobs["dgroup"]
            require(
                blobs["video"][OFFSETS["stage"]] == 1
                and summary["baseline_registered_breakpoints"]
                <= row["registered_breakpoints"]
                <= summary["maximum_registered_breakpoints"],
                "wait video stage/bounded debugger registry",
            )
            regs, segs = bytes.fromhex(row["cpu_regs"]), bytes.fromhex(row["segments"])
            require(
                len(regs) == 48 and len(segs) == 136 and row["unchanged_context"],
                "wait CPU extent/read-only assertion",
            )
            cs, ds, ss = (
                int.from_bytes(segs[a : a + 8], "little") for a in [8, 24, 16]
            )
            ip = int.from_bytes(regs[32:36], "little") & 65535
            sp = int.from_bytes(regs[16:20], "little") & 65535
            point = entries[label]
            require(
                (cs, ip, ds, ss, sp)
                == (row["cs"], row["ip"], row["dgroup_segment"], row["ss"], row["sp"])
                and cs == load_segment + point["segment"]
                and ip == point["offset"]
                and ds == load_segment + profile["dgroup"]
                and row["load_segment"] == load_segment,
                "wait own actual CPU/CS/DS/stack",
            )
            start = point["segment"] * 16 + point["offset"]
            require(
                bytes.fromhex(row["opcode"]) == module[start : start + 16]
                and memory[cs * 16 + ip : cs * 16 + ip + 16]
                == module[start : start + 16]
                and memory[ds * 16 : ds * 16 + 65536] == group
                and memory[ss * 16 + sp : ss * 16 + sp + 64].hex() == row["stack"],
                "wait full-memory own code/group/stack readback",
            )
            require(
                all(
                    group[at : at + size].hex() == row["fields"][name]
                    for name, at, size in profile["fields"]
                ),
                "wait all raw profile fields",
            )
            require(
                int.from_bytes(bytes.fromhex(row["fields"]["frame"]), "little") == frame
                and row["fields"]["stage"] == "01",
                "wait observed stage/frame fields",
            )
            if label in ["dialog_run", "continue_menu"]:
                target = entries[
                    "dialog_return" if label == "dialog_run" else "continue_return"
                ]
                require(
                    int.from_bytes(bytes.fromhex(row["stack"])[:2], "little")
                    == target["offset"],
                    "wait actual near caller return",
                )
            counts = row["lcg_calls"], row["ring_calls"]
            require(
                all(
                    a <= b <= c
                    for a, b, c in zip(prior_counts, counts, limit, strict=True)
                ),
                "wait independent ordered RNG bounds",
            )
            prior_counts = counts
            if label == "player_update":
                owners[str(frame + 1)] = row["fields"]["input"]
            observations.append(
                {
                    k: row[k]
                    for k in [
                        "ordinal",
                        "cue_kind",
                        "label",
                        "frame",
                        "cs",
                        "ip",
                        "dgroup_segment",
                        "memory_sha256",
                        "lcg_calls",
                        "ring_calls",
                    ]
                }
            )
    require(len(owners) == len(cues), "wait unique actual player input owners")
    return dict(
        passed=True,
        capture_sha256=sha(data),
        cues=cues,
        auxiliary_watchpoints=len(entries),
        records=len(observations),
        player_inputs=owners,
        observations=observations,
        scope=__doc__,
    )
