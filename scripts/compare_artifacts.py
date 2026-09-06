#!/usr/bin/env python3
"""Compare two DOS MZ/COM artifacts and report independent dimensions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from lib.pc98 import compare_blobs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--json", action="store_true", help="emit canonical JSON")
    args = parser.parse_args()

    result = compare_blobs(args.target.read_bytes(), args.candidate.read_bytes())
    result["inputs"] = {
        "target": str(args.target),
        "candidate": str(args.candidate),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"raw exact: {result['verdict']['raw_exact']}")
        print(
            "formats: "
            f"{result['formats']['left']} / {result['formats']['right']}"
        )
        raw = result["raw"]
        print(
            f"raw differences: {raw['differing_bytes']} "
            f"(first: {raw['first_difference']})"
        )
        if "mz" in result:
            mz = result["mz"]
            print(f"header fields exact: {mz['header_fields']['exact']}")
            print(f"relocation order exact: {mz['relocations']['ordered_exact']}")
            print(
                "relocation multiplicity exact: "
                f"{mz['relocations']['multiset_exact']}"
            )
            print(
                "relocation-site values exact: "
                f"{mz['relocations']['site_values']['exact']}"
            )
            print(f"program image exact: {mz['program_image']['exact']}")
            partition = mz["program_difference_partition"]
            print(
                "program differences at/outside relocation bytes: "
                f"{partition['at_relocation_site_bytes']} / "
                f"{partition['outside_relocation_site_bytes']}"
            )
            print(
                "relocation-normalized program exact: "
                f"{mz['relocation_normalized_program']['exact']}"
            )
            print(f"overlay exact: {mz['overlay']['exact']}")
    return 0 if result["verdict"]["raw_exact"] else 1


if __name__ == "__main__":
    sys.exit(main())
