#!/usr/bin/env python3
"""Actual SDL/X11 muted startup across three drivers and all nine BGM/SE modes."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
NATIVE=Path(__file__).resolve().parents[1]
from verify_host_window import latest,row
from verify import require_elf_x86_64
from private_x11 import require_private_xvfb

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('exe','hdi','font','rom','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--exe-sha256',required=True)
    a=parser.parse_args();private_display=require_private_xvfb();exe,hdi,font,rom=[p.resolve() for p in (a.exe,a.hdi,a.font,a.rom)]
    require_elf_x86_64(exe);assert sha(exe)==a.exe_sha256
    assert sha(hdi)=='0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
    assert sha(font)=='41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'
    assert sha(rom)=='53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8'
    pins={str(p):sha(p) for p in [exe,hdi,font,rom,Path(__file__),NATIVE/'port64/verify_host_window.py',NATIVE/'port64/private_x11.py']}
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);cases=[]
    for driver in ['pmd','pmd86','pmdb2']:
      for bgm in range(3):
       for se in range(3):
        name=f'{driver}-{bgm}-{se}';folder=out/name;folder.mkdir();save=folder/'saves';save.mkdir()
        cfg=bytes([1,6,2,bgm,se,1,0,0,0,10+bgm+se]);(save/'MIKO.CFG').write_bytes(cfg);(folder/'initial-MIKO.CFG').write_bytes(cfg)
        trace=folder/'trace/window.tsv';command=[str(exe),'--hdi',str(hdi),'--font-bmp',str(font),'--save-dir',str(save),'--title','--mute','--pmd-driver',driver,'--window-trace',str(trace.parent)]
        if driver!='pmd':command+=['--opna-rom',str(rom)]
        log=(folder/'window.log').open('wb');process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);started=time.monotonic()
        def x(*args):return subprocess.run(['xdotool',*args],check=True,capture_output=True,text=True).stdout.strip()
        try:
            deadline=time.monotonic()+90;window=None;r=None
            while time.monotonic()<deadline:
                if process.poll() is not None:raise RuntimeError('window exited before menu')
                r=latest(trace)
                if r:
                    if window is None:
                        windows=x('search','--onlyvisible','--pid',str(process.pid)).splitlines();assert len(windows)==1;window=windows[0];x('windowfocus','--sync',window)
                    assert r['audio_opens']==r['audio_failed']==0
                    if r['scene']=='menu':break
                time.sleep(.01)
            assert window and r['scene']=='menu','natural startup did not reach menu'
            x('key','Escape');process.wait(timeout=15);assert process.returncode==0
            assert (save/'MIKO.CFG').read_bytes()==cfg
            lines=trace.read_text().splitlines()
            terminal=[list(map(int,l.split()[1:])) for l in lines if l.startswith('E ')]
            rows=[row(l) for l in lines if l.startswith('R ')]
            assert len(terminal)==1 and terminal[0][0]==len(rows) and terminal[0][4:]==[0,0];assert rows and rows[0]['scene']=='startup' and rows[-1]['scene']=='menu'
            assert all(r['audio_opens']==r['audio_failed']==0 for r in rows)
            record=dict(passed=True,name=name,driver=driver,bgm=bgm,se=se,command=command,menu_refresh=r['seq'],refreshes=len(rows),elapsed=time.monotonic()-started,trace_sha256=sha(trace),cfg_sha256=sha(save/'MIKO.CFG'),score_sha256=sha(save/'GENSOU.SCR'))
            (folder/'receipt.json').write_text(json.dumps(record,indent=2)+'\n');cases.append(record);print(name,record['refreshes'],'PASS',flush=True)
            for p,h in pins.items():assert sha(p)==h
        finally:
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait()
            log.close()
    (out/'receipt.json').write_text(json.dumps(dict(passed=True,private_display=private_display,count=len(cases),pins=pins,cases=cases,scope=__doc__+' Natural logo/fireworks/title/menu on actual SDL/X11 under private Xvfb; ordinary Escape after menu; no physical audio or complete route acceptance.'),indent=2)+'\n')
if __name__=='__main__':main()
