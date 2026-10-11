#!/usr/bin/env python3
"""Compare the actual native TextPlane with original MAIN/MAINE text writers."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_exact(stream, size):
    data=stream.read(size)
    if len(data)!=size:
        raise ValueError(('incomplete text comparison stream',size,len(data)))
    return data


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--dos-root',type=Path,required=True)
    parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--reference',type=Path,
                        help='replay a retained original transcript instead of executing it again')
    args=parser.parse_args()
    root=args.dos_root.resolve()
    sys.path.insert(0,str(root/'scripts/runtime'))
    from verify_dos_text_gaiji import configured,Machine,original,START,END
    rows=configured();profiles=[];machines=[]
    for artifact,putca,putsa,textseg in (
            ('main',0x1b0c,0x1b50,0x768),('maine',0xfc4,0x1008,0x3f6)):
        target=original(artifact)
        target.update(putca=(0,putca),putsa=(0,putsa),textseg=textseg)
        for load in (0x1000,0x3333):
            profiles.append(dict(artifact=artifact,load=f'{load:04x}',pins=target['pins'],
                                 putca=f'0000:{putca:04X}',putsa=f'0000:{putsa:04X}',
                                 text_segment=f"{target['dg']:04X}:{textseg:04X}"))
            if not args.reference:machines.append(Machine(target,load))
    dependencies=('scripts/runtime/verify_dos_text_gaiji.py',
                  'scripts/runtime/verify_dos_vsync_lifecycle.py','scripts/lib/pc98.py')
    producers={name:sha((root/name).read_bytes()) for name in dependencies}
    prior=None
    if args.reference:
        prior=json.loads((args.reference/'receipt.json').read_text())
        assert prior['passed'] and prior['rows']==rows_as_json(rows)
        assert prior['profiles']==profiles and prior['dos_producers']==producers
        for name,digest in prior['files'].items():
            assert sha((args.reference/name).read_bytes())==digest,name
    args.output.mkdir(parents=True,exist_ok=False)
    vectors=args.output/'vectors.txt'
    vectors.write_text(''.join(' '.join(map(str,row))+'\n' for row in rows))
    process=subprocess.Popen([str(args.native.resolve()),'--vectors',str(vectors.resolve())],
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    controls=[];size=END-START
    original_path=(args.reference if prior else args.output)/'original.bin.gz'
    try:
        with gzip.open(original_path,'rb' if prior else 'wb',compresslevel=6) as target_stream, \
                gzip.open(args.output/'native.bin.gz','wb',compresslevel=6) as native_stream:
            for index,row in enumerate(rows):
                actual=read_exact(process.stdout,size+8000)
                native_stream.write(actual);memory,visible=actual[:size],actual[size:]
                expected_visible=memory[0xa0000-START:0xa0000-START+4000]+memory[0xa2000-START:0xa2000-START+4000]
                assert visible==expected_visible,('visible TextPlane projection',index)
                originals=[]
                for profile,machine in enumerate(machines if not prior else [None]*len(profiles)):
                    if prior:
                        expected=read_exact(target_stream,size)
                        writes=read_exact(target_stream,struct.unpack('<I',read_exact(target_stream,4))[0])
                        es=struct.unpack('<H',read_exact(target_stream,2))[0]
                    else:
                        expected,writes,es=machine.run(row,index&1)
                        target_stream.write(expected)
                        target_stream.write(struct.pack('<I',len(writes))+writes+struct.pack('<H',es))
                    record=dict(memory_sha256=sha(expected),writes_sha256=sha(writes),
                                write_bytes=len(writes),es=es)
                    if prior:assert record==prior['controls'][index]['originals'][profile]
                    if expected!=memory:
                        first=next((at for at,(a,b) in enumerate(zip(expected,memory)) if a!=b),None)
                        raise AssertionError(('text memory differs',index,profiles[profile],row[:3],
                                              None if first is None else hex(START+first)))
                    originals.append(record)
                controls.append(dict(index=index,native_memory_sha256=sha(memory),
                                     native_visible_sha256=sha(visible),originals=originals))
                if index%128==127:print(index+1,'native rows compared',flush=True)
            if prior:assert not target_stream.read(1)
        assert not process.stdout.read(1)
        assert process.wait(timeout=30)==0
        assert not process.stderr.read()
    except BaseException:
        process.kill();process.wait(timeout=30)
        (args.output/'native-stderr.txt').write_bytes(process.stderr.read())
        raise
    source=Path(__file__).resolve().parent
    receipt=dict(passed=True,rows=rows_as_json(rows),profiles=profiles,controls=controls,
                 comparisons=len(rows)*len(profiles),physical_start=START,physical_bytes=size,
                 native_sha256=sha(args.native.read_bytes()),dos_producers=producers,
                 source={name:sha((source/name).read_bytes()) for name in
                         ('registration_render.cpp','registration_render.hpp',
                          'text_address_contracts.cpp','verify_text_address.py','CMakeLists.txt')},
                 reference_receipt_sha256=sha((args.reference/'receipt.json').read_bytes()) if prior else None,
                 files={p.name:sha(p.read_bytes()) for p in args.output.iterdir()})
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('TextPlane',len(rows),'native rows /',receipt['comparisons'],'original memory comparisons PASS',flush=True)


def rows_as_json(rows):
    return [list(row) for row in rows]


if __name__=='__main__':main()
