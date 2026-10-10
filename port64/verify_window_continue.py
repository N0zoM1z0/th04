#!/usr/bin/env python3
"""Ordinary Linux X11 Continue/registration/fresh OP and physical-save restart.

Private Xvfb OS keys only. No actor, hit, score, life or clock injection.
Lunatic/lives1/Bombs0/Turbo is legal configuration. A separately declared
zero-score selected leaderboard section covers ranked Continue; missing score
covers ordinary unranked behavior. Neither trial is a full stage-clear route.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import time
from verify import source_manifest, require_elf_x86_64
from verify_host_window import latest, row

CONTINUE = bytes.fromhex('acb8b7bdb2b7beae')
CFG = bytes([3,1,0,2,1,1,0,0,0,8])

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def decode(data):
    assert len(data) == 1960
    result = []
    for at in range(0, len(data), 196):
        section = bytearray(data[at:at+196]); key0, key1 = section[:2]
        for i in range(4,195):
            rotate = ((section[i+1] >> 3) | (section[i+1] << 5)) & 255
            section[i] = (section[i] + key0 + (rotate ^ key1)) & 255
        section[195] = (section[195] + key0) & 255
        assert (section[2] - sum(section[4:])) & 255 == 0
        result.append(bytes(section))
    return result

def entries(section):
    result=[]
    for i in range(10):
        digits=[x-160 for x in section[94+8*i:102+8*i]]
        assert all(0 <= x <= 9 for x in digits)
        result.append(dict(name=section[4+9*i:12+9*i].hex(),credits=digits[0],
                           units=sum(digits[j]*10**(j-1) for j in range(1,8))))
    return result

class Writes:
    def __init__(self, saves, output, trace):
        lib=ctypes.CDLL(None,use_errno=True)
        lib.inotify_init1.argtypes=[ctypes.c_int];lib.inotify_init1.restype=ctypes.c_int
        lib.inotify_add_watch.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
        lib.inotify_add_watch.restype=ctypes.c_int
        self.fd=lib.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
        if self.fd < 0:raise OSError(ctypes.get_errno(),'inotify init')
        if lib.inotify_add_watch(self.fd,os.fsencode(saves),0x80) < 0:
            os.close(self.fd);raise OSError(ctypes.get_errno(),'inotify watch')
        self.saves,self.output,self.trace=saves,output,trace
        output.mkdir();self.records=[]
    def pump(self):
        while True:
            try:data=os.read(self.fd,65536)
            except BlockingIOError:return
            at=0
            while at < len(data):
                _,mask,_,size=struct.unpack_from('iIII',data,at)
                name=data[at+16:at+16+size].split(b'\0',1)[0].decode();at+=16+size
                if name not in ('GENSOU.SCR','MIKO.CFG'):continue
                contents=(self.saves/name).read_bytes()
                snapshot=self.output/(f'{len(self.records):03d}-'+name);snapshot.write_bytes(contents)
                state=latest(self.trace)
                self.records.append(dict(name=name,mask=mask,snapshot=snapshot.name,
                    sha256=sha(snapshot),observed_ns=time.monotonic_ns(),last_refresh=state['seq'] if state else 0))
    def close(self):
        self.pump();os.close(self.fd)

def trial(exe,hdi,font,out,fixture):
    out.mkdir();save=out/'saves';save.mkdir();(save/'MIKO.CFG').write_bytes(CFG)
    (out/'initial-MIKO.CFG').write_bytes(CFG)
    if fixture is not None:
        data=fixture.read_bytes();assert sha(fixture)=='17235a36dc5184c84f146c7f2799531e8bc8d8c1aed6b6c826b14bc80cf31fff'
        assert all(e['units']==0 for e in entries(decode(data)[3]))
        (save/'GENSOU.SCR').write_bytes(data);(out/'initial-GENSOU.SCR').write_bytes(data)
    trace=out/'trace/window.tsv'
    command=[str(exe),'--hdi',str(hdi),'--font-bmp',str(font),'--save-dir',str(save),'--title','--mute','--window-trace',str(trace.parent)]
    log=(out/'window.log').open('wb');writes=Writes(save,out/'physical-events',trace)
    process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
    held=set();actions=[];event_records=[]
    def x(*arguments):
        return subprocess.run(['xdotool',*arguments],capture_output=True,text=True,check=True).stdout.strip()
    def wait(predicate,timeout=60):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            writes.pump()
            if process.poll() is not None:raise RuntimeError('window exited during route')
            state=latest(trace)
            if state and predicate(state):return state
            time.sleep(.005)
        raise RuntimeError('route observation timeout; owned process will close in finally')
    def keys(desired,state):
        desired=set(desired)
        if desired==held:return
        for key in sorted(held-desired):x('keyup',key)
        for key in sorted(desired-held):x('keydown',key)
        actions.append(dict(seq=state['seq'],scene=state['scene'],keys=sorted(desired),issued_ns=time.monotonic_ns()))
        held.clear();held.update(desired)
    def press(key):
        state=wait(lambda _:True);keys([key],state);time.sleep(.12);state=wait(lambda _:True);keys([],state);time.sleep(.04)
    try:
        wait(lambda _:True);window=x('search','--onlyvisible','--pid',str(process.pid)).splitlines()
        assert len(window)==1;window=window[0];x('windowfocus','--sync',window)
        wait(lambda r:r['scene']=='menu');initial=(save/'GENSOU.SCR').read_bytes()
        (out/'op-initial-GENSOU.SCR').write_bytes(initial)
        press('Return');wait(lambda r:r['scene']=='character');press('Return')
        wait(lambda r:r['scene']=='shot');press('Return')
        state=wait(lambda r:r['scene']=='main');assert (state['character'],state['shot'],state['rank'],state['stage'])==(0,0,3,0)
        go_visits=0;go_start=0;was_go=False;last=0;deadline=time.monotonic()+180
        while time.monotonic()<deadline:
            state=wait(lambda r:r['seq']>last,timeout=10);last=state['seq']
            assert state['focused'], 'private game window lost focus'
            if state['program']==0 and state['generation']>2:
                keys([],state)
                if state['scene']=='menu':break
            elif state['scene']=='gameover':
                if not was_go:go_visits+=1;go_start=state['seq']
                was_go=True
                keys([] if (state['seq']-go_start)%20<10 else ['z' if go_visits==1 else 'Escape'],state)
            else:
                was_go=False
                if state['scene']=='main':keys(['z'],state)
                elif state['scene']=='registration':keys(['Escape'] if state['seq']%20>=10 else [],state)
                elif state['scene'] in ('dialog','maine'):keys(['z'] if state['seq']%20>=10 else [],state)
                else:keys([],state)
        else:raise RuntimeError('ordinary Continue route exceeded wall limit')
        assert go_visits==2
        subprocess.run(['import','-window',window,str(out/'fresh-op.png')],check=True)
        final=(save/'GENSOU.SCR').read_bytes();(out/'final-GENSOU.SCR').write_bytes(final)
        x('key','Escape');process.wait(timeout=15);assert process.returncode==0
        writes.pump();event_records=writes.records;writes.close();writes=None;log.close()
        rows=[row(line) for line in trace.read_text().splitlines() if line.startswith('R ')]
        blocks=[];block=[]
        for r in rows:
            assert r['audio_opens']==0 and r['audio_failed']==0
            if r['program']==1:
                assert r['score_units']==r['score_digits_units']+r['score_delta']
            if r['scene']=='gameover':block.append(r)
            elif block:blocks.append((block,r));block=[]
        if block:blocks.append((block,None))
        assert len(blocks)==2
        for b,_ in blocks:assert len({(r['frame'],r['x'],r['y']) for r in b})==1
        first,resume=blocks[0];second,child=blocks[1]
        assert resume['program']==1 and resume['frame']==first[0]['frame']+1
        assert first[0]['score_digits_units']>0 and first[0]['credits']==0
        assert any(r['credits']==1 and r['score_units']==0 and r['power']==1 and r['lives']==1 for r in first)
        assert child['program']==2 and child['generation']==3
        assert any(r['scene']=='registration' for r in rows)
        assert rows[-1]['program']==0 and rows[-1]['generation']==4 and rows[-1]['scene']=='menu'
        before_sections=decode(initial);after_sections=decode(final)
        # Every save rekeys the complete file. Compare decoded checksum and
        # payload, while preserving the independently checked key bytes.
        assert all(before_sections[i][2:]==after_sections[i][2:] for i in range(10) if i!=3)
        score_events=[e for e in event_records if e['name']=='GENSOU.SCR']
        ranked=[]
        for event in score_events:
            data=(out/'physical-events'/event['snapshot']).read_bytes();selected=entries(decode(data)[3])
            for entry in selected:
                if entry['name']==CONTINUE.hex():ranked.append((event,entry))
        if fixture is not None:
            assert ranked and any(e['credits']==0 and e['units']==first[0]['score_digits_units'] for _,e in ranked)
        else:
            assert not ranked and first[0]['score_digits_units'] < min(e['units'] for e in entries(before_sections[3]))
        assert (save/'MIKO.CFG').read_bytes()==CFG
        return dict(passed=True,command=command,initial_sha256=sha(out/'op-initial-GENSOU.SCR'),final_sha256=sha(out/'final-GENSOU.SCR'),
                    gameover=[dict(frame=b[0]['frame'],refreshes=len(b),score_before=b[0]['score_digits_units'],credits_before=b[0]['credits']) for b,_ in blocks],
                    continue_entries=[dict(event=e,entry=entry) for e,entry in ranked],actions=actions,
                    trace_sha256=sha(trace),physical_events=event_records)
    finally:
        for key in held:subprocess.run(['xdotool','keyup',key],check=False)
        if process.poll() is None:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait()
        if writes is not None:writes.close()
        if not log.closed:log.close()
        if writes is not None:event_records=writes.records
        (out/'actions.json').write_text(json.dumps(actions,indent=2)+'\n')
        (out/'physical-events.json').write_text(json.dumps(event_records,indent=2)+'\n')

def restart(exe,hdi,font,save,out):
    out.mkdir();trace=out/'trace/window.tsv';before={p.name:sha(p) for p in save.iterdir() if p.is_file()}
    command=[str(exe),'--hdi',str(hdi),'--font-bmp',str(font),'--save-dir',str(save),'--title','--mute','--window-trace',str(trace.parent)]
    log=(out/'window.log').open('wb');process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
    def x(*arguments):return subprocess.run(['xdotool',*arguments],check=True,capture_output=True,text=True).stdout.strip()
    def wait(predicate):
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            if process.poll() is not None:raise RuntimeError('restart exited')
            state=latest(trace)
            if state and predicate(state):return state
            time.sleep(.01)
        raise RuntimeError('restart observation timed out')
    def press(key):
        x('keydown',key);time.sleep(.12);x('keyup',key);time.sleep(.04)
    try:
        wait(lambda _:True);windows=x('search','--onlyvisible','--pid',str(process.pid)).splitlines();assert len(windows)==1
        window=windows[0];x('windowfocus','--sync',window)
        state=wait(lambda r:r['scene']=='menu');assert state['program']==0 and state['generation']==1
        # Four Up events reach Scores from Start regardless of disabled Extra.
        for _ in range(4):press('Up')
        press('Return');wait(lambda r:r['scene']=='ranking');time.sleep(1.2)
        subprocess.run(['import','-window',window,str(out/'scores.png')],check=True)
        press('Escape');wait(lambda r:r['scene']=='menu')
        x('key','Escape');process.wait(timeout=15);assert process.returncode==0
        after={p.name:sha(p) for p in save.iterdir() if p.is_file()};assert before==after
        rows=[row(line) for line in trace.read_text().splitlines() if line.startswith('R ')]
        assert rows and all(r['audio_opens']==0 and r['audio_failed']==0 for r in rows)
        return dict(passed=True,command=command,files_before=before,files_after=after,trace_sha256=sha(trace),
                    scope='New OS process reloads same physical files, naturally reaches menu/Scores/back/exit; file identities preserved. Screenshot is observation, not new independent original-pixel equality.')
    finally:
        subprocess.run(['xdotool','keyup','Escape','Up','Return'],check=False)
        if process.poll() is None:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait()
        log.close()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('exe','hdi','font','output','ranked-fixture'):parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args();root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root)
    exe,hdi,font,fixture=[p.resolve() for p in (a.exe,a.hdi,a.font,a.ranked_fixture)]
    require_elf_x86_64(exe)
    assert sha(hdi)=='0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
    assert sha(font)=='41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'
    pins={str(p):sha(p) for p in (exe,hdi,font,fixture)};out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    cases=[]
    for name,seed in [('unranked',None),('ranked',fixture)]:
        result=trial(exe,hdi,font,out/name,seed)
        result['restart']=restart(exe,hdi,font,out/name/'saves',out/(name+'-restart'))
        cases.append(dict(name=name,**result))
        assert source_manifest(root)[0]==mf
        for path,h in pins.items():assert sha(path)==h
        (out/(name+'-receipt.json')).write_text(json.dumps(result,indent=2)+'\n');print(name,result['gameover'],flush=True)
    (out/'receipt.json').write_text(json.dumps(dict(passed=True,source_manifest=mf,source_inputs=len(files),inputs=pins,cases=cases,scope=__doc__),indent=2)+'\n')
if __name__=='__main__':main()
