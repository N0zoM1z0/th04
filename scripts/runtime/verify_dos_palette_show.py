#!/usr/bin/env python3
"""Compare original and rebuilt palette_show port transcripts, including LCD.

Inputs are explicit palette/tone/PaletteNote values and notebook query bytes.
IN/OUT hooks record every port operation without accessing host hardware.
Original LCD self-modification remains enabled. This compares instruction I/O
and far-return state, not physical LCD output or elapsed hardware timing.
"""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re
import struct

import unicorn
from unicorn.x86_const import *

from verify_dos_vsync_lifecycle import original, candidate

SHA = lambda raw: hashlib.sha256(raw).hexdigest()

def fixtures():
    palettes = [bytes(48), bytes([255]*48), bytes((i*73+19)&255 for i in range(48))]
    tones = (-32768,-1,0,1,6,50,99,100,101,150,199,200,201,32767,32768,65535,65536,65736,131071)
    queries = ((0,0),(1,0),(255,0),(255,4))
    rows = [dict(tone=tone,note=note,query=list(query),palette=list(palette))
            for tone,note,query,palette in itertools.product(tones,(0,1,2,65535),queries,palettes)]
    for block,tone,query in itertools.product(range(256),(0,100,101,150,200),queries[:2]):
        palette=[]
        for lane in range(16):
            index=block*16+lane;r=index>>8;g=(index>>4)&15;b=index&15
            palette.extend(((r<<4)|((g+b)&15),(g<<4)|((r^b)&15),(b<<4)|((r+g+b)&15)))
        rows.append(dict(tone=tone,note=1,query=list(query),palette=palette))
    return rows

def original_record(artifact):
    record=original(artifact)
    entry,tone,note,palette={'main':(0x1f04,0x3a4,0x3d6,0x2a82),
                            'op':(0x1de0,0x586,0x5b8,0x1a96),
                            'maine':(0x19ec,0x132,0x164,0xeca)}[artifact]
    # The whole function includes both far returns and the LCD branch.
    code=bytes(record['body'][entry:entry+266])
    assert code[:3]==b'\xfc\x56\xa1' and code[3:5]==struct.pack('<H',tone)
    assert code[-3:]==b'\x5f\x5e\xcb'
    record.update(cs=0,entry=entry,tone=tone,note=note,palette=palette,
                  code_extent=266,code_sha256=SHA(code),original=True)
    return record

def compiled_record(exe, mp):
    record=candidate(exe,mp,Path(__file__))
    text=mp.read_text()
    def public(name, optional=False):
        hits=set(re.findall(r'(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?'+re.escape(name)+r'\s*$',text))
        if optional and not hits:return None
        assert len(hits)==1,(name,hits)
        return tuple(int(x,16) for x in hits.pop())
    cs,entry=public('PALETTE_SHOW');dg,tone=public('_PaletteTone');dg2,palette=public('_Palettes')
    assert dg==dg2==record['dg']
    note=public('_PaletteNote',True)
    if note:assert note[0]==dg
    record.update(cs=cs,entry=entry,tone=tone,note=note[1] if note else None,
                  palette=palette,original=False)
    return record

