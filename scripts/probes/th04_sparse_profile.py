"""Bind sparse observer fields and code seams to the executing MAIN and its MAP."""
from copy import deepcopy
from pathlib import Path

from capture_th04_dos_demos import map_symbols
from compare_th04_dos_ordinary_prefix import ordinary_profile
from th04_stage_waits import calls_to


def require(value, message):
    if not value:
        raise ValueError(message)


def bind_sparse_profile(main, original, declared, map_path=None):
    """Validate declarations before producing an ordinary, non-demo profile."""
    profile = deepcopy(declared)
    expected = ordinary_profile(main, original, map_path)
    for name in ('dgroup', 'module_size', 'signature'):
        require(profile[name] == expected[name], 'sparse own MAIN ' + name)
    require(profile['fields'] == [list(row) for row in expected['fields']],
            'sparse own MAP fields')
    hooks = [list(row) for row in expected['hooks'] if row[0] != 2]
    require([list(row) for row in profile['hooks'] if row[0] != 2] == hooks,
            'sparse own ordinary hooks')
    profile['hooks'] = hooks
    fields = {name: (offset, size) for name, offset, size in profile['fields']}
    require(fields['frame'][1] == 2 and fields['stage'][1] == 1,
            'sparse counter widths')
    header = int.from_bytes(main[8:10], 'little') * 16
    entries = profile['entries']
    for name in ('score', 'init_return', 'actor'):
        point = entries[name]
        at = header + point['segment'] * 16 + point['offset']
        require(main[at:at + 16].hex() == point['opcode'],
                'sparse own MZ entry ' + name)
    guard = profile['stage3_gameover_guard']
    at = header + guard['segment'] * 16 + guard['offset']
    require(main[at:at + 16].hex() == guard['opcode'], 'sparse own GameOver bytes')
    if map_path is None:
        require(main == original, 'sparse original artifact identity')
        require((entries['score']['segment'], entries['score']['offset']) == (0xaaf, 0x207)
                and (entries['init_return']['segment'], entries['init_return']['offset']) == (0xaaf, 0x7e)
                and (guard['segment'], guard['offset']) == (0xaaf, 0x3a51),
                'sparse pinned original seams')
    else:
        symbols = map_symbols(Path(map_path))
        segment, loop = symbols['gameplay_loop()']
        score_segment, score = symbols['score_update_and_render()']
        require(score_segment == segment, 'sparse own near score owner')
        end = min(offset for name, (seg, offset) in symbols.items()
                  if seg == segment and offset > loop and name.endswith(')'))
        score_returns = calls_to(main, segment, score, loop, end - loop)
        loop_returns = calls_to(main, segment, loop)
        require(len(score_returns) == len(loop_returns) == 1,
                'sparse unique own near call sites')
        require((entries['score']['segment'], entries['score']['offset']) == (segment, score_returns[0])
                and (entries['init_return']['segment'], entries['init_return']['offset']) == (segment, loop_returns[0] - 3),
                'sparse own MAP call/return seams')
        require((guard['segment'], guard['offset']) == symbols['gameover_run()'],
                'sparse own MAP GameOver owner')
        frame = fields['frame'][0].to_bytes(2, 'little')
        pattern = b'\xa3' + frame + b'\x25\x0f\x00'
        body = main[header + segment * 16 + loop:header + segment * 16 + end]
        sites = [loop + offset for offset in range(len(body)) if body.startswith(pattern, offset)]
        require(len(sites) == 1 and (entries['actor']['segment'], entries['actor']['offset']) == (segment, sites[0] + 3),
                'sparse own MAP frame-store owner')
    actor = entries['actor']
    store = actor['offset'] - 3
    at = header + actor['segment'] * 16 + store
    opcode = main[at:at + 16]
    require(opcode.startswith(b'\xa3' + fields['frame'][0].to_bytes(2, 'little') + b'\x25\x0f\x00'),
            'sparse frame-store instruction')
    profile['sparse_actor_boundary'] = dict(segment=actor['segment'], offset=store, opcode=opcode.hex())
    return profile
