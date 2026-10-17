#!/usr/bin/env python3
"""Compare an attested continuous Stage3 route, including three private Midboss bytes."""
import argparse
import json
from pathlib import Path

from attest_th04_stage3_route import attest_route
from compare_th04_stage_clear import compare_dos, compare_native

root = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["original", "candidate", "native-root", "native-frontend", "native-receipt", "output-dir"]:
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--stage3-updates", type=int, default=4000)
    p.add_argument("--stage2-budget", type=int, default=11000)
    args = p.parse_args()
    output = args.output_dir.resolve()
    output.mkdir()
    target = (root / ".analysis/targets/th04/main.exe").read_bytes()
    a, b = args.original.resolve(), args.candidate.resolve()
    ar, am, raw, events = attest_route(a, target, args.stage3_updates, args.stage2_budget)
    br, bm, braw, bevents = attest_route(b, target, args.stage3_updates, args.stage2_budget)
    for name, report in [("original", ar), ("candidate", br)]:
        (output / (name + "-attestation.json")).write_text(json.dumps(report, indent=2) + "\n")
    extents = [("midboss3_" + name, left, right, 1, 1) for name, left, right in
               zip(["pattern", "mirror", "patterns_done"], ar["stage3_private_offsets"],
                   br["stage3_private_offsets"], strict=True)]
    states = compare_dos(a, b, ar, br, am, bm, raw, braw, events, bevents, target, output,
                         stage3_extents=extents)
    report = compare_native(a, ar, am, raw, states, args.native_root.resolve(), args.native_frontend.resolve(),
        args.native_receipt.resolve(), output, stage3_updates=args.stage3_updates,
        stage3_private_offsets=ar["stage3_private_offsets"])
    print("ACTUAL CONTINUOUS STAGE3 VECTOR", report["passed"], report["compared_scalar_records"],
          report["pool_snapshots"], flush=True)


if __name__ == "__main__":
    main()
