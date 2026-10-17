#!/usr/bin/env python3
"""Capture sparse original MAIN live-font/video witnesses with ordinary keys.

Use a fresh output below .analysis/runtime/candidates. The plan names an
attested initial HDI, boundary profile, font/video ABI receipts, selected
score-return points, and actual observed dialogue/Continue frame cues.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
import tomllib

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/probes')]
from lib.pc98 import parse_mz
from th04_demo_video import LAYOUT


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while data:=stream.read(1024*1024):h.update(data)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--timeout',type=int,default=1800)
    args=parser.parse_args();out=args.output_dir.resolve()
    if out.exists() or not out.is_relative_to(ROOT/'.analysis/runtime/candidates'):
        parser.error('use a fresh private capture directory')
    resource.setrlimit(resource.RLIMIT_AS,(1536*1024*1024,1536*1024*1024))
    assert len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=19, 'launch with taskset and nice'
    plan=json.loads(args.plan.read_text());inputs={str(args.plan.resolve()):sha(args.plan)}
    def pin(name):
        row=plan[name];path=Path(row['path']).resolve()
        assert sha(path)==row['sha256'],(name,'identity drift')
        inputs[str(path)]=row['sha256'];return path
    image_source=pin('initial_hdi');font_source=pin('font_bmp')
    emulator_path=pin('emulator_receipt');emulator=json.loads(emulator_path.read_text())
    binary=Path(emulator['binary']);assert sha(binary)==emulator['binary_sha256'];inputs[str(binary)]=sha(binary)
    source=binary.parent.parent
    observer=ROOT/'scripts/probes/th04_demo_observer.inl'
    assert sha(observer)==emulator['observer_source_sha256']
    for name,key in [('src/cpu/core_normal.cpp','core_after_sha256'),('config.h','config_header_sha256')]:
        assert sha(source/name)==emulator[key];inputs[str(source/name)]=emulator[key]
    profile_path=pin('boundary_profile');profile=json.loads(profile_path.read_text())['original']
    # Kind2 terminates demo observers at frame3996. This ordinary capture
    # terminates only after the declared actual score-return checkpoints.
    profile['hooks']=[hook for hook in profile['hooks'] if hook[0]!=2]
    assert profile['dgroup']==0x2134 and profile['fields'][0]==['frame',0x538a,2]
    layout_path=pin('font_layout');layout=json.loads(layout_path.read_text())
    assert layout['passed'] and layout['emulator_sha256']==sha(binary)
    assert layout['layout']==dict(font_offset=312,font_bytes=528384,vga_size=535896)
    for name,digest in layout['source_inputs'].items():
        assert sha(Path(name))==digest;inputs[name]=digest
    video_layout_path=pin('video_layout');video_layout=json.loads(video_layout_path.read_text())
    assert video_layout['passed'] and video_layout['emulator_sha256']==sha(binary) and video_layout['layout']==LAYOUT
    for name,digest in video_layout.get('source_inputs',{}).items():
        assert sha(Path(name))==digest;inputs[name]=digest
    targets=tomllib.loads((ROOT/'config/targets.toml').read_text())['artifacts']
    for target in targets:
        if not target['id'].startswith('th04-'):continue
        path=ROOT/target['private_path'];data=path.read_bytes()
        assert len(data)==target['size'] and sha(path)==target['sha256'] and parse_mz(data).valid
        inputs[str(path)]=sha(path)
    main_path=ROOT/'.analysis/targets/th04/main.exe';mz=parse_mz(main_path.read_bytes())
    assert profile['module_size']==len(main_path.read_bytes())-6144
    assert profile['signature']==main_path.read_bytes()[6144:6176].hex()
    points=plan['points'];assert points and points==sorted(points) and len({tuple(p) for p in points})==len(points)
    assert all(type(s) is int and s in (0,1,2) and type(f) is int and 1<=f<=65535 for s,f in points)
    input_source=pin('stage_input') if 'stage_input' in plan else None
    if any(s==2 for s,_ in points):assert input_source is not None, 'Stage3 requires an actual physical input plan'
    if input_source is not None:
        lines=input_source.read_text(encoding='ascii').splitlines();header=lines[0].split()
        assert len(header)==4 and header[:2]==['TH04_STAGE_INPUT','1']
        input_stage,input_extent=map(int,header[2:]);assert input_stage in (0,2) and 0<input_extent<=65535
        assert len(lines)==input_extent+1 and points[-1]==[input_stage,input_extent], 'input extent must end at the final score sample'
        for frame,line in enumerate(lines[1:]):
            cells=list(map(int,line.split()));assert len(cells)==3 and cells[0]==frame and 0<=cells[1]<=63 and cells[2]==0
        for name in ['init_return']:
            point=profile['entries'][name];at=6144+point['segment']*16+point['offset'];assert main_path.read_bytes()[at:at+16].hex()==point['opcode']
        point=profile['stage3_gameover_guard'];at=6144+point['segment']*16+point['offset'];assert main_path.read_bytes()[at:at+16].hex()==point['opcode']
    cues=plan['ui_cues'];assert all(c['kind'] in ('dialogue','continue') for c in cues)
    if 'actor_dgroup' in plan:
        actor=plan['actor_dgroup']
        assert input_source is not None and actor==dict(stage=input_stage,extent=input_extent), 'actor stream must cover the declared input stage/extent'
        at=6144+0xaaf*16+0x1b3;opcode=main_path.read_bytes()[at:at+16].hex()
        assert opcode.startswith('a38a53'), 'original frame-store owner'
        profile['actor_boundary']=dict(segment=0xaaf,offset=0x1b3,opcode=opcode)
    out.mkdir(parents=True);capsule=out/'source';capsule.mkdir()
    # Freeze the imported observer closure, without mutating historical inputs.
    for directory in [ROOT/'scripts/probes',ROOT/'scripts/lib']:
        for path in directory.rglob('*.py'):
            if '__pycache__' not in path.parts:inputs[str(path)]=sha(path)
    for name in ['th04_demo_host_ram.py','th04_demo_video.py','th04_demo_dgroup.py','compare_th04_dos_demos.py']:
        shutil.copy2(ROOT/'scripts/probes'/name,capsule/name)
    shutil.copy2(ROOT/'scripts/probes/th04_sparse_font_gdb.py',capsule/'th04_ordinary_dgroup_gdb.py')
    if input_source is not None:
        shutil.copy2(ROOT/'scripts/probes/th04_sparse_input_gdb.py',capsule/'th04_sparse_input_gdb.py')
        shutil.copy2(input_source,capsule/'stage-inputs.txt')
    if 'actor_dgroup' in plan:
        shutil.copy2(ROOT/'scripts/probes/th04_sparse_actor_gdb.py',capsule/'th04_sparse_actor_gdb.py')
    keyboard=ROOT/'scripts/probes/th04_ordinary_keyboard.gdb';inputs[str(keyboard)]=sha(keyboard)
    text=keyboard.read_text()
    text=text.replace("sys.path.insert(0, os.environ['TH04_CLOCK_SOURCE_DIR'])", "sys.path.insert(0, "+repr(str(ROOT/'scripts'))+")\nsys.path.insert(0, "+repr(str(ROOT/'scripts/probes'))+")\nsys.path.insert(0, os.environ['TH04_CLOCK_SOURCE_DIR'])")
    # The historical adapter's regex is overescaped. Correct only this copy.
    text=text.replace("'\\\\bKBD_[A-Za-z0-9_]+\\\\b'", r"r'\bKBD_[A-Za-z0-9_]+\b'")
    text=text.replace("'/\\\\*.*?\\\\*/'", r"r'/\*.*?\*/'")
    old='active_dialog_frame = quit_frame if is_quit else continue_frame if is_continue else dialog_frame'
    assert text.count(old)==1
    text=text.replace(old,"active_dialog_frame = monitor.ui_point['frame']")
    # Keep a disabled clock watchpoint for later real UI waits.
    text=text.replace('clock.delete()','clock.enabled = False')
    if input_source is not None:
        anchor='    monitor = Monitor(out, ram)'
        assert text.count(anchor)==1
        text=text.replace(anchor,anchor+"\n    from th04_sparse_input_gdb import SparseInput\n    monitor.input_plan = SparseInput(monitor, globals())")
        anchor='    if process_recorder is not None and process_recorder.error:'
        assert text.count(anchor)==1
        text=text.replace(anchor,"    if monitor is not None and monitor.input_plan is not None and monitor.input_plan.pending:\n        monitor.input_plan.flush()\n        continue\n"+anchor)
    adapter=capsule/'keyboard.gdb';adapter.write_text(text)
    initial=out/'initial.hdi';shutil.copy2(image_source,initial)
    image=out/'execution.hdi';shutil.copy2(initial,image)
    shutil.copy2(font_source,out/'FREECG98.BMP')
    runtime=tomllib.loads((ROOT/'config/runtime.toml').read_text())
    config_source=ROOT/runtime['primary']['config'];assert sha(config_source)==runtime['primary']['config_sha256']
    inputs[str(config_source)]=sha(config_source)
    config=config_source.read_bytes();config=re.sub(rb'(?m)^cycles\s*=.*$',b'cycles = fixed 36000',config)
    config=config.replace(b'cputype = auto',b'cputype = pentium');(out/'dosbox-x.conf').write_bytes(config)
    (out/'profile.json').write_text(json.dumps(profile,indent=2)+'\n')
    shutil.copy2(args.plan,out/'font-plan.json')
    observer_profile=out/'observer-profile.txt'
    observer_profile.write_text(f"{profile['dgroup']:x} {profile['module_size']:x}\n"+profile['signature']+'\n'+str(len(profile['hooks']))+'\n'+''.join(f'{kind} {segment:x} {offset:x}\n' for kind,segment,offset in profile['hooks'])+str(len(profile['fields']))+'\n'+''.join(f'{offset:x} {size}\n' for _,offset,size in profile['fields']))
    debugger=Path(shutil.which('gdb')).resolve();inputs[str(debugger)]=sha(debugger)
    inputs[str(source/'include/keyboard.h')]=sha(source/'include/keyboard.h')
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',
        TH04_DEMO_PROFILE=str(observer_profile),TH04_DEMO_TRACE=str(out/'raw.txt'),TH04_DEMO_STOP_AFTER='1',
        TH04_CLOCK_INPUT_OUTPUT=str(out),TH04_CLOCK_KEYBOARD_HEADER=str(source/'include/keyboard.h'),
        TH04_CLOCK_SOURCE_DIR=str(capsule),TH04_ORDINARY_DGROUP='1',
        TH04_ORDINARY_DIALOG_FRAME='1',TH04_ORDINARY_CONTINUE_FRAME='1',
        XDG_CACHE_HOME=str(out/'cache'),XDG_CONFIG_HOME=str(out/'config'),XDG_DATA_HOME=str(out/'data'))
    if input_source is not None:env['TH04_SPARSE_STAGE_INPUT']=str(capsule/'stage-inputs.txt')
    command=[str(debugger),'-nx','-batch','-x',str(adapter),'--args',str(binary),'-defaultconf','-defaultmapper','-conf',str(out/'dosbox-x.conf'),'-fastlaunch','-nogui','-nomenu','-exit','-c',f'imgmount 2 "{image}" -t hdd -fs none','-c','boot -l c']
    frozen={str(p):sha(p) for p in capsule.rglob('*') if p.is_file()}
    (out/'launch.json').write_text(json.dumps(dict(command=command,inputs=inputs,capsule=frozen,plan=plan),indent=2)+'\n')
    start=time.monotonic();timeout=False
    with (out/'boot.log').open('wb') as log:
        child=subprocess.Popen(command,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        (out/'process.json').write_text(json.dumps(dict(pid=child.pid,started_ns=time.time_ns()))+'\n')
        try:code=child.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timeout=True;os.killpg(child.pid,signal.SIGTERM)
            try:code=child.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
    for name,digest in {**inputs,**frozen}.items():assert sha(Path(name))==digest,(name,'capture input changed')
    complete=not timeout and code==0 and b'TH04_SPARSE_FONTS_COMPLETE\n' in (out/'boot.log').read_bytes()
    files={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and p.suffix!='.pyc'}
    receipt=dict(complete=complete,timeout=timeout,exit=code,elapsed=time.monotonic()-start,
        command=command,source_files=inputs,capsule=frozen,files=files,
        initial_hdi_sha256=sha(initial),final_hdi_sha256=sha(image),
        emulator_sha256=sha(binary),main_sha256=sha(main_path),points=points,
        resource_budget='One low-priority CPU,1536MiB address-space bound,headless/muted',
        scope='Original candidate-local-attested DOSBox-X sparse live font/video/RAM evidence;optional declared-stage full DGROUP stream. No per-frame video/full conventional memory,guest assignments,native equivalence or exact promotion.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('SPARSE FONTS',complete,'elapsed',receipt['elapsed'],flush=True)
    return 0 if complete else 1


if __name__=='__main__':
    raise SystemExit(main())
