#!/usr/bin/env python3
"""Check MAINE graphics pages using original requests and font CPU kernels.

PI decode is an explicit dependency, checked separately against the preceding
native decoder; this is not an original whole-Ending video capture. The raster
model uses the original CPU-produced script stream, observed mask words and
original font-effect writes with a supplied CGROM adapter. No portable Scene
or Script implementation is imported to produce expected pages.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

import numpy as np
from PIL import Image

from verify_cutscene import Original, ending_assets, PAYLOAD_SHA

sha = lambda data: hashlib.sha256(data).hexdigest()


class Raster:
    def __init__(self, original, font, gaiji, pictures, masks):
        self.original = original; self.font = font; self.gaiji = gaiji; self.pictures = pictures
        self.box_masks = masks[1]; self.picture_masks = masks[0]
        self.pages = np.zeros((2, 400, 640), dtype=np.uint8)
        self.palette = bytes(48); self.saved = None; self.loaded = None
        self.shown = 0; self.access = 0; self.scroll = 0; self.tone = 100
        self.glyph_cache = {}

    def mask(self, words, row, width):
        # Independently unpack the little-endian EGC word as two MSB-first
        # bytes, then repeat those sixteen dots across the rectangle.
        bits = np.unpackbits(np.frombuffer(struct.pack('<H', words[row % 4]), dtype=np.uint8))
        return np.tile(bits.astype(bool), width//16)

    def rom(self, cell, column, selector):
        # CGROM addresses are supplied by original OUT instructions, not
        # re-created from the portable Shift-JIS conversion. The Anex86 BMP
        # has 256 ANK glyphs in its first sixteen rows, then JIS rows/cells.
        if column in (9,10):
            character = cell + (128 if column == 10 else 0)
            left, top = character*8, selector & 15
        else:
            left = column*16 + (0 if selector & 0x20 else 8)
            top = cell*16 + (selector & 15)
        return sum(int(self.font.getpixel((left+x,top)) == 0) << (7-x) for x in range(8))

    def glyph(self, x, y, sjis, color, weight):
        key = (sjis, weight, x & 7)
        if key not in self.glyph_cache:
            # Execute the target renderer and its weight helpers, with ROM
            # rows supplied from independent PIL/SJIS lookup. Color15 makes
            # the RMW write mask observable without introducing C++ weights.
            frame = self.original.glyph(None, weight, 15, 80+(x&7), 320, sjis, self.rom)
            self.glyph_cache[key] = np.frombuffer(frame, dtype=np.uint8).reshape(400, 640)[320:336,80:112] != 0
        mask = self.glyph_cache[key]
        left = x & ~7
        self.pages[self.access, y:y+16, left:left+32][mask] = color & 15

    def apply(self, line):
        words = line.split(); kind = words[0]
        if kind == 'END': return
        a, b, c, d, e = map(int, words[1:6])
        if kind == 'show': self.shown = a & 1
        elif kind == 'access': self.access = a & 1
        elif kind == 'snap': self.saved = self.pages[self.access,320:384,80:560].copy()
        elif kind == 'restore': self.pages[self.access,320:384,80:560] = self.saved
        elif kind == 'bg_free': self.saved = None
        elif kind == 'clear': self.pages[self.access].fill(0)
        elif kind == 'copy_page': self.pages[a&1] = self.pages[self.access]
        elif kind == 'text': self.glyph(a,b,c,d,e)
        elif kind == 'gaiji':
            base = 32 + int.from_bytes(self.gaiji[28:30], 'little') + c*32
            mask = np.unpackbits(np.frombuffer(self.gaiji[base:base+32], dtype=np.uint8)).reshape(16,16) != 0
            self.pages[self.access,b:b+16,a:a+16][mask] = d & 15
        elif kind == 'box_mask':
            for row in range(320,384):
                mask = self.mask(self.box_masks[a],row,480)
                self.pages[0,row,80:560][mask] = self.pages[1,row,80:560][mask]
            self.access = 0
        elif kind == 'pi_free': self.loaded = None
        elif kind == 'pi_load': self.loaded = self.pictures[bytes.fromhex(words[6]).decode('ascii').upper()]
        elif kind == 'pi_palette': self.palette = self.loaded[0]
        elif kind == 'pi_put': self.pages[self.access,b:b+400,a:a+640] = self.loaded[1]
        elif kind in ('quarter', 'pic_mask'):
            sx = 320 if c in (1,3) else 0; sy = 200 if c in (2,3) else 0
            picture = self.loaded[1][sy:sy+200,sx:sx+320]
            if kind == 'quarter': self.pages[self.access,b:b+200,a:a+320] = picture
            else:
                for row in range(200):
                    mask = self.mask(self.picture_masks[d],row,320)
                    self.pages[0,b+row,a:a+320][mask] = picture[row][mask]
                self.pages[1,b:b+200,a:a+320] = self.pages[0,b:b+200,a:a+320]
                self.shown = 0; self.access = 1
        elif kind == 'pic_copy':
            self.pages[1,b:b+200,a:a+320] = self.pages[0,b:b+200,a:a+320]; self.access = 1
        elif kind == 'clear_rect': self.pages[self.access,b:b+d,a:a+c] = 0
        elif kind == 'scroll': self.scroll = a
        elif kind == 'tone': self.tone = a
        elif kind == 'fade': self.tone = 100 if b else (200 if a else 0)


def run(exe, runner, *args):
    env = os.environ.copy(); env.setdefault('WINEDEBUG','-all')
    return subprocess.run(([runner] if runner else [])+[str(exe.resolve()), *map(str,args)],
                          env=env,capture_output=True,text=True,check=True).stdout


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target',type=Path,required=True);p.add_argument('--decoded-dir',type=Path,required=True)
    p.add_argument('--hdi',type=Path,required=True);p.add_argument('--font-bmp',type=Path,required=True)
    p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner')
    p.add_argument('--reference-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    args = p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    assets=ending_assets(args.hdi);private=out/'assets';private.mkdir(exist_ok=True)
    for name,body in assets.items():
        if name.startswith('_ED') or name.startswith('ED') and name.endswith('.PI') or name=='GAMEFT.BFT':
            (private/name).write_bytes(body)
    pictures={};decodes=[]
    for name in sorted(n for n in assets if n.startswith('ED') and n.endswith('.PI')):
        path=private/name;raw=private/(name+'.raw');run(args.exe,args.runner,'--decode',path,raw)
        decoded=raw.read_bytes();width,height=struct.unpack_from('<II',decoded)
        if (width,height)!=(640,400) or len(decoded)!=56+128000:raise ValueError('Ending PI dimensions differ')
        packed=np.frombuffer(decoded[56:],dtype=np.uint8);pixels=np.empty((400,640),dtype=np.uint8)
        pixels[:,::2]=(packed>>4).reshape(400,320);pixels[:,1::2]=(packed&15).reshape(400,320)
        pictures[name]=(decoded[8:56],pixels);decodes.append(dict(name=name,packed_sha256=sha(decoded[56:]),palette_sha256=sha(decoded[8:56])))
    original=Original(args.target,args.decoded_dir)
    font=Image.open(args.font_bmp).convert('L')
    raw=original.payload
    masks=[np.frombuffer(raw[0xeb3c:0xeb5c],dtype='<u2').reshape(4,4),
           np.frombuffer(raw[0xeb5c:0xeb84],dtype='<u2').reshape(5,4)]
    # Independent renderer controls include unaligned x, two ANK glyphs,
    # space and halfwidth kana. Compare the complete RMW output, including
    # original weight spill dots, at two DOS relocation loads.
    matrix=out/'font-controls';matrix.mkdir(exist_ok=True)
    lookup=Raster(original,font,assets['GAMEFT.BFT'],pictures,masks)
    fixtures=[(weight,color,x,y,text)
              for text,weight,(color,x,y) in itertools.product(
                  (0x82a0,0x8abf,0x2c34,0x4142,0x2041,0xa1a2),range(4),
                  [(15,80+s,320) for s in range(8)]+[(0,79,17),(5,160,128),(7,567,370)])]
    (matrix/'fixtures.txt').write_text(''.join(' '.join(map(str,f))+'\n' for f in fixtures))
    run(args.exe,args.runner,'--glyphs',args.font_bmp.resolve(),matrix/'fixtures.txt',matrix)
    second=Original(args.target,args.decoded_dir,0x1000)
    font_records=[]
    for index,(weight,color,x,y,text) in enumerate(fixtures):
        want=original.glyph(None,weight,color,x,y,text,lookup.rom)
        relocated=second.glyph(None,weight,color,x,y,text,lookup.rom)
        actual=(matrix/f'glyph-{index}.bin').read_bytes()
        if want!=relocated or want!=actual:
            at=next(i for i,(a,b) in enumerate(zip(want,actual)) if a!=b) if want!=actual else 0
            raise ValueError(f'font fixture{index} differs at {at%640},{at//640}')
        font_records.append(dict(fixture=list(fixtures[index]),sha256=sha(want)))
    records=[];glyphs={}
    for index,(name,body) in enumerate((n,b) for n,b in assets.items() if n.startswith('_ED')):
        expected=(args.reference_dir/f'{index*4:03d}-trace.txt').read_text().splitlines()
        if expected!=original.run(body,0):raise ValueError('retained script producer is not the fresh original')
        candidate=[i for i,l in enumerate(expected) if l.startswith(('box_mask 4 ','pic_mask ','pic_copy ','pi_put '))]
        chosen=set(candidate[i] for i in np.linspace(0,len(candidate)-1,12,dtype=int))
        route=out/name;route.mkdir(exist_ok=True);checkpoint=route/'checkpoints.txt'
        checkpoint.write_text('\n'.join(map(str,sorted(chosen)))+'\n')
        stdout=run(args.exe,args.runner,'--render',private,name,0,args.font_bmp.resolve(),checkpoint,route)
        (route/'stdout.txt').write_text(stdout)
        states={int(l.split()[0]):list(map(int,l.split()[1:])) for l in (route/'states.txt').read_text().splitlines()}
        if set(states)!=chosen:raise ValueError('native gallery omitted a checkpoint')
        raster=Raster(original,font,assets['GAMEFT.BFT'],pictures,masks)
        route_records=[]
        for event_index,line in enumerate(expected):
            raster.apply(line)
            if event_index not in chosen:continue
            native_states=states[event_index]
            if native_states!=[raster.shown,raster.access,raster.scroll,raster.tone]:raise ValueError('Ending page/palette clock differs')
            if (route/f'{event_index}.pal').read_bytes()!=raster.palette:raise ValueError('Ending palette bytes differ')
            for page in range(2):
                want=raster.pages[page].tobytes();actual=(route/f'{event_index}-{page}.bin').read_bytes()
                if want!=actual:
                    at=next(i for i,(a,b) in enumerate(zip(actual,want)) if a!=b)
                    raise ValueError(f'{name} checkpoint{event_index} page{page} differs at {at%640},{at//640}')
                route_records.append(dict(event=event_index,page=page,sha256=sha(want)))
            palette=(np.frombuffer(raster.palette,dtype=np.uint8).reshape(16,3)[:,[1,2,0]]>>4).astype(np.int32)
            tone=raster.tone
            rgb=(palette*tone//100 if tone<=100 else 15-(15-palette)*(200-tone)//100).astype(np.uint8)*17
            Image.fromarray(rgb[raster.pages[raster.shown]]).save(route/f'{event_index}.png')
        glyphs[name]=len(raster.glyph_cache)
        records.append(dict(name=name,checkpoints=route_records,reference_sha256=sha(('\n'.join(expected)+'\n').encode())))
    # The complete frame comparator must reject a changed source pixel.
    negative=bytearray(want);negative[80+320*640]^=1
    if bytes(negative)==actual:raise ValueError('negative pixel comparator did not reject')
    receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),cases=records,
        native_sha256=sha(args.exe.read_bytes()),font_sha256=sha(args.font_bmp.read_bytes()),payload_sha256=PAYLOAD_SHA,
        pi_decodes=decodes,original_font_controls=glyphs,font_matrix=font_records,negative_pixel_rejected=True,
        scope='Eight actual Ending scripts, twelve page/palette checkpoints each; both complete640x400 indexed pages. Expected font masks execute original MAINE0CC7:058C and weight helpers using supplied CGROM rows; original CPU script requests and observed DATA mask words drive the independent NumPy raster.',
        limits='PI decoding is an explicit separately regressed dependency. Gaiji comes from the independent PAR/BFT path. Graphics page/mask model is not a physical PC-98 capture or complete gameplay-to-score route; no audio, staff roll or DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(passed=True,routes=len(records),screens=sum(len(r['checkpoints']) for r in records),original_font_controls=sum(glyphs.values()))))


if __name__=='__main__':main()
