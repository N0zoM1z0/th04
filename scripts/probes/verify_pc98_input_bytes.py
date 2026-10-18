#!/usr/bin/env python3
"""Verify live byte/joystick sampling against pinned original MAIN instructions.

Run in the repository's bounded serial service. BIOS Shift and ready OPNA pins
are explicit controls; physical bus/CPU timing and whole-game fidelity remain
outside this functional Oracle. An optional earlier header demonstrates the
keyboard-only API gap. Four compiled semantic defects are always exercised.
"""


def main():
    import argparse,hashlib,json,shutil
    from pathlib import Path
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-root',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--before-header',type=Path)
    parser.add_argument('--compiler',type=Path,default=Path('/usr/bin/c++'))
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2];n=args.native_root.resolve();r=args.output_dir.resolve()
    if r.exists() or not r.is_relative_to(root/'.analysis'):
        parser.error('Use a fresh private output directory below .analysis')
    current=n/'port64/pc98_input.hpp'
    if not current.is_file() or not args.compiler.resolve().is_file():
        parser.error('Native header and compiler must exist')
    if args.before_header and (not args.before_header.is_file() or 'std::function<bool()> joystick_enabled' in args.before_header.read_text()):
        parser.error('The optional baseline must be the earlier keyboard-only ByteSource header')
    digest=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
    header_identity=digest(current);compiler_identity=digest(args.compiler.resolve())
    r.mkdir(parents=True)
    probe=Path(__file__).with_name('pc98_input_byte_probe.cpp')
    shutil.copy2(probe,r/'consumer.cpp')
    if args.before_header:
        (r/'before').mkdir();shutil.copy2(args.before_header,r/'before/pc98_input.hpp')
    import hashlib
    import json
    import sys
    from pathlib import Path

    sys.path.insert(0,str(root/'.analysis/reconstruction/probes/native-bgm-title-v1450/unicorn-2.1.4'))
    import unicorn
    from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_INSN,UC_HOOK_MEM_READ
    import unicorn.x86_const as x
    from unicorn.unicorn_py3.unicorn import uclib
    sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
    engine=Path(uclib._name).resolve()
    assert unicorn.__version__=='2.1.4' and sha(engine)=='ddb196ec82b52e502c18e4a34478bf7b9f61c83c2ebaa95c74d8ded45a95da9c'
    target=root/'.analysis/targets/th04/main.exe'
    assert sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
    module=target.read_bytes()[6144:]
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,module)
    u.reg_write(x.UC_X86_REG_DS,0x2134);u.reg_write(x.UC_X86_REG_SS,0x7000)
    initial_if=True
    state={};counts=dict(key_reads=0,shift_queries=0,enabled_queries=0,pin_reads=0,masked_bus_accesses=0)
    def point(name):
        action=int.from_bytes(u.mem_read(0x21340+0x3974,2),'little')
        shift=u.mem_read(0x21340+0x3976,1)[0]
        state['trace'].append(f'{name}:{action}:{shift},')
    def code(cpu,address,size,_):
        if address==0x130e0+0x6c4:point('B')
    def key(cpu,access,address,size,value,_):
        assert size==1 and bool(cpu.reg_read(x.UC_X86_REG_EFLAGS)&0x200)==initial_if
        counts['key_reads']+=1;point('K'+str(address-0x52a))
    def enabled(cpu,access,address,size,value,_):
        assert size==2 and bool(cpu.reg_read(x.UC_X86_REG_EFLAGS)&0x200)==initial_if
        counts['enabled_queries']+=1;point('E')
    def bios(cpu,number,_):
        assert number==0x18 and cpu.reg_read(x.UC_X86_REG_AH)==2
        assert bool(cpu.reg_read(x.UC_X86_REG_EFLAGS)&0x200)==initial_if
        counts['shift_queries']+=1;point('H');cpu.reg_write(x.UC_X86_REG_AL,state['shift'])
    def inp(cpu,port,size,_):
        assert size==1 and not cpu.reg_read(x.UC_X86_REG_EFLAGS)&0x200
        counts['masked_bus_accesses']+=1
        if port==0x188:return 0
        assert port==0x18a and state['register']==14
        counts['pin_reads']+=1;point('J');return state['pins']
    def outp(cpu,port,size,value,_):
        assert size==1 and not cpu.reg_read(x.UC_X86_REG_EFLAGS)&0x200
        counts['masked_bus_accesses']+=1
        if port==0x188:state['register']=value
        else:assert port==0x18a and state['register']==15 and value==0x80
    u.hook_add(UC_HOOK_CODE,code)
    u.hook_add(UC_HOOK_MEM_READ,key,None,0x52a,0x533)
    u.hook_add(UC_HOOK_MEM_READ,enabled,None,0x21340+0x39a,0x21340+0x39b)
    u.hook_add(UC_HOOK_INTR,bios)
    u.hook_add(UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN)
    u.hook_add(UC_HOOK_INSN,outp,None,1,0,x.UC_X86_INS_OUT)
    def execute(op,keys,shift,on,pins):
        u.mem_write(0x52a,keys);u.mem_write(0x21340+0x39a,int(on).to_bytes(2,'little'))
        state.update(shift=shift,pins=pins,register=None,trace=[])
        u.reg_write(x.UC_X86_REG_CS,0x130e);u.reg_write(x.UC_X86_REG_SP,0xfffa)
        u.reg_write(x.UC_X86_REG_EFLAGS,0x202 if initial_if else 2);u.mem_write(0x7fffa,b'\x00\x00\x00\x90')
        u.emu_start(0x130e0+(0x6bc if op=='R' else 0x6c4),0x90000,count=1000)
        assert u.reg_read(x.UC_X86_REG_CS)==0x9000 and u.reg_read(x.UC_X86_REG_IP)==0
        assert bool(u.reg_read(x.UC_X86_REG_EFLAGS)&0x200)==initial_if
        action=int.from_bytes(u.mem_read(0x21340+0x3974,2),'little')
        actual_shift=u.mem_read(0x21340+0x3976,1)[0]
        return f'{action} {actual_shift} {int(on)} {pins if on else 255} '+''.join(state['trace'])+'\n'
    seed=bytearray(10);seed[3]=16;seed[7]=8;seed=bytes(seed)
    inputs=[];expected=[]
    def case(op,keys,shift,on,pins):
        for o,k,s,e,p in [('R',seed,0,False,255),(op,keys,shift,on,pins)]:
            inputs.append(f'{o} {k.hex()} {int(s)} {int(e)} {p}\n')
            expected.append(execute(o,k,s,e,p))
    for group in range(10):
        for value in range(256):
            keys=bytearray(10);keys[group]=value
            for op in ['R','S']:case(op,bytes(keys),value&1,False,255)
    for on in [False,True]:
        for pins in range(256):
            for shift in [0,1]:
                for op in ['R','S']:case(op,bytes(10),shift,on,pins)
    assert len(inputs)==len(expected)==14336
    for start,end in [(0x130e0+0x6bc,0x130e0+0x7c5),(0x3658,0x3676)]:
        assert bytes(u.mem_read(start,end-start))==module[start:end]
    assert counts['key_reads']==8*14336 and counts['shift_queries']==counts['enabled_queries']==14336
    assert counts['pin_reads']==1024
    (r/'cases.input').write_text(''.join(inputs));(r/'oracle.stdout').write_text(''.join(expected))
    report=dict(passed=True,controlled_cases=7168,target_calls=14336,counts=counts,
        main_sha256=sha(target),engine_sha256=sha(engine),unicorn_version=unicorn.__version__,
        sampler_extent_sha256=hashlib.sha256(module[0x130e0+0x6bc:0x130e0+0x7c5]).hexdigest(),
        helper_extent_sha256=hashlib.sha256(module[0x3658:0x3676]).hexdigest(),
        input_sha256=sha(r/'cases.input'),output_sha256=sha(r/'oracle.stdout'),
        scope='Unchanged original MAIN reset/sense/helper instructions under explicit BIOS Shift and ready OPNA pin controls. '
              'Eight BIOS bytes, Shift query, enable read and optional masked pin transaction preserve original order and intermediate latch values. '
              'Only ten BIOS bytes and one enable word have narrow read hooks. This is real-mode functional instruction evidence, '
              'not original V86 IRQ scheduling, physical OPNA/CPU timing, host joystick support or complete-game acceptance.')
    (r/'oracle.json').write_text(json.dumps(report,indent=2)+'\n')
    print('ORIGINAL LIVE BYTE/JOYSTICK ORACLE PASS',len(inputs),counts,flush=True)
    # Caller IF belongs to the external CPU owner. The original helper must
    # restore both IF0 and IF1, while its declared OPNA accesses remain masked.
    if_controls=[]
    for op in ['R','S']:
        for shift in [0,1]:
            for on in [False,True]:
                for pins in [0xfd,0xff]:
                    values=[]
                    for initial_if in [False,True]:
                        execute('R',seed,0,False,255)
                        values.append(execute(op,bytes(10),shift,on,pins))
                    assert values[0]==values[1]
                    if_controls.append(dict(operation=op,shift=shift,enabled=on,pins=pins))
    primary=json.loads((r/'oracle.json').read_text())
    primary['caller_if_preservation_controls']=if_controls
    primary['additional_target_calls']=64
    (r/'oracle.json').write_text(json.dumps(primary,indent=2)+'\n')
    import hashlib
    import json
    import shutil
    import subprocess
    from pathlib import Path

    sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
    assert json.loads((r/'oracle.json').read_text())['passed']
    expected=(r/'oracle.stdout').read_bytes().splitlines();payload=(r/'cases.input').read_bytes()
    header=(n/'port64/pc98_input.hpp').read_text()
    shift='        sample.shift=source.shift();shift_=sample.shift;\n'
    a=header.index(shift);b=header.index('        return sample;',a)
    body=header[a:b]
    new='''        if(source.joystick_enabled) {
                sample.joystick_enabled=source.joystick_enabled();
                const auto pins=source.joystick_pins();
                if(sample.joystick_enabled) {
                    sample.joystick_pins=pins;
                    actions_|=std::uint16_t((~sample.joystick_pins)&0x3f);
                }
            }
    '''
    variants={
        'current':(header,True),
        'shift-after-joystick':(header[:a]+body.replace(shift,'')+shift+header[b:],True),
        'unmasked-pins':(header.replace('actions_|=std::uint16_t((~sample.joystick_pins)&0x3f);','actions_|=std::uint16_t(std::uint8_t(~sample.joystick_pins));',1),True),
        'read-disabled-pins':(header[:a]+shift+new+header[b:],True),
        'overwrite-latch':(header.replace('actions_|=std::uint16_t((~sample.joystick_pins)&0x3f);','actions_=std::uint16_t((~sample.joystick_pins)&0x3f);',1),True),
    }
    if args.before_header:variants={'before':((r/'before/pc98_input.hpp').read_text(),False),**variants}
    build=r/'consumers';build.mkdir();results={};commands=[]
    compiler=args.compiler.resolve()
    for name,(text,feature) in variants.items():
        d=build/name;d.mkdir();(d/'pc98_input.hpp').write_text(text)
        exe=d/'consumer';cmd=[str(compiler),'-std=c++17','-O1','-Wall','-Wextra','-Werror',
            '-fsanitize=undefined,bounds','-fno-sanitize-recover=all','-I',str(d)]
        if feature:cmd+=['-DJOYSTICK_BYTE_SOURCE']
        cmd+=[str(r/'consumer.cpp'),'-o',str(exe)]
        with (d/'compile.log').open('xb') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
        commands.append(cmd)
        run=subprocess.run([str(exe)],input=payload,capture_output=True,check=True)
        assert not run.stderr
        (d/'stdout').write_bytes(run.stdout);actual=run.stdout.splitlines();assert len(actual)==len(expected)==14336
        state_mismatches=sum(x.split()[:2]!=y.split()[:2] for x,y in zip(actual,expected,strict=True))
        trace=sum(x!=y for x,y in zip(actual,expected,strict=True))
        results[name]=dict(exit=run.returncode,state_mismatched_rows=state_mismatches,full_mismatched_rows=trace,
            header_sha256=sha(d/'pc98_input.hpp'),program_sha256=sha(exe),stdout_sha256=sha(d/'stdout'))
    assert results['current']['full_mismatched_rows']==0
    if args.before_header:assert results['before']['state_mismatched_rows']>0
    assert all(results[name]['full_mismatched_rows']>0 for name in variants if name not in ['before','current'])
    report=dict(passed=True,cases=7168,rows=14336,variants=results,commands=commands,
        current_header_sha256=sha(n/'port64/pc98_input.hpp'),compiler_path=str(compiler),compiler_sha256=sha(compiler),
        scope='Original target instructions provide all expected latch/Shift values and intermediate callback ordering. '
              'The pre-change byte API cannot consume joystick state. Current optional enable/pin callbacks preserve Shift-before-joystick order, '
              'skip disabled bus reads, mask low six bits and OR the game latch. Four compiled exit-zero defects reject. '
              'No hardware joystick producer, original CPU IRQ timing, full campaign or exact promotion is accepted.')
    (r/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print('LIVE BYTE SOURCE PASS',len(expected),{name:(v['state_mismatched_rows'],v['full_mismatched_rows']) for name,v in results.items()},flush=True)
    assert digest(current)==header_identity and digest(args.compiler.resolve())==compiler_identity
    comparison=json.loads((r/'comparison.json').read_text())
    comparison['producer_sources']={str(Path(__file__).resolve()):digest(Path(__file__)),str(probe):digest(probe)}
    comparison['native_root']=str(n)
    (r/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
