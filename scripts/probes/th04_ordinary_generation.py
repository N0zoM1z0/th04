"""Preserve and parse actual ordinary MAIN generation IDs without relabeling."""
from collections import Counter

from compare_th04_dos_demos import relocated_module, require


def split_generations(raw):
    """Partition the complete original stream at the actual second L record."""
    pieces = [bytearray(), bytearray()]
    generation = 0
    for line in raw.splitlines(keepends=True):
        cells = line.split()
        require(len(cells) >= 2, 'generation trace shape')
        if cells[0] == b'L':
            generation += 1
        require(generation in (1, 2) and cells[1] == str(generation).encode(),
                'actual generation order/identity')
        pieces[generation - 1].extend(line)
    require(generation == 2 and all(pieces), 'missing actual second generation')
    require(bytes(pieces[0] + pieces[1]) == raw, 'generation byte partition')
    return tuple(bytes(piece) for piece in pieces)


def parse_trace(text, main, expected, generation=1):
    bounded = expected.get('end_after')
    fields = expected['fields']
    names = [field[0] for field in fields]
    rows, resident_rows, events, pending = [], [], [], []
    sample_counts = []
    counts = Counter()
    load_segment = None
    terminal = False
    for line in text.splitlines():
        cells = line.split()
        kind = cells[0]
        require(not terminal, 'events after terminal')
        if kind == 'L':
            require(load_segment is None and len(cells) == 6 and cells[1] == str(generation), 'MAIN process extent')
            load_segment = int(cells[2], 16)
            require(bytes.fromhex(cells[-1]) == relocated_module(main, load_segment), 'loaded module drift')
        elif kind == 'R':
            require(load_segment is not None and len(cells) == 9 and cells[1] == str(generation), 'RNG event shape')
            index = int(cells[2])
            require(2 <= index < len(expected['hooks']), 'RNG hook index')
            hook, segment, offset = expected['hooks'][index]
            require(int(cells[3], 16) == load_segment + segment and int(cells[4], 16) == offset,
                    'RNG hook address')
            counts['lcg' if hook == 3 else 'ring'] += 1
            pending.append([index, int(cells[8], 16) if index in (4, 5, 7, 8) else None])
        elif kind in ('I', 'T'):
            require(load_segment is not None and len(cells) == len(fields) + 8 and cells[1] == str(generation),
                    'frame shape/process')
            _, segment, offset = expected['hooks'][0 if kind == 'I' else 1]
            require([int(x, 16) for x in cells[2:5]] ==
                    [load_segment + segment, offset, load_segment + expected['dgroup']], 'frame address')
            require([int(x) for x in cells[5:7]] == [counts['lcg'], counts['ring']], 'RNG event counters')
            values = {}
            for (name, _, size), value in zip(fields, cells[7:-1]):
                require(len(value) == size * 2 and len(bytes.fromhex(value)) == size, f'field width: {name}')
                values[name] = value
            resident = bytes.fromhex(cells[-1])
            require(len(resident) == 80 and resident[:11] == b'HUMAConfig\0' and resident[0x3e] == 0,
                    'ordinary resident identity')
            frame = int.from_bytes(bytes.fromhex(values['frame']), 'little')
            if kind == 'I':
                require(frame == len(rows), 'noncontiguous ordinary prefix')
                rows.append(values)
                sample_counts.append(dict(counts))
                resident_rows.append(resident.hex())
                events.append(pending)
                pending = []
            else:
                require(bounded is None, 'Demo terminal in bounded ordinary run')
                require(frame == 3996 and len(rows) == 3997 and values == rows[-1] and not pending,
                        'ordinary terminal extent')
                terminal = True
        else:
            raise ValueError('unknown trace event')
    return dict(rows=rows, resident=resident_rows, events=events, pending=pending,
                sample_counts=sample_counts, counts=counts, load_segment=load_segment, terminal=terminal)
