#!/usr/bin/env python3
"""Original OP font/SUPER kernels consume independent setup caller traces.

All two-page/palette/RGB bytes compare at every refresh, including both
window animations and text effects. PI decode, EGC rectangle copy, CGROM and
GRCG shadow are explicit adapters. Streams are compressed while consumed;
no physical video/audio or whole original OP/game claim follows.
"""
import argparse,gzip,hashlib,json,subprocess,struct
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
from verify_op_music_pixels import Fonts
from verify_op_ranking_pixels import Sprites,SIZE
from verify_cutscene import ending_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Raster:
    def __init__(self,target,decoded,assets,picture,font):
        self.fonts=[Fonts(target,decoded,load) for load in (0x1000,0x2000)]
        for f in self.fonts:f.gaiji=assets['GAMEFT.BFT'];f.font=Image.open(font).convert('L')
        self.sprites=[Sprites(target,decoded,load) for load in (0x1000,0x2000)]
        self.assets=assets;self.picture=picture;self.font_cache={};self.sprite_cache={};self.calls=0
    def reset(self):
        self.pages=np.zeros((2,400,640),dtype=np.uint8);self.access=0;self.tone=0;self.palette=bytes(48);self.loaded=False
    def apply(self,line):
        row=line.split();kind=row[0];tick,a,b,c,d=map(int,row[1:6]);raw=bytes.fromhex(row[6]) if row[6]!='-' else b''
        if kind=='tone':self.tone=a
        elif kind=='access':self.access=a
        elif kind=='load':assert raw==b'ms.pi' and not self.loaded;self.loaded=True
        elif kind=='palette':assert self.loaded;self.palette=self.picture[0]
        elif kind=='picture':assert self.loaded;self.pages[self.access]=self.picture[1]
        elif kind=='free':assert self.loaded;self.loaded=False
        elif kind=='copy':self.access=a;self.pages[a]=self.pages[1-a]
        elif kind=='rectangle':self.pages[0,b:b+d,a:a+c]=self.pages[1,b:b+d,a:a+c]
        elif kind=='text':
            key=(raw,a,b,d)
            if key not in self.font_cache:
                masks=[f.render(raw,a,b,d) for f in self.fonts];assert masks[0]==masks[1]
                self.font_cache[key]=np.frombuffer(masks[0],dtype=np.uint8).reshape(400,640)!=0;self.calls+=2
            self.pages[self.access][self.font_cache[key]]=c
        elif kind=='sprite':
            key=(a,b,c)
            if key not in self.sprite_cache:
                zero=[s.render(self.assets['MSWIN.BFT'],c,a,b,bytes(256000)) for s in self.sprites];assert zero[0]==zero[1]
                pixels=np.frombuffer(zero[0],dtype=np.uint8).reshape(400,640)
                background=np.arange(256000,dtype=np.uint8).reshape(400,640)&15;expected=background.copy();expected[pixels!=0]=pixels[pixels!=0]
                for s in self.sprites:assert s.render(self.assets['MSWIN.BFT'],c,a,b,background.tobytes())==expected.tobytes()
                self.sprite_cache[key]=pixels.copy();self.calls+=4
            pixels=self.sprite_cache[key];self.pages[self.access][pixels!=0]=pixels[pixels!=0]
    def snapshot(self):
        palette=(np.frombuffer(self.palette,dtype=np.uint8).reshape(16,3).astype(np.uint16)>>4)*self.tone//100*17
        return self.pages.tobytes()+self.palette+palette.astype(np.uint8)[self.pages[0]].tobytes()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','decoded-dir','exe','hdi','font-bmp','original-dir','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0]
    original=json.loads((a.original_dir/'receipt.json').read_text());assert original['passed'] and original['original_cpu_reexecuted']
    raw=(a.original_dir/'original.txt').read_bytes();assert sha(raw)==original['trace_sha256']
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);assets=ending_assets(a.hdi);private=out/'assets';private.mkdir()
    for name in ('MS.PI','MSWIN.BFT','GAMEFT.BFT'):(private/name).write_bytes(assets[name])
    subprocess.run([str((a.exe.parent/'th04-port64-cutscene-contracts').resolve()),'--decode',str(private/'MS.PI'),str(private/'MS.PI.decoded')],check=True,capture_output=True)
    body=(private/'MS.PI.decoded').read_bytes();assert struct.unpack_from('<II',body)==(640,400)
    packed=np.frombuffer(body[56:],dtype=np.uint8).reshape(400,320);pixels=np.empty((400,640),dtype=np.uint8);pixels[:,::2]=packed>>4;pixels[:,1::2]=packed&15
    selected=[0,18,22,26,63];fixtures=(a.original_dir/'fixtures.txt').read_text().splitlines();(out/'fixtures.txt').write_text('\n'.join(fixtures[i] for i in selected)+'\n')
    cases=[];case=[]
    for line in raw.decode().splitlines():
        case.append(line)
        if line.startswith('END '):cases.append(case);case=[]
    raster=None if a.reference_dir else Raster(a.target,a.decoded_dir,assets,(body[8:56],pixels),a.font_bmp)
    reference=gzip.open(a.reference_dir/'displays.bin.gz','rb') if a.reference_dir else None
    command=[str(a.exe.resolve()),'--pixels',str(out/'fixtures.txt'),str(private),str(a.font_bmp.resolve())]
    digest=hashlib.sha256();snapshots=0
    with (out/'stderr.txt').open('wb') as error,gzip.open(out/'displays.bin.gz','wb',compresslevel=6) as compressed:
        proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=error)
        try:
            for index in selected:
                if raster:raster.reset()
                lines=cases[index];cursor=0;last=int(lines[-1].split()[1])
                for tick in range(last+1):
                    if raster:
                        while cursor<len(lines)-1 and int(lines[cursor].split()[1])==tick:raster.apply(lines[cursor]);cursor+=1
                        expected=raster.snapshot()
                    else:expected=reference.read(SIZE)
                    actual=proc.stdout.read(SIZE)
                    if actual!=expected:
                        at=next((i for i,(x,y) in enumerate(zip(actual,expected)) if x!=y),min(len(actual),len(expected)))
                        (out/'mismatch.json').write_text(json.dumps(dict(case=index,tick=tick,snapshot=snapshots,offset=at,actual=actual[at:at+16].hex(),expected=expected[at:at+16].hex()),indent=2))
                        raise ValueError('setup full display differs')
                    compressed.write(actual);digest.update(actual);snapshots+=1
                if raster:assert cursor==len(lines)-1
            assert not proc.stdout.read(1);assert proc.wait(timeout=30)==0
            if reference:assert not reference.read(1)
        finally:
            if proc.poll() is None:proc.terminate();proc.wait(timeout=30)
            if reference:reference.close()
    assert source_manifest(root)[0]==manifest
    if a.reference_dir:
        previous=json.loads((a.reference_dir/'receipt.json').read_text());assert previous['passed'] and previous['display_sha256']==digest.hexdigest() and previous['snapshots']==snapshots
    receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,exe_sha256=sha(a.exe.read_bytes()),original_receipt_sha256=sha((a.original_dir/'receipt.json').read_bytes()),snapshots=snapshots,snapshot_size=SIZE,compared_bytes=snapshots*SIZE,display_sha256=digest.hexdigest(),compressed_sha256=sha((out/'displays.bin.gz').read_bytes()),original_kernel_calls=raster.calls if raster else None,assets={k:sha(assets[k]) for k in ('MS.PI','MSWIN.BFT','GAMEFT.BFT')},hdi_sha256=sha(a.hdi.read_bytes()),font_sha256=sha(a.font_bmp.read_bytes()),reference_dir=str(a.reference_dir) if a.reference_dir else None,command=command,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('setup full displays PASS',snapshots)
if __name__=='__main__':main()
