"""Full ordinary PC-98 video blocks at the after-update frame write."""
import gzip

from th04_demo_dgroup import HEADER, UPDATE_COUNT
from th04_demo_video import BLOCK_SIZE

MAGIC = b'TH04OV1\n'


def records(path, load, dgroup, cr0, cr3):
    previous = 0
    with gzip.open(path, 'rb') as stream:
        if stream.read(len(MAGIC)) != MAGIC:
            raise ValueError('ordinary video magic')
        for frame in range(1, UPDATE_COUNT + 1):
            header = stream.read(HEADER.size)
            if len(header) != HEADER.size:
                raise ValueError('truncated ordinary video header')
            if HEADER.unpack(header) != (1, frame, load, dgroup, cr0, 0, cr3):
                raise ValueError('ordinary video frame/load/CPU boundary')
            delta = stream.read(BLOCK_SIZE)
            if len(delta) != BLOCK_SIZE:
                raise ValueError('truncated ordinary video body')
            previous ^= int.from_bytes(delta, 'little')
            block = previous.to_bytes(BLOCK_SIZE, 'little')
            if block[0] != 0:
                raise ValueError('ordinary video stage')
            yield frame, block
        if stream.read(1):
            raise ValueError('extra ordinary video records')
