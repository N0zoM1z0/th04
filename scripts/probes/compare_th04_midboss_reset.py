#!/usr/bin/env python3
"""Require an observed Stage2 Midboss defeat and callback reset on a bounded route.

This consumes the complete stage-boundary attestation and native comparison.
Callback addresses retain each executable's own segment and relocation identity.
It accepts neither native pictures nor physical timing nor historical exactness.
"""

import argparse
import gzip
import hashlib
import json
import struct
from pathlib import Path

from attest_th04_stage_boundary import attest, records, require
from capture_th04_dos_demos import map_symbols


def sha(data):
    return hashlib.sha256(data).hexdigest()


def word(data, offset):
    return struct.unpack_from("<H", data, offset)[0]


def reset_layout(main, role, symbols, dgroup):
    """Decode the independently observed reset stores, including their relocation."""
    require(main[:2] == b"MZ", "Midboss own MZ")
    if role == "original":
        require(
            sha(main)
            == "077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b",
            "Midboss pinned original",
        )
        reset = (0x13A9, 0x642C)
        body, active = 0x53B4, 0x46B2
        callbacks = dict(invalidate=0x46B4, render=0x46BA, update=0x46B6)
    else:
        require(role == "candidate", "Midboss role")
        reset = symbols["midboss_reset()"]
        for name in ["_midboss", "_midboss_active"] + [
            "_midboss_" + x for x in ["invalidate", "render", "update"]
        ]:
            require(symbols[name][0] == dgroup, "Midboss own MAP DGROUP")
        body, active = symbols["_midboss"][1], symbols["_midboss_active"][1]
        callbacks = {
            name: symbols["_midboss_" + name][1]
            for name in ["invalidate", "render", "update"]
        }
    header = word(main, 8) * 16
    start = header + reset[0] * 16 + reset[1]
    code = main[start : start + 40]
    require(len(code) == 40 and code[:3] == b"\x55\x8b\xec", "Midboss reset entry")
    expected_sites = [
        callbacks["invalidate"],
        callbacks["render"],
        callbacks["update"] + 2,
        callbacks["update"],
    ]
    values = []
    for at, site in zip([3, 9, 15, 21], expected_sites, strict=True):
        require(
            code[at : at + 2] == b"\xc7\x06" and word(code, at + 2) == site,
            "Midboss reset callback store",
        )
        values.append(word(code, at + 4))
    require(
        values[0] == values[1]
        and code[27:29] == b"\xc6\x06"
        and word(code, 29) == active
        and code[31] == 0
        and code[32:34] == b"\xc7\x06"
        and word(code, 34) == body + 14
        and code[36:] == b"\x00\x00\x5d\xcb",
        "Midboss reset active/HP stores and return",
    )
    relocs = [
        struct.unpack_from("<HH", main, word(main, 24) + i * 4)
        for i in range(word(main, 6))
    ]
    inside = [
        (off, seg)
        for off, seg in relocs
        if start - header <= seg * 16 + off < start - header + 40
    ]
    require(inside == [(reset[1] + 19, reset[0])], "Midboss reset far relocation")
    near, far, segment = values[0], values[3], values[2]
    require(
        main[header + segment * 16 + near :][:1] == b"\xc3"
        and main[header + segment * 16 + far :][:1] == b"\xcb",
        "Midboss own near/far null return opcodes",
    )
    if role == "candidate":
        require(
            symbols["NULLFUNC_NEAR"] == (segment, near)
            and symbols["NULLFUNC_FAR"] == (segment, far),
            "Midboss own MAP null callbacks",
        )
    return dict(
        artifact_sha256=sha(main),
        reset_segment=reset[0],
        reset_offset=reset[1],
        reset_file_offset=start,
        reset_bytes=code.hex(),
        relocation_offset=reset[1] + 19,
        body=body,
        active=active,
        callbacks=callbacks,
        null_segment=segment,
        null_near=near,
        null_far=far,
    )


