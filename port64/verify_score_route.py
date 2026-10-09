#!/usr/bin/env python3
"""Bounded Quit/score-only MAINE frontend integration and original dispatch.

Actual OP/STD combat/contact reach Quit; native writer-close, registration,
verdict, fresh OP and second MAIN assertions run in the frontend fixture.
Original MAINE _main and frame_delay(100) execute at two loads. Initialization,
registration/verdict child calls, sound/exec are guarded adapters; measured
native child durations are supplied explicitly. This proves dispatch/order and
the100-refresh delay, not independent whole-child pixels or a complete game.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from unicorn.x86_const import UC_X86_REG_CS
from verify_congratulations import Original as MainOriginal, MAIN_SHA
from verify_cutscene import PAYLOAD_SHA
from verify import source_manifest, require_elf_x86_64

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class Original(MainOriginal):
    def body(self, u, address):
        cs=u.reg_read(UC_X86_REG_CS);segment=cs-self.load;ip=address-cs*16
        if segment==0xcc7 and ip==0x33:
            self.flow.append(['delay100',self.clock])
        super().body(u,address)
        if segment==0xa05 and ip in (0x27c4,0x20a8):
            self.clock+=self.child_ticks[0 if ip==0x27c4 else 1]

def controls(target, decoded, scenes):
    labels=('delay100','register','verdict','sound_fade4','exec_op')
    cases=[]
    for load in (0x1000,0x2000):
        original=Original(target,decoded,load);rows=[]
        for file in sorted(scenes.glob('*/flow.txt')):
            if not file.stat().st_size:continue  # Separately native-controlled failure.
            name=file.parent.name;character=int(name[1]);rank=int(name[4])
            flow=[list(map(int,row.split())) for row in file.read_text().splitlines()]
            assert [k for k,t in flow]==list(range(5)) and flow[0][1]==0
            original.child_ticks=[flow[2][1]-flow[1][1],flow[4][1]-flow[2][1]]
            assert min(original.child_ticks)>0
            original.run(character,rank,0,clock=True)
            expected=[[labels[k],tick] for k,tick in flow]
            assert original.flow==expected, (name,original.flow,expected)
            rows.append(dict(scene=name,flow=original.flow,child_duration_adapters=original.child_ticks))
        assert len(rows)==24
        cases.append(rows)
    assert cases[0]==cases[1], 'original MAINE dispatch changed with load segment'
    return cases[0]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','decoded-dir','hdi','font-bmp','exe','output-dir'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();out=args.output_dir.resolve()
    if out.exists():raise ValueError('use a fresh output directory')
    out.mkdir(parents=True)
    command=[str(args.exe.resolve()),'--hdi',str(args.hdi.resolve()),
        '--font-bmp',str(args.font_bmp.resolve()),'--mute','--score-route-checks',str(out/'scenes')]
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
    (out/'native.txt').write_bytes(result.stdout);(out/'stderr.txt').write_bytes(result.stderr)
    assert result.returncode==0, result.stderr.decode(errors='replace')
    lines=result.stdout.decode().splitlines()
    assert sum(row.startswith('SCORE_ROUTE ') for row in lines)==24
    assert sum(row.startswith('SCORE_ROUTE_FAILED ') for row in lines)==4
    rows=controls(args.target,args.decoded_dir,out/'scenes')
    original=out/'original.json';original.write_text(json.dumps(rows,indent=2)+'\n')
    mf,files=source_manifest(Path(__file__).resolve().parents[1]);require_elf_x86_64(args.exe)
    outputs={f.relative_to(out/'scenes').as_posix():sha(f) for f in sorted((out/'scenes').rglob('*')) if f.is_file()}
    receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),muted=True,
        source_manifest=mf,source_files=len(files),executable_sha256=sha(args.exe),
        target_sha256=sha(args.target),hdi_sha256=sha(args.hdi),font_sha256=sha(args.font_bmp),
        payload_sha256=PAYLOAD_SHA,main_body_sha256=MAIN_SHA,command=command,
        natural_bounded_routes=24,failed_writer_routes=4,original_cpu_reexecuted=True,
        load_segments=[4096,8192],original_sha256=sha(original),outputs=outputs,
        scope=__doc__)
    (out/'source-manifest.json').write_text(json.dumps(dict(sha256=mf,files=files),indent=2)+'\n')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS24 bounded OP/STD/Quit/registration/verdict/fresh OP/second MAIN routes;4 failed writers; two-load original MAINE dispatch/delay')
if __name__=='__main__':main()