def run(record,load,row):
    body=bytearray(record['body'])
    for at in record['sites']:
        value=struct.unpack_from('<H',body,at)[0];struct.pack_into('<H',body,at,(value+load)&65535)
    cpu=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16)
    cpu.mem_map(0,0x110000);cpu.mem_write(load*16,bytes(body))
    ds=load+record['dg'];cs=load+record['cs']
    for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x7000),
        (UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0xabcd),(UC_X86_REG_SI,0x1357),
        (UC_X86_REG_DI,0x2468),(UC_X86_REG_EFLAGS,2)):
        cpu.reg_write(reg,value)
    cpu.mem_write(0x7f000,struct.pack('<HH',0xff00,load))
    palette=bytes(row['palette']);tone=struct.pack('<H',row['tone']&65535)
    cpu.mem_write(ds*16+record['palette'],palette);cpu.mem_write(ds*16+record['tone'],tone)
    if record['note'] is not None:cpu.mem_write(ds*16+record['note'],struct.pack('<H',row['note']))
    io=[];patches=[];done=False
    def output(u,port,size,value,unused):
        assert size==1 and port in (0xa8,0xac,0xaa,0xae,0xf6),(port,size)
        io.append(['out',port,value])
    def input(u,port,size,unused):
        assert size==1 and port in (0x871e,0xae8e),(port,size)
        value=row['query'][0 if port==0x871e else 1];io.append(['in',port,value]);return value
    def finish(u,address,size,unused):
        nonlocal done
        done=True;u.emu_stop()
    def patch(u,access,address,size,value,unused):
        patches.append([address-load*16,size,value])
    cpu.hook_add(unicorn.UC_HOOK_INSN,output,None,1,0,UC_X86_INS_OUT)
    cpu.hook_add(unicorn.UC_HOOK_INSN,input,None,1,0,UC_X86_INS_IN)
    cpu.hook_add(unicorn.UC_HOOK_CODE,finish,None,load*16+0xff00,load*16+0xff00)
    if record['original']:
        cpu.hook_add(unicorn.UC_HOOK_MEM_WRITE,patch,None,load*16+record['entry'],load*16+record['entry']+265)
    cpu.emu_start(cs*16+record['entry'],0x10ffff,count=100000)
    assert done and cpu.reg_read(UC_X86_REG_SP)==0xf004
    for reg,value in ((UC_X86_REG_DS,ds),(UC_X86_REG_BP,0xabcd),(UC_X86_REG_SI,0x1357),(UC_X86_REG_DI,0x2468)):
        assert cpu.reg_read(reg)==value
    assert bytes(cpu.mem_read(ds*16+record['palette'],48))==palette
    assert bytes(cpu.mem_read(ds*16+record['tone'],2))==tone
    if record['note'] is not None:assert struct.unpack('<H',cpu.mem_read(ds*16+record['note'],2))[0]==row['note']
    if record['original']:
        assert len(patches)==int(row['note']!=0)
        if patches:assert patches[0][:2]==[record['entry']+0xe8,1]
    return dict(io=io,sp=0xf004,patches=patches)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--reference',type=Path)
    parser.add_argument('--exe',type=Path)
    parser.add_argument('--map',type=Path)
    parser.add_argument('--artifact',choices=('main','op','maine'))
    parser.add_argument('--diagnostic',action='store_true')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    rows=fixtures();total=0;differences=[];originals={}
    if not args.reference:
        assert not args.exe and not args.map and not args.diagnostic
        (args.output/'fixtures.json').write_text(json.dumps(rows)+'\n')
        for artifact in ((args.artifact,) if args.artifact else ('main','op','maine')):
            record=original_record(artifact);originals[artifact]={k:record[k] for k in ('pins','entry','tone','note','palette','code_extent','code_sha256')}
            (args.output/(artifact+'.bin')).write_bytes(bytes(record['body'][record['entry']:record['entry']+266]))
            with gzip.open(args.output/(artifact+'.jsonl.gz'),'wt') as stream:
                for load in (0x1000,0x3333):
                    for index,row in enumerate(rows):
                        result=run(record,load,row);result.update(load=load,index=index)
                        stream.write(json.dumps(result,separators=(',',':'))+'\n');total+=1
            print('Original palette output PASS',artifact,flush=True)
    else:
        ref=json.loads((args.reference/'receipt.json').read_text());assert ref['passed']
        for name,pin in ref['files'].items():assert SHA((args.reference/name).read_bytes())==pin
        assert json.loads((args.reference/'fixtures.json').read_text())==rows
        assert args.exe and args.map and args.artifact
        record=compiled_record(args.exe,args.map)
        with gzip.open(args.reference/(args.artifact+'.jsonl.gz'),'rt') as expected,gzip.open(args.output/'compiled.jsonl.gz','wt') as stream:
            for line in expected:
                old=json.loads(line);result=run(record,old['load'],rows[old['index']]);result.update(load=old['load'],index=old['index'])
                stream.write(json.dumps(result,separators=(',',':'))+'\n');total+=1
                if result['io']!=old['io']:differences.append(dict(index=old['index'],load=old['load']))
        originals=ref['originals']
    receipt=dict(passed=not differences,diagnostic=args.diagnostic,cases=total,fixture_count=len(rows),differences=differences,
        originals=originals,source_sha256=SHA(Path(__file__).read_bytes()),
        exe_sha256=SHA(args.exe.read_bytes()) if args.exe else None,map_sha256=SHA(args.map.read_bytes()) if args.map else None,
        reference_receipt_sha256=SHA((args.reference/'receipt.json').read_bytes()) if args.reference else None,
        files={p.name:SHA(p.read_bytes()) for p in args.output.iterdir()},scope=__doc__)
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    assert bool(differences)==args.diagnostic
    print('Palette output', 'PREDECESSOR REJECTED' if differences else 'PASS',total,len(differences),flush=True)

if __name__=='__main__':main()
