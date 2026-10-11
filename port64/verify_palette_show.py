#!/usr/bin/env python3
"""Compare shared native palette output and the actual startup DAC consumer.

Reuse full instruction transcripts from the three attested DOS originals.
The notebook query bytes are explicit inputs. This checks port order, DAC
register values and native consumer dispatch; it does not simulate LCD scanout.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()

def dac_image(operations):
    dac=[0]*48;color=None
    for kind,port,value in operations:
        if kind!='out':continue
        if port==0xa8:color=value;assert 0<=color<16
        elif port in (0xac,0xaa,0xae):
            assert color is not None and 0<=value<=15
            dac[color*3+{0xac:0,0xaa:1,0xae:2}[port]]=value
        else:assert port==0xf6 and value==0xa0
    return dac

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('root','reference','native','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--diagnostic',action='store_true')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    targets=tomllib.loads((args.root/'config/targets.toml').read_text())['artifacts']
    sys.path.insert(0,str(args.root/'scripts'));from lib.pc98 import parse_mz
    rows=json.loads((args.reference/'original/fixtures.json').read_text());assert len(rows)==3472
    command=[str(args.native.resolve()),'--rows']
    lines=[' '.join(map(str,[row['tone'],row['note'],*row['query'],*row['palette']])) for row in rows]
    raw=args.output/'native.jsonl'
    with raw.open('xb') as out:
        result=subprocess.run(command,input='\n'.join(lines)+'\n',text=True,stdout=out,stderr=subprocess.PIPE)
    (args.output/'stderr.txt').write_text(result.stderr)
    assert result.returncode==0,(result.returncode,result.stderr)
    results=[json.loads(line) for line in raw.read_text().splitlines()];assert len(results)==len(rows)
    raw_hash=sha(raw)
    compressed=args.output/'native.jsonl.gz'
    with raw.open('rb') as source,gzip.open(compressed,'wb') as sink:shutil.copyfileobj(source,sink)
    with gzip.open(compressed,'rb') as source:
        assert hashlib.sha256(source.read()).hexdigest()==raw_hash
    raw.unlink()
    differences=[];cases=0;references={}
    for artifact in ('main','op','maine'):
        folder=args.reference/('original' if artifact=='main' else 'original-'+artifact)
        receipt=json.loads((folder/'receipt.json').read_text());assert receipt['passed'] and receipt['cases']==6944
        for name,pin in receipt['files'].items():assert sha(folder/name)==pin,name
        assert json.loads((folder/'fixtures.json').read_text())==rows
        source=Path(receipt['source_carrier']) if 'source_carrier' in receipt else args.reference.parents[3]/'scripts/runtime/verify_dos_palette_show.py'
        assert sha(source)==receipt['source_sha256']
        original=receipt['originals'][artifact]
        assert len((folder/(artifact+'.bin')).read_bytes())==266
        assert sha(folder/(artifact+'.bin'))==original['code_sha256']
        target=next(record for record in targets if record['id']=='th04-'+artifact)
        packed=args.root/target['private_path'];assert packed.stat().st_size==target['size']
        assert sha(packed)==target['sha256']==original['pins']['packed'] and parse_mz(packed.read_bytes()).valid
        references[artifact]=dict(receipt_sha256=sha(folder/'receipt.json'),files=receipt['files'],original=original,producer_source_sha256=sha(source))
        seen=set();total=0
        with gzip.open(folder/(artifact+'.jsonl.gz'),'rt') as stream:
            for line in stream:
                original_row=json.loads(line);index=original_row['index'];row=rows[index]
                assert original_row['load'] in (0x1000,0x3333) and original_row['sp']==0xf004
                identity=(original_row['load'],index);assert identity not in seen;seen.add(identity);total+=1
                if args.diagnostic and row['note']:continue
                native=results[index];expected=dac_image(original_row['io']);bad=[]
                if native['startup']!=expected:bad.append('startup-dac')
                if not args.diagnostic:
                    if native['dac']!=expected:bad.append('dac')
                    if native['io']!=original_row['io']:bad.append('ordered-io')
                    if native['startup_reads']!=[port for kind,port,value in original_row['io'] if kind=='in']:bad.append('startup-query')
                if bad:differences.append(dict(artifact=artifact,index=index,load=original_row['load'],fields=bad))
                cases+=1
        assert total==6944
    record=dict(passed=not differences,diagnostic=args.diagnostic,cases=cases,fixture_count=len(rows),differences=differences,
        command=command,native_sha256=sha(args.native),source_sha256=sha(Path(__file__)),native_expanded_sha256=raw_hash,
        references=references,files={path.name:sha(path) for path in args.output.iterdir()},scope=__doc__)
    (args.output/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    assert bool(differences)==args.diagnostic
    print('Native palette', 'PREDECESSOR REJECTED' if differences else 'PASS',cases,len(differences),flush=True)

if __name__=='__main__':main()
