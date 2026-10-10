#!/usr/bin/env python3
"""Actual OS-window Normal route candidates, with independent outcome checks.

Only X11 keys on private Xvfb; no simulation, actor, score, life or clock writes.
Recorded keys, reference-position feedback and optional live read-only advice
are alternative candidates. All inputs use ordinary X11 keys. Observer CPU/I-O
cost is not dense Lunatic or uninstrumented host performance acceptance.
"""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
NATIVE=Path(__file__).resolve().parents[1]
from verify_host_window import latest,row
from verify_window_continue import Writes,decode,restart
from verify import require_elf_x86_64
from private_x11 import key_names,require_private_xvfb

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('exe','hdi','font','reference','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--exe-sha256',required=True)
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--track-position',action='store_true')
    modes.add_argument('--adaptive',action='store_true')
    a=parser.parse_args();private_display=require_private_xvfb();exe,hdi,font,reference=[p.resolve() for p in (a.exe,a.hdi,a.font,a.reference)]
    report=json.loads((reference.parent/'receipt.json').read_text());case=next(c for c in report['cases'] if c['name']==reference.name)
    assert reference.name=='normal-reimu' and report['passed'] and case['natural_clear']
    for name in ['inputs.txt','state.txt']:assert sha(reference/name)==case['files'][name]
    require_elf_x86_64(exe);assert sha(exe)==a.exe_sha256
    assert sha(hdi)=='0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
    assert sha(font)=='41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'
    inputs={int(t[0]):(int(t[1]),int(t[2])) for t in (l.split() for l in (reference/'inputs.txt').read_text().splitlines())}
    controls={};positions={}
    for line in (reference/'state.txt').read_text().splitlines():
        t=line.split()
        if 'CHILD' in t or int(t[18])!=0:continue
        # Reference state precedes advance; window state follows the last one.
        controls[(int(t[2]),int(t[3]))]=inputs[int(t[0])]
        positions[(int(t[2]),int(t[3]))]=(int(t[4]),int(t[5]))
    pins={str(p):sha(p) for p in [exe,hdi,font,Path(__file__),reference/'inputs.txt',reference/'state.txt',NATIVE/'port64/private_x11.py',NATIVE/'port64/verify_host_window.py',NATIVE/'port64/verify_window_continue.py']}
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);save=out/'saves';save.mkdir()
    cfg=bytes([1,6,2,2,1,1,0,0,0,13]);(save/'MIKO.CFG').write_bytes(cfg);(out/'initial-MIKO.CFG').write_bytes(cfg)
    trace=out/'trace/window.tsv';writes=Writes(save,out/'physical-events',trace)
    command=[str(exe),'--hdi',str(hdi),'--font-bmp',str(font),'--save-dir',str(save),'--title','--mute','--window-trace',str(trace.parent)]
    if a.adaptive:command.append('--window-route-advice')
    log=(out/'window.log').open('wb');actions=(out/'actions.jsonl').open('w');process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
    held=set();events=[];stages=set();scenes=set();last=0;missing=0;observed=0;started=time.monotonic();last_progress=0;success=False;error=None
    def x(*args):return subprocess.run(['xdotool',*args],check=True,capture_output=True,text=True).stdout.strip()
    def wait(predicate,timeout=60):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            writes.pump()
            if process.poll() is not None:raise RuntimeError('owned process exited during observation')
            r=latest(trace)
            if r and predicate(r):return r
            time.sleep(.001)
        raise RuntimeError('observation timeout; owned process closes in finally')
    def keys(desired,r):
        desired=set(desired)
        if desired==held:return
        for key in sorted(held-desired):x('keyup',key)
        for key in sorted(desired-held):x('keydown',key)
        held.clear();held.update(desired)
        actions.write(json.dumps(dict(seq=r['seq'],stage=r['stage'],frame=r['frame'],scene=r['scene'],keys=sorted(desired),issued_ns=time.monotonic_ns()))+'\n');actions.flush()
    def press(key):
        r=wait(lambda _:True);keys([key],r);time.sleep(.12);r=wait(lambda _:True);keys([],r);time.sleep(.04)
    try:
        wait(lambda _:True);windows=x('search','--onlyvisible','--pid',str(process.pid)).splitlines();assert len(windows)==1
        window=windows[0];x('windowfocus','--sync',window)
        wait(lambda r:r['scene']=='menu');initial=(save/'GENSOU.SCR').read_bytes();(out/'op-initial-GENSOU.SCR').write_bytes(initial)
        press('Return');wait(lambda r:r['scene']=='character');press('Return');wait(lambda r:r['scene']=='shot');press('Return')
        r=wait(lambda r:r['scene']=='main');assert (r['character'],r['shot'],r['rank'],r['stage'])==(0,0,1,0)
        deadline=time.monotonic()+2400
        while time.monotonic()<deadline:
            r=wait(lambda r:r['seq']>last,timeout=15);last=r['seq'];observed+=1
            assert r['focused'] and r['audio_opens']==r['audio_failed']==0
            scenes.add((r['program'],r['generation'],r['scene']))
            if r['program']==0 and r['generation']>2:
                keys([],r)
                if r['scene']=='menu':break
            elif r['scene']=='gameover':raise RuntimeError('recorded-key candidate reached Game Over; full no-Continue clear rejected')
            elif r['scene']=='main':
                if r['stage'] not in stages:
                    stages.add(r['stage']);subprocess.run(['import','-window',window,str(out/('stage-'+str(r['stage'])+'.png'))],check=True)
                value=controls.get((r['stage'],r['frame']))
                if value is None:missing+=1;value=(32,0)
                held_value,shift=value
                target=positions.get((r['stage'],r['frame']+1))
                if a.track_position and target is not None and not r['respawn']:
                    candidates=[]
                    for focus in [0,1]:
                        for dx in [-1,0,1]:
                            for dy in [-1,0,1]:
                                speed=(48 if dx and dy else 64)/(2 if focus else 1)
                                px=min(6016,max(128,r['x']+dx*speed));py=min(5632,max(128,r['y']+dy*speed))
                                distance=(px-target[0])**2+(py-target[1])**2
                                direction=(4 if dx<0 else 8 if dx>0 else 0)|(1 if dy<0 else 2 if dy>0 else 0)
                                candidates.append((distance,focus!=shift,direction,focus))
                    _,_,direction,shift=min(candidates)
                    held_value=(held_value&~15)|direction
                if a.adaptive:
                    assert 'advice_held' in r,'adaptive controller requires trace v3'
                    held_value,shift=r['advice_held'],r['advice_shift']
                desired=key_names(held_value,shift)
                keys(desired,r)
            elif r['scene']=='registration':keys(['Escape'] if r['seq']%20>=10 else [],r)
            elif r['scene'] in ('dialog','maine'):keys(['z'] if r['seq']%20>=10 else [],r)
            else:keys([],r)
            if time.monotonic()-last_progress>30:
                last_progress=time.monotonic();print(json.dumps(dict(elapsed=round(time.monotonic()-started),seq=r['seq'],scene=r['scene'],stage=r['stage'],frame=r['frame'],lives=r['lives'],bombs=r['bombs'],misses=r['misses'],missing_controls=missing)),flush=True)
        else:raise RuntimeError('full-route watchdog expired')
        assert (save/'MIKO.CFG').read_bytes()==cfg
        assert stages==set(range(6));assert (2,3,'maine') in scenes and (2,3,'registration') in scenes
        subprocess.run(['import','-window',window,str(out/'fresh-op.png')],check=True)
        final=(save/'GENSOU.SCR').read_bytes();(out/'final-GENSOU.SCR').write_bytes(final);sections=decode(final)
        assert sections[1][174]&1,'Normal clear did not persist Reimu A Extra admission'
        before=decode(initial);assert all(before[i][2:]==sections[i][2:] for i in range(10) if i!=1)
        keys([],r);x('key','Escape');process.wait(timeout=15);assert process.returncode==0
        writes.close();events=writes.records;writes=None;actions.close();log.close()
        lines=trace.read_text().splitlines()
        rows=[row(l) for l in lines if l.startswith('R ')]
        terminal=[list(map(int,l.split()[1:])) for l in lines if l.startswith('E ')]
        assert len(terminal)==1 and terminal[0][0]==len(rows) and terminal[0][4:]==[0,0]
        snapshots=[decode((out/'physical-events'/e['snapshot']).read_bytes()) for e in events if e['name']=='GENSOU.SCR']
        assert any(s[1][174]&1 for s in snapshots),'clear flag absent at the physical rename boundary'
        assert all(r['audio_opens']==r['audio_failed']==0 for r in rows)
        result=dict(passed=True,private_display=private_display,track_position=a.track_position,adaptive=a.adaptive,command=command,pins=pins,reference_result=case['result'],stages=sorted(stages),scenes=sorted(scenes),observed_refreshes=observed,missing_controls=missing,trace_sha256=sha(trace),physical_events=events,files={p.name:sha(p) for p in save.iterdir() if p.is_file()},scope=__doc__)
        result['restart']=restart(exe,hdi,font,save,out/'restart')
        for p,h in pins.items():assert sha(p)==h
        (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');success=True;print('FULL NORMAL WINDOW + PHYSICAL RESTART PASS',flush=True)
    except Exception as e:error=str(e);raise
    finally:
        for key in held:subprocess.run(['xdotool','keyup',key],check=False)
        if process.poll() is None:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait()
        if writes is not None:writes.close();events=writes.records
        actions.close();log.close()
        (out/'physical-events.json').write_text(json.dumps(events,indent=2)+'\n')
        (out/'terminal.json').write_text(json.dumps(dict(passed=success,error=error,private_display=private_display,track_position=a.track_position,adaptive=a.adaptive,pins=pins,command=command,stages=sorted(stages),scenes=sorted(scenes),last_refresh=last,missing_controls=missing,elapsed=time.monotonic()-started),indent=2)+'\n')
if __name__=='__main__':main()
