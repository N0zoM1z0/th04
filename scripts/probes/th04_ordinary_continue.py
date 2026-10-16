"""Validate real key-driven Continue cues and target-local reset witnesses."""
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

from capture_th04_dos_demos import map_symbols, sha
from compare_th04_dos_demos import require


def attest_continue(main, original, map_path, profile):
    require(sha(original) == '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b',
            'Continue target identity')
    score = next(offset for name, offset, _ in profile['fields'] if name == 'score_digits')
    power = next(offset for name, offset, _ in profile['fields'] if name == 'power')
    require(original[6144 + 0xe7ca:6144 + 0xe7ce] == bytes.fromhex('fe064943'),
            'Continue original counter instruction')
    if map_path is None:
        segment, offset = 0x0aaf, 0x3b8a
        require(score == 0x4349 and power == 0x4664, 'Continue original data ownership')
    else:
        symbols = map_symbols(map_path)
        segment, offset = symbols['gameover_continue_menu()']
        require(symbols['_score'] == symbols['_continues_used'] == (profile['dgroup'], score),
                'Continue score/counter alias ownership')
    start = int.from_bytes(main[8:10], 'little') * 16 + segment * 16 + offset
    body = main[start:start + 0x164]
    instructions = {bytes(i.bytes): i.address for i in Cs(CS_ARCH_X86, CS_MODE_16).disasm(body, offset)}
    counter = b'\xfe\x06' + score.to_bytes(2, 'little')
    reset_power = b'\xc6\x06' + power.to_bytes(2, 'little') + b'\x01'
    require(len(body) == 0x164 and counter in instructions and reset_power in instructions and
            bytes.fromhex('268a470e2688470d268a470c2688470b') in body,
            'Continue complete counter/power/resident-copy owner')
    return dict(segment=segment, offset=offset, size=len(body), sha256=sha(body),
                counter_offset=score, counter_ip=instructions[counter], counter_opcode=counter.hex())


def validate_release_resume(clock, wait, kind, frame, previous_end=0):
    actions = clock['actions']
    start, end = wait['action_start'], wait['action_end']
    require(wait['kind'] == kind and wait['frame'] == frame and
            wait['resumed_frame'] == frame + 1 and
            previous_end <= start < end <= len(actions), 'Continue wait boundary/actions')
    events = actions[start:end]
    first, last = events[0], events[-1]
    require(first['key'] == 'KBD_z' and first['pressed'] is False and
            first['frame'] == frame and first['tick'] >= wait['tick'] + 100,
            'Continue release-first keyboard event')
    require(any(e['key'] == 'KBD_enter' and e['pressed'] is True and
                e['frame'] == frame and e['tick'] >= first['tick'] + 500 for e in events),
            'Continue ordinary confirmation event')
    require(last['key'] == 'KBD_z' and last['pressed'] is True and
            last['frame'] == frame + 1 and last['tick'] == wait['resumed_tick'] and
            last['resident'] == wait['resident_after'], 'Continue resumed gameplay event')
    return end


def validate_wait_cues(clock, receipt):
    frames = [receipt['dialog_at_frame'], receipt['continue_at_frame']]
    require(0 < frames[0] < frames[1] < receipt['end_after'] - 1, 'Continue cue extent/order')
    kinds = ['dialogue', 'continue']
    postboss = receipt.get('post_boss_dialog_at_frame')
    if postboss is not None:
        require(type(postboss) is int and frames[-1] < postboss < receipt['end_after'] - 1,
                'post-Boss cue extent/order')
        frames.append(postboss)
        kinds.append('dialogue')
    waits, actions = clock['waits'], clock['actions']
    require(len(waits) == len(frames), 'Continue wait count')
    previous_end = 0
    for kind, frame, wait in zip(kinds, frames, waits):
        previous_end = validate_release_resume(clock, wait, kind, frame, previous_end)


def validate_transition(capture):
    frame = capture['receipt']['continue_at_frame']
    before, after = (bytes.fromhex(capture['resident'][i]) for i in (frame, frame + 1))
    left, right = (capture['rows'][i] for i in (frame, frame + 1))
    require(len(before) == len(after) == 80 and before[:11] == after[:11] == b'HUMAConfig\0',
            'Continue resident identity/extent')
    require(before[11] == 1 and after[11] == after[12] == before[12] and
            after[13] == after[14] == before[14], 'Continue natural last-life/credit restoration')
    a, b = bytes.fromhex(left['score_digits']), bytes.fromhex(right['score_digits'])
    require(len(a) == len(b) == 8 and a[0] < 3 and b[0] == a[0] + 1 and b[1:] == bytes(7),
            'Continue score/counter transition')
    require(right['power'] == '01' and left['stage'] == right['stage'] == '00' and
            int.from_bytes(bytes.fromhex(right['frame']), 'little') == frame + 1,
            'Continue power/stage/resumed boundary')
    return dict(frame=frame, resumed_frame=frame + 1, lives_before=before[11], lives_after=after[11],
                bombs_after=after[13], counter_before=a[0], counter_after=b[0],
                score_after=b.hex(), power_after=right['power'], natural_game_exit=False)
