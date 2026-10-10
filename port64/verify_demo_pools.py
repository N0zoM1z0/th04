#!/usr/bin/env python3
"""Compare complete native actor/effect records at the original pre-score seam.

Nine pools, including every inactive byte. Enemy script IDs are translated
to their original STD-relative offsets.
This does not accept pictures, global owners, scanout, process or Windows parity.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
from datetime import datetime, timezone
from verify import source_manifest, require_elf_x86_64
from verify_demo_state import sha, require

POOLS = (('shots',0xb55e,68,18),('enemies',0x8a92,32,64),
         ('sparks',0x53e2,96,16),('bullets',0x5a22,440,26),
         ('custom_entities',0xb204,32,26),('circles',0x9594,16,10),('items',0xaf34,32,20),
         ('pointnums',0x9634,400,16),('gather_circles',0x9292,16,42))
FRAME_BYTES = 4+sum(count*stride for _,_,count,stride in POOLS)
MAGIC = b'TH04NP2\n'

def read_frame(stream, demo, frame):
    raw=stream.read(FRAME_BYTES)
    require(len(raw)==FRAME_BYTES,'native pool complete frame extent')
    require(struct.unpack('<HH',raw[:4])==(demo,frame),'native pool frame order')
    return raw[4:]

def compare_demo(original, native, demo):
    result={name:dict(differing_frames=0,first_difference=None,
        original_hash=hashlib.sha256(),native_hash=hashlib.sha256()) for name,*_ in POOLS}
    frames=0
    for frame,data in original:
        require(frame==frames+1,'original pool frame order')
        body=read_frame(native,demo,frame);at=0
        for name,offset,count,stride in POOLS:
            size=count*stride;a=data[offset:offset+size];b=body[at:at+size];at+=size
            require(len(a)==len(b)==size,'paired pool extent')
            row=result[name];row['original_hash'].update(a);row['native_hash'].update(b)
            if a!=b:
                row['differing_frames']+=1
                if row['first_difference'] is None:
                    indices=[i for i in range(size) if a[i]!=b[i]]
                    row['first_difference']=dict(frame=frame,after_update=frame-1,
                        differing_bytes=len(indices),changes=[dict(offset=i,slot=i//stride,
                            record_offset=i%stride,original=a[i],native=b[i]) for i in indices[:24]])
        frames+=1
    require(frames==3996,'original complete demo pool extent')
    for name,_,count,stride in POOLS:
        row=result[name];row.update(passed=row['first_difference'] is None,updates=frames,
            bytes_per_frame=count*stride,original_sha256=row.pop('original_hash').hexdigest(),
            native_sha256=row.pop('native_hash').hexdigest())
    return dict(passed=all(row['passed'] for row in result.values()),updates=frames,pools=result)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('dos-root','original','original-dgroup','original-consumer','exe','output-dir'):
        p.add_argument('--'+name,required=True,type=Path)
    args=p.parse_args();root=Path(__file__).resolve().parents[1];dos=args.dos_root.resolve()
    sys.path.insert(0,str(dos/'scripts/probes'))
    from compare_th04_demo_dgroup import read_side, iter_side, attest_clear_calls, SOURCE_NAMES
    from compare_th04_dos_demos import load_capture
    from th04_demo_dgroup import BOUNDARY
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    manifest,sources=source_manifest(root);require_elf_x86_64(args.exe)
    receipt,profile,diagnostic=read_side(args.original_dgroup.resolve(),args.original.resolve(),args.original_consumer.resolve())
    require(receipt['role']=='original','pool reference role')
    target=Path(receipt['main_path']).read_bytes()
    require(len(target)==156258 and sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b','pool target identity')
    owner=target[6144+0x11ecb:6144+0x11f96]
    require(sha(owner)=='f41ff21e0254ae8050f35b00c514db046b74b4ae2b02538dd7856715a15dfed7','pool clear owner')
    all_offsets=[0xb55e,0x8a92,0x53e2,0x5a22,0xb204,0x9594,0xaf34,0x9634,0x9292]
    attest_clear_calls(owner,0x73db,0x185e,all_offsets)
    scalar_command=[sys.executable,str(root/'port64/verify_demo_state.py'),'--dos-root',str(dos),
        '--original',str(args.original.resolve()),'--exe',str(args.exe.resolve()),'--output-dir',str(out/'scalar-control')]
    scalar=subprocess.run(scalar_command,capture_output=True,timeout=300)
    (out/'scalar.stdout').write_bytes(scalar.stdout);(out/'scalar.stderr').write_bytes(scalar.stderr);scalar.check_returncode()
    scalar_receipt=json.loads((out/'scalar-control/receipt.json').read_text())
    require(scalar_receipt['passed'] and scalar_receipt['source_manifest_sha256']==manifest,'scalar producer/control')
    raw_path=out/'native-pools.bin'
    command=[str(args.exe.resolve()),str(out/'scalar-control/inputs'),str(raw_path)]
    run=subprocess.run(command,capture_output=True,timeout=300)
    (out/'native-observed.txt').write_bytes(run.stdout);(out/'native.stderr').write_bytes(run.stderr);run.check_returncode()
    require(run.stdout==(out/'scalar-control/native.txt').read_bytes(),'actor observer changed ordinary selected trace')
    results={}
    with raw_path.open('rb') as stream:
        require(stream.read(8)==MAGIC,'native pool magic')
        for n in range(1,5):
            results[str(n)]=compare_demo(iter_side(args.original_dgroup,n,profile,diagnostic),stream,n)
        require(stream.read(1)==b'','native pool trailing bytes')
    # Retain the complete native stream losslessly, with full restored readback.
    digest=hashlib.sha256();archive=out/'native-pools.bin.gz'
    with raw_path.open('rb') as source,archive.open('xb') as destination:
        with gzip.GzipFile(filename='',fileobj=destination,mode='wb',mtime=0) as packed:
            while chunk:=source.read(1024*1024):digest.update(chunk);packed.write(chunk)
    restored=hashlib.sha256();restored_size=0
    with gzip.open(archive,'rb') as stream:
        while chunk:=stream.read(1024*1024):restored.update(chunk);restored_size+=len(chunk)
    require(restored.hexdigest()==digest.hexdigest() and restored_size==raw_path.stat().st_size,'pool retention readback')
    reclaimed=raw_path.stat().st_blocks*512-archive.stat().st_blocks*512;raw_path.unlink()
    snapshot=out/'executed-reader';pins={}
    for module in list(sys.modules.values()):
        file=getattr(module,'__file__',None)
        if not file:continue
        path=Path(file).resolve()
        if not path.is_file() or path.suffix!='.py':continue
        for label,base in (('dos',dos),('native',root)):
            if path.is_relative_to(base) and not path.is_relative_to(base/'.analysis'):
                relative=path.relative_to(base);data=path.read_bytes();dest=snapshot/label/relative
                dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
                require(dest.read_bytes()==data,'pool reader source readback');pins[f'{label}/{relative}']=sha(data);break
    for name in SOURCE_NAMES:
        data=(args.original_consumer/name).read_bytes();dest=out/'executed-consumer'/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        require(sha(dest.read_bytes())==receipt['dgroup_stream']['consumer_source_sha256'][name],'consumer snapshot identity')
    require(source_manifest(root)[0]==manifest,'pool source drift')
    report=dict(passed=all(row['passed'] for row in results.values()),accepts_exact=False,boundary=BOUNDARY,
        demos=results,updates=15984,pool_bytes_per_frame=FRAME_BYTES-4,pool_extents=POOLS,
        source_manifest_sha256=manifest,source_files=sources,reader_dependencies=pins,
        native_sha256=sha(args.exe.read_bytes()),native_trace_sha256=digest.hexdigest(),
        native_trace_bytes=restored_size,native_archive_sha256=sha(archive.read_bytes()),reclaimed_allocated_bytes=reclaimed,
        original_receipt_sha256=sha((args.original_dgroup/'receipt.json').read_bytes()),
        ordinary_receipt_sha256=sha((args.original/'receipt.json').read_bytes()),
        scalar_control_receipt_sha256=sha((out/'scalar-control/receipt.json').read_bytes()),
        scalar_command=scalar_command,command=command,observed_utc=datetime.now(timezone.utc).isoformat(),
        scope=__doc__,limits='Other globals, pictures, scanout, process, Windows and cross-emulator remain open.')
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'],demos={n:{name:row['first_difference'] for name,row in demo['pools'].items() if not row['passed']} for n,demo in results.items()})))
    return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
