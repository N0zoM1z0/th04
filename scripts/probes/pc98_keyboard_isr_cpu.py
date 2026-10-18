"""Execute a captured BIOS IRQ1 ROM tail under an independent 16-bit CPU."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'.analysis/reconstruction/probes/native-bgm-title-v1450/unicorn-2.1.4'))
import unicorn
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_INSN
from unicorn.x86_const import (
    UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EDX, UC_X86_REG_EBX,
    UC_X86_REG_ESP, UC_X86_REG_EBP, UC_X86_REG_ESI, UC_X86_REG_EDI,
    UC_X86_REG_CS, UC_X86_REG_SS, UC_X86_REG_IP, UC_X86_REG_EFLAGS,
    UC_X86_INS_OUT,
)

REGS = [UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EDX, UC_X86_REG_EBX,
        UC_X86_REG_ESP, UC_X86_REG_EBP, UC_X86_REG_ESI, UC_X86_REG_EDI]


def identity():
    assert unicorn.__version__ == '2.1.4'
    from unicorn.unicorn_py3.unicorn import uclib
    p = Path(uclib._name).resolve()
    digest = hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()
    assert digest == 'ddb196ec82b52e502c18e4a34478bf7b9f61c83c2ebaa95c74d8ded45a95da9c'
    return dict(version=unicorn.__version__, engine=str(p), sha256=digest)


def visible(context):
    raw = bytes.fromhex(context['registers'])
    seg = bytes.fromhex(context['segments'])
    return dict(registers=[int.from_bytes(raw[i:i+4], 'little') for i in range(0, 32, 4)],
                cs=context['cs'], ip=context['ip'],
                ss=int.from_bytes(seg[16:24], 'little'), flags=context['flags'] & 0xffff)


def execute(tail, row, frame=None):
    """Project the recorded V86 state to 16-bit ISA; do not model V86 protection.

    Only the seven-byte sequence after the emulator callback
    enter this CPU. The non-x86 FE38 callback and BIOS C++ body are not stubbed
    into the instruction stream. No guest-PC repair or broad memory-read hook.
    """
    start = visible(row['context'])
    uc = Uc(UC_ARCH_X86, UC_MODE_16)
    uc.mem_map(0, 2*1024*1024)
    address = start['cs']*16+start['ip']
    uc.mem_write(address, tail)
    stack = start['ss']*16+(start['registers'][4] & 65535)
    uc.mem_write(stack, bytes.fromhex(row['stack']) if frame is None else frame)
    for reg, value in zip(REGS, start['registers'], strict=True):
        uc.reg_write(reg, value)
    uc.reg_write(UC_X86_REG_CS, start['cs'])
    uc.reg_write(UC_X86_REG_SS, start['ss'])
    uc.reg_write(UC_X86_REG_EFLAGS, start['flags'])
    instructions, writes = [], []

    def instruction(cpu, pc, size, _):
        instructions.append(dict(address=pc, bytes=bytes(cpu.mem_read(pc, size)).hex()))

    def output(cpu, port, size, value, _):
        writes.append(dict(port=port, size=size, value=value))

    uc.hook_add(UC_HOOK_CODE, instruction)
    uc.hook_add(UC_HOOK_INSN, output, None, 1, 0, UC_X86_INS_OUT)
    uc.emu_start(address, 0, count=5)
    result = dict(registers=[uc.reg_read(reg) for reg in REGS],
                  cs=uc.reg_read(UC_X86_REG_CS), ip=uc.reg_read(UC_X86_REG_IP),
                  ss=uc.reg_read(UC_X86_REG_SS), flags=uc.reg_read(UC_X86_REG_EFLAGS) & 0xffff)
    return dict(state=result, writes=writes, instructions=instructions)


def check(tail, before, after, frame=None):
    result = execute(tail, before, frame)
    assert result['writes'] == [dict(port=0, size=1, value=0x20)], 'EOI port/value/width'
    assert result['state'] == visible(after['context']), 'ROM-tail register/flags/stack return'
    assert len(result['instructions']) == 5, 'ROM-tail instruction extent'
    return result
