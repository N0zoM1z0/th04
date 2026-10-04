#!/usr/bin/env python3
"""Independent MAIN0AAF:712A..72A5 foreground state/request controls.

Execute original foreground, explosion, laser and custom render owners at
load2000 DS8000. Graphics callees are ordered request adapters, including
FFCD red versus FFC0 white, zoom and custom-circle mode/color/disable.
Complete actor35/additional16/explosion48/laser72/custom832 and flash/global
state is compared; actual pixels, PC98 hardware and whole battle are separate.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_AX
from verify_yuuka5_render import Original as Base
from verify_orange_render import explosion,renders as explosion_rows
from verify_yuuka6_motion import fixture as actor
from verify_yuuka6_entities import slot,circle
from verify_lasers import beam
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def __init__(self,target):
        self.in_entities=False;self.reject=False;super().__init__(target)
    def out(self,u,port,size,value,unused):
        try:
            if self.in_entities:
                if (port,size,value)!=(0x7c,1,0):raise ValueError('unexpected custom render OUT')
                self.render_draws.append([9,0,0,0,0,0,0,0]);return
            super().out(u,port,size,value,unused)
        except Exception as e:self.callback_error=e;u.emu_stop()
    def hook_body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if self.reject and (cs,ip)==(0x2aaf,0x712a):raise ValueError('injected Yuuka6 foreground callback rejection')
        if (cs,ip)==(0x2aaf,0x7054):self.in_entities=True
        if (cs,ip)==(0x2aaf,0x7129):self.in_entities=False
        def ret(cleanup,far=False):
            words=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2));u.reg_write(UC_X86_REG_SP,sp+cleanup)
            if far:u.reg_write(UC_X86_REG_CS,words[1])
            u.reg_write(UC_X86_REG_IP,words[0])
        if (cs,ip)==(0x2000,0x2838):
            plane,mask,pattern,y,x=struct.unpack('<HHHhh',u.mem_read(0x70000+sp+4,10))
            if mask!=0 or plane not in (0xffcd,0xffc0):raise ValueError('Yuuka6 plane draw contract differs')
            self.render_draws.append([11 if plane==0xffcd else 1,x,y,pattern,0,0,0,0]);ret(14,True);return
        if self.in_entities and cs==0x2aaf and ip in (0x1666,0x1672):
            if ip==0x1666:self.render_draws.append([12,0,0,0,0,0,0,0xc0])
            else:
                self.color=(u.reg_read(UC_X86_REG_AX)>>8)&255;self.render_draws.append([5,0,0,0,self.color,0,0,0])
            ret(2);return
        super().hook_body(u,address,size,unused)

def fixture(steps=1,frame=0,phase=2,sprite=128,damage=0,cycle=0,mirror_cycle=0,mirror_damage=0,mirror_state=2,aux=0,x=3072,y=1280,mx=1024,my=1280,exp=None,lasers=None,custom=None,rehit=0,big_clock=0):
    raw=bytearray(actor(sprite=sprite,x=x,y=y,aux=aux,mirror=mirror_state)[5:]);raw[15]=phase;raw[18]=damage;struct.pack_into('<hh',raw,30,mx,my)
    records=custom if custom is not None else [slot(marker=i*13+19) for i in range(31)]+[circle()]
    return [steps,frame,big_clock,73,0,cycle,mirror_cycle,mirror_damage,127,rehit,raw.hex(),bytes(range(16)).hex(),bytes(exp or [*explosion(),*explosion(),*explosion()]).hex(),bytes(itertools.chain.from_iterable(lasers or [beam(flag=1),beam(),beam()])).hex(),b''.join(records).hex()]

def fixtures():
    for index,(phase,sprite,damage,cy,mc,md,mirror,aux,frame) in enumerate(itertools.product((0,1,2,3,17,253,254,255),(0,128,255),(0,1,255),(0,1,254,255),(0,1,254,255),(0,255),(0,1,2,255),(0,1,255),(0,3,4,7,8,11,12,15))):
        if index%137==0:yield fixture(phase=phase,sprite=sprite,damage=damage,cycle=cy,mirror_cycle=mc,mirror_damage=md,mirror_state=mirror,aux=aux,frame=frame)
    for phase,damage,cycle in itertools.product((2,254,255),(0,1,255),range(256)):
        if (phase+damage+cycle)%7==0:yield fixture(phase=phase,damage=damage,cycle=cycle,mirror_cycle=255-cycle,mirror_damage=damage)
    for index,(x,y,mx,my) in enumerate(itertools.product((-32768,-17,-16,-1,0,6144,32767),repeat=4)):
        if index%7==0:yield fixture(x=x,y=y,mx=mx,my=my,damage=255,mirror_damage=255,aux=1)
    for r in explosion_rows():
        yield fixture(phase=r[4+15],damage=r[4+18],frame=r[0],big_clock=r[1],exp=r[44:])
    for flag,radius,outline in itertools.product((0,1,2,4,128,255),(-32768,-1,0,1,8,16,64,180,32767),(0,8,15,255)):
        yield fixture(lasers=[beam(flag=1),beam(flag=flag,radius=radius,color=outline),beam(flag=1,x=3200,marker=73)])
    for flag,damage,sc in itertools.product((0,1,2,15,16,47,48,255),(0,1,257),(0,1,2,255)):
        yield fixture(custom=[slot(flag=flag,damage=damage,marker=i*13+19) for i in range(31)]+[circle(flag=sc,radius=-32768,color=255,distance=32767)],damage=1,mirror_damage=1)
    for phase,cycle,rehit in itertools.product((2,254,255),(0,1,254,255),(0,1)):
        yield fixture(steps=40,phase=phase,cycle=cycle,mirror_cycle=255-cycle,damage=255,mirror_damage=255,rehit=rehit,aux=1,
                      custom=[slot(flag=16,marker=i*13+19) for i in range(31)]+[circle(flag=2)],exp=[*explosion(1),*explosion(1),*explosion(1)])

def seed(o,row):
    if len(row)!=15:raise ValueError('foreground fixture extent')
    o.reset();raw=bytes.fromhex(row[10]);assert len(raw)==35
    o.u.mem_write(0x853ca,raw[:24]);o.u.mem_write(0x846c6,raw[24:34]);o.write(0x46db,'B',raw[34]);o.u.mem_write(0x8bcde,bytes.fromhex(row[11]));o.u.mem_write(0x84298,bytes.fromhex(row[12]));o.u.mem_write(0x842d8,bytes.fromhex(row[13]));o.u.mem_write(0x8b204,bytes.fromhex(row[14]))
    o.write(0x18d8,'h',row[2]);o.write(0x3a4,'h',row[3]);o.write(0x5393,'B',row[4]);o.write(0x46c3,'2B',row[5],row[6]);o.write(0x46de,'B',row[7]);o.write(0x4669,'B',row[8])

def execute(o,row,step):
    o.render_draws=[];o.in_entities=False;o.in_laser=False;o.color=0;frame=(row[1]+step)&65535
    o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
    if row[9]:o.write(0x53dc,'B',bytes.fromhex(row[10])[18]);o.write(0x46de,'B',row[7])
    o.call_args(0x712a,cs=0x2aaf)
    raw=bytes(o.u.mem_read(0x853ca,24))+bytes(o.u.mem_read(0x846c6,10))+bytes(o.u.mem_read(0x846db,1))
    draws=[d+[0,0,0] if len(d)==5 else d for d in o.render_draws]
    values=[raw.hex(),o.u.mem_read(0x8bcde,16).hex(),o.u.mem_read(0x84298,48).hex(),o.u.mem_read(0x842d8,72).hex(),o.u.mem_read(0x8b204,832).hex(),*o.read(0x46c3,'2B'),*o.read(0x46de,'B'),*o.read(0x18d8,'h'),*o.read(0x3a4,'h'),*o.read(0x5393,'B'),*o.read(0x4669,'B'),len(draws),*itertools.chain.from_iterable(draws)]
    return ' '.join(map(str,values))+'\n'

def rejection(o):
    o.reset();o.reject=True
    try:o.call_args(0x712a,cs=0x2aaf)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('foreground callback rejection swallowed')
    finally:o.reject=False

def same(want,got):
    if want.split()!=got.split():raise ValueError('foreground original/native checkpoint differs')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--reference-dir',type=Path);p.add_argument('--limit',type=int);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());rejection(o)
    rows=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures());configured=('\n'.join(' '.join(map(str,r)) for r in rows)+'\n').encode()
    if a.reference_dir:
        ref=json.loads((a.reference_dir/'original-reference.json').read_text());fixture_path=a.reference_dir/'fixtures.txt';trace=a.reference_dir/'trace.txt.gz'
        if a.limit or not ref['passed'] or ref['target_sha256']!=sha(o.target) or sha(configured)!=ref['fixture_sha256'] or sha(fixture_path.read_bytes())!=ref['fixture_sha256']:raise ValueError('foreground reference identity differs')
    else:
        fixture_path=out/'fixtures.txt';fixture_path.write_bytes(configured);trace=out/'trace.txt.gz';digest=hashlib.sha256();records=0
        with gzip.open(trace,'wt',compresslevel=3) as f:
            for index,r in enumerate(rows):
                seed(o,r)
                for step in range(r[0]):line=execute(o,r,step);f.write(line);digest.update(line.encode());records+=1
                if index and index%1000==0:print('Original foreground',index,'fixtures PASS',flush=True)
        ref=dict(passed=True,target_sha256=sha(o.target),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),trace_records=records,cases=len(rows),source_manifest_sha256=manifest,scope=__doc__)
        (out/'original-reference.json').write_text(json.dumps(ref,indent=2)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)]
    digest=hashlib.sha256();records=0
    with gzip.open(trace,'rt') as wanted,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process:
        for index,(want,got) in enumerate(itertools.zip_longest(wanted,process.stdout)):
            try:same(want or '',got or '')
            except ValueError:
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=index,expected=want,actual=got),indent=2)+'\n');process.terminate();raise
            digest.update((' '.join(got.split())+'\n').encode());records+=1
        if process.wait()!=0:raise ValueError('foreground native consumer failed')
    if digest.hexdigest()!=ref['trace_sha256'] or records!=ref['trace_records']:raise ValueError('foreground reference digest/extent differs')
    try:same('abcd 1','abce 1')
    except ValueError:pass
    else:raise ValueError('one-byte mutation accepted')
    output=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve())],check=True,capture_output=True,text=True,env=env).stdout.strip()
    if output!='Stage 6 Yuuka foreground contracts PASS':raise ValueError('foreground contracts failed')
    if manifest!=source_manifest(root)[0]:raise ValueError('source changed during foreground controls')
    receipt=dict(passed=True,original_cpu_reexecuted=not bool(a.reference_dir),source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),trace_records=records,cases=len(rows),callback_rejection_passed=True,one_variable_rejection_passed=True,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,limits='Shared explosion body hardware mode/disable calls remain adapters; geometry and complete state are compared. Actual red/white/sprite/zoom/circle pixels, physical page/alias/VRAM/pacing and ordinary final battle join remain separate. No DOS exact promotion.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),records=records)))
if __name__=='__main__':main()
