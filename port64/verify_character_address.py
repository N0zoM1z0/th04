#!/usr/bin/env python3
"""Compare native character writers with original MAIN TEXT_PUTCA/PUTSA."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(stream,size):
    data=stream.read(size)
    if len(data)!=size:raise ValueError(('incomplete character stream',size,len(data)))
    return data


def visible(memory):
    return memory[0x20000:0x20000+4000]+memory[0x22000:0x22000+4000]


def configured():
    edges=((0,0),(79,0),(80,0),(79,24),(80,24),(2047,0),(2048,0),
           (28671,0),(28672,0),(32767,0),(65535,0),(20,32768),(20,65535))
    words=(0,0x7f,0x80,0xa5,0x2140,0x817f,0x82a0,0xe0fe,0xffff)
    texts=('-', '41','a5','8140','817f','fffe','810041','8081','4181','010002','81800042')
    rows=[('putca',x,y,c,attr,0xa000) for (x,y),c,attr in itertools.product(edges,words,(0,0xe1,0xffff))]
    rows += [('putsa',x,y,text,attr,0xa000) for (x,y),text,attr in itertools.product(edges,texts,(0,0xe1,0xffff))]
    rows += [('putca',20,1,c,0xe1,base) for c,base in itertools.product(words,(0x9000,0xa100))]
    rows += [('putsa',79,1,text,0xffff,base) for text,base in itertools.product(texts,(0x9000,0xa100))]
    for x,length in itertools.product((0,32767),(4095,4096,4097,32767,32768)):
        rows.append(('putsa',x,0,(b'A'*length).hex(),0xe1,0xa000))
    for x,length in itertools.product((0,32767),(2047,2048,2049,16383,16384)):
        rows.append(('putsa',x,0,(b'\x82\xa0'*length).hex(),0xe1,0xa000))
    return rows


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--dos-root',type=Path,required=True)
    parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--reference',type=Path,help='reuse retained complete original transcripts')
    args=parser.parse_args();dos=args.dos_root.resolve()
    sys.path.insert(0,str(dos/'scripts/runtime'))
    from verify_dos_text_gaiji import Machine,original,START,END
    reference=original('main');reference.update(putca=(0,0x229e),putsa=(0,0x22f6),textseg=0x768)
    class PaddedMachine(Machine):
        def run(self,row,interrupt):
            # The string owner supplies an extra zero after its C terminator.
            # It makes the original's next LODSB deterministic after a dangling lead.
            if row[0]=='putsa':
                length=len(bytes.fromhex(row[3])) if row[3]!='-' else 0
                at=self.layout['dg']*16+0x5000+length+1
                assert at>=len(self.body)
                self.cpu.mem_write(self.load*16+at,b'\0')
            return super().run(row,interrupt)
    producers={name:sha((dos/name).read_bytes()) for name in
               ('scripts/runtime/verify_dos_text_gaiji.py','scripts/runtime/verify_dos_vsync_lifecycle.py','scripts/lib/pc98.py')}
    prior=None;rows=configured()
    if args.reference:
        prior=json.loads((args.reference/'receipt.json').read_text())
        assert prior['passed'] and prior['original']==reference['pins']
        assert prior['dos_producers']==producers and prior['rows']==[list(row) for row in rows]
        for name,pin in prior['files'].items():assert sha((args.reference/name).read_bytes())==pin,name
    args.output.mkdir(parents=True,exist_ok=False)
    processes=[];dense_target=hashlib.sha256();dense_native=hashlib.sha256();controls=[]
    try:
        process=subprocess.Popen([str(args.native.resolve()),'--pairs'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        processes.append(process)
        machine=None if prior else PaddedMachine(reference,0x1000)
        folder=args.reference if prior else args.output
        with gzip.open(folder/'pairs-original.bin.gz','rb' if prior else 'wb',compresslevel=6) as target, \
                gzip.open(args.output/'pairs-native.bin.gz','wb',compresslevel=6) as native:
            for mode in range(2):
                for value in range(65536):
                    actual=read(process.stdout,8000);native.write(actual);dense_native.update(actual)
                    if prior:
                        expected=read(target,8000);count=struct.unpack('<I',read(target,4))[0]
                        assert count<=60 and count%10==0
                        writes=read(target,count);es=struct.unpack('<H',read(target,2))[0]
                    else:
                        payload=value if mode==0 else bytes((value>>8,value&255)).hex()
                        row=('putca' if mode==0 else 'putsa',20,10,payload,((value*257)^0xe1)&65535,0xa000)
                        memory,writes,es=machine.run(row,value&1);expected=visible(memory)
                        for address,width,word in struct.iter_unpack('<IHI',writes):
                            assert width==2 and (0xa0000<=address<0xa0000+4000 or 0xa2000<=address<0xa2000+4000)
                        target.write(expected+struct.pack('<I',len(writes))+writes+struct.pack('<H',es))
                    dense_target.update(expected+struct.pack('<I',len(writes))+writes+struct.pack('<H',es))
                    assert actual==expected,('character pair differs',mode,hex(value))
                print('putca' if mode==0 else 'putsa','all65536 character values PASS',flush=True)
            if prior:assert not target.read(1)
        assert not process.stdout.read(1) and process.wait(timeout=30)==0 and not process.stderr.read()
        vectors=args.output/'vectors.txt';vectors.write_text(''.join(' '.join(map(str,row))+'\n' for row in rows))
        process=subprocess.Popen([str(args.native.resolve()),'--vectors',str(vectors.resolve())],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        processes.append(process);size=END-START
        with gzip.open(folder/'memory-original.bin.gz','rb' if prior else 'wb',compresslevel=6) as target, \
                gzip.open(args.output/'memory-native.bin.gz','wb',compresslevel=6) as native:
            for load in (0x1000,0x3333):
                machine=None if prior else PaddedMachine(reference,load)
                # The native owner is independent of DOS load relocation. Reuse its
                # retained complete output when checking the second original load.
                source=None
                if load==0x3333:source=gzip.open(args.output/'memory-native.bin.gz','rb')
                try:
                    for index,row in enumerate(rows):
                        actual=read(process.stdout if source is None else source,size+8000)
                        if source is None:native.write(actual)
                        if prior:
                            expected=read(target,size);count=struct.unpack('<I',read(target,4))[0]
                            writes=read(target,count);es=struct.unpack('<H',read(target,2))[0]
                        else:
                            expected,writes,es=machine.run(row,index&1)
                            target.write(expected+struct.pack('<I',len(writes))+writes+struct.pack('<H',es))
                        assert expected==actual[:size] and visible(expected)==actual[size:],('text address differs',hex(load),index,row[:3])
                        control=dict(load=f'{load:04x}',index=index,memory_sha256=sha(expected),
                                     writes_sha256=sha(writes),write_bytes=len(writes),es=es,visible_sha256=sha(actual[size:]))
                        if prior:assert control==prior['controls'][len(controls)]
                        controls.append(control)
                    if source is not None:assert not source.read(1)
                finally:
                    if source is not None:source.close()
                if load==0x1000:native.close()
                print(f'{load:04x}',len(rows),'full memory controls PASS',flush=True)
            if prior:assert not target.read(1)
        assert not process.stdout.read(1) and process.wait(timeout=30)==0 and not process.stderr.read()
    except BaseException:
        for process in processes:
            if process.poll() is None:process.kill()
            process.wait(timeout=30)
        (args.output/'native-stderr.txt').write_bytes(b''.join(process.stderr.read() for process in processes))
        raise
    dense=dict(word_values=65536,string_byte_pairs=65536,load='1000',column=20,row=10,
               original_expanded_sha256=dense_target.hexdigest(),native_expanded_sha256=dense_native.hexdigest())
    if prior:assert dense==prior['dense']
    source=Path(__file__).resolve().parent
    receipt=dict(passed=True,original=reference['pins'],entries=dict(putca='0000:229E',putsa='0000:22F6'),
                 text_segment='2134:0768',nul_padding=2,dos_producers=producers,dense=dense,
                 rows=[list(row) for row in rows],controls=controls,native_sha256=sha(args.native.read_bytes()),
                 source={name:sha((source/name).read_bytes()) for name in
                         ('registration_render.cpp','registration_render.hpp','character_address_contracts.cpp',
                          'verify_character_address.py','CMakeLists.txt')},
                 reference_receipt_sha256=sha((args.reference/'receipt.json').read_bytes()) if prior else None,
                 files={path.name:sha(path.read_bytes()) for path in args.output.iterdir()})
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Character writers:',131072,'exhaustive conversion controls and',len(controls),'full memory comparisons PASS',flush=True)


if __name__=='__main__':main()
