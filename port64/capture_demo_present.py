#!/usr/bin/env python3
"""Capture full DOS demo video after the previous complete gameplay update.

Reuse the ordinary pinned capture driver with an explicit consumer projection.
The imported driver's ROOT and body stay unchanged; its __file__ selects copied
observer/stream files only. The separate MAGIC/boundary never accepts old video.
All game launches remain dummy-SDL, muted and serial on one low-priority CPU.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

BOUNDARY='after previous complete gameplay update, at next before-update or terminal scalar observer header'
MAGIC=b'TH04VP3\n'
CORE_ENTRY=0x5ea6f0
SCALAR_OFFSET=0x1de
SCALAR_WITNESS='488b2df3a37304488b1b4883c4204839eb7434'

def project_module(name,raw):
    if name=='th04_demo_dgroup.py':
        old="BOUNDARY = 'stage_frame write, before mod counters and score update'"
        if raw.count(old)!=1:raise ValueError('donor DGROUP boundary drift')
        return raw.replace(old,'BOUNDARY = '+repr(BOUNDARY),1)
    if name=='th04_demo_video.py':
        old="MAGIC = b'TH04VD2\\n'"
        if raw.count(old)!=1:raise ValueError('donor video magic drift')
        return raw.replace(old,"MAGIC = b'TH04VP3\\n'",1)
    raise ValueError('unexpected projected module')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('dos-root','emulator-receipt','video-layout','font-bmp','consumer-dir','output-dir'):
        p.add_argument('--'+name,required=True,type=Path)
    p.add_argument('--original',action='store_true')
    p.add_argument('--build-dir',type=Path);p.add_argument('--map',type=Path)
    args=p.parse_args();dos=args.dos_root.resolve();projection=args.consumer_dir.resolve()
    if not args.original and (args.build_dir is None or args.map is None):p.error('reconstructed capture requires build-dir and map')
    projection.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(dos/'scripts/probes'))
    import capture_th04_dos_demos as driver
    donor=Path(driver.__file__);assert driver.ROOT==dos
    pins={};sha=lambda data:hashlib.sha256(data).hexdigest()
    for name in ('th04_demo_observer.inl','th04_demo_host_ram.py'):
        data=(donor.parent/name).read_bytes();(projection/name).write_bytes(data);pins[name]=sha(data)
    for name in ('th04_demo_dgroup.py','th04_demo_video.py'):
        data=project_module(name,(donor.parent/name).read_text()).encode();(projection/name).write_bytes(data);pins[name]=sha(data)
    data=Path(__file__).with_name('demo_present_stream.gdb').read_bytes()
    (projection/'th04_demo_dgroup_stream.gdb').write_bytes(data);pins['th04_demo_dgroup_stream.gdb']=sha(data)
    body=donor.read_bytes();(projection/'driver_body.py').write_bytes(body)
    driver.__file__=str(projection/'driver_body.py')
    os.environ['TH04_PRESENT_DOS_ROOT']=str(dos)
    command=[str(Path(__file__).resolve()),'--video-stream','--emulator-receipt',str(args.emulator_receipt.resolve()),
             '--video-layout',str(args.video_layout.resolve()),'--font-bmp',str(args.font_bmp.resolve()),
             '--output-dir',str(args.output_dir.resolve())]
    if args.original:command.append('--original')
    else:command+=['--build-dir',str(args.build_dir.resolve()),'--map',str(args.map.resolve())]
    sys.argv=command;status=driver.main()
    record=dict(capture_exit=status,donor_driver=str(donor),donor_sha256=sha(body),projected_driver=str(driver.__file__),
        wrapper_sha256=sha(Path(__file__).read_bytes()),projected_source_sha256=pins,boundary=BOUNDARY,magic=MAGIC.hex(),
        output=str(args.output_dir.resolve()),scope=__doc__)
    (projection/'projection.json').write_text(json.dumps(record,indent=2)+'\n')
    return status

if __name__=='__main__':raise SystemExit(main())
