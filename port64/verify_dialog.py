#!/usr/bin/env python3
"""Compare native dialog requests and retained cursors to original MAIN CPU."""
import argparse,hashlib,itertools,json,os,struct,subprocess
import unicorn
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_effects import Original as Base
from probe_assets import main_assets
sha=lambda b:hashlib.sha256(b).hexdigest()
signed=lambda n:n if n<32768 else n-65536

class Original(Base):
    def __init__(self,target):
        self.held=0;self.dialog_events=[];self.error=None;self.clear_count=0;self.activations=0;super().__init__(target)
    def event(self,kind,a=0,b=0,c=0,d=0,name=b''):
        self.dialog_events.append(f'{kind} {a} {b} {c} {d} '+(name.hex() if name else '-'))
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size)
        except Exception as e:self.error=e;u.emu_stop()
    def body(self,u,address,size):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def words(count,far=True):return struct.unpack('<'+'H'*count,u.mem_read(0x70000+sp+(4 if far else 2),count*2))
        def ret(args,far=True):
            values=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
            u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+args)
            if far:u.reg_write(UC_X86_REG_CS,values[1])
            u.reg_write(UC_X86_REG_IP,values[0])
        def cstring(off,seg):
            value=bytearray()
            while True:
                c=u.mem_read(seg*16+off+len(value),1)[0]
                if not c:return bytes(value)
                value.append(c)
                if len(value)>20:raise ValueError('original filename exceeds scratch')
        if (cs,ip)==(0x2aaf,0x2bfb):self.activations+=1;ret(0);return
        if (cs,ip)==(0x330e,0x6bc):self.write(0x3974,'H',self.held);ret(0);return
        if (cs,ip)==(0x330e,0xd7):self.event(9,signed(words(1)[0]));ret(2);return
        if (cs,ip)==(0x330e,0x133):self.event(10,signed(words(1)[0]));ret(2);return
        if (cs,ip)==(0x2aaf,0x625b):self.event(17);ret(0,False);return
        if cs==0x2000 and ip==0x229e:
            attr,char,y,x=words(4)
            if (attr,char)!=(0xe1,32):raise ValueError('original box clear attributes differ')
            cx,cy,side=self.read(0x4290,'3h')
            index=self.clear_count%90
            if (x,y)!=(cx//8+index%30,cy//16+index//30):raise ValueError('original box clear geometry differs')
            if not index:self.event(0,cx,cy,side)
            self.clear_count+=1;ret(8);return
        if cs==0x2000 and ip==0x22f6:
            attr,off,seg,y,x=words(5);glyph=bytes(u.mem_read(seg*16+off,3))
            if glyph[2]!=0:raise ValueError('original text buffer lacks terminator')
            self.event(1,x*8,y*16,glyph[0]*256+glyph[1],attr);ret(10);return
        if (cs,ip)==(0x2000,0x1b0c):
            attr,glyph,y,x=words(4);self.event(2,x*8,y*16,glyph,attr);ret(8);return
        if (cs,ip)==(0x2aaf,0x255e):
            y,x=words(2,False);self.event(3,x,y);ret(4,False);return
        if (cs,ip)==(0x330e,0x4a0):
            pattern,y,x=words(3);self.event(4,x,y,pattern);ret(6);return
        if (cs,ip)==(0x2000,0x2d3e):
            pattern,y,x=words(3);self.event(5,signed(x),signed(y),pattern);ret(6);return
        if (cs,ip)==(0x2000,0x2b4e):
            last,first=words(2);self.event(6,first,last);ret(4);return
        if (cs,ip)==(0x2000,0x2a74):
            off,seg=words(2);self.event(7,name=cstring(off,seg));u.reg_write(UC_X86_REG_AX,1);ret(4);return
        if (cs,ip)==(0x330e,0x978):self.event(8,words(1)[0]);ret(2);return
        if (cs,ip)==(0x2000,0x1f04):self.event(11,signed(self.read(0x3a4,'H')[0]));ret(0);return
        if cs==0x2000 and ip in (0x622,0x666,0x2488,0x24c8):
            self.event(12,int(ip>=0x2488),int(ip in (0x622,0x2488)),words(1)[0]);ret(2);return
        if (cs,ip)==(0x330e,0x3b6):
            mode,off,seg=words(3);self.event(13,mode,name=cstring(off,seg));ret(6);return
        if (cs,ip)==(0x330e,0x2fc):self.event(14,words(1)[0]);ret(2);return
        if (cs,ip)==(0x330e,0x7c6):ret(0);return
        if (cs,ip)==(0x330e,0x7d2):self.event(15,words(1)[0]);ret(2);return
        if (cs,ip)==(0x330e,0x80c):ret(0);return
        if (cs,ip)==(0x2000,0x1d50):self.event(16,words(1)[0]);ret(2);return
        super().hook(u,address,size,None)
    def scene(self):
        self.error=None;self.clear_count=0
        try:self.call_args(0x2a7c,cs=0x2aaf)
        except Exception:
            if self.error:raise RuntimeError('original dialog hook rejected') from self.error
            raise
        if self.error:raise RuntimeError('original dialog hook rejected') from self.error
        if self.clear_count%90:raise ValueError('original incomplete box clear')
        off=self.read(0x428c,'H')[0];x,y,side,default=self.read(0x4290,'4h')
        self.dialog_events.append(f'END {off} {x} {y} {side} {default}')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--hdi',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--font-bmp',type=Path)
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    original=Original(args.target.read_bytes());assets=main_assets(args.hdi);cases=[]
    for name,body in assets.items():
        if name.startswith('_DM'):
            # Count outer stops independently by comparing successive original
            # calls until only separator bytes remain. No copied script parser.
            for held in (0,1):cases.append((name,body,held,0))
    # Synthetic controls cover unused commands/default inheritance, three-digit
    # limits, unknown commands and inner '#'. They never modify pinned targets.
    synthetic=[b'0\\=255\\ga8\\n\\$\\#',b'\\t\\e\\b1,2,3\\#',b'\\t1234\\b12,,34\\#',b'\\fi0\\fo2\\wi0\\wo2\\#',b'\\m$\\m*\\m,ABC.M26 \\d\\#',b'\\g2\\g\\k2\\#',b'0\\#1\\#\\#',b'\\Q\\Fz\\Ga7\\#']
    for index,body in enumerate(synthetic):
        for held in (0,1):cases.append((f'synthetic-{index}',body,held,1))
    results=[];env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--gates']
    native_gates=subprocess.run(command,capture_output=True,text=True,env=env,check=True).stdout.splitlines();expected_gates=[]
    for speed,page in itertools.product(range(256),(0,1,2)):
        original.reset();original.activations=0;original.error=None
        original.write(0x4277,'B',speed);original.write(0x46fc,'B',page);original.write(0x5394,'B',0);original.write(0x1868,'H',77)
        original.call_args(0x2454,cs=0x2aaf)
        if original.error:raise RuntimeError('gate hook rejected') from original.error
        result=original.u.reg_read(UC_X86_REG_AX)&255
        if original.activations!=result or original.read(0x1868,'H')[0]!=77+int(not result):raise ValueError('original activation/count side effect differs')
        expected_gates.append(f'{speed} {page} {result}')
    if expected_gates!=native_gates:raise ValueError('original dialog activation predicate differs')
    for index,(name,body,held,scenes) in enumerate(cases):
        original.reset();original.held=held;original.dialog_events=[]
        original.u.mem_write(0x90000,body+bytes(4));original.write(0x428c,'HH',0,0x9000)
        count=0
        while count<12:
            original.scene();count+=1
            if scenes and count==scenes:break
            at=original.read(0x428c,'H')[0]
            if at>len(body):raise ValueError('original dialog read escaped file')
            if all(c<=32 or c==127 for c in body[at:]):break
        else:raise ValueError('original dialog scene count exceeded bound')
        path=out/f'{index:03d}.txt';path.write_bytes(body)
        command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--trace',str(path),str(held),str(count)]
        actual=subprocess.run(command,capture_output=True,text=True,env=env,check=True).stdout.splitlines()
        expected=original.dialog_events
        if actual!=expected:
            i=next(i for i,(a,b) in enumerate(itertools.zip_longest(actual,expected)) if a!=b)
            (out/'mismatch.json').write_text(json.dumps(dict(name=name,held=held,event=i,actual=actual[max(0,i-3):i+4],expected=expected[max(0,i-3):i+4]),indent=2)+'\n');raise ValueError(f'{name} held{held} event{i} differs')
        trace='\n'.join(expected)+'\n';(out/f'{index:03d}-trace.txt').write_text(trace)
        results.append(dict(name=name,held=held,scenes=count,events=len(expected),input_sha256=sha(body),trace_sha256=sha(trace.encode())))
    font=None
    if args.font_bmp:
        from PIL import Image
        bitmap=Image.open(args.font_bmp).convert('L');pixels=[]
        for sjis in (0x82a0,0x8146,0xe8cb,0x9682,0x97c0,0x8db9):
            jis=sjis.to_bytes(2,'big').decode('shift_jis').encode('iso2022_jp')[3:5];row,cell=jis
            for y in range(16):
                for x in range(16):pixels.append('1' if bitmap.getpixel(((row-0x20)*16+x,cell*16+y))==0 else '0')
        command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--font-pixels',str(args.font_bmp.resolve())]
        actual=subprocess.run(command,capture_output=True,text=True,env=env,check=True).stdout.strip()
        if actual!=''.join(pixels):raise ValueError('PC-98 font pixels differ from independent image/encoding path')
        font=dict(glyphs=6,pixels=1536,font_bmp_sha256=sha(args.font_bmp.read_bytes()),mask_sha256=sha(actual.encode()),scope='Python SJIS/ISO2022JP encoding and PIL image pixels versus native font lookup; supplied emulator font, not an official ROM provenance claim.')
    receipt=dict(passed=True,cases=results,font=font,activation_controls=len(expected_gates),activation_trace_sha256=sha(('\n'.join(expected_gates)+'\n').encode()),target_sha256=sha(original.target),native_sha256=sha(args.exe.read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),scope='MAIN load2000 DS8000 main01 0AAF:2A7C/26CC/25DA/26A3 and2454 activation. Complete ordered box/text/face/sprite/resource/palette/audio/delay/wait/scroll requests and retained offset/cursor/side/default after every original scene; activation also checks original dialog invocation and STD frame count.',limits='Input, graphics, waits, fades, sprite/CDG/file/audio consumers intercepted. Native asynchronous host frame pacing and complete dialog/game video remain separate; no DOS exact promotion.')
    receipt.update(unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()))
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(results),events=sum(r['events'] for r in results),scenes=sum(r['scenes'] for r in results))))
if __name__=='__main__':main()
