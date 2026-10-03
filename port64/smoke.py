#!/usr/bin/env python3
"""Check independent PI hashes and deterministic cross-host UI/MAIN fixtures."""

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
EXPECTED_CHARACTER_BMP_SHA256 = (
    "c1a795a36c2603004fed9309200af833ff8718434b4ba8de2c0977eb2acda199"
)
EXPECTED_SHOT_BMP_SHA256 = (
    "12aa7616f49283462bb7c9dd41c3198fd66865a758da79ad24cf63de817ee438"
)
EXPECTED_HANDOFF_BMP_SHA256 = (
    "0b2c0f8cebb9e1c0e600de3bee29feb8f225efb5b798cb3a387b6c5538bb55c5"
)

EXPECTED_MAIN_BMP_SHA256 = (
    "4cbbe895725e39fc1fb9b5c6271579833ab69c975824e0c91d20275066317f52"
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
        character = Path(work) / "character.bmp"
        shot = Path(work) / "shot.bmp"
        handoff = Path(work) / "handoff.bmp"
        main_scene = Path(work) / "main.bmp"
        result = subprocess.run(
            prefix + [str(args.exe.resolve()), "--hdi", str(args.hdi.resolve()),
                      "--title-screenshot", str(title),
                      "--options-screenshot", str(options),
                      "--character-screenshot", str(character),
                      "--shot-screenshot", str(shot),
                      "--handoff-screenshot", str(handoff),
                      "--main-screenshot", str(main_scene)],
            capture_output=True, text=True, check=True,
        )
        assert "MAIN scene frames=60 player=5232,2960" in result.stdout, result.stdout
        digest = hashlib.sha256(title.read_bytes()).hexdigest()
        assert digest == EXPECTED_TITLE_BMP_SHA256, digest
        print(f"title 640x400 SHA256={digest}")
        options_digest = hashlib.sha256(options.read_bytes()).hexdigest()
        assert options_digest == EXPECTED_OPTIONS_BMP_SHA256, options_digest
        print(f"options 640x400 SHA256={options_digest}")
        character_digest = hashlib.sha256(character.read_bytes()).hexdigest()
        assert character_digest == EXPECTED_CHARACTER_BMP_SHA256, character_digest
        print(f"character selection 640x400 SHA256={character_digest}")
        shot_digest = hashlib.sha256(shot.read_bytes()).hexdigest()
        assert shot_digest == EXPECTED_SHOT_BMP_SHA256, shot_digest
        print(f"shot selection 640x400 SHA256={shot_digest}")
        handoff_digest = hashlib.sha256(handoff.read_bytes()).hexdigest()
        assert handoff_digest == EXPECTED_HANDOFF_BMP_SHA256, handoff_digest
        print(f"MAIN handoff 640x400 SHA256={handoff_digest}")
        main_digest = hashlib.sha256(main_scene.read_bytes()).hexdigest()
        assert main_digest == EXPECTED_MAIN_BMP_SHA256, main_digest
        print(f"MAIN live fixture 640x400 SHA256={main_digest}")
    print("port64 smoke: PASS")


if __name__ == "__main__":
    main()
