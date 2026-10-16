"""Read DOS process ownership from conventional RAM without DOS service calls."""
import hashlib


ARTIFACTS = {'OP.EXE': 'th04-op', 'MAIN.EXE': 'th04-main',
             'MAINE.EXE': 'th04-maine', 'ZUN.COM': 'th04-zun'}


def artifact_for_path(raw):
    name = raw.replace(b'/', b'\\').rsplit(b'\\', 1)[-1].upper()
    return ARTIFACTS.get(name.decode('ascii', errors='replace'))


def c_string(memory, address, limit=260):
    if not 0 <= address < len(memory):
        raise ValueError('DOS string outside conventional RAM')
    end = memory.find(b'\0', address, min(len(memory), address + limit))
    if end < 0:
        raise ValueError('unterminated DOS string')
    return memory[address:end]


def process_owner(memory, cs, ip):
    """Require a unique initial PSP-owned MCB covering the actual caller PC."""
    linear = cs * 16 + ip
    if not 0 <= linear < len(memory):
        return None
    rows = []
    for at in range(0x500, linear, 16):
        if memory[at] not in (ord('M'), ord('Z')):
            continue
        header = at // 16
        owner = int.from_bytes(memory[at + 1:at + 3], 'little')
        size = int.from_bytes(memory[at + 3:at + 5], 'little')
        end = (header + 1 + size) * 16
        psp = owner * 16
        if (owner != header + 1 or size < 16 or end > len(memory) or
                not psp <= linear < end or memory[psp:psp + 2] != b'\xcd\x20'):
            continue
        env_segment = int.from_bytes(memory[psp + 0x2c:psp + 0x2e], 'little')
        env = env_segment * 16
        if env < 16 or env + 16 > len(memory) or memory[env - 16] not in (ord('M'), ord('Z')):
            continue
        env_size = int.from_bytes(memory[env - 13:env - 11], 'little') * 16
        if not 0 < env_size <= 32768 or env + env_size > len(memory):
            continue
        block = memory[env:env + env_size]
        tail = block.find(b'\0\0')
        if tail < 0 or int.from_bytes(block[tail + 2:tail + 4], 'little') != 1:
            continue
        try:
            executable = c_string(block, tail + 4)
        except ValueError:
            continue
        rows.append(dict(psp_segment=owner, parent_psp=int.from_bytes(memory[psp + 0x16:psp + 0x18], 'little'),
                         load_segment=owner + 16, mcb_segment=header, mcb_paragraphs=size,
                         mcb_hex=memory[at:at + 16].hex(), psp_hex=memory[psp:psp + 256].hex(),
                         environment_segment=env_segment, environment_sha256=hashlib.sha256(block).hexdigest(),
                         executable_hex=executable.hex(), environment_artifact=artifact_for_path(executable)))
    if len(rows) > 1:
        raise ValueError('ambiguous DOS process MCB/PSP ownership')
    return rows[0] if rows else None
