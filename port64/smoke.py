#!/usr/bin/env python3
"""Check a 64-bit port build against independently verified PI pixel hashes."""

import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile


EXPECTED = {"CONG10.PI": "232AE649", "CONG14.PI": "EDFA0534"}
EXPECTED_TITLE_BMP_SHA256 = (
    "b52ea8615865bfc11945fbe23828b7c391d8424c998062a8abfb5d62b4b31d2a"
)
EXPECTED_OPTIONS_BMP_SHA256 = (
    "a064338b0cfb89f7e418a85ab6bc84a7ea5ef835e4ca995b68772e0aef368185"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--hdi", type=Path, required=True)
    parser.add_argument(
        "--runner", help="optional executable runner, for example wine"
    )
    args = parser.parse_args()
    prefix = [args.runner] if args.runner else []
    with tempfile.TemporaryDirectory(prefix="th04-port64-") as work:
        for member, expected in EXPECTED.items():
            bmp = Path(work) / (member + ".bmp")
            result = subprocess.run(
                prefix + [str(args.exe.resolve()), "--hdi", str(args.hdi.resolve()),
                 "--member", member, "--output", str(bmp)],
                capture_output=True, text=True, check=True,
            )
            assert f"FNV32={expected}" in result.stdout, result.stdout
            data = bmp.read_bytes()
            assert data[:2] == b"BM" and len(data) == 768054, member
            print(result.stdout.strip())
        title = Path(work) / "title.bmp"
        options = Path(work) / "options.bmp"
        result = subprocess.run(
            prefix + [str(args.exe.resolve()), "--hdi", str(args.hdi.resolve()),
                      "--title-screenshot", str(title),
                      "--options-screenshot", str(options)],
            capture_output=True, text=True, check=True,
        )
        digest = hashlib.sha256(title.read_bytes()).hexdigest()
        assert digest == EXPECTED_TITLE_BMP_SHA256, digest
        print(f"title 640x400 SHA256={digest}")
        options_digest = hashlib.sha256(options.read_bytes()).hexdigest()
        assert options_digest == EXPECTED_OPTIONS_BMP_SHA256, options_digest
        print(f"options 640x400 SHA256={options_digest}")
    print("port64 smoke: PASS")


if __name__ == "__main__":
    main()
