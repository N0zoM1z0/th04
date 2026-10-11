#!/usr/bin/env python3
"""Capture actual headless FrontEnd demos and diagnose selected raw displays.

Scalar acceptance uses all 15988 original before-update/terminal boundaries.
Pictures are diagnostic: original is after actors before score/background tail;
native is after the complete FrontEnd update. Raw VRAM includes invisible cache.
No physical scanout, composited original RGB or complete picture acceptance.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from verify import source_manifest, require_elf_x86_64
from verify_demo_state import sha, require, parse_native, compare, TARGET_SHA256

SAMPLES = (1,2,3,72,73,74,1952,3379,3709,3996)

def display_rows(raw):
    lines=raw.decode('ascii').splitlines()
    require(len(lines)==4*len(SAMPLES),'complete display sample extent')
    result=[]
    for index,line in enumerate(lines):
        cells=line.split()
        require(len(cells)==6,'display metadata fields')
        demo,frame=index//len(SAMPLES)+1,SAMPLES[index%len(SAMPLES)]
        require(cells[:2]==[str(demo),str(frame)] and cells[3]==f'demo{demo}-frame{frame}',
                'display sample order/name')
        stage,tone,scroll=map(int,(cells[2],cells[4],cells[5]))
        require(stage==[3,0,2,1][demo-1] and 0<=tone<=200 and 0<=scroll<400,
                'display metadata range')
        result.append(dict(demo=demo,frame=frame,stage=stage,stem=cells[3],tone=tone,scroll=scroll))
    return result

def decode_graphics(graphics,gdc,modes):
    """Instantaneous programmed GDC model; deliberately excludes FIFO/scan timing.

    DOSBox-X vga_pc98_gdc.cpp load_display_partition and vga_draw.cpp analog
    16-colour scanout define this limited pitch/row-height recipe.
    """
    require(len(graphics)==262144 and len(gdc)==232 and len(modes)==8,'raw graphics extent')
    require(modes[1] in (0,1) and modes[5]==1,'analog display page/mode')
    require((int.from_bytes(gdc[184:186],'little'),int.from_bytes(gdc[180:182],'little'),
             int.from_bytes(gdc[182:184],'little'),gdc[172],gdc[207],gdc[202])==(40,400,40,1,0,1),
             'unsupported GDC recipe')
    addresses=[]
    for part in range(4):
        p=gdc[152+4*part:156+4*part]
        require(not p[3]&0xc0,'unsupported GDC IM/WD')
        start=p[0]+256*p[1]+65536*(p[2]&3)
        length=(p[2]>>4)+((p[3]&63)<<4) or 1024
        for y in range(min(length,400-len(addresses)//80)):
            addresses.extend((2*(start+40*y)+x)&32767 for x in range(80))
        if len(addresses)==32000:break
    require(len(addresses)==32000,'GDC partition extent')
    page=modes[1]*32768;pixels=bytearray(256000)
    for i,address in enumerate(addresses):
        values=[graphics[plane*65536+page+address] for plane in range(4)]
        for bit in range(8):
            pixels[i*8+bit]=sum(((value>>(7-bit))&1)<<plane for plane,value in enumerate(values))
    return bytes(pixels)

def canonical_tram(raw):
    require(len(raw)==16384,'raw text extent')
    return raw[:4000]+raw[8192:12192]

def label_cells(text):
    require(len(text)==8000,'canonical text extent')
    start=2*(12*80+18)
    return text[start:start+36]+text[4000+start:4000+start+36]

def differences(a,b):
    require(len(a)==len(b),'paired display extent')
    count=0;first=None
    for offset,(left,right) in enumerate(zip(a,b)):
        if left!=right:
            count+=1
            if first is None:first=dict(offset=offset,original=left,native=right)
    return dict(differing_bytes=count,first_difference=first,
                original_sha256=sha(a),native_sha256=sha(b))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('dos-root','original','original-video','original-consumer','exe','hdi','output-dir'):
        p.add_argument('--'+name,required=True,type=Path)
    args=p.parse_args();root=Path(__file__).resolve().parents[1];dos=args.dos_root.resolve()
    sys.path.insert(0,str(dos/'scripts/probes'))
    from compare_th04_dos_demos import load_capture
    from compare_th04_demo_video import read_side, iter_side
    from th04_demo_video import OFFSETS, SIZES, BOUNDARY
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    manifest,sources=source_manifest(root);require_elf_x86_64(args.exe)
    parent,original,_=load_capture(args.original.resolve())
    receipt,profile,diagnostic=read_side(args.original_video.resolve(),args.original.resolve(),args.original_consumer.resolve())
    require(parent['role']==receipt['role']=='original' and parent['main_sha256']==TARGET_SHA256
            and receipt['demos']==4,'original reference identity')
    require(sha(args.hdi.read_bytes())==parent['original_hdi_sha256'],'native game-data image identity')
    inputs=out/'inputs';inputs.mkdir()
    for fat,name in (('GENSOU  SCR','GENSOU.SCR'),('MIKO    CFG','MIKO.CFG')):
        (inputs/name).write_bytes(bytes.fromhex(parent['starting_files'][fat]['hex']))
    command=[str(args.exe.resolve()),'--hdi',str(args.hdi.resolve()),'--pmd-driver','none','--mute',
             '--save-dir',str(inputs),'--demo-pictures',str(out/'capture')]
    environment=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    run=subprocess.run(command,capture_output=True,env=environment,timeout=600)
    (out/'stdout.log').write_bytes(run.stdout);(out/'stderr.log').write_bytes(run.stderr);run.check_returncode()
    capture=out/'capture';scalar=compare(original,parse_native((capture/'state.txt').read_bytes()))
    rows=display_rows((capture/'displays.txt').read_bytes());observations=[];consumed=0
    expected={'state.txt','displays.txt','save'}|{row['stem']+suffix for row in rows for suffix in ('.indices','.rgb','.tram')}
    if (capture/'shake.txt').is_file():expected.add('shake.txt')
    require({path.name for path in capture.iterdir()}==expected,'native capture file extent')
    for demo in range(1,5):
        selected={row['frame']:row for row in rows if row['demo']==demo}
        for frame,raw in iter_side(args.original_video,demo,profile,diagnostic):
            consumed+=1
            if frame not in selected:continue
            row=selected[frame];stem=row['stem'];path=out/'original'/(stem+'.bin');path.parent.mkdir(exist_ok=True);path.write_bytes(raw)
            indices=(capture/(stem+'.indices')).read_bytes();rgb=(capture/(stem+'.rgb')).read_bytes();tram=(capture/(stem+'.tram')).read_bytes()
            require(len(indices)==256000 and len(rgb)==768000 and len(tram)==8000,'native display byte extent')
            require(all(value<16 for value in indices),'native palette index width')
            gd=raw[OFFSETS['gdc']+232:OFFSETS['gdc']+464];modes=raw[OFFSETS['modes']:OFFSETS['modes']+8]
            decoded=decode_graphics(raw[OFFSETS['graphics']:OFFSETS['graphics']+SIZES['graphics']],gd,modes)
            text=canonical_tram(raw[OFFSETS['text']:OFFSETS['text']+SIZES['text']])
            require(raw[0]==row['stage'],'native/original resource stage')
            observations.append(dict(**row,raw_original_sha256=sha(raw),native_rgb_sha256=sha(rgb),
                graphics=differences(decoded,indices),text=differences(text,tram),
                demo_label=differences(label_cells(text),label_cells(tram)),
                original_param_ram=gd[152:168].hex(),original_modes=modes.hex()))
    require(consumed==15984 and len(observations)==4*len(SAMPLES),'complete video reference EOF/samples')
    for name in ('GENSOU.SCR','MIKO.CFG'):
        require((capture/'save'/name).read_bytes()==(inputs/name).read_bytes(),'demo physical save/config drift')
    pins={};snapshot=out/'executed-source'
    for row in sources:
        path=root/row['path'];data=path.read_bytes();require(sha(data)==row['sha256'],'producer source changed')
        destination=snapshot/'native'/row['path'];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
    for module in list(sys.modules.values()):
        file=getattr(module,'__file__',None)
        if not file:continue
        path=Path(file).resolve()
        if not path.is_file() or path.suffix!='.py' or not path.is_relative_to(dos/'scripts'):continue
        relative=path.relative_to(dos);data=path.read_bytes();destination=snapshot/'dos'/relative
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data);pins[str(relative)]=sha(data)
    require(source_manifest(root)[0]==manifest,'source manifest drift')
    label_passed=all(row['demo_label']['differing_bytes']==0 for row in observations)
    report=dict(passed=scalar['passed'] and label_passed,scalar=scalar,demo_label_passed=label_passed,diagnostic_only=True,picture_acceptance=False,
        original_boundary=BOUNDARY,native_boundary='after-complete-FrontEnd-update-and-background-before-host-present',
        original_records=consumed,display_samples=len(observations),observations=observations,
        source_manifest_sha256=manifest,source_files=sources,dos_reader_sha256=pins,
        original_receipt_sha256=sha((args.original/'receipt.json').read_bytes()),
        original_video_receipt_sha256=sha((args.original_video/'receipt.json').read_bytes()),
        native_program_sha256=sha(args.exe.read_bytes()),hdi_sha256=sha(args.hdi.read_bytes()),command=command,
        limits=__doc__)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'],scalar_boundaries=15988,display_samples=len(observations),demo_label_passed=report['demo_label_passed'],picture_acceptance=False)))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
