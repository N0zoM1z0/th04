#!/usr/bin/env python3
"""Reduce attested real-PC-98 full-pool IRQ counters; not a natural-route/FPS claim."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import struct

from inspect_th04_handoff_trace import game_file, inspect_products
from th04_bullet_load_trace import FIELDS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    receipt_path = run / "receipt.json"
    receipt = json.loads(receipt_path.read_text())
    image = (run / "execution.hdi").read_bytes()
    products = inspect_products(run, receipt, image)
    data = game_file(image,b"BLOAD   BIN")
    assert len(data) == 192*len(FIELDS)*2
    records = [dict(zip(FIELDS,struct.unpack_from("<14H",data,i*28))) for i in range(192)]
    metrics = [("reseed",2,3),("update",3,4),("render",5,6),
               ("seed_through_work",2,7),("seed_through_delay",2,8)]
    phases = []
    for phase in range(6):
        rows = records[phase*32:(phase+1)*32]
        assert all(row["phase"] == phase and row["rank"] == 3 and row["turbo"] == 1 for row in rows)
        assert all(row["slowdown_factor"] == 1 for row in rows)
        assert {row["active_bullets"] for row in rows} == {0 if phase==0 else 120 if phase==1 else 340 if phase==2 else 440}
        assert {row["pellets_rendered"] for row in rows} == {0 if phase in (0,5) else 120 if phase==1 else 240}
        stats = {}
        for label,start,end in metrics:
            ticks = [(row[FIELDS[end]]-row[FIELDS[start]]) & 65535 for row in rows]
            assert max(ticks) < 100
            stats[label] = dict(total_ticks=sum(ticks),mean_ticks=statistics.mean(ticks),
                                maximum_ticks=max(ticks),zero_tick_samples=ticks.count(0))
        # Frame spacing excludes the per-phase reseed boundary and final file
        # write. It remains a full-frame *instrumented* fixture observation.
        ticks = [(records[i+1]["frame_start_tick"]-records[i]["frame_start_tick"]) & 65535
                 for i in range(phase*32,phase*32+31)]
        stats["frame_spacing"] = dict(total_ticks=sum(ticks),mean_ticks=statistics.mean(ticks),maximum_ticks=max(ticks))
        phases.append(dict(phase=phase,active_bullets=rows[0]["active_bullets"],stats=stats))
    digest = lambda data: hashlib.sha256(data).hexdigest()
    report = dict(observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,
                  runtime_receipt_sha256=digest(receipt_path.read_bytes()),
                  diagnostic_file_sha256=digest(data),products=products,fields=FIELDS,
                  records=records,phases=phases,passed=True,
                  limitations="VSync-sized IRQ-counter quantization, stationary synthetic pool, forced Turbo, reseed/instrumentation cost, one emulator; no Windows FPS or complete Lunatic route acceptance.")
    (run/"bullet-load-summary.json").write_text(json.dumps(report,indent=2)+"\n")
    for row in phases:
        print(f"phase={row['phase']} bullets={row['active_bullets']} "
              f"update_ticks={row['stats']['update']['total_ticks']} "
              f"render_ticks={row['stats']['render']['total_ticks']} "
              f"frame_mean_ticks={row['stats']['frame_spacing']['mean_ticks']:.3f}")
    print("PASS attested six-phase real-PC-98 dense-pool fixture")


if __name__ == "__main__":
    main()
