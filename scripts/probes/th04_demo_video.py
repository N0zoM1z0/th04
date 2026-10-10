"""Read and decode full PC-98 demo VRAM/palette state without guest accessors."""
from __future__ import annotations

import gzip
from pathlib import Path

from compare_th04_dos_demos import require
from th04_demo_dgroup import HEADER, UPDATE_COUNT, BOUNDARY

MAGIC = b'TH04VD2\n'
LAYOUT = dict(vga_size=535896, vga_mem_linear=535824, vga_mem_size=535840,
              gdc_size=232, param_ram=152, scan_address=170, display_pitch=184,
              active_display_lines=180, active_display_words_per_line=182,
              display_mode=192, video_framing=193, display_enable=202,
              cursor_enable=203, cursor_blink=204, cursor_blink_rate=198,
              doublescan=207, row_height=172, drawing_end=216, drawing_status=228)
MODES = ('pc98_gdc_vramop', 'GDC_display_plane', 'GDC_display_plane_pending',
         'GDC_display_plane_wait_for_vsync', 'pc98_display_enable', 'gdc_analog',
         'pc98_40col_text', 'pc98_256kb_boundary')
SIZES = dict(stage=1, text=16384, graphics=262144, analog=768, digital=8,
             text_palette=32, gdc=464, modes=len(MODES))
OFFSETS = {}
BLOCK_SIZE = 0
for _name, _size in SIZES.items():
    OFFSETS[_name] = BLOCK_SIZE
    BLOCK_SIZE += _size
SYMBOL_SIZES = dict(vga=LAYOUT['vga_size'], pc98_gdc=464, pc98_pal_analog=768,
                    pc98_pal_digital=8, pc98_text_palette=32,
                    pc98_pgraph_current_cpu_page=8, pc98_pgraph_current_display_page=8,
                    **{name: 1 for name in MODES})


class VideoRam:
    def __init__(self, read_memory, symbols):
        self.read_memory, self.symbols = read_memory, symbols

    def read(self, address, size):
        data = bytes(self.read_memory(address, size))
        require(len(data) == size, 'short host video read')
        return data

    def integer(self, address, size):
        return int.from_bytes(self.read(address, size), 'little')

    def capture(self, stage):
        mode = bytes(self.integer(self.symbols[name], 1) for name in MODES)
        require(not mode[0] & 0x20 and mode[1] <= 1 and mode[2] <= 1
                and mode[7] == 0, 'unsupported PC-98 video bank mode')
        vga = self.symbols['vga']
        base = self.integer(vga+LAYOUT['vga_mem_linear'], 8)
        size = self.integer(vga+LAYOUT['vga_mem_size'], 4)
        require(base != 0 and size >= 0x44000, 'PC-98 backing RAM extent')
        cpu = self.integer(self.symbols['pc98_pgraph_current_cpu_page'], 8)
        display = self.integer(self.symbols['pc98_pgraph_current_display_page'], 8)
        require(cpu == base+0x4000+(mode[0] & 1)*0x8000
                and display == base+0x4000+mode[1]*0x8000,
                'PC-98 page pointers disagree with selectors')
        block = (bytes((stage,))+self.read(base, SIZES['text'])
                 +self.read(base+0x4000, SIZES['graphics'])
                 +self.read(self.symbols['pc98_pal_analog'], SIZES['analog'])
                 +self.read(self.symbols['pc98_pal_digital'], SIZES['digital'])
                 +self.read(self.symbols['pc98_text_palette'], SIZES['text_palette'])
                 +self.read(self.symbols['pc98_gdc'], SIZES['gdc'])+mode)
        require(len(block) == BLOCK_SIZE, 'complete video block extent')
        return block, dict(backing_ram=base, backing_bytes=size, cpu_page=cpu, display_page=display)


def regions(block):
    """Exact raw planes/palettes and programmed GDC state, with no pixel mask."""
    require(len(block) == BLOCK_SIZE, 'complete video block extent')
    result = {name: block[OFFSETS[name]:OFFSETS[name]+SIZES[name]]
              for name in ('stage', 'text', 'analog', 'digital', 'text_palette', 'modes')}
    start = OFFSETS['graphics']
    for plane in range(4):
        for page in range(2):
            at = start+plane*65536+page*32768
            result[f'plane{plane}_page{page}'] = block[at:at+32768]
    # Preserve the complete GDC in the stream. Scan/raster/FIFO/drawing clock
    # internals are diagnostic data, not programmed presentation state.
    for index in range(2):
        start = OFFSETS['gdc']+index*LAYOUT['gdc_size']
        for name, size in (('param_ram', 16), ('active_display_lines', 2),
                           ('active_display_words_per_line', 2), ('display_pitch', 2),
                           ('display_mode', 1), ('video_framing', 1), ('display_enable', 1),
                           ('cursor_enable', 1), ('cursor_blink', 1), ('cursor_blink_rate', 1),
                           ('doublescan', 1), ('row_height', 1)):
            at = start+LAYOUT[name]
            result[f'gdc{index}_{name}'] = block[at:at+size]
    return result


def records(path: Path, process, load, dgroup, expected_stage, cr0, cr3):
    previous = 0
    with gzip.open(path, 'rb') as stream:
        require(stream.read(len(MAGIC)) == MAGIC, 'video stream magic')
        for frame in range(1, UPDATE_COUNT+1):
            header = stream.read(HEADER.size)
            require(len(header) == HEADER.size, 'incomplete video header')
            p, f, l, d, c0, c4, c3 = HEADER.unpack(header)
            require((p, f, l, d, c0, c4, c3) == (process, frame, load, dgroup, cr0, 0, cr3),
                    'video process/frame/load/CPU boundary')
            encoded = stream.read(BLOCK_SIZE)
            require(len(encoded) == BLOCK_SIZE, 'incomplete video block')
            previous ^= int.from_bytes(encoded, 'little')
            block = previous.to_bytes(BLOCK_SIZE, 'little')
            require(block[0] == expected_stage, 'video demo stage')
            yield frame, block
        require(stream.read(1) == b'', 'extra video record bytes')
