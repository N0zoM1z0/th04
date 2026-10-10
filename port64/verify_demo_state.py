#!/usr/bin/env python3
"""Pair ordinary native MAIN with an attested complete original DOS demo trace.

The native probe uses original replay/STD/MAP assets and valid starting scores.
Compare every selected before-update/terminal field, full RNG ring and exact
post-initialization draw counts. DOS caller identities, complete actor pools,
video, physical timing and OP/MAIN process teardown are outside this reader.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from verify import source_manifest, require_elf_x86_64

TARGET_SHA256 = '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
FIELDS = ('demo','frame','decision','input','shift_raw','stage','score_digits',
          'score_delta','score_delta_frame','lcg','ring','ring_cursor','player_pos',
          'power','hit','invincibility','respawn','lives','bombs','misses','bombs_used',
          'lcg_calls','ring_calls')

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)

def little(value: str, size: int, signed: bool = False) -> str:
    return int(value).to_bytes(size, 'little', signed=signed).hex()

def parse_native(raw: bytes) -> dict[int, list[dict]]:
    lines = raw.decode('ascii').splitlines()
    require(len(lines) == 4*3997, 'native complete four-demo extent')
    result = {n: [] for n in range(1, 5)}
    last_counts = (0, 0)
    for index, line in enumerate(lines):
        cells = line.split()
        require(len(cells) == 24, 'native field count')
        n, frame = index//3997+1, index%3997
        require((int(cells[0]), int(cells[1])) == (n, frame), 'native frame order')
        require(cells[2] == ('T' if frame == 3996 else 'I'), 'native terminal decision')
        require(len(cells[6]) == 16 and len(cells[10]) == 512, 'native score/ring extent')
        require(bytes.fromhex(cells[6]).hex() == cells[6] and
                bytes.fromhex(cells[10]).hex() == cells[10], 'native canonical byte fields')
        counts = int(cells[22]), int(cells[23])
        if frame == 0:
            require(counts == (0, 0), 'native initialization count boundary')
            last_counts = counts
        require(all(old <= new < 2**64 for old, new in zip(last_counts, counts)), 'native RNG count order')
        last_counts = counts
        row = dict(demo=n, frame=little(cells[1],2), decision=cells[2],
            input=little(cells[3],2), shift_raw=little(cells[4],1), stage=little(cells[5],1),
            score_digits=cells[6], score_delta=little(cells[7],4), score_delta_frame=little(cells[8],4),
            lcg=little(cells[9],4), ring=cells[10], ring_cursor=little(cells[11],2),
            player_pos=little(cells[12],2,True)+little(cells[13],2,True),
            power=little(cells[14],1), hit=little(cells[15],1), invincibility=little(cells[16],1),
            respawn=little(cells[17],1), lives=int(cells[18]), bombs=int(cells[19]),
            misses=int(cells[20]), bombs_used=int(cells[21]), lcg_calls=counts[0], ring_calls=counts[1])
        require(all(0 <= row[key] <= 255 for key in ('lives','bombs','misses','bombs_used')), 'native resident byte width')
        result[n].append(row)
    return result

def compare(original: dict, native: dict) -> dict:
    require(set(original) == set(native) == {1,2,3,4}, 'paired demo numbers')
    report = dict(passed=True, fields=list(FIELDS), boundary='after-demo-before-update-v1',
        gameplay_boundaries=4*3996, terminal_boundaries=4, first_difference=None, demos={})
    for n in range(1,5):
        require(len(original[n]) == len(native[n]) == 3997, 'paired complete frame extent')
        differences = []
        for frame, (a,b) in enumerate(zip(original[n], native[n])):
            changed = {key:dict(original=a[key],native=b[key]) for key in FIELDS if a[key] != b[key]}
            if changed:
                differences.append(dict(frame=frame,fields=changed))
        first = differences[0] if differences else None
        report['demos'][str(n)] = dict(passed=not differences, differing_boundaries=len(differences), first_difference=first)
        if differences:
            report['passed'] = False
            if report['first_difference'] is None:
                report['first_difference'] = dict(demo=n,**first)
    return report

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('dos-root','original','exe','output-dir'):
        parser.add_argument('--'+name,required=True,type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    dos_root = args.dos_root.resolve()
    sys.path.insert(0,str(dos_root/'scripts/probes'))
    from compare_th04_dos_demos import load_capture
    from capture_th04_dos_demos import Fat12, parse_archive, ARCHIVES, u16, u32
    output = args.output_dir.resolve(); output.mkdir(parents=True,exist_ok=False)
    manifest, source_files = source_manifest(root)
    receipt, original, diagnostics = load_capture(args.original.resolve())
    require(receipt['role'] == 'original' and receipt['demos'] == 4 and
            receipt['main_sha256'] == TARGET_SHA256, 'pinned original four-demo role')
    scores = bytes.fromhex(receipt['starting_files']['GENSOU  SCR']['hex'])
    image = (args.original/'prepared/diagnostic.hdi').read_bytes()
    fs = Fat12(bytearray(image)); entry = fs.find_entry([fs.root],b'GENSO      ')
    dirs = [fs.cluster_offset(k) for k in fs.chain(u16(fs.image,entry+26))]
    entry = fs.find_entry(dirs,ARCHIVES['main']['fat_name'])
    archive = fs.file_bytes(u16(fs.image,entry+26),u32(fs.image,entry+28))
    _, assets = parse_archive(archive,'main',ARCHIVES['main'])
    inputs=output/'inputs'; (inputs/'save').mkdir(parents=True)
    (inputs/'save/GENSOU.SCR').write_bytes(scores)
    configuration=bytes.fromhex(receipt['starting_files']['MIKO    CFG']['hex'])
    (inputs/'MIKO.CFG').write_bytes(configuration)
    asset_pins={}
    for n in range(4):
        for name in (f'DEMO{n+1}.REC',f'ST0{n}.STD',f'ST0{n}.MAP'):
            data=assets[name]; (inputs/name).write_bytes(data); asset_pins[name]=sha(data)
    require_elf_x86_64(args.exe)
    command=[str(args.exe.resolve()),str(inputs)]
    run=subprocess.run(command,capture_output=True,timeout=300)
    (output/'native.txt').write_bytes(run.stdout);(output/'stderr.log').write_bytes(run.stderr)
    run.check_returncode()
    require((inputs/'save/GENSOU.SCR').read_bytes() == scores, 'native physical score drift')
    native=parse_native(run.stdout); report=compare(original,native)
    payload=json.dumps(original,sort_keys=True,separators=(',',':')).encode()+b'\n'
    (output/'original-rows.json.gz').write_bytes(gzip.compress(payload,mtime=0))
    require(gzip.decompress((output/'original-rows.json.gz').read_bytes()) == payload, 'original row retention')
    snapshot=output/'executed-source'; dependencies={}
    for record in source_files:
        relative=record['path']; data=(root/relative).read_bytes()
        require(sha(data)==record['sha256'],'native source changed while executing')
        destination=snapshot/'native'/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
        require(destination.read_bytes()==data,'native frozen source readback')
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if not name:continue
        path=Path(name).resolve()
        if not path.is_file() or path.suffix != '.py':continue
        for owner,base in (('dos',dos_root),('native',root)):
            if path.is_relative_to(base) and not path.is_relative_to(base/'.analysis'):
                relative=path.relative_to(base);data=path.read_bytes();destination=snapshot/owner/relative
                destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
                require(destination.read_bytes()==data,'reader dependency frozen readback')
                dependencies[f'{owner}/{relative.as_posix()}']=sha(data);break
    require(source_manifest(root)[0]==manifest,'native source manifest changed')
    report.update(source_manifest_sha256=manifest,source_files=source_files,reader_dependencies=dependencies,
        original_receipt_sha256=sha((args.original/'receipt.json').read_bytes()),original_diagnostics=diagnostics,
        native_sha256=sha(args.exe.read_bytes()),native_trace_sha256=sha(run.stdout),command=command,
        asset_sha256=asset_pins,starting_scores_sha256=sha(scores),starting_configuration_sha256=sha(configuration),observed_utc=datetime.now(timezone.utc).isoformat(),
        scope=__doc__,limits='No complete pool/pixel, DOS caller identity, frontend/process, Windows or cross-emulator acceptance.')
    (output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ('passed','gameplay_boundaries','terminal_boundaries','first_difference','demos')}))
    return 0 if report['passed'] else 1
if __name__=='__main__':
    raise SystemExit(main())
