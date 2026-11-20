#!/usr/bin/env python3
"""Screen stable literals that feed an address use within a DOS code block."""

from argparse import ArgumentParser
from collections import defaultdict, deque
import json
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_16, CS_GRP_CALL, CS_GRP_IRET, CS_GRP_JUMP, CS_GRP_RET
from capstone.x86_const import X86_OP_IMM, X86_OP_MEM, X86_OP_REG

from audit_th04_dos_pi import EXES, PRIVATE, map_rows, sha
from lib.pc98 import parse_mz

REGISTER_FAMILIES = {
    register: names.split()[0]
    for names in ("ax eax ah al", "bx ebx bh bl", "cx ecx ch cl", "dx edx dh dl",
                  "si esi", "di edi", "bp ebp", "sp esp")
    for register in names.split()
}
SEGMENTS = {"ds", "es", "ss", "fs", "gs"}
BRANCH_GROUPS = (CS_GRP_CALL, CS_GRP_IRET, CS_GRP_JUMP, CS_GRP_RET)
ARITHMETIC = {"add", "sub", "and", "or", "shl", "shr", "sar", "inc", "dec", "neg",
              "not", "adc", "sbb"}


def stable_register_uses(code: list[bytes], origin: int) -> list[tuple]:
    """Follow literal origins through register operations and adjacent PUSH/POP.

    Clear the local state at control transfers. The results are candidates
    for source review, including possible inline data decoded as instructions.
    """
    decoder = Cs(CS_ARCH_X86, CS_MODE_16)
    decoder.detail = True
    decoder.skipdata = True
    registers = {}
    pushed = ()
    hits = []
    for instruction in decoder.disasm(code[0], origin):
        if not instruction.id:
            registers.clear()
            pushed = ()
            continue

        def family(register):
            name = instruction.reg_name(register)
            return REGISTER_FAMILIES.get(name, name)

        def seeds(register):
            return registers.get(family(register), ())

        operands = instruction.operands
        mnemonic = instruction.mnemonic
        branch = any(instruction.group(group) for group in BRANCH_GROUPS)
        literal = ()
        if (mnemonic in {"mov", "push"} and operands[-1].type == X86_OP_IMM
                and instruction.imm_size):
            begin = instruction.address - origin + instruction.imm_offset
            end = begin + instruction.imm_size
            if all(body[begin:end] == code[0][begin:end] for body in code[1:]):
                literal = ((instruction.address, operands[-1].imm,
                            f"{mnemonic} {instruction.op_str}"),)

        use = set()
        for operand in operands:
            if operand.type == X86_OP_MEM and mnemonic != "lea":
                use.update(seeds(operand.mem.base))
                use.update(seeds(operand.mem.index))
            elif branch and operand.type == X86_OP_REG:
                use.update(seeds(operand.reg))
        if mnemonic == "mov" and operands[0].type == X86_OP_REG:
            if family(operands[0].reg) in SEGMENTS and operands[1].type == X86_OP_REG:
                use.update(seeds(operands[1].reg))
        if mnemonic == "pop" and operands[0].type == X86_OP_REG:
            if family(operands[0].reg) in SEGMENTS:
                use.update(pushed)
        for address, number, producer in sorted(use):
            hits.append((address, number, producer, instruction.address,
                         f"{mnemonic} {instruction.op_str}"))

        result = ()
        if mnemonic == "mov" and operands[0].type == X86_OP_REG:
            result = literal or (seeds(operands[1].reg) if operands[1].type == X86_OP_REG else ())
            if operands[0].size == 1:
                result = tuple(set(result) | set(seeds(operands[0].reg)))
        elif mnemonic == "lea":
            result = tuple(set(seeds(operands[1].mem.base)) | set(seeds(operands[1].mem.index)))
        elif mnemonic in ARITHMETIC and operands[0].type == X86_OP_REG:
            result = seeds(operands[0].reg)
        elif mnemonic == "pop":
            result = pushed

        pushed = ()
        if mnemonic == "push":
            pushed = literal or (seeds(operands[0].reg) if operands[0].type == X86_OP_REG else ())
        for register in instruction.regs_access()[1]:
            registers.pop(family(register), None)
        if result and operands[0].type == X86_OP_REG:
            registers[family(operands[0].reg)] = result
        if branch or mnemonic.startswith("loop") or mnemonic in {"int", "int3"}:
            registers.clear()
            pushed = ()
    return hits


