#!/usr/bin/env python3
"""Compare all ordinary title state, three complete text rows and actual BB calls.

The target callback is replayed from its observed after-actor DGROUP with its
clock reversed by one update. The entry handoff has frame0 and draws nothing.
Text/BB/CRT callees execute unchanged, with separately attested file-backed BB
masks at a component allocation and explicit GRCG hardware. No game callee is
adapted. Graphics pixel equivalence belongs to the separate four-plane Oracle.
"""
import argparse,gzip,hashlib,json,struct,sys
from pathlib import Path
from compare_th04_dos_ordinary_prefix import load
from th04_ordinary_dgroup import records as groups
from th04_ordinary_video import records as videos
from th04_demo_video import OFFSETS,SIZES
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/runtime'))
from verify_dos_hud_titles import TitlesMachine

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def opened(path):return path.open('rb') if path.exists() else gzip.open(str(path)+'.gz','rb')
def fields(data):
    word=lambda at:struct.unpack_from('<H',data,at)[0]
    return [data[0x1b62],word(0x469c),data[0x46a0],data[0x1b63],data[0x1bb6],data[0x4684],data[0x469a],word(0x4680),word(0x4682),word(0x4686)]

def compare(original,native,target,bb,updates):
    import unicorn
    if unicorn.__version__!='2.1.4':raise ValueError('pinned Unicorn2.1.4 required')
    load(original,target);t=json.loads((original/'ordinary-terminal.json').read_text());p=json.loads((original/'profile.json').read_text())
    if not 0<updates<t['frame']:raise ValueError('complete ordinary title extent')
    machine=TitlesMachine(t['load_segment'],bb);machine.seed();lines=(native/'title-state.txt').read_text().splitlines()
    if len(lines)!=updates:raise ValueError('ordinary title-state extent')
    changes={key:dict(differing_frames=0,differences=[]) for key in ('fields','BB calls','stage-number-row','stage-name-row','BGM-row')}
    hashes={key:[hashlib.sha256(),hashlib.sha256()] for key in changes};replayed=0
    def check(key,frame,expected,actual):
        for h,value in zip(hashes[key],(expected,actual),strict=True):h.update(value)
        if expected!=actual:
            entry=changes[key];entry['differing_frames']+=1
            if len(entry['differences'])<8:entry['differences'].append(dict(frame=frame,original=expected.hex()[:512],native=actual.hex()[:512]))
    with opened(native/'title-rows.bin') as stream:
        if stream.read(8)!=b'TH04TI1\n' or stream.read(4)!=bytes(4) or len(stream.read(960))!=960:raise ValueError('title initial row record')
        for (frame,data),(video_frame,video) in zip(groups(original/'ordinary-dgroup.bin.gz',t['load_segment'],t['dgroup_segment'],p['fields'],t['cr0'],t['cr3'],t['frame']),videos(original/'ordinary-video.bin.gz',t['load_segment'],t['dgroup_segment'],t['cr0'],t['cr3'],t['frame']),strict=True):
            if frame!=video_frame:raise ValueError('ordinary title boundary mismatch')
            if frame>updates:continue
            pieces=lines[frame-1].split('|');actual_fields=list(map(int,pieces[0].split()));expected_fields=fields(data)
            if len(actual_fields)!=11 or actual_fields[0]!=frame:raise ValueError('title field width/order')
            check('fields',frame,struct.pack('<10H',*expected_fields),struct.pack('<10H',*actual_fields[1:]))
            callback=expected_fields[1];draws=[]
            if callback in (0x6446,0x66a5):
                clock=0x46a0 if callback==0x6446 else 0x1b63
                if data[clock]:
                    machine.u.mem_write(machine.ds*16,data);machine.write(clock,'B',data[clock]-1)
                    # Reverse the dissolve-state change only on the frames
                    # where it advances. Frame0 initializes its own sprite.
                    before=data[clock]-1;sprite=data[0x1bb6]
                    if before>=192:
                        if before!=192 and not before&1:sprite=(sprite-1)&255
                    elif 0<before<=32 and not before&3 and sprite!=16:
                        if sprite==0:sprite=23
                        elif sprite>16:sprite-=1
                    machine.write(0x1bb6,'B',sprite);machine.write(0x1b66,'H',0x8000);machine.write(0x768,'H',0xa000)
                    observed=machine.call(callback);replayed+=1;draws=observed['draws']
                    actual_replay=[observed['callback'],observed['titles'],observed['boss'],observed['sprite'],observed['stage_id'],observed['bgm_id'],*observed['lengths']]
                    if actual_replay!=expected_fields[1:]:raise ValueError(('title target reversal failed',frame,expected_fields[1:],actual_replay))
            actual_draws=[tuple(map(int,value.split())) for value in pieces[1:]]
            encode=lambda rows:json.dumps(rows,separators=(',',':')).encode()
            check('BB calls',frame,encode(draws),encode(actual_draws))
            if stream.read(4)!=struct.pack('<I',frame):raise ValueError('title row order')
            body=stream.read(960)
            if len(body)!=960:raise ValueError('complete title text rows')
            text=video[OFFSETS['text']:OFFSETS['text']+SIZES['text']]
            for index,(key,row) in enumerate((('stage-number-row',11),('stage-name-row',13),('BGM-row',23))):
                expected=text[row*160:row*160+160]+text[8192+row*160:8192+row*160+160]
                check(key,frame,expected,body[index*320:index*320+320])
        if stream.read(1):raise ValueError('trailing title rows')
    for key,result in changes.items():result.update(passed=not result['differing_frames'],original_sha256=hashes[key][0].hexdigest(),native_sha256=hashes[key][1].hexdigest())
    return dict(passed=all(value['passed'] for value in changes.values()),frames=updates,target_callback_replays=replayed,comparisons=changes,target_sha256=hashlib.sha256(target).hexdigest(),original_receipt_sha256=digest(original/'receipt.json'),bb_sha256=hashlib.sha256(bb).hexdigest(),reader_sha256=digest(Path(__file__)),native_files={p.name:digest(p) for p in native.iterdir() if p.name in ('title-state.txt','title-rows.bin','title-rows.bin.gz')},scope=__doc__+' Exact whole80-column character/attribute row extents at the real actor boundary; no byte masks. All original streams consumed through EOF. No timing, complete natural picture, other globals or exact promotion.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('original','native','target','bb','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--updates',type=int,default=8000);a=parser.parse_args()
    result=compare(a.original.resolve(),a.native.resolve(),a.target.read_bytes(),a.bb.read_bytes(),a.updates)
    with a.output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(passed=result['passed'],differences={key:value['differing_frames'] for key,value in result['comparisons'].items()})));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