def decode(group, layout, load_segment):
    body = group[layout["body"] : layout["body"] + 22]
    active = group[layout["active"]]
    require(active in [0, 1], "Midboss boolean active")
    expected = dict(
        invalidate=struct.pack("<H", layout["null_near"]),
        render=struct.pack("<H", layout["null_near"]),
        update=struct.pack(
            "<HH", layout["null_far"], load_segment + layout["null_segment"]
        ),
    )
    callbacks = {
        name: group[off : off + len(expected[name])]
        for name, off in layout["callbacks"].items()
    }
    require(
        all(
            (value == expected[name]) == (not active)
            for name, value in callbacks.items()
        ),
        "Midboss active versus own relocated null callbacks",
    )
    return dict(
        active=active,
        hp=int.from_bytes(body[14:16], "little", signed=True),
        phase=body[17],
        phase_frame=int.from_bytes(body[18:20], "little", signed=True),
        raw=body.hex(),
        callbacks={name: value.hex() for name, value in callbacks.items()},
    )


def lifecycle(actors, complete_updates):
    """Derive transitions from observations; a fixed stop is never proof of reset."""
    require(
        list(actors) == list(range(1, complete_updates + 1)),
        "Midboss complete actor extent",
    )
    transitions = []
    previous = None
    for frame, row in actors.items():
        key = row["active"], row["phase"]
        if key != previous:
            transitions.append(
                dict(
                    frame=frame,
                    **{k: row[k] for k in ["active", "phase", "hp", "phase_frame"]},
                )
            )
            previous = key
    require(
        [(v["active"], v["phase"]) for v in transitions]
        == [(0, 255), (1, 0), (1, 1), (1, 2), (1, 3), (0, 3)],
        "Midboss actual activation/attack/defeat/exit/reset sequence",
    )
    _, activated, attack, defeated, exited, reset = transitions
    require(
        activated["hp"] > 0
        and activated["phase_frame"] == 1
        and attack["hp"] > 0
        and attack["phase_frame"] == 0
        and defeated["hp"] <= 0
        and defeated["phase_frame"] == 0
        and exited["hp"] == reset["hp"] == 0
        and exited["phase_frame"] == reset["phase_frame"] == 64
        and reset["frame"] == exited["frame"] + 1
        and complete_updates - reset["frame"] >= 64,
        "Midboss real damage, defeat duration and post-reset tail",
    )
    tail = [actors[f] for f in range(reset["frame"], complete_updates + 1)]
    require(
        all(v["raw"] == tail[0]["raw"] and v["active"] == 0 for v in tail),
        "Midboss stable raw state after reset",
    )
    return dict(
        transitions=transitions,
        activation_frame=activated["frame"],
        defeat_frame=defeated["frame"],
        exit_frame=exited["frame"],
        reset_frame=reset["frame"],
        post_reset_updates=complete_updates - reset["frame"],
    )


