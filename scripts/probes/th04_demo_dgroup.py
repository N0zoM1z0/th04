"""Versioned compressed DGROUP records at the after-actor frame increment."""
from __future__ import annotations

import gzip
import struct

MAGIC_RAW = b'TH04DG1\n'
MAGIC = b'TH04DG2\n'
HEADER = struct.Struct('<HHHHIII')
DGROUP_SIZE = 65536
UPDATE_COUNT = 3996
BOUNDARY = 'stage_frame write, before mod counters and score update'


class FrameSequence:
    """Wait for BSS zeroing, then require every actual frame increment."""
    def __init__(self, initial: int, limit: int = UPDATE_COUNT):
        self.ready = initial == 0
        self.frames = 0
        self.limit = limit

    def observe(self, frame: int) -> bool:
        if not self.ready:
            self.ready = frame == 0
            return False
        if frame == 0 and self.frames == 0:
            return False
        if frame != self.frames+1 or frame > self.limit:
            raise ValueError('unexpected stage_frame write %d after %d' % (frame, self.frames))
        self.frames = frame
        return True


def records(path, process: int, load: int, dgroup: int, fields: list,
            replay: bytes, cr0: int, cr3: int):
    """Reject truncation/order/address/stage errors while yielding every update.

    This seam follows rendering and input_reset_sense(). Consumed replay input
    is checked by the unchanged ordinary before-update observer, whose complete
    raw trace must agree with an independent ordinary run. Keep post-reset input
    and Shift bytes intact; the paired reader compares them at this seam.
    """
    offsets = {name: (offset, size) for name, offset, size in fields}
    if len(replay) != 8000 or not 1 <= process <= 4:
        raise ValueError('stream replay/process contract')
    with gzip.open(path, 'rb') as stream:
        magic = stream.read(len(MAGIC))
        if magic not in (MAGIC, MAGIC_RAW):
            raise ValueError('DGROUP stream magic')
        previous = 0
        for frame in range(1, UPDATE_COUNT+1):
            header = stream.read(HEADER.size)
            if len(header) != HEADER.size:
                raise ValueError('truncated DGROUP header')
            number, observed_frame, load_segment, data_segment, pg0, pg4, pg3 = HEADER.unpack(header)
            if number != process or observed_frame != frame:
                raise ValueError('missing/duplicate/out-of-order DGROUP frame')
            if (load_segment != load or data_segment != dgroup
                    or pg0 != cr0 or pg3 != cr3 or pg4 & 0x20):
                raise ValueError('DGROUP load/CPU address mismatch')
            data = stream.read(DGROUP_SIZE)
            if len(data) != DGROUP_SIZE:
                raise ValueError('truncated DGROUP body')
            if magic == MAGIC:
                previous ^= int.from_bytes(data, 'little')
                data = previous.to_bytes(DGROUP_SIZE, 'little')
            def value(name):
                offset, size = offsets[name]
                if offset < 0 or size <= 0 or offset+size > DGROUP_SIZE:
                    raise ValueError('DGROUP field range')
                return data[offset:offset+size]
            if value('frame') != frame.to_bytes(2, 'little'):
                raise ValueError('DGROUP frame/body mismatch')
            if value('stage') != bytes(((3, 0, 2, 1)[process-1],)):
                raise ValueError('DGROUP stage mismatch')
            yield frame, data
        # This read also verifies the gzip footer/CRC and rejects extra members.
        if stream.read(1):
            raise ValueError('extra DGROUP frame/trailing data')
