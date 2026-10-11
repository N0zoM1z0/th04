#!/usr/bin/env python3
"""Pair complete post-update DOS video with retained actual native FrontEnd.

All ordinary scalar/caller controls must remain byte-identical to their parent.
Canonical full TRAM is compared at an aligned score boundary. Full programmed
graphics indices remain diagnostic: no original font/blink/scanout acceptance.
Native products keep their v1376 compiled producer, separately from this reader.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tarfile
from capture_demo_present import BOUNDARY,MAGIC,CORE_ENTRY,SCALAR_OFFSET,SCALAR_WITNESS,project_module
from verify_demo_pictures import display_rows,decode_graphics,canonical_tram,differences,label_cells
from verify_demo_state import require,sha,parse_native,compare,TARGET_SHA256

def attest_format(magic,boundary):
    require((magic,boundary)==(MAGIC,BOUNDARY),'presentation format/seam selection')

def attest_projection(dos,consumer):
    donor=dos/'scripts/probes'
    expected={'th04_demo_dgroup_stream.gdb':Path(__file__).with_name('demo_present_stream.gdb').read_bytes(),
              'th04_demo_host_ram.py':(donor/'th04_demo_host_ram.py').read_bytes()}
    for name in ('th04_demo_video.py','th04_demo_dgroup.py'):
        expected[name]=project_module(name,(donor/name).read_text()).encode()
    for name,data in expected.items():require((consumer/name).read_bytes()==data,'presentation consumer source drift: '+name)
    return {name:sha(data) for name,data in expected.items()}

def attest_site(metadata,layout):
    biases={metadata['video_symbols'][name]-row['address'] for name,row in layout['symbols'].items()}
    require(len(biases)==1,'presentation ELF bias')
    site=metadata['scalar_site'];bias=biases.pop()
    require(site==dict(core_address=bias+CORE_ENTRY,site_address=bias+CORE_ENTRY+SCALAR_OFFSET,
                      elf_offset=SCALAR_OFFSET,instruction_witness=SCALAR_WITNESS),'presentation scalar site witness')

def retained_capture(base):
    journal=json.loads((base/'retention.json').read_text());proof=json.loads((base/'retention-readback.json').read_text())
    require(proof['passed'] and proof['journal_sha256']==sha((base/'retention.json').read_bytes()),'native retention proof')
    archive=base/journal['archive'];require(sha(archive.read_bytes())==journal['archive_sha256'],'native complete archive identity')
    wanted={row['path']:row for row in journal['files'] if row['path'].startswith(('gnu-v4/capture/','ubsan-v4/capture/'))}
    captured={}
    with tarfile.open(archive,'r:gz') as stream:
        for member in stream:
            if member.name not in wanted:continue
            require(member.name not in captured and member.isfile(),'native archive duplicate/type')
            data=stream.extractfile(member).read();row=wanted[member.name]
            require(len(data)==row['size'] and sha(data)==row['sha256'],'native restored capture identity')
            captured[member.name]=data
    require(set(captured)==set(wanted),'native complete selected archive extent')
    return captured

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('dos-root','original','ordinary-reference','original-consumer','native-evidence','output-dir'):
        p.add_argument('--'+name,required=True,type=Path)
    args=p.parse_args();dos=args.dos_root.resolve();consumer=args.original_consumer.resolve();out=args.output_dir.resolve()
    out.mkdir(parents=True,exist_ok=False);pins=attest_projection(dos,consumer)
    # Isolated process imports the attested projected format first. No globals
    # in an already imported old-boundary reader are rewritten.
    sys.path[:0]=[str(consumer),str(dos/'scripts/probes')]
    from compare_th04_demo_video import read_side,iter_side
    from compare_th04_dos_demos import load_capture
    from th04_demo_video import MAGIC as executed_magic,BOUNDARY as executed_boundary,OFFSETS,SIZES
    attest_format(executed_magic,executed_boundary)
    receipt,profile,diagnostic=read_side(args.original,args.ordinary_reference,consumer)
    require(receipt['role']=='original' and receipt['demos']==4 and receipt['main_sha256']==TARGET_SHA256,'presentation original role/extent')
    metadata=json.loads((args.original/'video-stream.json').read_text())
    layout=json.loads(Path(receipt['video_stream']['layout_receipt_path']).read_text());attest_site(metadata,layout)
    _,scalar,_=load_capture(args.original);base=args.native_evidence.resolve();raw=retained_capture(base)
    variants={};selected={}
    for variant in ('gnu-v4','ubsan-v4'):
        old=base/variant;producer=json.loads((old/'receipt.json').read_text())
        require(producer['passed'] and producer['scalar']['passed'] and producer['demo_label_passed'],'retained native producer acceptance')
        program=base/('build-'+variant)/'th04-port64'
        require(sha(program.read_bytes())==producer['native_program_sha256'],'retained native ELF identity')
        for row in producer['source_files']:
            require(sha((old/'executed-source/native'/row['path']).read_bytes())==row['sha256'],'retained native source identity')
        state=compare(scalar,parse_native(raw[variant+'/capture/state.txt']));require(state['passed'],'actual FrontEnd selected scalar/count control')
        rows=display_rows((old/'capture/displays.txt').read_bytes());selected[variant]={(x['demo'],x['frame']):x for x in rows}
        variants[variant]=dict(scalar=state,producer_receipt_sha256=sha((old/'receipt.json').read_bytes()),
            compiled_source_manifest_sha256=producer['source_manifest_sha256'],native_program_sha256=producer['native_program_sha256'],observations=[])
    consumed=0
    for demo in range(1,5):
        for frame,data in iter_side(args.original,demo,profile,diagnostic):
            consumed+=1
            if (demo,frame) not in selected['gnu-v4']:continue
            row=selected['gnu-v4'][(demo,frame)];stem=row['stem'];path=out/'original'/(stem+'.bin')
            path.parent.mkdir(exist_ok=True);path.write_bytes(data)
            gd=data[OFFSETS['gdc']+232:OFFSETS['gdc']+464];modes=data[OFFSETS['modes']:OFFSETS['modes']+8]
            pixels=decode_graphics(data[OFFSETS['graphics']:OFFSETS['graphics']+SIZES['graphics']],gd,modes)
            text=canonical_tram(data[OFFSETS['text']:OFFSETS['text']+SIZES['text']])
            for variant,result in variants.items():
                prefix=variant+'/capture/'+stem
                indices=raw[prefix+'.indices'];tram=raw[prefix+'.tram'];rgb=raw[prefix+'.rgb']
                require(len(indices)==256000 and len(tram)==8000 and len(rgb)==768000,'native complete display extent')
                result['observations'].append(dict(**row,original_raw_sha256=sha(data),native_rgb_sha256=sha(rgb),
                    text=differences(text,tram),graphics=differences(pixels,indices),
                    demo_label=differences(label_cells(text),label_cells(tram)),
                    original_param_ram=gd[152:168].hex(),original_modes=modes.hex()))
    require(consumed==15984 and all(len(r['observations'])==40 for r in variants.values()),'complete presentation reference/sample extent')
    for result in variants.values():
        result['text_passed']=all(x['text']['differing_bytes']==0 for x in result['observations'])
        result['label_passed']=all(x['demo_label']['differing_bytes']==0 for x in result['observations'])
    dependencies={};snapshot=out/'executed-reader'
    for module in list(sys.modules.values()):
        file=getattr(module,'__file__',None)
        if not file:continue
        path=Path(file).resolve()
        if not path.is_file() or path.suffix!='.py':continue
        for name,root in (('consumer',consumer),('dos',dos/'scripts'),('native',Path(__file__).parent)):
            if not path.is_relative_to(root):continue
            relative=Path(name)/path.relative_to(root)
            if name=='dos':relative=Path(name)/'scripts'/path.relative_to(root)
            body=path.read_bytes();destination=snapshot/relative
            destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(body);dependencies[str(relative)]=sha(body);break
    donors={}
    for name in ('th04_demo_dgroup.py','th04_demo_video.py','th04_demo_host_ram.py'):
        body=(dos/'scripts/probes'/name).read_bytes();destination=snapshot/'dos/scripts/probes'/name
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(body);donors[name]=sha(body)
    report=dict(passed=all(r['text_passed'] and r['label_passed'] for r in variants.values()),variants=variants,
        original_records=consumed,boundary=BOUNDARY,picture_acceptance=False,original_receipt_sha256=sha((args.original/'receipt.json').read_bytes()),
        ordinary_receipt_sha256=sha((args.ordinary_reference/'receipt.json').read_bytes()),consumer_source_sha256=pins,
        executed_reader_sha256=dependencies,projection_donor_sha256=donors,limits=__doc__)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'],original_records=consumed,variants={k:dict(text_passed=v['text_passed'],label_passed=v['label_passed']) for k,v in variants.items()},picture_acceptance=False)))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
