#!/usr/bin/env python3
"""Locate emulator-side CPU faults in attested, unmodified native MAIN code."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_16

from build_th04_cpu_fault_emulator import ROOT, attest
from inspect_th04_handoff_trace import game_file, prepared_baseline
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz

FIELDS = ("vector", "cs", "ip", "ss", "sp", "ds", "es", "ax", "bx", "cx", "dx",
          "si", "di", "bp", "raw_lazy_flags")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_packets(log: str) -> list[dict]:
    faults = []
    for line in log.splitlines():
        if not line.startswith("TH04_CPUFAULT"):
            continue
        words = line.split()
        if (len(words) != 17 or words[0] != "TH04_CPUFAULT"
                or not words[1].isdigit() or int(words[1]) != len(faults)
                or len(faults) >= 32
                or not re.fullmatch(r"[0-9A-F]{2}", words[2])
                or any(not re.fullmatch(r"[0-9A-F]{4}", w) for w in words[3:16])
                or not re.fullmatch(r"[0-9A-F]{8}", words[16])):
            raise ValueError("malformed or out-of-order emulator CPU fault")
        fault = dict(zip(FIELDS, (int(w, 16) for w in words[2:])))
        if fault["vector"] not in (0, 6):
            raise ValueError("unexpected observed CPU vector")
        faults.append(dict(id=len(faults), **fault))
    return faults


def relocate(image: bytes, load_segment: int) -> bytes:
    if not parse_mz(image).valid:
        raise ValueError("invalid native MZ")
    body = bytearray(image[int.from_bytes(image[8:10], "little") * 16:])
    table = int.from_bytes(image[24:26], "little")
    for index in range(int.from_bytes(image[6:8], "little")):
        entry = image[table + index * 4:table + index * 4 + 4]
        at = int.from_bytes(entry[:2], "little") + 16 * int.from_bytes(entry[2:], "little")
        value = (int.from_bytes(body[at:at + 2], "little") + load_segment) & 0xFFFF
        body[at:at + 2] = value.to_bytes(2, "little")
    return bytes(body)


def locate(fault: dict, code: bytes, image: bytes, map_text: str) -> dict | None:
    matches = []
    for segment, offset, size, module in re.findall(
            r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})"
            r"\s+C=CODE\b[^\n]*\bM=(\S+)", map_text):
        segment, offset, size = (int(v, 16) for v in (segment, offset, size))
        if not offset <= fault["ip"] < offset + size:
            continue
        load = (fault["cs"] - segment) & 0xFFFF
        relative = segment * 16 + fault["ip"]
        if load * 16 + len(image) > 0xA0000:
            continue
        loaded = relocate(image, load)
        if loaded[relative:relative + len(code)] != code:
            continue
        symbols = []
        for s, o, name in re.findall(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([^\n]+)$", map_text):
            o = int(o, 16)
            if int(s, 16) == segment and offset <= o <= fault["ip"] and "C=" not in name:
                symbols.append((o, name.strip()))
        nearest = max(symbols, default=None)
        matches.append(dict(main_load_segment=load, segment=segment,
                            relative_load_address=relative, module=module,
                            code_bytes_matched=len(code),
                            nearest_public=(dict(offset=nearest[0], name=nearest[1]) if nearest else None)))
    if len(matches) > 1:
        raise ValueError("fault code has ambiguous MAIN ownership")
    return matches[0] if matches else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--require-fault", action="store_true")
    args = parser.parse_args()
    run = args.run_dir.resolve()
    if not run.is_relative_to(ROOT / ".analysis/runtime/candidates"):
        parser.error("run must be private")
    runtime = json.loads((run / "receipt.json").read_text())
    if runtime.get("cpu_debugger") is not None:
        from prepare_th04_primary_cpu_debugger import attest_debugger
        override = runtime["cpu_debugger"]
        emulator_path = Path(override["receipt"])
        emulator = attest_debugger(emulator_path)
    else:
        override = runtime["emulator_override"]
        emulator_path = Path(override["receipt"])
        emulator = attest(emulator_path)
    if (sha(emulator_path.read_bytes()) != override["receipt_sha256"]
            or emulator["binary_sha256"] != runtime["emulator_sha256"]):
        raise ValueError("runtime emulator identity drift")
    prepared_baseline(run, runtime)
    prepared = json.loads((run.parent / "receipt.json").read_text())
    image = (run / "execution.hdi").read_bytes()
    if sha(image) != runtime["executed_hdi_sha256"]:
        raise ValueError("executed image identity drift")
    products = {}
    for name, product in prepared["products"].items():
        short_name = product["file"].upper().split(".")
        data = game_file(image, (short_name[0].ljust(8) + short_name[1].ljust(3)).encode("ascii"))
        if len(data) != product["size"] or sha(data) != product["sha256"]:
            raise ValueError(f"executed {name} identity drift")
        products[name] = dict(sha256=sha(data), size=len(data))
        if name == "main":
            main_image = data
    link_path = Path(prepared["products"]["main"]["build_receipt"]).resolve()
    if not link_path.is_relative_to(ROOT / ".analysis/reconstruction/probes"):
        raise ValueError("MAIN link receipt must be private")
    link = json.loads(link_path.read_text())["link"]
    map_data = (link_path.parent / "source" / link["map"]).read_bytes()
    if (link["exit"] or link["mz"]["sha256"] != sha(main_image)
            or sha(map_data) != link["map_sha256"]):
        raise ValueError("MAIN link/MAP identity drift")
    log = (run / "boot.log").read_bytes()
    if sha(log) != runtime["boot_log_sha256"]:
        raise ValueError("runtime log identity drift")
    faults = decode_packets(log.decode("utf-8"))
    decoder = Cs(CS_ARCH_X86, CS_MODE_16)
    for fault in faults:
        snapshots = {}
        for name, size in (("code", 64), ("stack", 64), ("data", 65536)):
            path = run / f'cpu-fault-{fault["id"]:02d}-{name}.bin'
            if not path.exists():
                continue
            data = path.read_bytes()
            if len(data) != size:
                raise ValueError("incomplete CPU snapshot")
            snapshots[name] = dict(file=path.name, sha256=sha(data), size=size)
        fault["snapshots"] = snapshots
        if "code" not in snapshots:
            continue
        code = (run / snapshots["code"]["file"]).read_bytes()
        fault["instructions"] = [dict(offset=i.address, bytes=i.bytes.hex(),
                                      text=f"{i.mnemonic} {i.op_str}")
                                 for i in list(decoder.disasm(code, fault["ip"]))[:6]]
        owner = locate(fault, code, main_image, map_data.decode("ascii"))
        fault["main_owner"] = owner
        if "stack" in snapshots:
            stack = (run / snapshots["stack"]["file"]).read_bytes()
            fault["stack_words"] = [int.from_bytes(stack[i:i+2], "little") for i in range(0, 64, 2)]
        if owner is None or "data" not in snapshots:
            continue
        data = (run / snapshots["data"]["file"]).read_bytes()
        state = {}
        for name, relative, size in (("_stage_id", 0, 1), ("_rank", 0, 1),
                                    ("_stage_frame", 0, 2), ("_boss", 15, 1),
                                    ("_boss", 16, 2), ("_boss_statebyte", 0, 1)):
            locations = set(re.findall(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+"
                                       + re.escape(name) + r"\s*$", map_data.decode("ascii")))
            if len(locations) != 1:
                raise ValueError(f"ambiguous state symbol: {name}")
            segment, offset = (int(v, 16) for v in next(iter(locations)))
            if fault["ds"] != (owner["main_load_segment"] + segment) & 0xFFFF:
                state[name + f"+{relative}"] = dict(ds_matches_owner=False)
                continue
            at = offset + relative
            state[name + f"+{relative}"] = dict(ds_matches_owner=True, offset=at,
                                               value=int.from_bytes(data[at:at+size], "little"))
        fault["main_state"] = state
    report = dict(scope="experimental emulator CPU observations with unchanged products; not normal-game acceptance",
                  runtime_receipt_sha256=sha((run / "receipt.json").read_bytes()),
                  executed_products=products, map_sha256=sha(map_data), faults=faults)
    output = run / "emulator-cpu-fault.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(dict(report=str(output), faults=faults)))
    if args.require_fault and not faults:
        raise ValueError("no guest CPU exception was recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
