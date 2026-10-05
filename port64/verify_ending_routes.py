#!/usr/bin/env python3
"""Traverse native MAIN normally, then compare eight Ending scripts' graphics.

The reference gallery is produced by verify_cutscene_pixels.py from original
CPU requests/font kernels. This consumer checks integration and RGB display;
it is not an independent new physical PC-98 capture or an audio Oracle.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
from verify import source_manifest

sha = lambda data: hashlib.sha256(data).hexdigest()

def equal(actual, expected, label):
    if actual != expected:
        raise ValueError(label+' differs')

def verify(reference, output, lines):
    receipt = json.loads((reference/'receipt.json').read_text())
    if not receipt['passed'] or len(receipt['cases']) != 8:
        raise ValueError('original Ending gallery is incomplete')
    events = {c['name']: c for c in receipt['cases']}
    routes = {}
    for line in lines:
        if not line.startswith('MAINE Ending route='):
            continue
        fields = dict(word.split('=', 1) for word in line.split() if '=' in word)
        if fields['route'] in routes:
            raise ValueError('duplicate Ending route')
        routes[fields['route']] = fields
    matrices = list(itertools.product(('easy', 'normal', 'lunatic'), ('reimu', 'marisa'), ('a', 'b'), ('idle', 'shot')))
    if set(routes) != {'-'.join(m)+'-' for m in matrices}:
        raise ValueError('expected 24 natural character/rank/shot/input routes')
    records = []
    for rank, character, shot, shooting in matrices:
        prefix = '-'.join((rank, character, shot, shooting))+'-'
        script = f'_ED{int(character=="marisa")}{int(shot=="b")}{int(rank=="easy")}.TXT'
        route = routes[prefix]
        if (route['script'] != script or route['progression'] != 'staff_roll_pending'
                or route['generation'] != '3' or route['fade'] != '273' or route['captures'] != '12'):
            raise ValueError('route selection or MAIN/MAINE lifecycle differs: '+prefix)
        if int(route['total']) <= int(route['std']) or int(route['spawned']) < int(route['collected']) or route['slow'] != '0':
            raise ValueError('headless run statistics invariant differs: '+prefix)
        reference_route = reference/script
        states = {int(s.split()[0]): tuple(map(int, s.split()[1:])) for s in (reference_route/'states.txt').read_text().splitlines()}
        actual_states = {int(s.split()[0]): tuple(map(int, s.split()[1:])) for s in (output/(prefix+'states.txt')).read_text().splitlines()}
        if actual_states != states:
            raise ValueError('integration page/access/scroll/tone state differs: '+prefix)
        controls = []
        expected_hashes = {(c['event'], c['page']): c['sha256'] for c in events[script]['checkpoints']}
        for event, (shown, access, scroll, tone) in states.items():
            pages = []
            for page in (0, 1):
                expected = (reference_route/f'{event}-{page}.bin').read_bytes()
                if sha(expected) != expected_hashes[(event, page)]:
                    raise ValueError('retained original page changed')
                equal((output/f'{prefix}{event}-{page}.bin').read_bytes(), expected, prefix+'page'+str(page))
                pages.append(expected)
            palette = (reference_route/f'{event}.pal').read_bytes()
            equal((output/f'{prefix}{event}.pal').read_bytes(), palette, prefix+'palette')
            rgb = (np.frombuffer(palette, dtype=np.uint8).reshape(16, 3)>>4).astype(np.int32)
            t = max(0, min(200, tone))
            rgb = ((rgb*t//100 if t <= 100 else 15-(15-rgb)*(200-t)//100)*17).astype(np.uint8)
            indexed = np.frombuffer(pages[shown], dtype=np.uint8).reshape(400, 640)
            expected_rgb = rgb[np.roll(indexed, -scroll, axis=0)].tobytes()
            image = Image.open(output/f'{prefix}{event}.bmp').convert('RGB')
            if image.size != (640, 400):
                raise ValueError('Ending display dimensions differ')
            equal(image.tobytes(), expected_rgb, prefix+'display RGB')
            controls.append(dict(event=event, page0_sha256=sha(pages[0]), page1_sha256=sha(pages[1]),
                                 palette_sha256=sha(palette), rgb_sha256=sha(expected_rgb)))
        records.append(dict(route=prefix, counters=route, checkpoints=controls))
    changed = bytearray(pages[0]); changed[80+320*640] ^= 1
    try:
        equal(bytes(changed), pages[0], 'injected changed pixel')
    except ValueError:
        pass
    else:
        raise ValueError('complete pixel comparator accepted its negative control')
    return records

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('exe', 'hdi', 'font-bmp', 'gallery-dir', 'output-dir'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--runner'); p.add_argument('--existing-log', type=Path)
    p.add_argument('--staff-gallery',type=Path)
    p.add_argument('--verdict-gallery',type=Path)
    p.add_argument('--congratulations-gallery',type=Path)
    p.add_argument('--target',type=Path);p.add_argument('--decoded-dir',type=Path)
    args = p.parse_args(); out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    manifest, _ = source_manifest(Path(__file__).resolve().parents[1])
    if sha(args.hdi.read_bytes()) != '0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd':
        raise ValueError('original HDI identity differs')
    for reference in args.gallery_dir.glob('_ED*.TXT'):
        (out/(reference.name+'-checkpoints.txt')).write_bytes((reference/'checkpoints.txt').read_bytes())
    command = ([args.runner] if args.runner else [])+[str(args.exe.resolve()), '--hdi', str(args.hdi.resolve()),
        '--font-bmp', str(args.font_bmp.resolve()), '--ending-screenshots', str(out)]
    if args.existing_log:
        log = args.existing_log.read_text()
    else:
        env = os.environ.copy(); env.setdefault('WINEDEBUG', '-all')
        completed = subprocess.run(command, env=env, capture_output=True, text=True)
        log = completed.stdout
        (out/'stdout.log').write_text(log); (out/'stderr.log').write_text(completed.stderr)
        completed.check_returncode()
    records = verify(args.gallery_dir, out, log.splitlines())
    staff_routes=[]
    if args.staff_gallery:
        proof=json.loads((args.staff_gallery/'receipt.json').read_text())
        assert proof['passed'] and len(proof['cases'])==8 and len(proof['kernel_controls'])>=240
        final=max(c['event'] for c in proof['pages'])
        final_hashes={c['page']:c['sha256'] for c in proof['pages'] if c['event']==final}
        palette=(args.staff_gallery/'pages'/f'{final}.pal').read_bytes()
        for line in log.splitlines():
            if not line.startswith('MAINE Staff Roll route='):continue
            fields=dict(word.split('=',1) for word in line.split() if '=' in word)
            assert fields['progression']=='verdict_pending' and int(fields['events'])==proof['cases'][0]['requests']
            for page in (0,1):assert sha((out/(fields['route']+f'staff-final-{page}.bin')).read_bytes())==final_hashes[page]
            assert (out/(fields['route']+'staff-final.pal')).read_bytes()==palette
            staff_routes.append(fields)
        assert len(staff_routes)==24 and len({r['route'] for r in staff_routes})==24
    verdict_routes=[]
    if args.verdict_gallery:
        if not args.target or not args.decoded_dir:raise ValueError('verdict target/recovery inputs required')
        from verify_cutscene import ending_assets
        from verify_verdict import Original
        from verify_verdict_pixels import VerdictRaster
        proof=json.loads((args.verdict_gallery/'receipt.json').read_text())
        assert proof['passed'] and proof['complete_pages']==160 and proof['full_string_kernels']>=500
        decoded=(args.verdict_gallery/'UDE.raw').read_bytes();assert sha(decoded)==proof['pi_decoder']['decoded_sha256']
        assets=ending_assets(args.hdi)
        assert proof['font_sha256']==sha(args.font_bmp.read_bytes()) and proof['gaiji_sha256']==sha(assets['GAMEFT.BFT'])
        original=Original(args.target,args.decoded_dir,assets['_UDE.TXT'],0x2000)
        raster=VerdictRaster(args.target,args.decoded_dir,args.font_bmp,assets['GAMEFT.BFT'],decoded)
        for line in log.splitlines():
            if not line.startswith('MAINE Verdict route='):continue
            fields=dict(w.split('=',1) for w in line.split() if '=' in w);prefix=fields['route']
            assert fields['progression']=='congratulations_pending' and fields['generation']=='3'
            values=list(map(int,(out/(prefix+'verdict-input.txt')).read_text().split()));assert len(values)==29
            assert values[1]==(4 if prefix.startswith('easy-') else 5),'natural route published the wrong stage'
            trace=original.run(values);end=trace[-1].split()
            assert [int(fields[k]) for k in ('skill','std','random','line')]==[int(end[i]) for i in (1,4,3,6)]
            canvas,palette,state=raster.render(trace);hashes=[]
            assert state[:3]==[0,0,100]
            for page in (0,1):
                expected=canvas[page].tobytes()
                equal((out/(prefix+f'verdict-{page}.bin')).read_bytes(),expected,prefix+'verdict page')
                hashes.append(sha(expected))
            equal((out/(prefix+'verdict.pal')).read_bytes(),palette,prefix+'verdict palette')
            rgb=((np.frombuffer(palette,dtype=np.uint8).reshape(16,3)>>4)*17)[canvas[0]].tobytes()
            equal(Image.open(out/(prefix+'verdict.bmp')).convert('RGB').tobytes(),rgb,prefix+'verdict RGB')
            verdict_routes.append(dict(route=prefix,fields=fields,page_sha256=hashes,palette_sha256=sha(palette),rgb_sha256=sha(rgb)))
        assert len(verdict_routes)==24 and len({r['route'] for r in verdict_routes})==24
    congratulations_routes=[]
    if args.congratulations_gallery:
        proof=json.loads((args.congratulations_gallery/'receipt.json').read_text())
        assert proof['passed'] and proof['complete_pages']==20 and proof['clock_controls']==50
        from verify_cutscene import ending_assets
        assets=ending_assets(args.hdi)
        pictures={row['name']:row for row in proof['picture_cases']}
        expected_routes={r['route'] for r in records}
        for line in log.splitlines():
            if not line.startswith('MAINE Congratulations route='):continue
            fields=dict(w.split('=',1) for w in line.split() if '=' in w);prefix=fields['route']
            rank,character,*_=prefix.split('-');rank_index={'easy':0,'normal':1,'lunatic':3}[rank]
            name=f'CONG{int(character=="marisa")}{rank_index}.PI';picture=pictures[name]
            assert fields['picture'].upper()==name and fields['generation']=='3'
            assert fields['delay']=='100' and fields['progression']=='registration_pending'
            assert sha(assets[name])==picture['picture_sha256']
            data=(args.congratulations_gallery/(name+'.raw')).read_bytes()
            assert sha(data)==picture['decoded_sha256']
            indexed=bytes(v for b in data[56:] for v in (b>>4,b&15));palette=data[8:56]
            hashes=[]
            for page in (0,1):
                assert sha(indexed)==picture['page_sha256'][page]
                equal((out/(prefix+f'congratulations-{page}.bin')).read_bytes(),indexed,prefix+'congratulations page')
                hashes.append(sha(indexed))
            equal((out/(prefix+'congratulations.pal')).read_bytes(),palette,prefix+'congratulations palette')
            rgb=((np.frombuffer(palette,dtype=np.uint8).reshape(16,3)>>4)*17)[np.frombuffer(indexed,dtype=np.uint8)].tobytes()
            image=Image.open(out/(prefix+'congratulations.bmp')).convert('RGB')
            assert image.size==(640,400)
            equal(image.tobytes(),rgb,prefix+'congratulations RGB')
            congratulations_routes.append(dict(route=prefix,fields=fields,page_sha256=hashes,
                palette_sha256=sha(palette),rgb_sha256=sha(rgb)))
        assert len(congratulations_routes)==24 and {r['route'] for r in congratulations_routes}==expected_routes
    after, _ = source_manifest(Path(__file__).resolve().parents[1]); assert after == manifest
    receipt = dict(passed=True, observed_utc=datetime.now(timezone.utc).isoformat(), command=command,
                   executable_sha256=sha(args.exe.read_bytes()), source_manifest_sha256=manifest,
                   gallery_receipt_sha256=sha((args.gallery_dir/'receipt.json').read_bytes()),
                   hdi_sha256=sha(args.hdi.read_bytes()), font_sha256=sha(args.font_bmp.read_bytes()),
                   natural_routes=len(records), complete_pages=576, palette_states=288, rgb_frames=288,
                   staff_routes=staff_routes,staff_complete_pages=2*len(staff_routes),
                   verdict_routes=verdict_routes,verdict_complete_pages=2*len(verdict_routes),verdict_rgb_frames=len(verdict_routes),
                   congratulations_routes=congratulations_routes,congratulations_complete_pages=2*len(congratulations_routes),
                   congratulations_rgb_frames=len(congratulations_routes),negative_pixel_rejected=True, routes=records,
                   scope='Natural menu/STD/dialogue/boss traversal through Good or Bad Ending, Staff Roll and optional verdict/congratulations. Congratulations reuses original main clocks and pinned PI decoder regression with complete pages/RGB;holds at registration entry after100 refreshes. Verdict uses fresh original CPU on published resident values and original full-string font kernels; STD/LCG ownership and complete indexed/RGB pages checked. Player death, Bomb, Continue, Extra, audio and save remain outside this path. RGB is computed presentation, not physical PC-98 capture.')
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k: receipt[k] for k in ('passed', 'natural_routes', 'complete_pages', 'palette_states', 'rgb_frames')}, indent=2))

if __name__ == '__main__':
    main()
