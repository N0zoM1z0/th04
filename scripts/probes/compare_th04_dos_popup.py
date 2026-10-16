#!/usr/bin/env python3
"""Compare complete popup/BGM text rows and popup state at ordinary boundaries.

The popup and BGM owners have separate verdicts. The aggregate fails if either
row differs; a passing popup owner never accepts a missing BGM title or picture.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
from compare_th04_dos_ordinary_prefix import load
from th04_ordinary_video import records as video_records
from th04_ordinary_dgroup import records as data_records
from th04_demo_video import OFFSETS,SIZES

def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        while block:=stream.read(1024*1024):digest.update(block)
    return digest.hexdigest()

def rows_file(directory):
    path=directory/'popup-rows.bin'
    return path.open('rb') if path.is_file() else gzip.open(directory/'popup-rows.bin.gz','rb')

def compare(original: Path,native: Path,target: bytes,updates: int):
    capture=load(original,target)
    terminal=json.loads((original/'ordinary-terminal.json').read_text())
    profile=json.loads((original/'profile.json').read_text())
    if not 0<updates<terminal['frame']:raise ValueError('popup paired complete extent')
    t=terminal
    video=video_records(original/'ordinary-video.bin.gz',t['load_segment'],t['dgroup_segment'],t['cr0'],t['cr3'],t['frame'])
    data=data_records(original/'ordinary-dgroup.bin.gz',t['load_segment'],t['dgroup_segment'],profile['fields'],t['cr0'],t['cr3'],t['frame'])
    regions={name:dict(differing_frames=0,differing_bytes=0,differences=[]) for name in ('popup-row','bgm-row')}
    state_path=native/'popup-state.txt';state_lines=state_path.read_text().splitlines() if state_path.is_file() else None
    if state_lines is not None and len(state_lines)!=updates:raise ValueError('popup state observation extent')
    states=dict(passed=None,differing_frames=0,differences=[],scope='not captured')
    native_hash={name:hashlib.sha256() for name in regions};original_hash={name:hashlib.sha256() for name in regions}
    with rows_file(native) as stream:
        if stream.read(8)!=b'TH04PU1\n' or stream.read(4)!=bytes(4) or len(stream.read(640))!=640:raise ValueError('popup initial native record')
        for (frame,block),(observed,group) in zip(video,data,strict=True):
            if frame!=observed:raise ValueError('popup video/DGROUP boundary')
            if frame>updates:continue
            if stream.read(4)!=struct.pack('<I',frame):raise ValueError('popup native boundary order')
            body=stream.read(640)
            if len(body)!=640:raise ValueError('popup complete native rows')
            text=block[OFFSETS['text']:OFFSETS['text']+SIZES['text']]
            for index,(name,row) in enumerate((('popup-row',2),('bgm-row',23))):
                expected=text[row*160:row*160+160]+text[8192+row*160:8192+row*160+160]
                actual=body[index*320:index*320+320];native_hash[name].update(actual);original_hash[name].update(expected)
                changes=[i for i in range(320) if expected[i]!=actual[i]]
                if changes:
                    result=regions[name];result['differing_frames']+=1;result['differing_bytes']+=len(changes)
                    if len(result['differences'])<8:result['differences'].append(dict(frame=frame,differing_bytes=len(changes),first=[dict(offset=i,original=expected[i],native=actual[i]) for i in changes[:8]]))
            if state_lines is not None:
                columns=state_lines[frame-1].split()
                if len(columns)!=11 or int(columns[0])!=frame:raise ValueError('popup state native order/width')
                expected=[group[0x1b64],int.from_bytes(group[0x4688:0x468a],'little',signed=True),group[0x468a],group[0x468b],int.from_bytes(group[0x4696:0x4698],'little',signed=True),int.from_bytes(group[0x4698:0x469a],'little',signed=True),group[0x469b],int.from_bytes(group[0x469e:0x46a0],'little'),int.from_bytes(group[0x46a2:0x46a6],'little'),group[0x468c:0x4695].hex()]
                actual=[*map(int,columns[1:10]),columns[10]]
                if actual!=expected:
                    states['differing_frames']+=1
                    if len(states['differences'])<8:states['differences'].append(dict(frame=frame,original=expected,native=actual))
        if stream.read(1):raise ValueError('popup native trailing records')
    for name,result in regions.items():result.update(passed=result['differing_frames']==0,original_sha256=original_hash[name].hexdigest(),native_sha256=native_hash[name].hexdigest(),bytes_per_frame=320)
    if state_lines is not None:states.update(passed=states['differing_frames']==0,scope='All scalar popup fields and complete9-byte shift buffer at the actual after-actor/pre-score observer.')
    return dict(passed=all(row['passed'] for row in regions.values()) and states['passed'] is True,popup_passed=regions['popup-row']['passed'] and states['passed'] is True,frames=updates,regions=regions,popup_state=states,target_sha256=hashlib.sha256(target).hexdigest(),original_receipt_sha256=sha(original/'receipt.json'),reader_source_sha256=sha(Path(__file__)),native_files={p.name:sha(p) for p in native.iterdir() if p.name in ('popup-rows.bin','popup-rows.bin.gz','popup-state.txt')},scope=__doc__+' Complete80-column rows include160 character bytes and160 attribute bytes each; no ignored byte mask. Native row observations follow the complete update; these rows have no score-tail writer. Popup state uses the actor observer on both sides. No complete picture, scanout, timing, other globals or exact promotion.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('original','native','target','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--updates',type=int,default=8000)
    a=p.parse_args();result=compare(a.original.resolve(),a.native.resolve(),a.target.read_bytes(),a.updates)
    with a.output.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps(dict(passed=result['passed'],popup_passed=result['popup_passed'],regions={name:row['differing_frames'] for name,row in result['regions'].items()},popup_state=result['popup_state']['differing_frames'])))
    return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
