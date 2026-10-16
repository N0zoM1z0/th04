#!/usr/bin/env python3
"""Compare all title fields, complete TRAM, BB calls and four GRCG planes."""
import argparse,gzip,hashlib,json,os,struct,subprocess,sys,tempfile
from pathlib import Path
from verify import source_manifest,require_elf_x86_64
sha=lambda data:hashlib.sha256(data).hexdigest()

def configured():
    rows=[]
    # Complete stage/BGM lifecycles, all playchars, names and halfwidth lengths.
    for stage in range(7):
        for character in range(2):
            rows.append(('S',stage,character,0,399 if stage%2 else -16,1,0))
            rows.extend(('U',) for _ in range(228))
            rows.append(('B',));rows.extend(('U',) for _ in range(228))
    # Gengetsu's alternate ID and every legal table entry under a boss callback.
    for bgm in range(17):
        rows.append(('S',0,0,bgm,9,1,1));rows.extend(('U',) for _ in range(33))
        rows.append(('F',0,192,0,0,bgm,0,0,0,1));rows.extend(('U',) for _ in range(36))
    # Shared sprite/clock edges, including BYTE wrapping and the distinct reset.
    for boss in (0,1):
        for frame in (31,32,33,191,192,193,223,224,225,254,255):
            for sprite in (0,15,16,22,23,24,255):
                if frame<192 and sprite>=24:continue
                rows.append(('S',0,0,0,0,0,boss))
                rows.append(('F',frame if not boss else 0,frame if boss else 0,sprite,0,0,22,14,14,boss))
    return rows

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('dos-root','exe','bb','output-dir'):parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args();root=Path(__file__).resolve().parents[1];dos=a.dos_root.resolve();sys.path.insert(0,str(dos/'scripts/runtime'))
    import unicorn
    if unicorn.__version__!='2.1.4':raise ValueError('title Oracle requires pinned Unicorn2.1.4;1.0.2 misexecutes strlen RETF after REPNE')
    from verify_dos_hud_titles import TitlesMachine
    manifest,sources=source_manifest(root);require_elf_x86_64(a.exe);out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    rows=configured();plan='\n'.join(' '.join(map(str,row)) for row in rows)+'\n';(out/'vectors.txt').write_text(plan)
    profiles=[];bb=a.bb.read_bytes()
    for load in (0x1000,0x3333):
        machine=TitlesMachine(load,bb);differences=[];native_digest=hashlib.sha256();original_digest=hashlib.sha256();failures=0
        with (out/'vectors.txt').open('rb') as source,(out/('stderr-%04x.txt'%load)).open('wb') as errors,gzip.open(out/('original-%04x.jsonl.gz'%load),'wt',compresslevel=1) as transcript:
            process=subprocess.Popen([str(a.exe.resolve()),'--vectors',str(a.bb.resolve())],stdin=source,stdout=subprocess.PIPE,stderr=errors,env=dict(os.environ,UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
            try:
                for index,op in enumerate(rows):
                    if op[0]=='S':
                        _,stage,character,bgm,scroll,active,boss=op;machine.seed(stage,character,bgm,scroll,active);machine.write(0x469c,'H',0x66a5 if boss else 0x6446)
                    elif op[0]=='B':
                        bgm=stage*2+2 if stage!=3 or character==0 else 16
                        machine.write(0x469a,'B',bgm);machine.write(0x469c,'H',0x66a5)
                    elif op[0]=='F':
                        _,frame,boss_frame,sprite,stage_id,bgm,sl,bl,bossl,boss=op
                        for at,fmt,value in ((0x46a0,'B',frame),(0x1b63,'B',boss_frame),(0x1bb6,'B',sprite),(0x4684,'B',stage_id),(0x469a,'B',bgm),(0x4680,'h',sl),(0x4682,'h',bl),(0x4686,'h',bossl),(0x469c,'H',0x66a5 if boss else 0x6446)):machine.write(at,fmt,value)
                    expected=machine.call();header=process.stdout.readline();pieces=header.decode().rstrip('\n').split('|')
                    fields=[expected['titles'],expected['boss'],expected['sprite'],expected['stage_id'],expected['bgm_id'],*expected['lengths'],expected['callback']]
                    actual_fields=list(map(int,pieces[0].split()));draws=[tuple(map(int,piece.split())) for piece in pieces[1:]]
                    actual=process.stdout.read(16384+131072)
                    if len(actual)!=147456:raise ValueError('incomplete native title vector')
                    expected_bytes=expected.pop('text')+expected.pop('graphics');native_digest.update(header+actual)
                    expected_header=(' '.join(map(str,fields))+''.join('|'+' '.join(map(str,draw)) for draw in expected['draws'])+'\n').encode();original_digest.update(expected_header+expected_bytes)
                    wrong=[]
                    if actual_fields!=fields:wrong.append('fields')
                    if draws!=expected['draws']:wrong.append('BB calls')
                    if actual[:16384]!=expected_bytes[:16384]:wrong.append('complete TRAM')
                    if actual[16384:]!=expected_bytes[16384:]:wrong.append('four complete graphics planes')
                    if wrong:
                        failures+=1
                        if len(differences)<8:differences.append(dict(index=index,operation=op,wrong=wrong,original=fields,native=actual_fields,original_draws=expected['draws'][:2],native_draws=draws[:2]))
                    transcript.write(json.dumps(dict(index=index,operation=op,state=expected,bytes_sha256=sha(expected_bytes)))+'\n')
                if process.stdout.read(1):raise ValueError('trailing native title vectors')
                if process.wait(timeout=30):raise ValueError('native title vector process failed')
            finally:
                if process.poll() is None:process.kill();process.wait()
        profiles.append(dict(load_segment=load,cases=len(rows),differing_cases=failures,differences=differences,native_sha256=native_digest.hexdigest(),original_sha256=original_digest.hexdigest(),visited_original_instructions=len(machine.visited)))
        print('TITLE ORACLE',hex(load),'cases',len(rows),'different',failures,flush=True)
    if source_manifest(root)[0]!=manifest:raise ValueError('title source closure changed')
    result=dict(passed=all(not row['differing_cases'] for row in profiles),profiles=profiles,source_manifest_sha256=manifest,source_files=sources,executable_sha256=sha(a.exe.read_bytes()),bb_sha256=sha(bb),unicorn_version=unicorn.__version__,unicorn_library_sha256=sha(Path(unicorn.__file__).parent.joinpath('lib/libunicorn.so.2').read_bytes()),oracle_sources={str(p):sha(p.read_bytes()) for p in (dos/'scripts/runtime/verify_dos_hud_titles.py',dos/'scripts/runtime/verify_dos_hud_popup.py',dos/'scripts/runtime/verify_dos_text_gaiji.py',dos/'scripts/runtime/verify_dos_vsync_lifecycle.py')},files={p.name:sha(p.read_bytes()) for p in out.iterdir()},scope=__doc__+' Actual original callbacks, CRT strlen, text/gaiji, scroll helper and BB blitter. Only GRCG hardware and a caller return sentinel are adapted. All original OUTs retained in transcripts. Includes every legal string ID, both playchars, full lifecycles, rolling, shared-clock transitions and BYTE edges at two loads. No timing, complete natural picture, process/campaign or exact promotion.')
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=result['passed'],profiles=profiles)));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
