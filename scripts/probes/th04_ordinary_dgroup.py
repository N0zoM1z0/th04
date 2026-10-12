"""Complete ordinary DGROUP records at the actual after-actor frame write."""
import gzip

from th04_demo_dgroup import DGROUP_SIZE, HEADER, UPDATE_COUNT

MAGIC = b'TH04OG1\n'
BOUNDARY = 'ordinary stage_frame write, before mod counters and score update'


def records(path, load, dgroup, fields, cr0, cr3):
    offsets = {name: (offset, size) for name, offset, size in fields}
    previous = 0
    with gzip.open(path, 'rb') as stream:
        if stream.read(len(MAGIC)) != MAGIC:
            raise ValueError('ordinary DGROUP magic')
        for frame in range(1, UPDATE_COUNT + 1):
            header = stream.read(HEADER.size)
            if len(header) != HEADER.size:
                raise ValueError('truncated ordinary DGROUP header')
            process, observed, module, data_segment, pg0, pg4, pg3 = HEADER.unpack(header)
            if (process != 1 or observed != frame or module != load or data_segment != dgroup
                    or pg0 != cr0 or pg3 != cr3 or pg4 & 0x20):
                raise ValueError('ordinary DGROUP order/load/CPU mismatch')
            delta = stream.read(DGROUP_SIZE)
            if len(delta) != DGROUP_SIZE:
                raise ValueError('truncated ordinary DGROUP body')
            previous ^= int.from_bytes(delta, 'little')
            data = previous.to_bytes(DGROUP_SIZE, 'little')
            for name, expected in [('frame', frame.to_bytes(2, 'little')), ('stage', b'\0')]:
                offset, size = offsets[name]
                if size != len(expected) or data[offset:offset + size] != expected:
                    raise ValueError('ordinary DGROUP field mismatch: ' + name)
            yield frame, data
        if stream.read(1):
            raise ValueError('extra ordinary DGROUP records')