def scan(artifact: str, directories: list[Path]) -> dict:
    maps, images, inputs = [], [], []
    for directory in directories:
        manifest = json.loads((directory / "build.json").read_bytes())
        product = manifest["products"][artifact]
        receipt_path = Path(product["build_receipt"]).resolve()
        if not receipt_path.is_relative_to(PRIVATE):
            raise ValueError("product link receipt is outside .analysis")
        receipt = json.loads(receipt_path.read_bytes())
        if receipt["artifact"] != f"th04-{artifact}":
            raise ValueError(f"{artifact}: product receipt identity drift")
        (map_path,) = (receipt_path.parent / "source").glob(f"obj/**/{artifact}-native.map")
        map_digest = sha(map_path.read_bytes())
        expected_map = receipt.get("link", {}).get("map_sha256")
        if expected_map and map_digest != expected_map:
            raise ValueError(f"{artifact}: linked MAP identity drift")
        data = (directory / EXES[artifact]).read_bytes()
        if sha(data) != product["sha256"] or len(data) != product["size"]:
            raise ValueError(f"{artifact}: linked MZ identity drift")
        parsed = parse_mz(data)
        if not parsed.valid:
            raise ValueError(f"{artifact}: invalid MZ")
        maps.append(map_rows(map_path))
        images.append(parsed.program_image)
        inputs.append({"exe_sha256": sha(data), "map_sha256": map_digest,
                       "build_receipt_sha256": sha(receipt_path.read_bytes())})
    if len({source["exe_sha256"] for source in inputs}) != len(inputs):
        raise ValueError(f"{artifact}: expected distinct baseline and shifted layouts")

    other_owners = []
    for rows in maps[1:]:
        owners = defaultdict(deque)
        for row in rows:
            if row.size:
                owners[row.owner].append(row)
        other_owners.append(owners)

    candidates, scanned = [], 0
    for owner in maps[0]:
        if not owner.size or owner.kind != "CODE":
            continue
        # Product OMF modules have a source extension in the TLINK MAP.
        if not owner.module.lower().endswith((".asm", ".c", ".cpp", ".inc")):
            continue
        corresponding = [owner] + [rows[owner.owner].popleft() for rows in other_owners]
        if any(row.size != owner.size for row in corresponding):
            raise ValueError(f"{artifact}: contribution size changed for {owner.module}")
        bodies = [image[row.start:row.start + row.size]
                  for image, row in zip(images, corresponding, strict=True)]
        scanned += owner.size
        for ip, number, producer, sink_ip, sink in stable_register_uses(bodies, owner.offset):
            candidates.append({"module": owner.module, "frame": f"{owner.frame:04X}", "ip": f"{ip:04X}",
                               "number": number, "producer": producer, "sink_ip": f"{sink_ip:04X}",
                               "sink": sink})
    return {"inputs": inputs, "scanned_code_bytes": scanned, "candidates": candidates}


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--shifted", required=True, nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    inputs = [path.resolve() for path in [args.baseline, *args.shifted]]
    output = args.output.resolve()
    if output.exists() or not all(path.is_relative_to(PRIVATE) for path in [*inputs, output]):
        parser.error("use private inputs and a fresh output below .analysis")
    result = {artifact: scan(artifact, inputs) for artifact in EXES}
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for artifact, details in result.items():
        print(artifact, details["scanned_code_bytes"], "code bytes,", len(details["candidates"]), "uses")


if __name__ == "__main__":
    main()
