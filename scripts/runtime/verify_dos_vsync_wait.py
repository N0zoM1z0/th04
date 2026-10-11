#!/usr/bin/env python3
"""Compare complete original and linked DOS VSync wait consumers.

GDC status and Count1 word operands are explicit instruction-boundary stimuli.
The pinned Unicorn unrestricted MEM_READ hook has a verified far-return issue,
so this reader leaves it disabled. Additional controls inject
actual original/candidate IRQ bodies with real IRET frames. No wait opcode or
return is replaced. This is not measured PC-98 polling/ISR latency.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,re,struct
import capstone,unicorn
from unicorn.x86_const import *
from verify_dos_vsync_lifecycle import original,candidate
from lib.omf import describe_omf
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REGS={'AX':UC_X86_REG_AX,'BX':UC_X86_REG_BX,'CX':UC_X86_REG_CX,'DX':UC_X86_REG_DX,
      'SI':UC_X86_REG_SI,'DI':UC_X86_REG_DI,'BP':UC_X86_REG_BP,'DS':UC_X86_REG_DS,
      'ES':UC_X86_REG_ES,'SS':UC_X86_REG_SS,'SP':UC_X86_REG_SP,'FLAGS':UC_X86_REG_EFLAGS}
SEEDS={'AX':0x5aa5,'BX':0xa55a,'CX':0x1357,'DX':0x2468,'SI':0x98ef,'DI':0x5678,
       'BP':0xabcd,'ES':0x4b00,'SS':0x7000,'SP':0xf000,'FLAGS':0x202}
PRESERVED=('SI','DI','BP','DS','ES','SS')
def layout_wait(layout,entry,size):
    l=dict(layout);l['wait']=entry;l['wait_size']=size
    cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_16);cs.detail=True
    span=l['body'][l['cs']*16+entry:l['cs']*16+entry+size];ins=list(cs.disasm(span,entry))
    assert sum(i.size for i in ins)==size and any(i.mnemonic=='retf'for i in ins)
    reads=[]
    for i in ins:
        for op in i.operands:
            if op.type==capstone.x86.X86_OP_MEM and op.mem.disp==l['count1'] and not op.mem.base and not op.mem.index:
                assert op.size==2;reads.append(i.address)
    l['wait_reads']=sorted(set(reads));l['wait_instructions']=[f'{i.address:04x} {i.mnemonic} {i.op_str}'for i in ins]
    return l

def original_wait(artifact):
    l=original(artifact);pattern=b'\x80\x3e'+struct.pack('<H',l['owner'])+b'\x00';b=l['body']
    hits=[i for i in range(len(b)-7)if b[i:i+5]==pattern and b[i+7:i+9]==b'\xeb\x00'];assert len(hits)==1
    l=layout_wait(l,hits[0],38);assert len(l['wait_reads'])==2 and l['wait_instructions'][-1].endswith('retf ')
    return l

def linked_wait(exe,mp,source,receipt):
    l=candidate(exe,mp,source);text=mp.read_text()
    symbols=set(re.findall(r'(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?VSYNC_WAIT\s*$',text));assert len(symbols)==1
    seg,entry=(int(x,16)for x in symbols.pop())
    build=json.loads(receipt.read_text());owners=[]
    def walk(value):
        if isinstance(value,dict):
            if value.get('source')=='src/shared/hardware/vsync_wait.cpp':owners.append(value)
            for child in value.values():walk(child)
        elif isinstance(value,list):
            for child in value:walk(child)
    walk(build);assert len(owners)==1;record=owners[0];objects=record.get('objects')or[record['object']];assert len(objects)==1
    obj=receipt.parent/'source'/objects[0];assert sha(obj)==record['object_sha256']
    omf=describe_omf(obj.read_bytes());assert omf['valid'] and 'TC86 Borland C++ 4.02' in omf['translator_comments']
    assert record['source_sha256']==sha(source.with_name('vsync_wait.cpp'))
    spans=re.findall(r'(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE\b.*\bM='+re.escape(omf['module_name'])+r'\s',text)
    l['wait_object_sha256']=sha(obj);l['wait_module']=omf['module_name'];l['build_receipt_sha256']=sha(receipt)
    spans=[tuple(int(x,16)for x in row)for row in spans if int(row[2],16)];assert len(spans)==1
    cs,off,size=spans[0];assert cs==seg and off==entry
    l['irq_cs']=l['cs'];l['cs']=seg;l=layout_wait(l,entry,size)
    aliases=set(re.findall(r'(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?_vsync_OwnerMask\s*$',text))
    if aliases:assert aliases=={(f'{l["dg"]:04X}',f'{l["owner"]:04X}')}
    l['owner_public_alias']=bool(aliases)
    return l

def execute(l,load,owner,initial,change,irq=None,owner_after=None):
    u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);u.mem_map(0,0x110000)
    image=bytearray(l['body'])
    for at in l['sites']:struct.pack_into('<H',image,at,(struct.unpack_from('<H',image,at)[0]+load)&65535)
    u.mem_write(load*16,bytes(image));cs=load+l['cs'];ds=load+l['dg'];base=ds*16;stop=cs*16+0xff00
    u.mem_write(base+l['owner'],bytes([owner]));u.mem_write(base+l['count1'],struct.pack('<H',initial));u.mem_write(base+l['count2'],struct.pack('<H',0xbeef));u.mem_write(base+l['proc'],bytes(4))
    if irq:u.mem_write(base+l['inc'],struct.pack('<H',irq[0]));u.mem_write(base+l['acc'],struct.pack('<H',irq[1]))
    seeds=dict(SEEDS,DS=ds)
    for name,value in seeds.items():u.reg_write(REGS[name],value)
    u.reg_write(UC_X86_REG_CS,cs);u.mem_write(0x7f000,struct.pack('<HH',0xff00,cs))
    counts=[initial,initial,initial,change];signals=[0x21,0x60,0x81,0x40,0xa1]
    reads=[];ports=[];writes=[];trace=[];done=False;stage='wait';pending=None;resume=False;irq_return=None;pulses=0;irq_steps=[];irq_landing=None;irq_return_frames=[];changed_owner=False
    def code(cpu,address,size,unused):
        nonlocal done,pending,resume,irq_landing,changed_owner
        trace.append((stage,cpu.reg_read(UC_X86_REG_CS)-load,address-cpu.reg_read(UC_X86_REG_CS)*16,bytes(cpu.mem_read(address,size)).hex()))
        if stage=='irq' and address==irq_return:
            irq_landing=(cpu.reg_read(UC_X86_REG_CS),address-cpu.reg_read(UC_X86_REG_CS)*16);cpu.emu_stop();return
        if stage=='wait' and address==stop:done=True;cpu.emu_stop();return
        if stage=='wait' and address-cs*16 in l['wait_reads']:
            assert owner
            if owner_after is not None and len(reads)==1 and not changed_owner:
                cpu.mem_write(base+l['owner'],bytes([owner_after]));changed_owner=True
            if irq and reads:
                if resume:resume=False
                else:pending=address;cpu.emu_stop();return
            if not irq:
                assert len(reads)<len(counts),'Count1 stimulus exhausted'
                u.mem_write(base+l['count1'],struct.pack('<H',counts[len(reads)]))
            reads.append(struct.unpack('<H',cpu.mem_read(base+l['count1'],2))[0])
    def memory_write(cpu,access,address,size,value,unused):
        if base+l['count1']<=address<base+l['count2']+2 or address==base+l['acc'] or address==base+l['owner']:
            writes.append((stage,address-base,size,value))
    def incoming(cpu,port,size,unused):
        nonlocal changed_owner
        assert stage=='wait' and port==0xa0 and size==1 and len(ports)<len(signals),'unexpected GDC read'
        if owner_after is not None and not ports:
            cpu.mem_write(base+l['owner'],bytes([owner_after]));changed_owner=True
        value=signals[len(ports)];ports.append(('in',port,size,value));return value
    def outgoing(cpu,port,size,value,unused):
        assert stage=='irq' and (port,size,value)in ((0,1,0x20),(0x64,1,0x20));ports.append(('out',port,size,value))
    u.hook_add(unicorn.UC_HOOK_CODE,code);u.hook_add(unicorn.UC_HOOK_MEM_WRITE,memory_write)
    u.hook_add(unicorn.UC_HOOK_INSN,incoming,None,1,0,UC_X86_INS_IN);u.hook_add(unicorn.UC_HOOK_INSN,outgoing,None,1,0,UC_X86_INS_OUT)
    u.emu_start(cs*16+l['wait'],0x10ffff,count=10000)
    while pending is not None and not done:
        assert irq and pulses<5;pulses+=1;address=pending;pending=None
        retcs=u.reg_read(UC_X86_REG_CS);retip=address-retcs*16;flags=u.reg_read(UC_X86_REG_EFLAGS)&65535;sp=u.reg_read(UC_X86_REG_SP);ss=u.reg_read(UC_X86_REG_SS)
        assert flags&0x200;u.mem_write(ss*16+sp-6,struct.pack('<HHH',retip,retcs,flags));u.reg_write(UC_X86_REG_SP,sp-6);u.reg_write(UC_X86_REG_EFLAGS,flags&~0x300)
        irq_cs=load+l.get('irq_cs',l['cs']);u.reg_write(UC_X86_REG_CS,irq_cs);stage='irq';irq_return=address
        u.emu_start(irq_cs*16+l['irq'],0x10ffff,count=1000)
        # Pinned Unicorn's paused IP is the low linear address, not guest IP.
        # Gate the actual CODE-hook landing/CS and real IRET stack unwind.
        assert irq_landing==(retcs,retip) and u.reg_read(UC_X86_REG_CS)==retcs and u.reg_read(UC_X86_REG_SP)==sp
        paused_ip=u.reg_read(UC_X86_REG_IP);assert paused_ip==(address&65535)
        irq_return_frames.append(dict(cs=retcs,logical_ip=retip,paused_api_ip=paused_ip,sp=sp,flags=u.reg_read(UC_X86_REG_EFLAGS)&65535))
        irq_landing=None

        one=struct.unpack('<H',u.mem_read(base+l['count1'],2))[0];two=struct.unpack('<H',u.mem_read(base+l['count2'],2))[0];acc=struct.unpack('<H',u.mem_read(base+l['acc'],2))[0];irq_steps.append([one,two,acc])
        stage='wait';irq_return=None;resume=True;u.emu_start(address,0x10ffff,count=10000)
    assert done and u.reg_read(UC_X86_REG_SP)==0xf004,dict(done=done,load=load,owner=owner,initial=initial,change=change,irq=irq,reads=reads,ports=ports,pending=pending,pulses=pulses,ip=u.reg_read(UC_X86_REG_IP),cs=u.reg_read(UC_X86_REG_CS),sp=u.reg_read(UC_X86_REG_SP),stop=stop,stack=bytes(u.mem_read(0x7f000,4)).hex(),trace_prefix=trace[:38])
    regs={name:u.reg_read(reg)&65535 for name,reg in REGS.items()}
    assert all(regs[name]==seeds[name]for name in PRESERVED)
    one=struct.unpack('<H',u.mem_read(base+l['count1'],2))[0];two=struct.unpack('<H',u.mem_read(base+l['count2'],2))[0];mask=u.mem_read(base+l['owner'],1)[0];assert mask==(owner if owner_after is None else owner_after)
    assert owner_after is None or changed_owner
    assert not any(row[0]=='wait'for row in writes),'wait writes counter/owner state'
    observation=dict(counts=[one,two],owner=mask,counter_reads=reads,ports=ports,registers=regs,pulses=pulses,irq_steps=irq_steps,irq_return_frames=irq_return_frames,writes=writes,trace=trace)
    def require(ok,reason):
        if not ok:raise AssertionError(dict(reason=reason,observed=observation))
    if irq:
        require(owner and pulses and one==(initial+1)&65535 and two==0xbef0,'owned IRQ waiter failed to consume one Count1 change')
        assert ports==[('out',0,1,0x20),('out',0x64,1,0x20)]*pulses
        acc=irq[1];n=0;expected=[]
        for _ in range(pulses):summed=acc+irq[0];acc=summed&65535;n+=int(summed<65536);expected.append([(initial+n)&65535,(0xbeef+n)&65535,acc])
        assert n==1 and irq_steps==expected
    elif owner:require(reads==counts and one==change and two==0xbeef and not ports,'owned waiter must use Count1 inequality without GDC I/O')
    else:assert not reads and one==initial and two==0xbeef and [row[3]for row in ports]==signals
    return observation

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--artifact',choices=('main','op','maine'),required=True)
    for name in ('candidate-exe','candidate-map','candidate-source','candidate-receipt','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=False);target=original_wait(a.artifact);compiled=linked_wait(a.candidate_exe,a.candidate_map,a.candidate_source,a.candidate_receipt)
    rows=[];mismatches=[];register_differences={}
    cases=[(load,owner,initial,(initial+step)&65535,None,None)for load,owner,initial,step in itertools.product((0x1000,0x3333),(0,1,251,255),(0,1,4,100,65534,65535),(1,256,-1))]
    cases += [(load,owner,initial,0,irq,None)for load,owner,initial,irq in itertools.product((0x1000,0x3333),(251,255),(0,65535),((0,0),(13311,60000),(65535,3)))]
    cases += [(load,owner,initial,(initial+1)&65535,None,0 if owner else 255)for load,owner,initial in itertools.product((0x1000,0x3333),(0,251),(0,65535))]
    for load,owner,initial,change,irq,owner_after in cases:
        expected=execute(target,load,owner,initial,change,irq,owner_after)
        try:
            actual=execute(compiled,load,owner,initial,change,irq,owner_after)
            keys=('counts','owner','counter_reads','ports','pulses','irq_steps');ok=all(expected[k]==actual[k]for k in keys)
            differences={name:[value,actual['registers'][name]]for name,value in expected['registers'].items()if actual['registers'][name]!=value}
            for name in differences:register_differences[name]=register_differences.get(name,0)+1
        except AssertionError as e:
            detail=e.args[0]if e.args else 'postcondition failed'
            actual=dict(error=detail.get('reason','postcondition failed'),observed=detail.get('observed'))if isinstance(detail,dict)else dict(error=str(detail))
            ok=False;differences={}
        rows.append(dict(load=f'{load:04x}',owner=owner,initial=initial,change=change,irq=irq,owner_after=owner_after,equal=ok,original=expected,candidate=actual,raw_register_differences=differences))
        if not ok:mismatches.append(len(rows)-1)
    lib=Path(unicorn.__file__).parent/'lib/libunicorn.so'
    j=dict(passed=not mismatches,artifact=a.artifact,cases=len(rows),irq_cases=sum(bool(row['irq'])for row in rows),owner_change_cases=sum(row['owner_after']is not None for row in rows),source_sha256=sha(Path(__file__)),target={k:v for k,v in target.items()if k not in ('body','sites')},candidate={k:v for k,v in compiled.items()if k not in ('body','sites')},unicorn_version=unicorn.__version__,unicorn_library_sha256=sha(lib),wait_source_sha256=sha(a.candidate_source.with_name('vsync_wait.cpp')),register_differences=register_differences,rows=rows,mismatches=mismatches,scope='Complete original/compiled far wait consumer: count/owner/ordered I/O, Pascal stack and callee-saved registers. Explicit counter/status stimuli plus actual ISR/IRET injection at two relocated loads. Raw register differences retain recorded artifact DS layout and AX/BX/CX/DX/FLAGS incidental returns; no full register/byte identity or physical polling/IRQ timing claim.')
    (a.output_dir/'receipt.json').write_text(json.dumps(j,indent=2)+'\n');print('DOS VSYNC WAIT',a.artifact,len(rows),'cases',len(mismatches),'differences',register_differences,flush=True)
    return int(not j['passed'])
if __name__=='__main__':raise SystemExit(main())
