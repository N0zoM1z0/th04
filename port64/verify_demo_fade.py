#!/usr/bin/env python3
"""Compare Demo blackout WORD speed, all palette publications and tone stores.

Reuse complete OP/MAINE blackout instruction controls and full wait streams.
Each wait represents one explicit logical refresh; physical IRQ/CPU timing is
outside this model. The actual old Demo source is checked with a bounded clock.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
import struct,subprocess,sys,tomllib

sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('root','native','reference','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--predecessor',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    prior=json.loads((args.reference/'receipt.json').read_text());assert prior['passed'] and prior['original_controls']==96
    for name,pin in prior['files'].items():assert sha(args.reference/name)==pin,name
    controls=json.loads((args.reference/'original.json').read_text());assert len(controls)==96
    targets=tomllib.loads((args.root/'config/targets.toml').read_text())['artifacts']
    for artifact in ('op','maine'):
        target=next(row for row in targets if row['id']=='th04-'+artifact);packed=args.root/target['private_path']
        assert packed.stat().st_size==target['size'] and sha(packed)==target['sha256']==prior['originals'][artifact]['pins']['packed']
        fn=prior['originals'][artifact]['functions']['0'];assert fn['entry']=='0000:0666' and fn['length']==62
        assert sha(args.reference/(artifact+'-0.bin'))==fn['sha256']
    selected=[row for row in controls if row['direction']==0];assert len(selected)==48
    for row in selected:
        digest=hashlib.sha256();size=0;last=0
        with gzip.open(args.reference/row['carrier'],'rb') as stream:
            while raw:=stream.read(65532):
                assert len(raw)%6==0;digest.update(raw);size+=len(raw)
                for tick,tone in struct.iter_unpack('<Ih',raw):
                    assert tick==last+1;last=tick
        assert size==row['wait_bytes']==row['waits']*6 and digest.hexdigest()==row['wait_expanded_sha256']
        assert last==row['waits'] and len(row['shows'])==18 and len(row['tone_writes'])==19
    baseline=[row for row in selected if row['artifact']=='op' and row['load']=='1000'];assert len(baseline)==12
    vectors=args.output/'vectors.txt';vectors.write_text(''.join(str(row['speed'])+'\n' for row in baseline))
    command=[str(args.native.resolve()),'--fade-shows',str(vectors.resolve())]
    result=subprocess.run(command,capture_output=True)
    (args.output/'native.txt').write_bytes(result.stdout);(args.output/'stderr.txt').write_bytes(result.stderr)
    assert result.returncode==0 and not result.stderr,(result.returncode,result.stderr)
    native=[];current=None
    for line in result.stdout.decode().splitlines():
        columns=line.split();kind=columns[0];values=list(map(int,columns[1:]))
        if kind=='CASE':
            assert values==[len(native)];current=dict(shows=[],stores=[],folded=[]);native.append(current)
        elif kind=='SHOW':current['shows'].append(values)
        elif kind=='STORE':current['stores'].append(values)
        elif kind=='TONE':current['folded'].append(values)
        else:assert kind=='END' and len(values)==1;current['waits']=values[0]
    assert len(native)==12
    for row,observed in zip(baseline,native):
        assert observed['shows']==row['shows'] and observed['stores']==row['tone_writes'] and observed['waits']==row['waits']
        assert observed['folded'][-1]==[row['waits'],0]
        assert all(other['shows']==observed['shows'] and other['tone_writes']==observed['stores'] and other['waits']==observed['waits'] for other in selected if other['speed']==row['speed'])
    predecessor=[]
    if args.predecessor:
        arguments=''.join(f"{row['speed']} {row['waits']+2}\n" for row in baseline)
        old=subprocess.run([str(args.predecessor.resolve())],input=arguments.encode(),capture_output=True)
        (args.output/'predecessor.txt').write_bytes(old.stdout);(args.output/'predecessor-stderr.txt').write_bytes(old.stderr);assert old.returncode==0
        old_rows=[json.loads(line) for line in old.stdout.decode().splitlines()];assert len(old_rows)==12
        for row,observed in zip(baseline,old_rows):
            equal=observed['constructed'] and observed['finished'] and observed['ticks']==row['waits'] and observed['tone']==0
            if not equal:predecessor.append(dict(speed=row['speed'],argument_word=row['argument_word'],observed=observed))
        assert len(predecessor)==7
    receipt=dict(passed=True,original_controls=48,native_vectors=12,shows=216,tone_stores=228,predecessor_rejections=predecessor,
        command=command,native_sha256=sha(args.native),source_sha256=sha(Path(__file__)),original_receipt_sha256=sha(args.reference/'receipt.json'),reference=str(args.reference),originals=prior['originals'],
        files={path.name:sha(path) for path in args.output.iterdir()},scope=__doc__)
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Demo WORD fade PASS',len(selected),'original controls,12 vectors,216 shows,228 stores; old rejects',len(predecessor),flush=True)

if __name__=='__main__':main()
