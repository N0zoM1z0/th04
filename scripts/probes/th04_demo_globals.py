"""Pinned pointer-free DOS demo state owners; never mask callback addresses.

Each original offset has an actual instruction witness in the attested MAIN.
Candidate ownership requires its linked MAP and a corresponding instruction
operand in the bounded code owner. Structure widths follow maintained ABI
declarations; the complete structures, including inactive bytes, are compared.
"""
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

from capture_th04_dos_demos import sha
from compare_th04_dos_demos import require

# name, original DGROUP offset, bytes, target CS:IP, instruction bytes,
# address operand index, structure-member addend, candidate owner, code window.
FIELDS = (
    ('boss', 0x53ca, 24, 0x13a9, 0xa4e6, 'c606d95300', 2, 15, 'boss_reset()', 0, 0x47),
    ('boss_statebyte', 0xbcde, 16, 0x13a9, 0xa6e5, 'a2debc', 1, 0, 'stage2_setup()', 0, 0xd3),
    ('boss_hitbox_radius', 0xbcf0, 4, 0x13a9, 0xa5dc, 'c706f0bc8001', 2, 0, 'stage1_setup()', 0, 0x10b),
    ('boss_phase_timed_out', 0x23ed, 1, 0x13a9, 0xa511, 'c606ed2301', 2, 0, 'boss_reset()', 0, 0x47),
    ('midboss', 0x53b4, 22, 0x13a9, 0xa57a, 'c706b453000c', 2, 0, 'stage1_setup()', 0, 0x10b),
    ('midboss_active', 0x46b2, 1, 0x13a9, 0x6447, 'c606b24600', 2, 0, 'midboss_reset()', 0, 0x28),
    ('midboss4_aim_toggle', 0x185e, 1, 0x13ff, 0x1072, 'fe065e18', 2, 0, 'midboss4_update()', -0x500, 0x850),
    ('player_pos', 0x464e, 12, 0x0aaf, 0x5f77, 'c7064e46000c', 2, 0, 'player_update()', -0x200, 0x300),
    ('player_option_pos_cur', 0x466c, 4, 0x0aaf, 0x60e3, '66a36c46', 2, 0, 'player_update()', 0, 0x200),
    ('player_option_pos_prev', 0x4670, 4, 0x0aaf, 0x60db, '66a37046', 2, 0, 'player_update()', 0, 0x200),
    ('player_option_patnum', 0x4674, 2, 0x0aaf, 0x61a5, 'ff367446', 2, 0, 'player_render()', 0, 0x17e),
    ('player_is_hit', 0x4669, 1, 0x0aaf, 0x5fed, 'c606694600', 2, 0, 'player_update()', 0, 0x200),
    ('player_invincibility_time', 0x4662, 1, 0x0aaf, 0x5fdb, 'fe0e6246', 2, 0, 'player_update()', 0, 0x200),
    ('player_respawn_motion_time', 0x4663, 1, 0x0aaf, 0x6021, '803e634600', 2, 0, 'player_update()', 0, 0x200),
    ('player_input_prev', 0x464c, 2, 0x0aaf, 0x608e, '89364c46', 2, 0, 'player_update()', 0, 0x200),
    ('power', 0x4664, 1, 0x0aaf, 0x5eea, '28066446', 2, 0, 'player_update()', -0x200, 0x300),
    ('shot_level', 0x4665, 1, 0x0aaf, 0x617f, '803e654602', 2, 0, 'player_render()', 0, 0x17e),
    ('shot_time', 0x4666, 1, 0x0aaf, 0x5948, 'c606664600', 2, 0, 'shots_reset()', 0, 0x1a),
    ('miss_time', 0x466a, 1, 0x0aaf, 0x6001, 'c6066a4628', 2, 0, 'player_update()', 0, 0x200),
    ('shot_laser_time', 0x42c8, 2, 0x0aaf, 0x593d, 'c706c8420000', 2, 0, 'shots_reset()', 0, 0x1a),
    ('shot_laser_style', 0x42ca, 1, 0x0aaf, 0x5943, 'c606ca4200', 2, 0, 'shots_reset()', 0, 0x1a),
    ('byte_259A7', 0x4667, 1, 0x0aaf, 0x594d, 'c606674600', 2, 0, 'shots_reset()', 0, 0x1a),
)


def attest_fields(target, candidate, symbols, dgroup):
    require(len(target) == 156258 and sha(target) ==
            '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b',
            'global state requires pinned Japanese MAIN')
    header = int.from_bytes(candidate[8:10], 'little')*16
    decoder = Cs(CS_ARCH_X86, CS_MODE_16)
    decoder.skipdata = True
    extents, witnesses = [], []
    for name, left, size, seg, ip, hex_bytes, operand, addend, owner, lo, hi in FIELDS:
        pattern = bytes.fromhex(hex_bytes)
        require(int.from_bytes(pattern[operand:operand+2], 'little') == left+addend,
                f'{name} original witness operand')
        position = 6144+seg*16+ip
        require(target[position:position+len(pattern)] == pattern, f'{name} original instruction witness')
        data_seg, right = symbols['_'+name]
        require(data_seg == dgroup and 0 <= right <= 65536-size, f'{name} candidate DGROUP extent')
        code_seg, entry = symbols[owner]
        require(0 <= entry+lo < entry+hi <= 65536, f'{name} code owner boundary')
        start, end = header+code_seg*16+entry+lo, header+code_seg*16+entry+hi
        body = candidate[start:end]
        require(len(body) == hi-lo, f'{name} complete candidate owner')
        patched = pattern[:operand]+(right+addend).to_bytes(2, 'little')+pattern[operand+2:]
        at = next((instruction.address-(entry+lo)
                   for instruction in decoder.disasm(body, entry+lo)
                   if instruction.id and bytes(instruction.bytes) == patched), -1)
        require(at >= 0, f'{name} candidate instruction witness')
        extents.append((name, left, right, 1, size))
        witnesses.append(dict(name=name, size=size, original_segment=seg, original_ip=ip,
                              original_instruction=pattern.hex(), candidate_owner=owner,
                              candidate_segment=code_seg, candidate_ip=entry+lo+at,
                              candidate_instruction=patched.hex(), candidate_window_sha256=sha(body)))
    return extents, witnesses
