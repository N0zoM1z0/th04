#!/usr/bin/env python3
"""Compare actual pending OP demo-entry frames with original palette instructions.

Only idle-menu preparation and 17 pending fade refreshes run. MAIN receives
no update. Original DAC writes are expanded through the retained analog DAC
projection; this is a component image check, not complete original OP scanout.
"""
import argparse
import array
import gzip
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()

def rgb8(value):
    six=(value<<2)|(value>>2)
    return (six<<2)|(six>>4)

def dac_image(operations):
    result=[0]*48;color=None
    for kind,port,value in operations:
        assert kind=='out'
        if port==0xa8:color=value;assert color<16
        else:
            assert color is not None and port in (0xac,0xaa,0xae)
            result[color*3+{0xac:0,0xaa:1,0xae:2}[port]]=value
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('root','native','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--reference',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    hdi=args.root/'.analysis/runtime/images/zun.hdi'
    font=args.root/'.analysis/runtime/candidates/dos-demo-v1369-original-video-v2/FREECG98.BMP'
    reset=args.root/'.analysis/runtime/candidates/dos-demo-v1365-original/receipt.json'
    reset_data=json.loads(reset.read_text());assert reset_data['capture_complete'] and reset_data['exit_code']==0 and not reset_data['timeout']
    inputs=args.output/'inputs';inputs.mkdir()
    score_record=reset_data['starting_files']['GENSOU  SCR'];score=bytes.fromhex(score_record['hex'])
    assert len(score)==score_record['size'] and hashlib.sha256(score).hexdigest()==score_record['sha256']
    (inputs/'scores.SCR').write_bytes(score)
    pins={str(path):sha(path) for path in (hdi,font,reset,inputs/'scores.SCR')}
    command=[str(args.native.resolve()),'--hdi',str(hdi),'--font-bmp',str(font),'--mute','--pmd-driver','none','--save-dir',str(inputs),'--demo-entry-palette-checks',str(args.output/'capture')]
    result=subprocess.run(command,capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
    (args.output/'stdout.log').write_bytes(result.stdout);(args.output/'stderr.log').write_bytes(result.stderr)
    assert result.returncode==0,(result.returncode,result.stderr.decode(errors='replace'))
    for path,pin in pins.items():assert sha(Path(path))==pin,path
    capture=args.output/'capture';raw_palette=(capture/'palette.bin').read_bytes();indices=(capture/'indices.bin').read_bytes()
    assert len(raw_palette)==48 and len(indices)==640*400 and max(indices)<16
    states=[list(map(int,line.split())) for line in (capture/'states.txt').read_text().splitlines()]
    assert len(states)==18
    expected_tones=[100]+[100-6*at for at in range(17)]
    assert [row[0] for row in states]==list(range(18)) and [row[1] for row in states]==expected_tones
    assert [row[2] for row in states]==[0]+[1]*17
    assert len({tuple(row[3:]) for row in states})==1
    if args.reference:
        prior=json.loads((args.reference/'receipt.json').read_text());assert prior['passed']
        assert prior['palette_sha256']==hashlib.sha256(raw_palette).hexdigest()
        assert prior['indices_sha256']==hashlib.sha256(indices).hexdigest()
        for name,pin in prior['oracle_files'].items():assert sha(args.reference/name)==pin,name
        oracle_path=args.reference/'original.jsonl.gz';oracle_receipt=args.reference/'oracle-receipt.json'
    else:
        frozen=args.root/'.analysis/worktrees/dos-palette-note-v1415'
        helper=frozen/'scripts/runtime/verify_dos_palette_show.py'
        sys.path.insert(0,str(helper.parent));from verify_dos_palette_show import original_record,run
        record=original_record('op');assert record['code_extent']==266
        oracle_path=args.output/'original.jsonl.gz';oracle_receipt=args.output/'oracle-receipt.json'
        with gzip.open(oracle_path,'wt') as stream:
            for load in (0x1000,0x3333):
                for at,tone in enumerate(expected_tones):
                    row=dict(tone=tone,note=0,query=[0,0],palette=list(raw_palette))
                    observation=run(record,load,row);observation.update(index=at,load=load,tone=tone)
                    stream.write(json.dumps(observation,separators=(',',':'))+'\n')
        (args.output/'op.bin').write_bytes(bytes(record['body'][record['entry']:record['entry']+266]))
        oracle_receipt.write_text(json.dumps(dict(passed=True,cases=36,original_pins=record['pins'],code_sha256=record['code_sha256'],helper=str(helper),helper_sha256=sha(helper),palette_sha256=hashlib.sha256(raw_palette).hexdigest()),indent=2)+'\n')
    original=json.loads(oracle_receipt.read_text());assert original['passed'] and original['cases']==36
    assert sha(Path(original['helper']))==original['helper_sha256']
    oracle_code=(args.reference if args.reference else args.output)/'op.bin'
    assert len(oracle_code.read_bytes())==266 and sha(oracle_code)==original['code_sha256']
    with gzip.open(oracle_path,'rt') as stream:observations=[json.loads(line) for line in stream]
    assert len(observations)==36
    for at in range(18):
        first,second=observations[at],observations[18+at]
        assert first['index']==second['index']==at and first['tone']==second['tone']==expected_tones[at]
        assert first['load']==0x1000 and second['load']==0x3333 and first['io']==second['io']
        assert first['sp']==second['sp']==0xf004 and len(first['io'])==64
    image=capture/'argb.bin';assert image.stat().st_size==18*len(indices)*4 and sys.byteorder=='little'
    differences=[];old_formula=[];baseline=None
    with image.open('rb') as stream:
        for at,tone in enumerate(expected_tones):
            pixels=array.array('I');pixels.frombytes(stream.read(len(indices)*4));assert pixels.itemsize==4
            dac=dac_image(observations[at]['io']);colors=[0xff000000|(rgb8(dac[c*3])<<16)|(rgb8(dac[c*3+1])<<8)|rgb8(dac[c*3+2]) for c in range(16)]
            expected=array.array('I',(colors[index] for index in indices))
            bad=sum(a!=b for a,b in zip(pixels,expected))
            if bad:differences.append(dict(index=at,tone=tone,pixels=bad))
            if baseline is None:baseline=pixels
            else:
                # The retired source multiplied already expanded RGB8 channels.
                # This is its formula projection, not a compiled prior program.
                old=array.array('I',(0xff000000|((((value>>16)&255)*tone//100)<<16)|((((value>>8)&255)*tone//100)<<8)|((value&255)*tone//100) for value in baseline))
                old_bad=sum(a!=b for a,b in zip(old,expected))
                if old_bad:old_formula.append(dict(index=at,tone=tone,pixels=old_bad))
        assert not stream.read(1)
    image_pin=sha(image);compressed=capture/'argb.bin.gz'
    with image.open('rb') as source,gzip.open(compressed,'wb') as sink:
        while raw:=source.read(1048576):sink.write(raw)
    with gzip.open(compressed,'rb') as stream:assert hashlib.sha256(stream.read()).hexdigest()==image_pin
    image.unlink()
    record=dict(passed=not differences,snapshots=18,pixels_checked=18*len(indices),original_controls=36,differences=differences,old_rgb8_formula_differences=old_formula,
        palette_sha256=hashlib.sha256(raw_palette).hexdigest(),indices_sha256=hashlib.sha256(indices).hexdigest(),argb_expanded_sha256=image_pin,
        native_sha256=sha(args.native),source_sha256=sha(Path(__file__)),command=command,input_pins=pins,
        oracle_files={str(path.relative_to(args.output)):sha(path) for path in (oracle_path,oracle_receipt,oracle_code) if args.output in path.parents},
        oracle_reference=str(args.reference) if args.reference else None,oracle_receipt_sha256=sha(oracle_receipt),
        files={str(path.relative_to(args.output)):sha(path) for path in args.output.rglob('*') if path.is_file()},scope=__doc__)
    (args.output/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    assert not differences and len(old_formula)==16
    print('Demo entry palette PASS',len(states),record['pixels_checked'],'pixels; old formula differs in',len(old_formula),'frames',flush=True)

if __name__=='__main__':main()
