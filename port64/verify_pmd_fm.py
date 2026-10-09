#!/usr/bin/env python3
"""Original EFC Timer A state and complete ordered FM effect register writes.

Executes the unchanged three HDI COM drivers with the real MIKO.EFC. DOS,
installation chip mirrors and injected IRQ flags remain explicit adapters.
Music stays stopped: restoration of a running musical voice is a future chip
owner. Timer/PIC housekeeping is excluded from FM register events. No audio
backend, synthesis, physical timing, frontend capability or exact promotion.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import unicorn as U
from verify import source_manifest, require_elf_x86_64, require_pe_x86_64
from verify_pmd_driver import directory_files, install, DRIVERS, HDI_SHA
from verify_cutscene import ending_assets

LAYOUT = {'PMD.COM': (0x3698, 0x31e9, 0x88),
          'PMD86.COM': (0x46a6, 0x40b5, 0x188),
          'PMDB2.COM': (0x42ae, 0x3cbd, 0x88)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def operations():
    result = []
    for effect in range(17):
        result += [('P', effect)] + [('T', 2)] * 8 + [('T', 0)] * 4
        result += [('T', 1)] * 256
        result += [('P', effect)] + [('T', 3)] * 16
        result += [('P', (effect + 1) % 17)] + [('T', 1)] * 8 + [('S', 0)]
    return result


def mirror(d, name):
    port = LAYOUT[name][2]
    return [d.registers.get((port + bank * 4, register), 0)
            for bank in range(2) for register in range(256)]


def original_row(d, name, address):
    part, global_state, port = LAYOUT[name]
    raw = bytes(d.u.mem_read(d.load * 16 + part, 96))
    g = bytes(d.u.mem_read(d.load * 16 + global_state, 2))
    u16 = lambda at: struct.unpack_from('<H', raw, at)[0]
    i16 = lambda at: struct.unpack_from('<h', raw, at)[0]
    i8 = lambda at: struct.unpack_from('<b', raw, at)[0]
    position, loop = u16(0), u16(2)
    row = [g[1], g[0], position-address if position else 0,
           loop-address if loop else 0, raw[4], raw[5], u16(6), i16(8),
           i16(10), i16(12), i16(14), i16(16), raw[0x12], raw[0x13],
           raw[0x14], raw[0x15], i8(0x16), raw[0x17], raw[0x18],
           raw[0x19], i8(0x1a), raw[0x1b], raw[0x1c], raw[0x2f],
           raw[0x31], raw[0x32], raw[0x33], *raw[0x34:0x38],
           raw[0x38], raw[0x39], raw[0x3a], raw[0x3c], raw[0x3d],
           raw[0x3e], raw[0x55], raw[0x59], raw[0x5a], raw[0x5e], raw[0x5f]]
    work = d.service(0x1000)
    pointers = struct.unpack('<11H', d.u.mem_read((d.load + work['ds'])*16+work['dx'], 22))
    row += [d.u.mem_read(d.load*16+p+0x3b, 1)[0] for p in pointers[:6]]
    row += mirror(d, name)
    selected = {}
    writes = []
    for _, p, size, value in d.ports:
        if size != 1:
            raise ValueError('unexpected FM I/O width')
        if p in (port, port + 4):
            selected[p] = value
        elif p in (port + 2, port + 6):
            bank = (p-port-2)//4
            register = selected.get(p-2)
            if register is None:
                raise ValueError('FM register write lacks address')
            # 27 is the Timer A/B ACK/enable seam, not an effect voice write.
            if register != 0x27:
                writes += [bank, register, value]
    row += [len(writes)//3] + writes
    return row


def produce(args, root, out, manifest):
    binaries = directory_files(args.hdi)
    assets = ending_assets(args.hdi)
    resource = out/'MIKO.EFC';resource.write_bytes(assets['MIKO.EFC'])
    ops = operations();operation = out/'operations.txt'
    operation.write_text(''.join(f'{op} {value}\n' for op, value in ops))
    outputs = {p.name: sha(p) for p in (resource, operation)}
    cases, first = [], {}
    for load in (0x1000, 0x2000):
        for name, (_, _, board, _, _) in DRIVERS.items():
            d = install(binaries[name], name, load)
            address = d.write_resource(0xb00, assets['MIKO.EFC'])['offset']
            initial = out/f'{name}-mirror.txt'
            initial_bytes = (' '.join(map(str, mirror(d, name)))+'\n').encode()
            if initial.exists():
                if initial.read_bytes() != initial_bytes:raise ValueError('relocated initial mirror differs')
            else:initial.write_bytes(initial_bytes)
            path = out/f'{name}-{load:04x}.txt'
            with path.open('w') as stream:
                for tick, (op, value) in enumerate(ops):
                    d.ticks=tick;d.ports=[]
                    if op=='P':d.service(0xc00|value)
                    elif op=='S':d.service(0xd00)
                    else:d.irq(value)
                    row=original_row(d,name,address)
                    stream.write(' '.join(map(str,row))+'\n')
            outputs[initial.name]=sha(initial);outputs[path.name]=sha(path)
            if name in first and outputs[path.name]!=first[name]:raise ValueError('relocated FM effect state/register differs')
            first[name]=outputs[path.name]
            cases.append(dict(driver=name,board=board,load=load,mirror=initial.name,reference=path.name,rows=len(ops)))
            print(f'Original FM EFC {name} load{load:04x}: {len(ops)} rows PASS',flush=True)
    if source_manifest(root)[0]!=manifest:raise ValueError('source changed during original FM reference')
    return dict(cases=cases,rows=sum(c['rows'] for c in cases),outputs=outputs,
                hdi_sha256=HDI_SHA,drivers={n:dict(size=len(data),sha256=hashlib.sha256(data).hexdigest(),state=f'PSP:{LAYOUT[n][0]:04x}') for n,data in binaries.items() if n in DRIVERS},
                unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)))


def consume(args, root, out, manifest):
    ref=args.reference.resolve();producer=json.loads((ref/'receipt.json').read_text())
    if not producer['passed'] or len(producer['cases'])!=6:raise ValueError('incomplete FM EFC reference')
    for name,digest in producer['outputs'].items():
        if sha(ref/name)!=digest:raise ValueError('FM reference changed: '+name)
    runs=[];outputs={}
    for binary in args.binary:
        binary=binary.resolve()
        (require_pe_x86_64 if binary.suffix=='.exe' else require_elf_x86_64)(binary)
        host=binary.parent.name;directory=out/host;directory.mkdir()
        for c in producer['cases']:
            target=directory/c['reference'];command=[str(binary),str(ref/'MIKO.EFC'),str(c['board']),str(ref/c['mirror']),str(ref/'operations.txt'),str(target)]
            subprocess.run(command,check=True)
            actual=target.read_bytes();expected=(ref/c['reference']).read_bytes()
            if actual!=expected:
                a=actual.splitlines();e=expected.splitlines()
                for i,(x,y) in enumerate(zip(a,e)):
                    if x!=y:
                        xx=list(map(int,x.split()));yy=list(map(int,y.split()));diff=[(j,t,v) for j,(t,v) in enumerate(zip(yy,xx)) if t!=v]
                        raise ValueError(f'FM {host} {c["driver"]} row{i}: fields(expected,native)={diff[:12]}, sizes={len(yy)}/{len(xx)}')
                raise ValueError('FM trace length differs')
            outputs[target.relative_to(out).as_posix()]=sha(target)
            runs.append(dict(binary=str(binary),binary_sha256=sha(binary),driver=c['driver'],load=c['load'],rows=c['rows']))
        print(f'Native FM {host}: {producer["rows"]} rows PASS',flush=True)
    if source_manifest(root)[0]!=manifest:raise ValueError('source changed during FM consumption')
    return dict(runs=runs,rows=producer['rows'],outputs=outputs,reference_source_manifest=producer['source_manifest'],reference_receipt_sha256=sha(ref/'receipt.json'))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--hdi',type=Path);parser.add_argument('--reference',type=Path)
    parser.add_argument('--binary',type=Path,action='append',default=[]);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root);out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    if args.reference:
        if not args.binary:parser.error('consumer needs --binary')
        result=consume(args,root,out,manifest)
    else:
        if args.hdi is None:parser.error('producer needs --hdi')
        result=produce(args,root,out,manifest)
    result.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,source_files=len(files),command=sys.argv,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
