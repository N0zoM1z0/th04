#!/usr/bin/env python3
"""Original Marisa foreground and shared NPC backdrop controls; draw consumers adapted."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP
from verify_reimu_render import Original as Base,compare as compare_background
from verify_orange_render import explosion,renders as explosion_rows
from verify_marisa import bit
from verify_orange import boss
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base):
    def hook_body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def ret(cleanup):
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+cleanup)
            u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off)
        if (cs,ip)==(0x2000,0x1562) and not getattr(self,'raw_line',False):
            ey,ex,y,x=struct.unpack('<4h',u.mem_read(0x70000+sp+4,8))
            self.render_draws.append([5,x,y,0,self.color,ex,ey]);ret(12);return
        if (cs,ip)==(0x2000,0x2b78):
            planes,mask,pattern,y,x=struct.unpack('<HHHhh',u.mem_read(0x70000+sp+4,10))
            if planes!=0xffc0 or mask!=0:raise ValueError('Marisa rolling white plane contract differs')
            self.render_draws.append([8,x,y,pattern,0,0,0]);ret(14);return
        super().hook_body(u,address,size,unused)

def private(alive=4):
    # DATA432E..4347 includes the otherwise unowned byte4335.
    return list(struct.pack('<8BH8h',17,3,1,254,alive,1,2,173,0x35d1,96,160,240,320,72,112,192,264))
def render_row(phase=2,frame=0,sprite=128,damage=0,x=3072,y=1024,alive=4,pool=None,e=None):
    b=boss(phase,0,x=x,y=y);b[14]=sprite;b[18]=damage
    pool=pool if pool is not None else [bit(flag=1,pattern=136+i,x=1280+i*1024,y=512+i*640,damage=i*257) for i in range(4)]+[bit(flag=255,marker=i*11) for i in range(4,32)]
    return [frame,0,73,0,*b,*range(16),*(e or [*explosion(),*explosion(),*explosion()]),*private(alive),*itertools.chain.from_iterable(pool)]
def render_rows():
    for phase,sprite,frame,damage,alive in itertools.product((0,1,2,3,253,254,255),(0,4,128,135,139,255),(0,7,15),(0,1,255),range(5)):
        yield render_row(phase=phase,sprite=sprite,frame=frame,damage=damage,alive=alive)
    edges=(-32768,-257,-256,-255,-17,-16,-1,0,5887,5888,6143,6144,32767)
    for phase,flag,x,y,damage in itertools.product((0,2,254,255),(0,1,128,255),edges,edges,(0,1,257,-32768)):
        pool=[bit(flag=flag,x=x,y=y,damage=damage)]+[bit(marker=i*11) for i in range(1,32)]
        yield render_row(phase=phase,x=x,y=y,pool=pool,alive=0)
    for row in explosion_rows():
        yield row+private(0)+list(itertools.chain.from_iterable(bit(marker=i*11) for i in range(32)))

def compare_render(o,a,out,rows):
    configured=('\n'.join(' '.join(map(str,row)) for row in rows)+'\n').encode()
    fixture=out/'render-fixtures.txt';trace=out/'render-trace.txt'
    if a.reference_dir:
        ref=json.loads((a.reference_dir/'receipt.json').read_text());control=ref['controls']['render']
        original=a.reference_dir/'render-trace.txt'
        if not ref['passed'] or ref['target_sha256']!=sha(o.target) or sha(configured)!=control['fixture_sha256'] or sha(original.read_bytes())!=control['trace_sha256']:
            raise ValueError('Marisa render reference identity/configuration differs')
        expected=original.read_text().splitlines()
        if len(configured.splitlines())!=control['cases'] or len(expected)!=control['cases']:raise ValueError('reference count differs')
    else:
        expected=[]
        for text in configured.decode().splitlines():
            row=list(map(int,text.split()));frame,clock,tone,changed=row[:4]
            o.reset();o.render_draws=[];o.color=0
            o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
            o.u.mem_write(0x853ca,bytes(row[4:28]));o.u.mem_write(0x8bcde,bytes(row[28:44]));o.u.mem_write(0x84298,bytes(row[44:92]));o.u.mem_write(0x8432e,bytes(row[92:118]));o.u.mem_write(0x8b204,bytes(row[118:]))
            o.write(0x18d8,'h',clock);o.write(0x3a4,'h',tone);o.write(0x5393,'B',changed)
            o.call_args(0x4281,cs=0x2aaf)
            b=bytearray(row[4:28]);b[18]=0 if b[15]<254 else b[18]
            if o.u.mem_read(0x853ca,24)!=bytes(b) or o.u.mem_read(0x8bcde,16)!=bytes(row[28:44]):raise ValueError('Marisa foreground wrote unrelated BOSS state')
            draws=[d+[0,0] if len(d)==5 else d for d in o.render_draws]
            value=[o.u.mem_read(0x84298,48).hex(),*o.read(0x18d8,'h'),*o.read(0x3a4,'h'),*o.read(0x5393,'B'),*o.read(0x53dc,'B'),o.u.mem_read(0x8432e,26).hex(),o.u.mem_read(0x8b204,832).hex(),len(draws),*itertools.chain.from_iterable(draws)]
            expected.append(' '.join(map(str,value)))
    fixture.write_bytes(configured);trace.write_text('\n'.join(expected)+'\n')
    # Persist original-only expectations BEFORE native comparison. A candidate
    # mismatch cannot erase the independently produced CPU trace.
    if not a.reference_dir:
        (out/'original-reference.json').write_text(json.dumps(dict(passed=True,target_sha256=sha(o.target),controls={'render':dict(cases=len(expected),fixture_sha256=sha(configured),trace_sha256=sha(trace.read_bytes()))},scope='Original CPU expectations only; native comparison not implied.'),indent=2)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    got=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--render-vectors',str(fixture)],check=True,capture_output=True,text=True,env=env).stdout.splitlines()
    for i,(want,actual) in enumerate(itertools.zip_longest(expected,got)):
        if want is None or actual is None or want.split()!=actual.split():
            (out/'render-mismatch.json').write_text(json.dumps(dict(case=i,input=configured.decode().splitlines()[i],expected=want,actual=actual),indent=2)+'\n');raise ValueError(f'Marisa render case{i} differs')
    return dict(cases=len(expected),fixture_sha256=sha(configured),trace_sha256=sha(trace.read_bytes()))

def line_rows():
    for x,y,ex,ey in itertools.product((-128,31,32,33,160,414,415,416,640),(-128,15,16,17,200,382,383,384,512),(32,160,415),(16,200,383)):
        yield [x,y,ex,ey];yield [ex,ey,x,y]
    outside=((-128,-128),(640,-128),(-128,512),(640,512),(31,200),(416,200),(160,15),(160,384))
    for a,b in itertools.product(outside,repeat=2):yield [*a,*b]

def compare_lines(o,a,out,rows):
    inputs=[];expected=[]
    for row in rows:
        o.reset();o.raw_line=True;o.render_draws=[]
        # Match stage_state_init's actual playfield clip. Y is relative in the
        # line helper, and ClipYT_seg adds16 physical rows back to VRAM.
        o.write(0x32c,'6h',32,383,415,16,367,383);o.write(0x338,'H',0xa850)
        bits=bytearray(32000)
        def write(u,access,at,size,value,unused):
            for byte in range(size):
                dest=at-0xa8000+byte
                if 0<=dest<32000:bits[dest]|=(value>>(byte*8))&255
        handle=o.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,write)
        try:
            x,y,ex,ey=row;o.call_args(0x1562,(ey,ex,y,x),far=True,cs=0x2000)
        finally:o.u.hook_del(handle)
        inputs.append(' '.join(map(str,row)));expected.append(bits.hex())
    fixture=out/'line-fixtures.txt';trace=out/'line-trace.txt';fixture.write_text('\n'.join(inputs)+'\n');trace.write_text('\n'.join(expected)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    lines=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--line-vectors',str(fixture)],check=True,capture_output=True,text=True,env=env).stdout.splitlines()
    for index,(want,got) in enumerate(itertools.zip_longest(expected,lines)):
        if want is None or got is None or want!=got.strip():
            (out/'line-mismatch.json').write_text(json.dumps(dict(case=index,input=inputs[index],expected=want,actual=got),indent=2)+'\n');raise ValueError(f'Marisa line case{index} differs')
    return dict(cases=len(inputs),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('target','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--reference-dir',type=Path);p.add_argument('--only',choices=('render','background','line'));p.add_argument('--limit',type=int)
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    if a.reference_dir and a.limit:raise ValueError('reference replay requires complete fixtures')
    manifest=source_manifest(Path(__file__).resolve().parents[1])[0];o=Original(a.target.read_bytes())
    class Rejecting(Original):
        def hook_body(self,u,address,size,unused):
            if address==0x2aaf0+0x4281:raise ValueError('injected Marisa render rejection')
            super().hook_body(u,address,size,unused)
    bad=Rejecting(o.target)
    try:bad.call_args(0x4281,cs=0x2aaf)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('render callback rejection swallowed')
    results={}
    for mode,rows in [('render',render_rows()),('background',itertools.product(range(256),(-32768,-65,-64,-63,-8,-7,-1,0,1,2,3,7,8,55,56,63,64,65,119,120,127,128,32767))),('line',line_rows())]:
        if a.only and a.only!=mode:continue
        rows=itertools.islice(rows,a.limit) if a.limit else rows
        results[mode]=compare_lines(o,a,out,rows) if mode=='line' else (compare_render(o,a,out,rows) if mode=='render' else compare_background(o,a,out,mode,rows))
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during Marisa render controls')
    receipt=dict(passed=True,line_cpu_reexecuted='line' in results,original_cpu_reexecuted=not bool(a.reference_dir),callback_rejection_passed=True,controls=results,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='MAIN load2000 DS8000 bits0AAF:419E..4280/foreground4281..42F0 and shared NPC backdrop77E7..7873. Ordered body/line/bit/explosion requests, visible damage consumption, full retained private26/pool832 and explosion/flash state. Line controls execute original0000:1562 and clipping079A with actual stage32..415/16..383 bounds, signed IDIV and CPU write masks.',limits='Sprite/line/CDG/tile/filler hardware consumers adapted. Alive count0..4; invalid larger counts excluded. Sprite pixels, GUI pacing, physical page/scroll/alias behavior separate; line masks use a bounded CPU write shadow, not physical color hardware. No DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(passed=True,controls=results)))
if __name__=='__main__':main()
