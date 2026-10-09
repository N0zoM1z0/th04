#!/usr/bin/env python3
"""Muted actual OP options/children and score-only MAINE sound ownership.

Original OP options and MAINE _main execute at two relocated loads. Graphics,
resident drivers, child scenes, files and initialization are guarded adapters.
OP control is a representative full-state Oracle; MAIN and MAINE SE execute
their own controllers. No FM synthesis, physical timer, complete startup,
natural full-game or actual Windows acceptance follows.
"""
import argparse,hashlib,json,struct,subprocess,unicorn
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_op_score import Original as OpBase
from verify_sound_control import Original as OpControl
from verify_congratulations import Original as MaineMain
from verify_cutscene import Original as MaineBase
from verify_sound_join import MainControl
from verify_maine_join import return_to_caller
from verify import source_manifest,require_elf_x86_64

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class Options(OpBase):
    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
        if pair==(0xa74,0xff00):self.done=True;u.emu_stop();return
        if pair[0]==0xa74 and (0x912<=pair[1]<0xc1e or 0x6e8<=pair[1]<0x756):return
        if pair==(0xa74,0x497):return_to_caller(u,4,False);return
        if pair[0]==0xda1:
            def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
            ip=pair[1]
            if ip==0x264:
                self.calls.append(['command',words(1)[0]]);return_to_caller(u,2);return
            if ip==0x2d4:
                se,bgm=words(2);self.calls.append(['configure',bgm,se]);return_to_caller(u,4);return
            if ip==0x3ba:
                function,off,seg=words(3);name=bytes(u.mem_read(seg*16+off,13)).split(b'\0')[0].decode('ascii')
                self.calls.append(['load',function,name]);return_to_caller(u,6);return
            if ip in (0x8d6,0x8e2,0x91c):
                self.calls.append(['reset'] if ip==0x8d6 else ['play',words(1)[0]] if ip==0x8e2 else ['update'])
                return_to_caller(u,2 if ip==0x8e2 else 0);return
        raise ValueError(f'unexpected options consumer {pair}')
    def run_option(self,bgm,se,row,key):
        u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data)
        resident=bytearray(256);resident[15]=1;resident[58]=3;resident[59]=2;resident[16]=bgm;resident[24]=se;resident[73]=1
        u.mem_write(0x90000,bytes(resident));self.write(0x1a64,'HH',0,0x9000)
        self.write(0x107,'B',1);self.write(0x1a6d,'B',1);self.write(0x9b,'B',row)
        self.write(0x2710,'H',key);self.write(0x1a6a,'H',0x497)
        self.calls=[];self.error=None;self.done=False
        for reg,value in [(UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),
                          (UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
        u.mem_write(0x7f000,struct.pack('<H',0xff00));u.emu_start(self.cs*16+0x912,0x10ffff,count=20000)
        if self.error:raise self.error
        assert self.done and u.reg_read(UC_X86_REG_SP)==0xf002
        return [u.mem_read(0x90010,1)[0],u.mem_read(0x90018,1)[0]],self.calls

class Entry(MaineMain):
    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
        if pair==(0xcc7,0x7cc):self.initialized+=1
        if pair==(0xcc7,0x33a):self.modes.append(list(struct.unpack('<HH',u.mem_read(0x70000+sp+4,4))))
        if pair==(0xcc7,0x4a2):raise ValueError('TH04 MAINE entry unexpectedly loaded SE')
        super().body(u,address)
    def check(self,character,rank,end):
        self.initialized=0;self.modes=[];self.run(character,rank,end)
        assert self.initialized==1 and self.modes==[[0,0]]
        return self.flow

class MaineSE(MaineBase):
    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16)
        if pair==(0xcc7,0xff00):self.done=True;u.emu_stop();return
        if pair[0]==0xcc7 and 0x924<=pair[1]<0x9b6:return
        if pair==(0,0x32c6):return_to_caller(u,2);return
        raise ValueError(f'unexpected MAINE SE consumer {pair}')
    def invoke(self,ip,arg=None):
        u=self.u;cs=self.load+0xcc7;self.done=False;self.error=None
        for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),
                          (UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
        values=[0xff00,cs]+([] if arg is None else [arg])
        u.mem_write(0x7f000,struct.pack('<'+'H'*len(values),*values));u.emu_start(cs*16+ip,0x10ffff,count=10000)
        if self.error:raise self.error
        assert self.done and u.reg_read(UC_X86_REG_SP)==0xf000+2*len(values)
    def state(self):return self.read(0x5a0,'B')[0],*self.read(0x600,'BB')
    def action(self,kind,value):
        if kind in (2,5):self.invoke(0x924)
        if kind in (0,2):self.invoke(0x930,value)
        if kind in (1,2,6):self.invoke(0x96a)

def rows(path):return [r.split() for r in path.read_text().splitlines()]
def option_calls(trace):
    result=[]
    for r in trace:
        kind=int(r[0]);action,value=int(r[3]),int(r[4])
        if kind==2:result.append(['configure',int(r[6]),int(r[7])])
        elif kind==3:
            if action==2:result.extend([['reset'],['play',value],['update']])
            elif action==3:result.append(['command',value])
            elif action==4:result.append(['load',value,r[5]])
            else:raise ValueError('unreviewed option audio event')
    return result

def controls(args,scenes):
    options=[];entries=[];states=0
    for load in (0x1000,0x2000):
        original=Options(args.op,args.op_decoded,load);results=[]
        for case in sorted((scenes/'options').glob('*/case.txt'),key=lambda p:int(p.parent.name)):
            bgm,se,row,key,wanted_bgm,wanted_se=map(int,case.read_text().split())
            observed,calls=original.run_option(bgm,se,row,key)
            assert observed==[wanted_bgm,wanted_se],(case,observed)
            assert calls==option_calls(rows(case.parent/'sound.txt')),(case,calls)
            results.append([bgm,se,row,key,observed,calls])
        assert len(results)==216
        options.append(results)
        entry=Entry(args.maine,args.maine_decoded,load)
        entries.append([[c,r,e,entry.check(c,r,e)] for c in range(2) for r in range(4) for e in (0,253,254,255)])
    assert options[0]==options[1] and entries[0]==entries[1]
    paths=sorted((scenes/'menus').glob('*/sound.txt'))+sorted((scenes/'score').glob('*/sound.txt'))
    assert len(paths)==32
    for load in (0x1000,0x2000):
        controller=OpControl(args.op,args.op_decoded,load)
        for path in paths:
            actions=[];checks=[];program=None;se_original=None;lifetime=[]
            def finish():
                nonlocal states
                if program is None:return
                initial=[0,0,0,96,255,0,bytes(13)]
                answer=controller.run(0,(initial,actions)).decode().splitlines()
                history=[[0,0,0,96,255,0,bytes(13).hex()]]+[r.split()[2:] for r in answer if r.startswith('STATE ')]
                for at,expected in checks:
                    actual=[str(v) for v in history[at]]
                    assert actual==expected,(path,program,at,actual,expected)
                    states+=1
            for r in rows(path):
                kind,p,g,a,value=map(int,r[:5])
                if kind==0:
                    finish();actions=[];checks=[];program=p;lifetime.append([p,g])
                    if p==1:
                        se_original=MainControl(args.main.read_bytes(),load);se_original.write(0x8f4,'B',0)
                    elif p==2:
                        se_original=MaineSE(args.maine,args.maine_decoded,load)
                        se_original.write(0x5a0,'B',0);se_original.write(0x600,'BB',255,0)
                    else:se_original=None
                if kind==1:
                    finish();program=None;continue
                assert program==p and len(r)==18,(path,r)
                checks.append((len(actions),r[10:17]))
                if se_original:
                    assert list(se_original.state())==list(map(int,[r[11],r[14],r[15]])),(path,'own SE',r)
                def action(op,x=0,b=0,name=bytes(13)):
                    actions.append([op,x,b,0,0,255 if op==0 else 0,name])
                if kind==2:
                    action(0,int(r[6]),int(r[7]))
                    if se_original:se_original.write(0x8f4 if p==1 else 0x5a0,'B',2 if int(r[7])==2 else 0)
                elif kind==3:
                    assert not (p==2 and a==4 and value==0xb00),("MAINE entry must not load EFS",path)
                    if a==0:action(3,value)
                    elif a in (1,6):action(4,1)
                    elif a==2:action(2);action(3,value);action(4,1)
                    elif a==3:action(1,value)
                    elif a==4:
                        name=r[5].encode();assert len(name)<=8
                        action(5,value,name=name+bytes(13-len(name)))
                    elif a==5:action(2)
                    else:raise ValueError('unreviewed sound action')
                    if se_original:
                        if p==1:se_original.action(a,value)
                        else:se_original.action(a,value)
            finish()
            if path.parent.parent.name=='menus':assert lifetime==[[0,1],[2,3],[0,4],[1,5]],lifetime
            elif 'p4' not in path.parent.name and 'p3' not in path.parent.name:
                assert lifetime==[[0,1],[1,2],[2,3],[0,4],[1,5]],lifetime
    return dict(options=options[0],maine_entry=entries[0],control_snapshots=states,scene_traces=len(paths))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('op','op-decoded','maine','maine-decoded','main','hdi','font','exe','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--reference-dir',type=Path)
    args=p.parse_args();root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root)
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);require_elf_x86_64(args.exe)
    command=[str(args.exe.resolve()),'--hdi',str(args.hdi.resolve()),'--font-bmp',str(args.font.resolve()),'--mute','--pmd-driver','none','--sound-scene-checks',str(out/'scenes')]
    with (out/'launch.log').open('wb') as log:
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
    observed=controls(args,out/'scenes');(out/'original.json').write_text(json.dumps(observed,indent=2)+'\n')
    assert source_manifest(root)[0]==manifest
    outputs={p.relative_to(out/'scenes').as_posix():sha(p) for p in sorted((out/'scenes').rglob('*')) if p.is_file()}
    reference_sha=None
    if args.reference_dir:
        previous=json.loads((args.reference_dir/'receipt.json').read_text())
        assert previous['passed'] and previous['source_manifest']==manifest
        assert previous['outputs']==outputs,"complete cross-host frontend outputs differ"
        assert previous['original_sha256']==sha(out/'original.json')
        for name,digest in previous['outputs'].items():
            assert sha(args.reference_dir/'scenes'/name)==digest
        reference_sha=sha(args.reference_dir/'receipt.json')
    receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,source_files=len(files),
        command=command,exe_sha256=sha(args.exe),target_sha256={n:sha(getattr(args,n)) for n in ('op','main','maine')},
        hdi_sha256=sha(args.hdi),font_sha256=sha(args.font),original_cpu_reexecuted=True,loads=[4096,8192],
        option_cases=len(observed['options']),maine_entry_cases=len(observed['maine_entry']),control_snapshots=observed['control_snapshots'],
        original_sha256=sha(out/'original.json'),outputs=outputs,scope=__doc__)
    receipt['reference_receipt_sha256']=reference_sha
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Sound scenes PASS',receipt['option_cases'],'OP options;',receipt['maine_entry_cases'],'MAINE entries;',receipt['control_snapshots'],'control snapshots')
if __name__=='__main__':main()
