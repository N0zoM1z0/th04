#!/usr/bin/env python3
"""Export a private, reproducible address/relocation bundle for one MZ target."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys

from lib.pc98 import digest_bytes, parse_mz
from lib.targets import (
    TargetError,
    find_artifact,
    load_target_manifest,
    read_verified_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "targets.toml"
PRIVATE_ROOT = (ROOT / ".analysis").resolve()


def parse_u16(value: str) -> int:
    parsed = int(value, 0)
    if not 0 <= parsed <= 0xFFFF:
        raise argparse.ArgumentTypeError("value must fit in an unsigned 16-bit word")
    return parsed


def private_output(path: Path) -> Path:
    resolved = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if resolved == PRIVATE_ROOT or PRIVATE_ROOT not in resolved.parents:
        raise TargetError("analysis bundles must remain below the ignored .analysis directory")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_id")
    parser.add_argument(
        "--load-segment",
        type=parse_u16,
        default=0x1000,
        help="hypothetical DOS load-module segment (default: 0x1000)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="output directory below .analysis (default: .analysis/bundles/ID)",
    )
    args = parser.parse_args()

    try:
        manifest = load_target_manifest(MANIFEST)
        artifact = find_artifact(manifest, args.artifact_id)
        if artifact["format"] != "mz":
            raise TargetError("analysis bundles currently require a DOS MZ artifact")
        data = read_verified_artifact(ROOT, artifact)
        output = private_output(
            args.output or Path(".analysis") / "bundles" / args.artifact_id
        )
    except TargetError as error:
        parser.error(str(error))

    image = parse_mz(data)
    relocated = image.relocated_program_image(args.load_segment)
    normalized = image.normalized_program_image()
    output.mkdir(parents=True, exist_ok=True)
    (output / "load-module.bin").write_bytes(image.program_image)
    (output / "load-module.relocation-normalized.bin").write_bytes(normalized)
    relocated_name = f"load-module.relocated-{args.load_segment:04X}.bin"
    (output / relocated_name).write_bytes(relocated)

    rows = [
        "index,table_segment,table_offset,module_linear,file_offset,"
        "stored_word,relocated_word,runtime_segment,runtime_offset"
    ]
    relocation_records: list[dict[str, object]] = []
    for index, relocation in enumerate(image.relocations):
        stored_word = struct.unpack_from("<H", image.program_image, relocation.linear)[0]
        relocated_word = struct.unpack_from("<H", relocated, relocation.linear)[0]
        runtime_segment = (args.load_segment + relocation.segment) & 0xFFFF
        record = {
            "index": index,
            "table_segment": relocation.segment,
            "table_offset": relocation.offset,
            "module_linear": relocation.linear,
            "file_offset": image.header.header_size + relocation.linear,
            "stored_word": stored_word,
            "relocated_word": relocated_word,
            "runtime_segment": runtime_segment,
            "runtime_offset": relocation.offset,
        }
        relocation_records.append(record)
        rows.append(
            f"{index},0x{relocation.segment:04X},0x{relocation.offset:04X},"
            f"0x{relocation.linear:X},0x{record['file_offset']:X},"
            f"0x{stored_word:04X},0x{relocated_word:04X},"
            f"0x{runtime_segment:04X},0x{relocation.offset:04X}"
        )
    (output / "relocations.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    header = image.header
    metadata = {
        "schema_version": 1,
        "artifact": {
            "id": artifact["id"],
            "size": len(data),
            "sha256": digest_bytes(data),
            "canonicality": manifest["source"]["canonicality"],
        },
        "interpretation": {
            "format": "dos-mz",
            "load_segment": args.load_segment,
            "entry": {
                "relative_cs": header.initial_relative_cs,
                "ip": header.initial_ip,
                "runtime_cs": (args.load_segment + header.initial_relative_cs) & 0xFFFF,
            },
            "stack": {
                "relative_ss": header.initial_relative_ss,
                "sp": header.initial_sp,
                "runtime_ss": (args.load_segment + header.initial_relative_ss) & 0xFFFF,
            },
            "header_size": header.header_size,
            "declared_file_size": header.declared_file_size,
            "load_module_size": len(image.program_image),
            "overlay_size": len(image.overlay),
            "relocation_count": len(image.relocations),
        },
        "outputs": {
            "load_module": {
                "path": "load-module.bin",
                "sha256": digest_bytes(image.program_image),
            },
            "relocation_normalized": {
                "path": "load-module.relocation-normalized.bin",
                "sha256": digest_bytes(normalized),
                "diagnostic_only": True,
            },
            "relocated": {
                "path": relocated_name,
                "sha256": digest_bytes(relocated),
            },
            "relocations": {
                "path": "relocations.csv",
                "count": len(relocation_records),
            },
        },
    }
    (output / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"exported {artifact['id']}: {len(image.program_image)} load-module bytes, "
        f"{len(image.relocations)} relocations -> {output.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