def compare(original, candidate, paired_path, native_frontend, native_receipt, updates):
    paired = json.loads(paired_path.read_text())
    require(
        paired["passed"]
        and paired["compared_scalar_records"] == 2 * updates + 3
        and {"midboss", "midboss_active"} <= set(paired["extra_state_fields"])
        and paired["scalar_and_boss_differing_records"] == 0
        and not paired["consumed_input_errors"]
        and not paired["homing_errors"]
        and len(paired["pools"]) == 9
        and all(v["passed"] for v in paired["pools"].values())
        and set(paired["native_input_files"])
        == {"stage-native.jsonl", "stage2-pools.bin"},
        "Midboss complete paired native comparison",
    )
    require(
        sha(native_receipt.read_bytes()) == paired["native_producer_receipt_sha256"]
        and all(
            sha((native_frontend / name).read_bytes()) == digest
            for name, digest in paired["native_input_files"].items()
        ),
        "Midboss actual native producer binding",
    )
    native = [
        json.loads(s)
        for s in (native_frontend / "stage-native.jsonl").read_text().splitlines()
    ]
    require(
        len(native) == 2 * updates + 6
        and [v["ordinal"] for v in native] == list(range(2 * updates + 6)),
        "Midboss complete native extent/order",
    )
    native_by = {
        (v["label"], word(bytes.fromhex(v["fields"]["frame"]), 0)): v for v in native
    }
    require(len(native_by) == len(native), "Midboss unique native observations")
    target = Path(
        json.loads((original / "profile.json").read_text())["main_path"]
    ).read_bytes()
    results = {}
    all_actors = {}
    for role, capture in [("original", original), ("candidate", candidate)]:
        proof, _, _, _ = attest(
            capture, target, stage2_updates=updates, require_bounded_watchpoints=True
        )
        require(
            proof == paired[role + "_attestation"],
            "Midboss independent complete attestation",
        )
        profile = json.loads((capture / "profile.json").read_text())
        main = Path(profile["main_path"]).read_bytes()
        symbols = (
            map_symbols(Path(profile["map_path"])) if role == "candidate" else None
        )
        layout = reset_layout(main, role, symbols, profile["dgroup"])
        actors, memory_rows = {}, {}
        compared = 0
        for meta, group, _ in records(capture):
            if meta["label"] not in ["stage2-actor", "stage2-score"]:
                continue
            row = decode(group, layout, meta["load_segment"])
            observed = native_by[(meta["label"], meta["frame"])]["fields"]
            require(
                row["raw"] == observed["midboss"]
                and row["active"] == int(observed["midboss_active"], 16),
                "Midboss raw NPC/active versus actual native",
            )
            compared += 1
            if meta["label"] == "stage2-actor":
                actors[meta["frame"]] = row
                if meta["memory"]:
                    memory = gzip.decompress(
                        (capture / "stage-boundary" / meta["memory"]).read_bytes()
                    )
                    require(
                        sha(memory) == meta["memory_sha256"],
                        "Midboss full-memory identity",
                    )
                    ds = meta["dgroup_segment"] * 16
                    require(
                        decode(memory[ds : ds + 65536], layout, meta["load_segment"])
                        == row,
                        "Midboss raw full-memory NPC/callback owners",
                    )
                    memory_rows[meta["frame"]] = dict(
                        frame=meta["frame"],
                        memory_sha256=meta["memory_sha256"],
                        load_segment=meta["load_segment"],
                        dgroup_segment=meta["dgroup_segment"],
                        **row,
                    )
        require(compared == 2 * updates, "Midboss actor/score extent")
        events = lifecycle(actors, updates)
        required_frames = {updates}
        for key in ["activation_frame", "defeat_frame", "exit_frame", "reset_frame"]:
            frame = events[key]
            required_frames.update([frame - 1, frame, frame + 1])
        require(
            required_frames <= memory_rows.keys(),
            "Midboss independent adjacent full-memory witnesses",
        )
        results[role] = dict(
            layout=layout,
            lifecycle=events,
            compared_actor_score_records=compared,
            full_memory_witnesses=[memory_rows[f] for f in sorted(required_frames)],
        )
        all_actors[role] = {
            f: {k: v for k, v in row.items() if k != "callbacks"}
            for f, row in actors.items()
        }
    require(
        all_actors["original"] == all_actors["candidate"],
        "Midboss all raw actor states",
    )
    return dict(
        passed=True,
        stage2_updates=updates,
        roles=results,
        paired_comparison_sha256=sha(paired_path.read_bytes()),
        native_producer_receipt_sha256=sha(native_receipt.read_bytes()),
        scope=__doc__,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--paired-comparison", type=Path, required=True)
    p.add_argument("--native-frontend", type=Path, required=True)
    p.add_argument("--native-receipt", type=Path, required=True)
    p.add_argument("--stage2-updates", type=int, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    report = compare(
        a.original,
        a.candidate,
        a.paired_comparison,
        a.native_frontend,
        a.native_receipt,
        a.stage2_updates,
    )
    a.output.write_text(json.dumps(report, indent=2) + "\n")
    print("ACTUAL MIDBOSS RESET PASS", report["roles"]["original"]["lifecycle"])
