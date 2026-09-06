#!/usr/bin/env python3
"""Exercise Oracle dimensions with private TH01-TH05 positive/negative controls."""

from __future__ import annotations

import json
from pathlib import Path
import struct
import sys
import tomllib

from lib.pc98 import compare_blobs, parse_mz


ROOT = Path(__file__).resolve().parents[1]


def check(name: str, condition: bool, details: str) -> dict[str, object]:
    return {"name": name, "passed": bool(condition), "details": details}


def compare(original: bytes, candidate: bytes) -> dict[str, object]:
    return compare_blobs(original, candidate)


def mz_mutation_cases(game: str, original: bytes) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    image = parse_mz(original)

    invalid_size = bytearray(original)
    struct.pack_into("<H", invalid_size, 0x02, 0)
    struct.pack_into("<H", invalid_size, 0x04, 0xFFFF)
    result = compare(original, bytes(invalid_size))
    results.append(
        check(
            f"{game}: invalid declared-size mutation",
            not result["verdict"]["raw_exact"]
            and not result["format_integrity"]["both_valid"]
            and "invalid-mz-structure" in result["routing_hints"],
            "must reject an MZ declared extent beyond the physical file",
        )
    )

    header_mutation = bytearray(original)
    struct.pack_into(
        "<H", header_mutation, 0x0A, image.header.minimum_extra_allocation ^ 1
    )
    result = compare(original, bytes(header_mutation))
    results.append(
        check(
            f"{game}: header mutation",
            not result["verdict"]["raw_exact"]
            and not result["mz"]["header_fields"]["exact"]
            and result["mz"]["program_image"]["exact"]
            and "header-only-difference" in result["routing_hints"],
            "must isolate a header-field mismatch from the program image",
        )
    )

    if len(image.relocations) >= 2:
        order_mutation = bytearray(original)
        table = image.header.relocation_table_offset
        first = order_mutation[table : table + 4]
        second = order_mutation[table + 4 : table + 8]
        order_mutation[table : table + 4] = second
        order_mutation[table + 4 : table + 8] = first
        result = compare(original, bytes(order_mutation))
        results.append(
            check(
                f"{game}: relocation order mutation",
                not result["verdict"]["raw_exact"]
                and not result["mz"]["relocations"]["ordered_exact"]
                and result["mz"]["relocations"]["set_exact"]
                and result["mz"]["program_image"]["exact"],
                "must distinguish ordered relocation bytes from the relocation set",
            )
        )

    valid_relocation = next(
        (
            relocation
            for relocation in image.relocations
            if relocation.linear <= len(image.program_image) - 2
        ),
        None,
    )
    if valid_relocation is not None:
        relocated_word_mutation = bytearray(original)
        relocated_file_offset = image.header.header_size + valid_relocation.linear
        relocated_word_mutation[relocated_file_offset] ^= 0x01
        result = compare(original, bytes(relocated_word_mutation))
        results.append(
            check(
                f"{game}: relocated-word mutation",
                not result["mz"]["program_image"]["exact"]
                and result["mz"]["relocation_normalized_program"]["exact"]
                and result["mz"]["relocations"]["ordered_exact"]
                and not result["mz"]["relocations"]["site_values"]["exact"]
                and "relocated-word-values-only" in result["routing_hints"],
                "must localize a value-only relocation mismatch without accepting it",
            )
        )

        relocation_bytes = {
            byte
            for relocation in image.relocations
            for byte in (relocation.linear, relocation.linear + 1)
        }
        relocated_a = image.relocated_program_image(0x1234)
        relocated_b = image.relocated_program_image(0x2345)
        results.append(
            check(
                f"{game}: load-segment relocation invariant",
                all(
                    relocated_a[index] == relocated_b[index]
                    for index in range(len(image.program_image))
                    if index not in relocation_bytes
                ),
                "varying the hypothetical load segment may change only relocation words",
            )
        )

    relocation_bytes = {
        byte
        for relocation in image.relocations
        for byte in (relocation.linear, relocation.linear + 1)
    }
    program_index = next(
        index
        for index in range(len(image.program_image))
        if index not in relocation_bytes
    )
    program_mutation = bytearray(original)
    program_mutation[image.header.header_size + program_index] ^= 0x01
    result = compare(original, bytes(program_mutation))
    results.append(
        check(
            f"{game}: non-relocation program mutation",
            not result["mz"]["program_image"]["exact"]
            and not result["mz"]["relocation_normalized_program"]["exact"]
            and "non-relocation-program-content-difference"
            in result["routing_hints"],
            "must remain visible after relocation normalization",
        )
    )

    result = compare(original, original + b"\xA5")
    results.append(
        check(
            f"{game}: overlay mutation",
            not result["verdict"]["raw_exact"]
            and result["mz"]["program_image"]["exact"]
            and not result["mz"]["overlay"]["exact"]
            and "overlay-only-difference" in result["routing_hints"],
            "must isolate bytes beyond the MZ-declared image",
        )
    )
    return results


def main() -> int:
    manifest = tomllib.loads(
        (ROOT / "config" / "targets.toml").read_text(encoding="utf-8")
    )
    corpus = list(manifest["artifacts"])
    missing = [
        item["private_path"]
        for item in corpus
        if not (ROOT / item["private_path"]).is_file()
    ]
    if missing:
        print(
            "error: calibration targets are missing; run import_targets.py "
            "with --include-all-games-smoke\n" + "\n".join(missing),
            file=sys.stderr,
        )
        return 1

    results: list[dict[str, object]] = []
    for artifact in corpus:
        data = (ROOT / artifact["private_path"]).read_bytes()
        result = compare(data, data)
        results.append(
            check(
                f"{artifact['id']}: self comparison",
                result["verdict"]["raw_exact"],
                "real target must be raw exact with itself",
            )
        )

    for game in ("th01", "th02", "th03", "th04", "th05"):
        representative = max(
            (
                item
                for item in corpus
                if item["game"] == game and item["format"] == "mz"
            ),
            key=lambda item: len(
                parse_mz((ROOT / item["private_path"]).read_bytes()).relocations
            ),
        )
        results.extend(
            mz_mutation_cases(
                game, (ROOT / representative["private_path"]).read_bytes()
            )
        )

    for com_artifact in (item for item in corpus if item["format"] == "com"):
        com = (ROOT / com_artifact["private_path"]).read_bytes()
        com_mutation = bytearray(com)
        com_mutation[len(com_mutation) // 2] ^= 0x01
        result = compare(com, bytes(com_mutation))
        results.append(
            check(
                f"{com_artifact['id']}: flat COM mutation",
                not result["verdict"]["raw_exact"]
                and not result["com_image"]["exact"],
                "must reject a single changed COM byte",
            )
        )

    output = {
        "schema_version": 1,
        "fixture": "private legally supplied TH01-TH05 executable corpus",
        "passed": all(item["passed"] for item in results),
        "cases": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
