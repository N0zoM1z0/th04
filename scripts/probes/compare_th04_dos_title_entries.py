#!/usr/bin/env python3
"""Compare title state/whole text rows and actual runtime BB entry arguments.

Use original read-only code-fetch events rather than replaying the callback
from its later after-scroll DGROUP. Entry left/top/cel are actual registers.
Colors and raster pixels have separate independent component/picture Oracles.
"""
import argparse,gzip,hashlib,json,struct,sys
from pathlib import Path
from compare_th04_dos_ordinary_prefix import load
from compare_th04_dos_titles import fields
from th04_ordinary_dgroup import records as groups
from th04_ordinary_video import records as videos
from th04_demo_video import OFFSETS,SIZES
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/runtime'))
from verify_dos_text_gaiji import original as target_layout

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def opened(path):return path.open('rb') if path.is_file() else gzip.open(str(path)+'.gz','rb')
def compare(original,native,target,updates):
    load(original,target);terminal=json.loads((original/'ordinary-terminal.json').read_text());profile=json.loads((original/'profile.json').read_text())
    if not 0<updates<terminal['frame']:raise ValueError('complete paired title extent')
    summary=json.loads((original/'title-draws-summary.json').read_text());plan=summary['frames'];observed=summary['observed'];events=original/'title-draws.jsonl'
    if not summary['complete'] or plan!=sorted(set(plan)) or not plan or not all(1<=f<=updates for f in plan):raise ValueError('actual BB entry interval plan')
    if {int(frame) for frame in observed}!=set(plan) or digest(events)!=summary['jsonl_sha256']:raise ValueError('actual BB entry summary identity/extent')
    expected_calls={frame:[] for frame in plan};last=0;layout=target_layout('main');opcode=layout['body'][0xaaf0+0x15aa:0xaaf0+0x15ba]
    with events.open() as stream:
        for line in stream:
            row=json.loads(line);frame=row['frame'];regs=bytes.fromhex(row['registers']);segs=bytes.fromhex(row['segments']);stack=bytes.fromhex(row['stack'])
            if frame<last or frame not in expected_calls or row['stage_frame']!=frame-1:raise ValueError('BB entry frame/order')
            last=frame;cs=terminal['load_segment']+0xaaf;ds=terminal['dgroup_segment']
            if (row['cs'],row['ip'],row['load_segment'],row['dgroup_segment'])!=(cs,0x15aa,terminal['load_segment'],ds):raise ValueError('BB entry artifact/segment identity')
            if not row['unchanged_context'] or row['opcode']!=opcode.hex() or row['watched_guest_linear']!=cs*16+0x15aa:raise ValueError('BB entry opcode/read-only evidence')
            if len(regs)!=48 or len(segs)!=136 or len(stack)!=16 or int.from_bytes(stack[:2],'little')!=0x63f0:raise ValueError('BB entry raw register/caller extent')
            if (int.from_bytes(segs[8:16],'little'),int.from_bytes(segs[24:32],'little'),int.from_bytes(regs[32:36],'little')&65535)!=(cs,ds,0x15aa):raise ValueError('BB entry raw CS:IP/DS')
            args=tuple(int.from_bytes(regs[start:start+2],'little') for start in (0,8,4))
            if args!=(row['left'],row['top'],row['sprite']):raise ValueError('BB entry argument register identity')
            expected_calls[frame].append(args)
    if sum(map(len,expected_calls.values()))!=summary['events'] or any(len(expected_calls[f])!=observed[str(f)] for f in plan):raise ValueError('BB entry complete call counts')
    lines=(native/'title-state.txt').read_text().splitlines()
    if len(lines)!=updates:raise ValueError('native title state extent')
    regions={key:dict(differing_frames=0,differences=[]) for key in ('fields','actual-BB-entry-arguments','stage-number-row','stage-name-row','BGM-row')};hashes={key:[hashlib.sha256(),hashlib.sha256()] for key in regions}
    def check(key,frame,expected,actual):
        for h,value in zip(hashes[key],(expected,actual),strict=True):h.update(value)
        if expected!=actual:
            result=regions[key];result['differing_frames']+=1
            if len(result['differences'])<8:result['differences'].append(dict(frame=frame,original=expected.hex()[:512],native=actual.hex()[:512]))
    with opened(native/'title-rows.bin') as stream:
        if stream.read(8)!=b'TH04TI1\n' or stream.read(4)!=bytes(4) or len(stream.read(960))!=960:raise ValueError('native initial title rows')
        t=terminal
        for (frame,data),(vframe,video) in zip(groups(original/'ordinary-dgroup.bin.gz',t['load_segment'],t['dgroup_segment'],profile['fields'],t['cr0'],t['cr3'],t['frame']),videos(original/'ordinary-video.bin.gz',t['load_segment'],t['dgroup_segment'],t['cr0'],t['cr3'],t['frame']),strict=True):
            if frame!=vframe:raise ValueError('title video/DGROUP boundary')
            if frame>updates:continue
            pieces=lines[frame-1].split('|');actual_fields=list(map(int,pieces[0].split()))
            if len(actual_fields)!=11 or actual_fields[0]!=frame:raise ValueError('native title fields/order')
            check('fields',frame,struct.pack('<10H',*fields(data)),struct.pack('<10H',*actual_fields[1:]))
            calls=[tuple(map(int,value.split())) for value in pieces[1:]]
            if any(len(call)!=4 for call in calls):raise ValueError('native BB draw width')
            if frame in expected_calls:
                encode=lambda values:json.dumps(values,separators=(',',':')).encode()
                check('actual-BB-entry-arguments',frame,encode(expected_calls[frame]),encode([call[:3] for call in calls]))
            if stream.read(4)!=struct.pack('<I',frame):raise ValueError('native title row order')
            body=stream.read(960)
            if len(body)!=960:raise ValueError('native complete title rows')
            text=video[OFFSETS['text']:OFFSETS['text']+SIZES['text']]
            for index,(key,row) in enumerate((('stage-number-row',11),('stage-name-row',13),('BGM-row',23))):
                check(key,frame,text[row*160:row*160+160]+text[8192+row*160:8192+row*160+160],body[index*320:index*320+320])
        if stream.read(1):raise ValueError('native trailing title rows')
    for key,result in regions.items():result.update(passed=not result['differing_frames'],original_sha256=hashes[key][0].hexdigest(),native_sha256=hashes[key][1].hexdigest())
    return dict(passed=all(value['passed'] for value in regions.values()),frames=updates,entry_intervals=len(plan),entry_interval_first=plan[0],entry_interval_last=plan[-1],actual_BB_calls=summary['events'],comparisons=regions,original_receipt_sha256=digest(original/'receipt.json'),entry_jsonl_sha256=digest(events),reader_sha256=digest(Path(__file__)),scope=__doc__+' Original MAIN_01_TEXT0AAF:15AA entry and0AAF:63F0 caller, with unchanged raw CPU state. Complete three80-column character/attribute rows and all title fields cover8000 updates; actual calls cover the explicitly armed intervals. No constructed pre-scroll state,coordinate fit,color mask,physical scanout or historical exact promotion.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('original','native','target','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--updates',type=int,default=8000);args=parser.parse_args();result=compare(args.original.resolve(),args.native.resolve(),args.target.read_bytes(),args.updates)
    with args.output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(passed=result['passed'],entry_intervals=result['entry_intervals'],actual_BB_calls=result['actual_BB_calls'],different={key:value['differing_frames'] for key,value in result['comparisons'].items()})));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
