#!/usr/bin/env python3
"""Compare actual Stage2 clear and first Stage3 update with explicit timing failures."""
import argparse
import gzip
import hashlib
import itertools
import json
import sys
from pathlib import Path

from attest_th04_stage_clear import attest_clear
from attest_th04_stage_boundary import records, require
from capture_th04_dos_demos import map_symbols
from compare_th04_dos_ordinary_prefix import load
from compare_th04_demo_dgroup import attest_pools
from th04_demo_globals import attest_fields
from compare_th04_demo_video import summarize_pair
from th04_stage_waits import attest_native_waits

root = Path(__file__).resolve().parents[2]


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def compare_dos(a, b, ar, br, am, bm, raw, braw, events, bevents, target, output, stage3_extents=()):
    require([(m["label"], m["stage"], m["frame"]) for m in am] ==
            [(m["label"], m["stage"], m["frame"]) for m in bm], "clear paired complete boundary order")
    require(list(raw) == list(braw), "clear paired actual raw extents")
    ap, bp = [load(c, target)["receipt"] for c in [a, b]]
    symbols = map_symbols(Path(bp["map_path"]))
    profile = json.loads((b / "profile.json").read_text())
    extents = attest_pools(ap, bp, symbols, profile["dgroup"])
    states, _ = attest_fields(target, Path(bp["main_path"]).read_bytes(), symbols, profile["dgroup"])
    extents += states
    owners = {name: dict(differing_records=0, first_difference=None,
                        original=hashlib.sha256(), candidate=hashlib.sha256()) for name, *_ in [*extents, *stage3_extents]}
    raw_errors = []
    for key, left in raw.items():
        changed = {name: dict(original=value, candidate=braw[key]["fields"][name])
                   for name, value in left["fields"].items()
                   if name != "resident_pointer" and value != braw[key]["fields"][name]}
        if changed:
            raw_errors.append(dict(stage=key[0], frame=key[1], fields=changed))
    input_changes, quit_changes = [], []

    def paired():
        for (ma, ga, va), (mb, gb, vb) in zip(records(a), records(b), strict=True):
            for name, oa, ob, count, stride in [*extents, *(stage3_extents if ma["stage"] == 2 else ())]:
                x, y = ga[oa:oa + count * stride], gb[ob:ob + count * stride]
                row = owners[name]
                row["original"].update(x)
                row["candidate"].update(y)
                if x != y:
                    row["differing_records"] += 1
                    if row["first_difference"] is None:
                        row["first_difference"] = dict(ordinal=ma["ordinal"], label=ma["label"], frame=ma["frame"],
                            changes=[dict(offset=i, original=x[i], candidate=y[i]) for i in range(len(x)) if x[i] != y[i]][:24])
            if ma["fields"]["input"] != mb["fields"]["input"]:
                input_changes.append(dict(label=ma["label"], frame=ma["frame"], stage=ma["stage"],
                    original=ma["fields"]["input"], candidate=mb["fields"]["input"]))
            if ma["quit"] != mb["quit"]:
                quit_changes.append(dict(label=ma["label"], frame=ma["frame"], original=ma["quit"], candidate=mb["quit"]))
            yield (ma["ordinal"] + 1, va), (mb["ordinal"] + 1, vb)

    left, right = itertools.tee(paired())
    video = summarize_pair((p[0] for p in left), (p[1] for p in right), expected_updates=len(am))
    for row in owners.values():
        row.update(passed=row["first_difference"] is None,
                   original_sha256=row.pop("original").hexdigest(), candidate_sha256=row.pop("candidate").hexdigest())
    require(ar["stage2_waits"]["cues"] == br["stage2_waits"]["cues"], "clear paired actual wait cues")
    docs = [json.loads((c / "stage2-waits.json").read_text()) for c in [a, b]]
    wait_fields, wait_owners, images = [], [], [[], []]
    for index, (ma, mb) in enumerate(zip(docs[0]["rows"], docs[1]["rows"], strict=True)):
        require((ma["label"], ma["frame"], ma["cue_kind"]) ==
                (mb["label"], mb["frame"], mb["cue_kind"]), "clear paired wait record order")
        changed = {name: dict(original=value, candidate=mb["fields"][name])
                   for name, value in ma["fields"].items()
                   if name != "resident_pointer" and value != mb["fields"][name]}
        if changed:
            wait_fields.append(dict(index=index, label=ma["label"], frame=ma["frame"], fields=changed))
        groups = [gzip.decompress((c / "stage2-waits" / m["dgroup"]).read_bytes())
                  for c, m in zip([a, b], [ma, mb], strict=True)]
        for name, oa, ob, count, stride in extents:
            if groups[0][oa:oa + count * stride] != groups[1][ob:ob + count * stride]:
                wait_owners.append(dict(index=index, label=ma["label"], owner=name))
        for side, (c, m) in enumerate(zip([a, b], [ma, mb], strict=True)):
            images[side].append((index + 1, gzip.decompress((c / "stage2-waits" / m["video"]).read_bytes())))
    wait_video = summarize_pair(iter(images[0]), iter(images[1]), expected_updates=len(docs[0]["rows"]))
    waits = dict(passed=not wait_fields and not wait_owners and wait_video["passed"] and
                 wait_video["raw_gdc_differing_frames"] == 0 and
                 ar["stage2_waits"]["player_inputs"] == br["stage2_waits"]["player_inputs"],
                 scalar_differences=wait_fields, pools_and_states_differences=wait_owners,
                 player_inputs_passed=ar["stage2_waits"]["player_inputs"] == br["stage2_waits"]["player_inputs"],
                 video=wait_video)
    report = dict(passed=not raw_errors and events == bevents and all(v["passed"] for v in owners.values()) and
                  not input_changes and not quit_changes and video["passed"] and
                  video["raw_gdc_differing_frames"] == 0 and waits["passed"],
                  stage2_complete_updates=ar["stage2_complete_updates"], stage3_complete_updates=ar["stage3_complete_updates"],
                  boundary_records=len(am), scalar_rng_passed=not raw_errors and events == bevents,
                  scalar_differences=raw_errors, pools_and_states=owners, quit_differences=quit_changes,
                  post_reset_input_differences=len(input_changes), post_reset_input_first_differences=input_changes[:12],
                  video_regions_passed=video["passed"], raw_gdc_differing_records=video["raw_gdc_differing_frames"],
                  stage2_waits=waits, scope=__doc__ + " Complete actual route; post-reset keys and raw GDC remain failed aggregate fields.")
    for name, data in [("dos-comparison.json", report), ("dos-video.json", video), ("dos-waits.json", waits)]:
        (output / name).write_text(json.dumps(data, indent=2) + "\n")
    return states


