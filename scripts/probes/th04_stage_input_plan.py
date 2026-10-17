"""Parse physical device intent separately from the expected DOS input latch.

V1: frame, physical six-button mask, reserved zero; latch must equal the mask.
V2: frame, physical mask (six buttons plus Escape), expected unsigned latch.
The expected word is an assertion about an actual read, never a guest write.
"""


def parse_stage_input(raw):
    lines = raw.decode('ascii').splitlines()
    if not lines:
        raise ValueError('empty stage input plan')
    header = lines[0].split()
    if len(header) != 4 or header[0] != 'TH04_STAGE_INPUT' or header[1] not in ('1', '2'):
        raise ValueError('stage input format/version')
    version, stage, extent = map(int, header[1:])
    if stage not in (0, 2) or not 0 < extent <= 65535 or len(lines) != extent + 1:
        raise ValueError('stage input stage/extent')
    physical, expected = [], []
    allowed = 63 if version == 1 else 63 | 4096
    for frame, line in enumerate(lines[1:]):
        cells = list(map(int, line.split()))
        if len(cells) != 3 or cells[0] != frame:
            raise ValueError('stage input frame order')
        buttons, latch = cells[1:]
        if buttons < 0 or buttons & ~allowed:
            raise ValueError('unsupported physical key mask')
        if version == 1:
            if latch != 0:
                raise ValueError('v1 reserved shift must be zero')
            latch = buttons
        elif not 0 <= latch <= 65535:
            raise ValueError('expected latch outside unsigned word')
        physical.append(buttons)
        expected.append(latch)
    return version, stage, extent, tuple(physical), tuple(expected)
