#!/usr/bin/env python3
"""Replay the bounded DOS stage-epoch comparison and optional native observations.

Raw GDC and post-reset key differences remain explicit failures of the DOS
aggregate. Native consumed inputs are checked against preceding loop samples;
post-reset DOS key_det has separate ownership. Native pictures and physical
clock behavior are outside this comparison.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--dos-root", type=Path, default=root)
p.add_argument("--original", type=Path, required=True)
p.add_argument("--candidate", type=Path, required=True)
p.add_argument("--native-root", type=Path, required=True)
p.add_argument("--native-frontend", type=Path, required=True)
p.add_argument("--native-receipt", type=Path, required=True)
p.add_argument("--output-dir", type=Path, required=True)
p.add_argument("--source-snapshot", type=Path)
p.add_argument("--stage2-updates", type=int, default=600)
p.add_argument("--require-midboss", action="store_true")
args = p.parse_args()
root = args.dos_root.resolve()
r = args.output_dir.resolve()
r.mkdir()
n = args.native_root.resolve()
sys.path.insert(0, str(n / "port64"))
from attest_th04_stage_boundary import attest, records, require
from compare_th04_dos_ordinary_prefix import load
from capture_th04_dos_demos import map_symbols
from compare_th04_demo_dgroup import attest_pools
from th04_demo_globals import attest_fields
from verify_demo_pools import POOLS, read_frame
from compare_th04_demo_video import summarize_pair

sha = lambda b: hashlib.sha256(b).hexdigest()
target = (root / ".analysis/targets/th04/main.exe").read_bytes()
a = args.original.resolve()
b = args.candidate.resolve()
ar, am, raw, events = attest(a, target, args.source_snapshot, args.stage2_updates)
br, bm, braw, bevents = attest(b, target, args.source_snapshot, args.stage2_updates)
assert [(x["label"], x["stage"], x["frame"]) for x in am] == [
    (x["label"], x["stage"], x["frame"]) for x in bm
]
assert events == bevents
scalar_bad = []
for key, row in raw.items():
    changed = {
        name: dict(original=value, candidate=braw[key]["fields"][name])
        for name, value in row["fields"].items()
        if name != "resident_pointer" and value != braw[key]["fields"][name]
    }
    if changed:
        scalar_bad.append(dict(stage=key[0], frame=key[1], fields=changed))
ap = load(a, target, args.source_snapshot)["receipt"]
bp = load(b, target, args.source_snapshot)["receipt"]
symbols = map_symbols(Path(bp["map_path"]))
dgroup = json.loads((b / "profile.json").read_text())["dgroup"]
extents = attest_pools(ap, bp, symbols, dgroup)
states, witnesses = attest_fields(
    target, Path(bp["main_path"]).read_bytes(), symbols, dgroup
)
extents.extend(states)
rows = {
    name: dict(
        differing_records=0,
        first_difference=None,
        original=hashlib.sha256(),
        candidate=hashlib.sha256(),
    )
    for name, *_ in extents
}
post_inputs = []
for (ma, ga, va), (mb, gb, vb) in zip(records(a), records(b), strict=True):
    assert ma["ordinal"] == mb["ordinal"] and ma["label"] == mb["label"]
    for name, oa, ob, count, stride in extents:
        x, y = ga[oa : oa + count * stride], gb[ob : ob + count * stride]
        row = rows[name]
        row["original"].update(x)
        row["candidate"].update(y)
        if x != y:
            row["differing_records"] += 1
            if row["first_difference"] is None:
                row["first_difference"] = dict(
                    ordinal=ma["ordinal"],
                    label=ma["label"],
                    stage=ma["stage"],
                    frame=ma["frame"],
                    changes=[
                        dict(
                            offset=i,
                            slot=i // stride,
                            record_offset=i % stride,
                            original=x[i],
                            candidate=y[i],
                        )
                        for i in range(len(x))
                        if x[i] != y[i]
                    ][:24],
                )
    if ma["fields"]["input"] != mb["fields"]["input"]:
        post_inputs.append(
            dict(
                ordinal=ma["ordinal"],
                label=ma["label"],
                frame=ma["frame"],
                stage=ma["stage"],
                original=ma["fields"]["input"],
                candidate=mb["fields"]["input"],
            )
        )
for row in rows.values():
    row.update(
        passed=row["first_difference"] is None,
        original_sha256=row.pop("original").hexdigest(),
        candidate_sha256=row.pop("candidate").hexdigest(),
    )
video = summarize_pair(
    ((m["ordinal"] + 1, v) for m, g, v in records(a)),
    ((m["ordinal"] + 1, v) for m, g, v in records(b)),
    expected_updates=3 * args.stage2_updates + 7,
)
(r / "dos-video.json").write_text(json.dumps(video, indent=2) + "\n")
dos = dict(
    passed=not scalar_bad
    and all(v["passed"] for v in rows.values())
    and not post_inputs
    and video["passed"]
    and video["raw_gdc_differing_frames"] == 0,
    scalar_rng_passed=not scalar_bad and events == bevents,
    scalar_differences=scalar_bad,
    pools_and_states=rows,
    post_reset_input_differences=len(post_inputs),
    post_reset_input_first_differences=post_inputs[:8],
    video_regions_passed=video["passed"],
    raw_gdc_differing_records=video["raw_gdc_differing_frames"],
    scope=f"Same own-file bridge and{args.stage2_updates}Stage2updates;all35 comparable rawprofilefields/orderedRNG,9pools/22states,38configuredvideo regions. Postresetinput/rawGDC differences remain separate;not fullcampaign/timing/exactness.",
)
(r / "dos-comparison.json").write_text(json.dumps(dos, indent=2) + "\n")
print(
    "ACTUAL DOS EPOCH VECTOR",
    dos["scalar_rng_passed"],
    {k: v["differing_records"] for k, v in rows.items() if not v["passed"]},
    video["passed"],
    len(post_inputs),
    flush=True,
)
frontend = args.native_frontend.resolve()
native_receipt = json.loads(args.native_receipt.read_text())
require(
    native_receipt["passed"]
    and native_receipt["original_receipt_sha256"]
    == sha((a / "receipt.json").read_bytes()),
    "native stage producer input identity",
)
exe = Path(native_receipt["command"][0])
require(
    sha(exe.read_bytes()) == native_receipt["program_sha256"],
    "native stage executable identity",
)
native = [
    json.loads(s) for s in (frontend / "stage-native.jsonl").read_text().splitlines()
]
require(
    len(native) == 2 * args.stage2_updates + 6
    and [v["ordinal"] for v in native] == list(range(2 * args.stage2_updates + 6)),
    "native epoch extent/order",
)
expected = [
    ("stage1-actor", 9836),
    ("stage1-score", 9836),
    ("stage1-actor", 9837),
    ("stage1-score", 9837),
    ("stage1-return", 9837),
    ("init_return", 0),
] + [
    (label, frame)
    for frame in range(1, args.stage2_updates + 1)
    for label in ["stage2-actor", "stage2-score"]
]
require(
    [
        (v["label"], int.from_bytes(bytes.fromhex(v["fields"]["frame"]), "little"))
        for v in native
    ]
    == expected,
    "native actual stage/frame sequence",
)
post_reset_inputs = []
consumed_input_errors = []
homing_errors = []
required_native_fields = {
    "frame",
    "stage",
    "input",
    "score_digits",
    "score_delta",
    "score_delta_frame",
    "lcg",
    "ring",
    "ring_cursor",
    "player_pos",
    "power",
    "hit",
    "invincibility",
    "respawn",
    "boss",
    "boss_statebyte",
    "boss_hitbox_radius",
    "boss_phase_timed_out",
    "homing",
}
observed_fields = set(native[0]["fields"])
extra_fields = observed_fields - required_native_fields
raw_extents = {name: (left, count * stride) for name, left, _, count, stride in states}
require(
    required_native_fields <= observed_fields and extra_fields <= raw_extents.keys(),
    "native epoch required/known state fields",
)
require(
    not args.require_midboss or {"midboss", "midboss_active"} <= extra_fields,
    "native epoch required Midboss fields",
)
require(
    all(set(row["fields"]) == observed_fields for row in native),
    "native epoch stable observed field set",
)
# Retain only bounded state slices rather than every64KiB DGROUP record.
group_by_label = {
    (m["label"], m["frame"]): {
        "homing": g[0x4642:0x4646].hex(),
        **{
            name: g[off : off + size].hex()
            for name in extra_fields
            for off, size in [raw_extents[name]]
        },
    }
    for m, g, v in records(a)
}
by = {
    (x["label"], int.from_bytes(bytes.fromhex(x["fields"]["frame"]), "little")): x
    for x in native
}
checks = []
initial_calls = raw[(0, 0)]["lcg_calls"]
metadata = am
for m in metadata:
    label = m["label"]
    frame = m["frame"]
    mapped = (
        "stage1-score"
        if label == "stage1-score"
        else "stage1-return"
        if label == "gameplay_return"
        else "init_return"
        if label == "init_return"
        else label
        if label in ["stage2-actor", "stage2-score"]
        else None
    )
    if mapped is None:
        continue
    nn = by[(mapped, frame)]
    changed = {
        name: dict(original=m["fields"].get(name), native=value)
        for name, value in nn["fields"].items()
        if name != "homing" and name in m["fields"] and m["fields"][name] != value
    }
    # Volatile key_det has different reset ownership from the consumed native input.
    if label in ["stage2-actor", "stage2-score"]:
        if "input" in changed:
            post_reset_inputs.append(dict(label=label, frame=frame, **changed["input"]))
        changed.pop("input", None)
        expected_input = raw[(1, frame - 1)]["fields"]["input"]
        if nn["fields"]["input"] != expected_input:
            consumed_input_errors.append(
                dict(
                    label=label,
                    frame=frame,
                    original=expected_input,
                    native=nn["fields"]["input"],
                )
            )
    group = group_by_label[(label, frame)]
    for name in extra_fields:
        expected_value = group[name]
        if nn["fields"][name] != expected_value:
            changed[name] = dict(original=expected_value, native=nn["fields"][name])
    expected_homing = group["homing"]
    if nn["fields"]["homing"] != expected_homing:
        homing_errors.append(
            dict(
                label=label,
                frame=frame,
                original=expected_homing,
                native=nn["fields"]["homing"],
            )
        )
    resident = bytes.fromhex(m["resident"])
    stats = dict(
        lives=resident[11],
        bombs=resident[13],
        misses=resident[49],
        bombs_used=resident[50],
        lcg_calls=m["lcg_calls"] - initial_calls,
        ring_calls=m["ring_calls"],
    )
    changed.update(
        {
            name: dict(original=value, native=nn[name])
            for name, value in stats.items()
            if nn[name] != value
        }
    )
    if changed:
        checks.append(dict(label=label, frame=frame, fields=changed))
pools = {name: dict(differing_records=0, first_difference=None) for name, *_ in POOLS}
original_pool_rows = (
    (m, g)
    for m, g, v in records(a)
    if m["label"] == "init_return" or m["label"] == "stage2-actor"
)
with (frontend / "stage2-pools.bin").open("rb") as stream:
    assert stream.read(8) == b"TH04OP1\n"
    observed_pool_rows = 0
    for frame, (meta, g) in enumerate(original_pool_rows):
        require(
            meta["frame"] == frame and frame <= args.stage2_updates,
            "native epoch streamed pool order/extent",
        )
        body = read_frame(stream, 0, frame)
        observed_pool_rows += 1
        at = 0
        for name, off, count, stride in POOLS:
            size = count * stride
            x, y = g[off : off + size], body[at : at + size]
            at += size
            if x != y:
                row = pools[name]
                row["differing_records"] += 1
                if row["first_difference"] is None:
                    row["first_difference"] = dict(
                        frame=frame,
                        changes=[
                            dict(
                                offset=i,
                                slot=i // stride,
                                record_offset=i % stride,
                                original=x[i],
                                native=y[i],
                            )
                            for i in range(size)
                            if x[i] != y[i]
                        ][:24],
                    )
    require(
        observed_pool_rows == args.stage2_updates + 1,
        "native epoch complete streamed pools",
    )
    assert stream.read(1) == b""
for row in pools.values():
    row["passed"] = row["first_difference"] is None
report = dict(
    passed=not checks
    and not consumed_input_errors
    and not homing_errors
    and all(v["passed"] for v in pools.values()),
    native_input_files={
        name: sha((frontend / name).read_bytes())
        for name in ["stage-native.jsonl", "stage2-pools.bin"]
    },
    native_producer_receipt_sha256=sha(args.native_receipt.read_bytes()),
    extra_state_fields=sorted(extra_fields),
    original_attestation=ar,
    candidate_attestation=br,
    compared_scalar_records=2 * args.stage2_updates + 3,
    consumed_input_errors=consumed_input_errors,
    homing_errors=homing_errors,
    post_reset_input_differences=len(post_reset_inputs),
    post_reset_input_first_differences=post_reset_inputs[:8],
    scalar_and_boss_differing_records=len(checks),
    first_scalar_differences=checks[:12],
    pools=pools,
    lcg_count_origin=dict(
        original_initial_main=initial_calls,
        native="Existing prefix-relative count begins after first MAIN initialization",
    ),
    scope=f"Recorded native producer versus attested original bridge, Stage2 initialization and{args.stage2_updates} actor/score pairs. LCG calls use the independently observed first-MAIN count origin; ring calls accumulate native per-fill counters. Every consumed input, homing coordinate and inactive pool byte is compared. Volatile post-reset keys remain measured separately. No Stage2 picture, timing, campaign or exact claim.",
)
(r / "native-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    "ACTUAL NATIVE EPOCH VECTOR",
    report["passed"],
    len(checks),
    {k: v["differing_records"] for k, v in pools.items() if not v["passed"]},
    flush=True,
)