def compare_native(capture, ar, metadata, raw, states, native_root, frontend, producer_path, output,
                   stage3_updates=1, stage3_private_offsets=()):
    require(type(stage3_updates) is int and 0 < stage3_updates <= 65535, "clear native configured Stage3 extent")
    extended = stage3_updates != 1 or bool(stage3_private_offsets)
    require(not extended or len(stage3_private_offsets) == 3, "clear native three private Stage3 owners")
    sys.path.insert(0, str(native_root / "port64"))
    from verify_demo_pools import POOLS, read_frame
    receipt = json.loads(producer_path.read_text())
    require(receipt["passed"] and receipt["original_receipt_sha256"] == file_sha(capture / "receipt.json"),
            "clear native original-input receipt")
    require(file_sha(Path(receipt["command"][0])) == receipt["program_sha256"], "clear native actual program identity")
    names = ["stage-native.jsonl", "stage2-pools.bin", "stage2-consumed.txt", "stage2-blocks.txt",
             "stage3-pools.bin", "stage3-consumed.txt", "stage-clear.json"]
    if extended: names.append("stage3-blocks.txt")
    require(set(receipt["diagnostic_files"]) == set(names) and
            all(file_sha(frontend / name) == receipt["diagnostic_files"][name] for name in names),
            "clear native complete output identity")
    updates = ar["stage2_complete_updates"]
    clear = json.loads((frontend / "stage-clear.json").read_text())
    require(clear["complete"] and clear["stage2_complete_updates"] == updates and clear["stage3_complete_updates"] == stage3_updates
            and clear["stage2_update_budget"] == ar["stage2_update_budget"]
            and clear["unused_stage2_inputs"] == ar["stage2_update_budget"] - updates, "clear native independently observed extent")
    native = [json.loads(line) for line in (frontend / "stage-native.jsonl").open()]
    expected = [("stage1-actor", 9836), ("stage1-score", 9836), ("stage1-actor", 9837),
                ("stage1-score", 9837), ("stage1-return", 9837), ("init_return", 0)]
    expected += [(label, frame) for frame in range(1, updates + 1) for label in ["stage2-actor", "stage2-score"]]
    expected += [("stage2-return", updates), ("stage3-init", 0)]
    expected += [(label, frame) for frame in range(1, stage3_updates + 1)
                 for label in ["stage3-actor", "stage3-score"]]
    require([(v["ordinal"], v["label"], int.from_bytes(bytes.fromhex(v["fields"]["frame"]), "little")) for v in native]
            == [(i, label, frame) for i, (label, frame) in enumerate(expected)], "clear native full record order")
    required = {"frame", "stage", "input", "score_digits", "score_delta", "score_delta_frame", "lcg", "ring", "ring_cursor",
                "player_pos", "power", "hit", "invincibility", "respawn", "boss", "boss_statebyte", "boss_hitbox_radius",
                "boss_phase_timed_out", "homing", "midboss", "midboss_active"}
    require(all(set(v["fields"]) == required | ({"midboss3_private"} if extended and v["resource_stage"] == 2 else set())
                for v in native), "clear native complete stable fields")
    raw_extents = {name: (left, count * stride) for name, left, _, count, stride in states}
    require({"midboss", "midboss_active"} <= raw_extents.keys(), "clear native Midboss owners")
    by = {(v["label"], int.from_bytes(bytes.fromhex(v["fields"]["frame"]), "little")): v for v in native}
    consumed = {}
    for stage, file, size in [(1, "stage2-consumed.txt", updates), (2, "stage3-consumed.txt", stage3_updates)]:
        cells = [list(map(int, line.split())) for line in (frontend / file).read_text().splitlines()]
        require(len(cells) == size and all(len(row) == 2 and row[0] == i + 1 and 0 <= row[1] <= 65535
                                        for i, row in enumerate(cells)), "clear actual player input order/extent")
        consumed.update({(stage, f): value.to_bytes(2, "little").hex() for f, value in cells})
    if extended:
        require((frontend / "stage3-blocks.txt").read_bytes() == b"", "clear no undeclared Stage3 wait")
    initial = raw[(0, 0)]["lcg_calls"]
    ui = attest_native_waits(frontend, ar["stage2_waits"], raw, initial)
    checks, input_errors, homing_errors, volatile, counterfactual = [], [], [], [], []
    compared = 0
    pools = {name: dict(differing_records=0, first_difference=None) for name, *_ in POOLS}
    streams = {1: (frontend / "stage2-pools.bin").open("rb"), 2: (frontend / "stage3-pools.bin").open("rb")}
    pool_counts = {1: 0, 2: 0}
    for stream in streams.values(): require(stream.read(8) == b"TH04OP1\n", "clear native pool header")
    try:
        for m, group, video in records(capture):
            label, frame, stage = m["label"], m["frame"], m["stage"]
            mapped = {"gameplay_return": "stage1-return", "stage3-init-return": "stage3-init"}.get(label, label)
            selected = label in ["stage1-score", "gameplay_return", "init_return", "stage2-actor", "stage2-score",
                                 "stage2-return", "stage3-init-return", "stage3-actor", "stage3-score"]
            if selected:
                nn = by[(mapped, frame)]
                changed = {name: dict(original=m["fields"].get(name), native=value) for name, value in nn["fields"].items()
                           if name != "homing" and name in m["fields"] and m["fields"][name] != value}
                post_reset = label in ["stage2-actor", "stage2-score", "stage2-return", "stage3-init-return", "stage3-actor", "stage3-score"]
                if post_reset and "input" in changed:
                    volatile.append(dict(label=label, frame=frame, **changed.pop("input")))
                if label in ["stage2-actor", "stage2-score", "stage3-actor", "stage3-score"]:
                    expected_input = raw[(stage, frame - 1)]["fields"]["input"]
                    owned_input = ar["stage2_waits"]["player_inputs"].get(str(frame), expected_input) if stage == 1 else expected_input
                    if owned_input != expected_input and label.endswith("actor"):
                        counterfactual.append(dict(stage=stage, frame=frame, loop=expected_input, player_entry=owned_input))
                    if consumed[(stage, frame)] != owned_input:
                        input_errors.append(dict(stage=stage, frame=frame, actual=consumed[(stage, frame)], original=owned_input))
                for name in ["midboss", "midboss_active"]:
                    off, size = raw_extents[name]
                    expected_value = group[off:off + size].hex()
                    if nn["fields"][name] != expected_value:
                        changed[name] = dict(original=expected_value, native=nn["fields"][name])
                if extended and stage == 2:
                    private = bytes(group[off] for off in stage3_private_offsets).hex()
                    if nn["fields"]["midboss3_private"] != private:
                        changed["midboss3_private"] = dict(original=private, native=nn["fields"]["midboss3_private"])
                if nn["fields"]["homing"] != group[0x4642:0x4646].hex():
                    homing_errors.append(dict(label=label, frame=frame, original=group[0x4642:0x4646].hex(), native=nn["fields"]["homing"]))
                resident = bytes.fromhex(m["resident"])
                stats = dict(lives=resident[11], bombs=resident[13], misses=resident[49], bombs_used=resident[50],
                             lcg_calls=m["lcg_calls"] - initial, ring_calls=m["ring_calls"],
                             resource_stage=stage, resident_stage=resident[17])
                changed.update({name: dict(original=value, native=nn[name]) for name, value in stats.items() if nn[name] != value})
                if changed: checks.append(dict(label=label, frame=frame, fields=changed))
                compared += 1
            pool_stage = 1 if label in ["init_return", "stage2-actor"] else 2 if label in ["stage3-init-return", "stage3-actor"] else None
            if pool_stage is not None:
                require(frame == pool_counts[pool_stage], "clear native pool frame extent")
                body = read_frame(streams[pool_stage], 0, frame)
                pool_counts[pool_stage] += 1
                at = 0
                for name, off, count, stride in POOLS:
                    size = count * stride
                    x, y = group[off:off + size], body[at:at + size]
                    at += size
                    if x != y:
                        item = pools[name]
                        item["differing_records"] += 1
                        if item["first_difference"] is None:
                            item["first_difference"] = dict(stage=pool_stage, frame=frame,
                                changes=[dict(offset=i, original=x[i], native=y[i]) for i in range(size) if x[i] != y[i]][:24])
        require(pool_counts == {1: updates + 1, 2: stage3_updates + 1} and compared == 2 * updates + 2 * stage3_updates + 5,
                "clear native full scalar/pool extents")
        require(all(stream.read(1) == b"" for stream in streams.values()), "clear native trailing pool bytes")
    finally:
        for stream in streams.values(): stream.close()
    for value in pools.values(): value["passed"] = value["first_difference"] is None
    report = dict(passed=not checks and not input_errors and not homing_errors and all(v["passed"] for v in pools.values()),
                  compared_scalar_records=compared, pool_snapshots=sum(pool_counts.values()), pools=pools,
                  scalar_and_boss_differing_records=len(checks), first_scalar_differences=checks[:16],
                  consumed_input_errors=input_errors[:16], homing_errors=homing_errors[:16],
                  post_reset_input_differences=len(volatile), post_reset_input_first_differences=volatile[:12],
                  loop_input_counterfactual=counterfactual, native_waits=ui, original_attestation=ar,
                  native_input_files={name: file_sha(frontend / name) for name in names},
                  native_producer_receipt_sha256=file_sha(producer_path),
                  scope="Complete actual Stage2 clear/Stage3 first update against actual original DOS. Every declared scalar field, nine complete pools, Midboss, consumed input and continuous RNG is checked. All post-reset volatile keys remain separately measured. Native does not expose the DOS free routine's intermediate ABI state; native entry/exit and completed initialization/update are compared. Native pictures, physical timing, campaigns and exactness remain open.")
    if extended:
        report.update(stage3_complete_updates=stage3_updates, stage3_private_offsets=list(stage3_private_offsets),
                      scope="Complete original DOS two-stage prefix and bounded Stage3 route against actual native consumed inputs, all declared scalars, nine complete pools, three private Midboss3 bytes and continuous RNG. Volatile keys remain separate. Configured no-wait Stage3 only; pictures, physical timing, campaigns and exactness remain open.")
    (output / "native-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["original", "candidate", "native-root", "native-frontend", "native-receipt", "output-dir"]:
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--dos-root", type=Path, default=root)
    p.add_argument("--stage2-budget", type=int, default=11000)
    args = p.parse_args()
    output = args.output_dir.resolve();output.mkdir()
    target = (args.dos_root.resolve() / ".analysis/targets/th04/main.exe").read_bytes()
    ar, am, raw, events = attest_clear(args.original.resolve(), target, stage2_updates=args.stage2_budget, require_bounded_watchpoints=True)
    br, bm, braw, bevents = attest_clear(args.candidate.resolve(), target, stage2_updates=args.stage2_budget, require_bounded_watchpoints=True)
    states = compare_dos(args.original.resolve(), args.candidate.resolve(), ar, br, am, bm, raw, braw, events, bevents, target, output)
    report = compare_native(args.original.resolve(), ar, am, raw, states, args.native_root.resolve(),
                            args.native_frontend.resolve(), args.native_receipt.resolve(), output)
    print("ACTUAL COMPLETE STAGE CLEAR VECTOR", report["passed"], report["compared_scalar_records"], report["pool_snapshots"], flush=True)


if __name__ == "__main__": main()
