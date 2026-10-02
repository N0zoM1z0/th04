#!/usr/bin/env python3
"""Check a 64-bit port build against independently verified PI pixel hashes."""

import argparse
from pathlib import Path
import subprocess
import tempfile


EXPECTED = {"CONG10.PI": "232AE649", "CONG14.PI": "EDFA0534"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--hdi", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="th04-port64-") as work:
        for member, expected in EXPECTED.items():
            bmp = Path(work) / (member + ".bmp")
            result = subprocess.run(
                [str(args.exe.resolve()), "--hdi", str(args.hdi.resolve()),
                 "--member", member, "--output", str(bmp)],
                capture_output=True, text=True, check=True,
            )
            assert f"FNV32={expected}" in result.stdout, result.stdout
            data = bmp.read_bytes()
            assert data[:2] == b"BM" and len(data) == 768054, member
            print(result.stdout.strip())
    print("port64 smoke: PASS")


if __name__ == "__main__":
    main()
