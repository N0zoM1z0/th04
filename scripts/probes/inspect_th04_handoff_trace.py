#!/usr/bin/env python3
"""Inspect private MAIN cleanup and MAINE initialization checkpoints."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import tomllib

from prepare_th04_maine_diagnostic_hdi import Fat12, u16, u32

ROOT = Path(__file__).resolve().parents[2]
INIT_CALLS = {
    0x21: "mem_assign_dos", 0x22: "pfsetbufsiz", 0x23: "vram_planes_set",
    0x24: "vsync_start", 0x25: "egc_start", 0x26: "graph_400line",
    0x27: "js_start", 0x28: "pfstart", 0x29: "bgm_init",
}


def decode_scores(data: bytes) -> list[dict]:
    """Decode the ten 196-byte sections with the maintained TH04 codec."""
    if len(data) != 1960:
        raise ValueError("invalid GENSOU.SCR length")
    sections = []
    for section in range(10):
        encoded = data[section * 196:(section + 1) * 196]
        plain = bytearray(encoded)
        for i in range(4, 195):
            following = encoded[i + 1]
            feedback = ((following >> 3) | (following << 5)) & 255
            plain[i] = (encoded[0] + (feedback ^ encoded[1]) + encoded[i]) & 255
        plain[195] = (encoded[195] + encoded[0]) & 255
        scores = []
        for place in range(10):
            digits = plain[94 + place * 8:102 + place * 8]
            scores.append(sum((digit - 0xA0) * 10 ** i for i, digit in enumerate(digits))
                          if all(0xA0 <= digit <= 0xA9 for digit in digits) else None)
        sections.append(dict(rank=section % 5, playchar=section // 5,
                             checksum_valid=(int.from_bytes(plain[2:4], "little")
                                             - sum(plain[4:])) & 255 == 0,
                             scores=scores, names_hex=bytes(plain[4:94]).hex(),
                             decoded_sha256=hashlib.sha256(plain[4:]).hexdigest()))
    return sections


def prepared_baseline(run: Path, receipt: dict) -> bytes:
    prepared_receipt = (run.parent / "receipt.json").read_bytes()
    prepared = (run.parent / "diagnostic.hdi").read_bytes()
    if (hashlib.sha256(prepared_receipt).hexdigest() != receipt["prepared_receipt_sha256"]
            or hashlib.sha256(prepared).hexdigest() != receipt["prepared_hdi_sha256"]):
        raise ValueError("prepared baseline identity drift")
    return prepared


def inspect_products(run: Path, receipt: dict, image: bytes) -> dict:
    prepared_baseline(run, receipt)
    prepared = json.loads((run.parent / "receipt.json").read_text())
    products = prepared["products"]
    if not products and prepared["artifact_source"] == "pinned originals":
        targets = tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
        products = {
            target["id"].removeprefix("th04-"):
                dict(file=target["dos_path"].rsplit("/", 1)[-1],
                     size=target["size"], sha256=target["sha256"])
            for target in targets
            if target["id"] in {"th04-main", "th04-op", "th04-maine", "th04-zun"}
        }
    if set(products) != {"main", "op", "maine", "zun"}:
        raise ValueError("a four-product game run is required for product inspection")
    observed = {}
    for artifact, expected in products.items():
        stem, extension = expected["file"].upper().split(".")
        data = game_file(image, (stem.ljust(8) + extension.ljust(3)).encode("ascii"))
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != expected["size"] or digest != expected["sha256"]:
            raise ValueError(f"executed {artifact} identity drift")
        observed[artifact] = dict(size=len(data), sha256=digest)
    return observed


def game_file(image: bytes, short_name: bytes) -> bytes:
    fs = Fat12(bytearray(image))
    folder = fs.find_entry([fs.root], b"GENSO      ")
    directory = [fs.cluster_offset(c) for c in fs.chain(u16(fs.image, folder + 26))]
    entry = fs.find_entry(directory, short_name)
    return fs.file_bytes(u16(fs.image, entry + 26), u32(fs.image, entry + 28))


def inspect_score_save(run: Path, receipt: dict, executed: bytes) -> dict:
    prepared = prepared_baseline(run, receipt)
    before = game_file(prepared, b"GENSOU  SCR")
    after = game_file(executed, b"GENSOU  SCR")
    old, new = decode_scores(before), decode_scores(after)
    if not all(section["checksum_valid"] for section in old):
        raise ValueError("score baseline checksum failed")
    changed = [i for i in range(10) if old[i]["decoded_sha256"] != new[i]["decoded_sha256"]]
    valid = all(section["checksum_valid"] and None not in section["scores"] for section in new)
    return dict(before_sha256=hashlib.sha256(before).hexdigest(),
                after_sha256=hashlib.sha256(after).hexdigest(), sections=new,
                changed_sections=changed, valid=valid, saved=bool(changed) and valid)


def decode_config(data: bytes) -> dict:
    if len(data) != 10:
        raise ValueError("invalid MIKO.CFG length")
    rank, lives, bombs, bgm, se, turbo = data[:6]
    return dict(options_hex=data[:6].hex(), rank=rank, lives=lives, bombs=bombs,
                bgm_mode=bgm, se_mode=se, turbo_mode=turbo,
                resident_segment=int.from_bytes(data[6:8], "little"), debug=data[8],
                checksum_valid=(sum(data[:6]) & 255) == data[9],
                options_valid=(rank <= 3 and 1 <= lives <= 6 and bombs <= 2
                               and bgm <= 2 and se <= 2 and turbo <= 1))


def reduce_config_save(before: bytes, after: bytes) -> dict:
    old, new = decode_config(before), decode_config(after)
    if not old["checksum_valid"]:
        raise ValueError("config baseline checksum failed")
    valid = (new["checksum_valid"] and new["options_valid"]
             and new["resident_segment"] == 0 and new["debug"] == 0)
    changed = before[:6] != after[:6]
    return dict(before=old, after=new, changed_options=changed, valid=valid,
                saved=changed and valid,
                before_sha256=hashlib.sha256(before).hexdigest(),
                after_sha256=hashlib.sha256(after).hexdigest())


def inspect_config_save(run: Path, receipt: dict, executed: bytes) -> dict:
    before = game_file(prepared_baseline(run, receipt), b"MIKO    CFG")
    after = game_file(executed, b"MIKO    CFG")
    return reduce_config_save(before, after)


def reduce_checkpoints(files: dict[str, bytes]) -> dict:
    records = {}
    for name, data in sorted(files.items()):
        marker = int(name[2:4], 16)
        if len(data) != 8:
            raise ValueError(f"invalid checkpoint length: {name}")
        values = struct.unpack("<4H", data)
        if values[0] != marker:
            raise ValueError(f"checkpoint marker disagrees with filename: {name}")
        records[name[:4]] = dict(marker=marker, detail=values[1], psp=values[2],
                                program_paragraphs=values[3])
    completed = [name for marker, name in INIT_CALLS.items() if f"ME{marker:02X}" in records]
    initialized = ("ME02" in records and "ME20" in records
                   and len(completed) == len(INIT_CALLS)
                   and records.get("ME21", {}).get("detail") == 0)
    return {
        "scope": "private call-completion checkpoints; absence does not identify an internal cause",
        "records": records,
        "main_cleanup_completed": all(f"MX{i:02X}" in records for i in range(14)),
        "main_exec_attempted": "MX1E" in records,
        "main_exec_returned": "MX1F" in records,
        "maine_entered": "ME00" in records,
        "maine_init_completed_calls": completed,
        "maine_initialized": initialized,
        "registration_returned": "ME92" in records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--require-maine-initialized", action="store_true")
    parser.add_argument("--inspect-products", action="store_true")
    parser.add_argument("--inspect-score", action="store_true")
    parser.add_argument("--require-score-saved", action="store_true")
    parser.add_argument("--inspect-config", action="store_true")
    parser.add_argument("--require-config-options", metavar="HEX",
                        help="require changed, valid, saved six-byte options matching HEX")
    args = parser.parse_args()
    if args.require_config_options is not None:
        try:
            expected = bytes.fromhex(args.require_config_options)
        except ValueError:
            parser.error("config options must be six hexadecimal bytes")
        if len(expected) != 6:
            parser.error("config options must be six hexadecimal bytes")
        args.require_config_options = expected.hex()
    run = args.run_dir.resolve()
    if not run.is_relative_to(ROOT / ".analysis"):
        parser.error("run directory must be private")
    receipt_data = (run / "receipt.json").read_bytes()
    receipt = json.loads(receipt_data)
    image = (run / "execution.hdi").read_bytes()
    if hashlib.sha256(image).hexdigest() != receipt["executed_hdi_sha256"]:
        raise ValueError("executed image identity drift")
    fs = Fat12(bytearray(image))
    directory = fs.find_entry([fs.root], b"GENSO      ")
    offsets = [fs.cluster_offset(c) for c in fs.chain(u16(fs.image, directory + 26))]
    files = {}
    for start in offsets:
        for entry in range(start, start + fs.cluster_bytes, 32):
            name = bytes(fs.image[entry:entry + 11])
            if name[0] == 0:
                break
            if (name[:2] in (b"MX", b"ME") and name[4:] == b"    BIN"
                    and all(c in b"0123456789ABCDEF" for c in name[2:4])):
                files[name.decode()] = fs.file_bytes(u16(fs.image, entry + 26),
                                                     u32(fs.image, entry + 28))
    result = reduce_checkpoints(files)
    if args.inspect_products:
        result["executed_products"] = inspect_products(run, receipt, image)
    if args.inspect_score or args.require_score_saved:
        result["score_save"] = inspect_score_save(run, receipt, image)
    if args.inspect_config or args.require_config_options is not None:
        result["config_save"] = inspect_config_save(run, receipt, image)
        if args.require_config_options is not None:
            result["config_save"]["expected_options_hex"] = args.require_config_options
            result["config_save"]["matches_expected"] = (
                result["config_save"]["after"]["options_hex"] == args.require_config_options)
    result["run_receipt_sha256"] = hashlib.sha256(receipt_data).hexdigest()
    (run / "handoff-state.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    return int((args.require_maine_initialized and not result["maine_initialized"])
               or (args.require_score_saved and not result["score_save"]["saved"])
               or (args.require_config_options is not None
                   and not (result["config_save"]["saved"]
                            and result["config_save"]["matches_expected"])))


if __name__ == "__main__":
    raise SystemExit(main())
