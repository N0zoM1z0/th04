#!/usr/bin/env python3
"""X11 integration probe for SDL or Wine/Win32 held-key movement (run under Xvfb)."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from PIL import Image
from probe_assets import main_assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--hdi', type=Path, required=True)
    parser.add_argument('--runner')
    parser.add_argument('--playchar',choices=['reimu','marisa'],default='reimu')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault('WINEDEBUG', '-all')
    command = ([args.runner] if args.runner else []) + [str(args.exe.resolve()), '--hdi', str(args.hdi.resolve()), '--title']
    assets = main_assets(args.hdi)
    sheet, colors = assets['MIKO.BFT' if args.playchar=='reimu' else 'MARI.BFT'], assets['ST00.BFT']
    word = lambda b,at:int.from_bytes(b[at:at+2],'little')
    at = 32+word(sheet,28)+(48 if sheet[5]&128 else 0)
    palette_at = 32+word(colors,28)
    palette = [tuple((colors[palette_at+i*3+j]>>4)*17 for j in (1,2,0)) for i in range(16)]
    samples = []
    for y in range(48):
        for x in range(32):
            packed = sheet[at+y*16+x//2]
            color = (packed&15) if x%2 else packed>>4
            if color: samples.append((x,y,palette[color]))
    samples = samples[::max(1,len(samples)//64)]
    previous_left, previous_top = [416], [624]
    log = (output/'window.log').open('w')
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
    held = []
    try:
        deadline = time.monotonic() + 30
        window = None
        while time.monotonic() < deadline:
            found = subprocess.run(['xdotool','search','--onlyvisible','--name','TH04 native x64'],capture_output=True,text=True)
            if found.returncode == 0:
                window = found.stdout.splitlines()[-1]
                break
            if process.poll() is not None:
                raise RuntimeError('window process exited before creation')
            time.sleep(0.1)
        if window is None: raise RuntimeError('window creation timed out')
        # Window creation precedes SDL renderer initialization; allow its
        # initial event pump to establish focus before sending menu keys.
        time.sleep(1.0)
        subprocess.run(['xdotool','windowfocus','--sync',window],check=True)
        for step in range(3):
            if step==1 and args.playchar=='marisa':
                subprocess.run(['xdotool','key','Right'],check=True)
                time.sleep(0.2)
            subprocess.run(['xdotool','key','Return'],check=True)
            time.sleep(0.3)
        time.sleep(1.5)  # Let the startup white-flash interval expire.

        def snapshot(name):
            path = output/(name+'.png')
            subprocess.run(['import','-window',window,str(path)],check=True)
            image = Image.open(path).convert('RGB')
            if image.size != (1280,800): raise RuntimeError('window probe requires 2x client capture')
            # Match nontransparent pixels of the ORIGINAL idle player cel.
            # The scrolling background cannot be treated as black or masked
            # by a single color. This independent BFNT interpretation also
            # checks the renderer's orientation, palette and transparency.
            pixels = image.load()
            low = previous_left[0]-10
            high = previous_left[0]+(10 if name=='initial' else 330)
            for top in range(previous_top[0]-8,previous_top[0]+9):
                for left in range(low,min(high,image.width-64)+1):
                    if all(pixels[left+2*x,top+2*y]==rgb for x,y,rgb in samples):
                        previous_left[0], previous_top[0] = left,top
                        return left+32
            raise RuntimeError('original player sprite was not found in MAIN scene')


        initial = snapshot('initial')
        subprocess.run(['xdotool','keydown','Right'],check=True); held.append('Right')
        time.sleep(0.5)
        subprocess.run(['xdotool','keyup','Right'],check=True); held.remove('Right')
        time.sleep(0.06)
        normal = snapshot('normal')
        subprocess.run(['xdotool','keydown','Shift_L','Right'],check=True); held += ['Shift_L','Right']
        time.sleep(0.5)
        subprocess.run(['xdotool','keyup','Right','Shift_L'],check=True); held.clear()
        time.sleep(0.06)
        slow = snapshot('shift')
        normal_delta, slow_delta = normal-initial, slow-normal
        if not (150 < normal_delta < 310 and 50 < slow_delta < normal_delta*0.8):
            raise RuntimeError(f'held-key movement failed: {normal_delta}, {slow_delta}')
        # Match the original low-power shot's two BFNT cels. Holding Z must
        # emit multiple moving volleys; after release and a full travel time,
        # every one must leave the field. Background motion alone cannot pass.
        small=assets['MIKO16.BFT'];small_at=32+word(small,28)+(48 if small[5]&128 else 0)
        shot_masks=[]
        for cel in (0,1) if args.playchar=='reimu' else (6,7):
            mask=[]
            for y in range(16):
                for x in range(16):
                    packed=small[small_at+cel*128+y*8+x//2]
                    color=packed&15 if x%2 else packed>>4
                    if color:mask.append((x,y,palette[color]))
            shot_masks.append(mask)
        def shot_snapshot(name):
            path=output/(name+'.png')
            subprocess.run(['import','-window',window,str(path)],check=True)
            image=Image.open(path).convert('RGB');pixels=image.load();tops=[]
            for top in range(16,620):
                for left in range(previous_left[0]+14,previous_left[0]+19):
                    if any(all(pixels[left+x*2,top+y*2]==color for x,y,color in mask)
                           for mask in shot_masks):
                        if not tops or top>tops[-1]+2:tops.append(top)
                        break
            return tops
        subprocess.run(['xdotool','keydown','z'],check=True);held.append('z')
        time.sleep(0.5)
        shot_tops=shot_snapshot('shooting')
        subprocess.run(['xdotool','keyup','z'],check=True);held.remove('z')
        time.sleep(0.8)
        released_tops=shot_snapshot('released')
        if len(shot_tops)<2 or released_tops:
            raise RuntimeError(f'held Z firing/release failed: {shot_tops}, {released_tops}')
        subprocess.run(['xdotool','key','Escape'],check=True)
        process.wait(timeout=10)
        if process.returncode != 0: raise RuntimeError('window exit failed')
        receipt = {
            'passed':True,'observed_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'exe_sha256':hashlib.sha256(args.exe.read_bytes()).hexdigest(),
            'runner':args.runner,'playchar':args.playchar,'normal_delta_display_pixels':normal_delta,
            'shift_delta_display_pixels':slow_delta,
            'held_z_shot_tops':shot_tops,'released_shot_tops':released_tops,
            'limits':'Real X11 held keys through SDL or Wine/Win32; loose wall-clock bounds verify direction and Shift response, not exact frame cadence or native Windows host pacing.'
        }
        (output/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        print(json.dumps(receipt,sort_keys=True))
    finally:
        for key in held: subprocess.run(['xdotool','keyup',key],check=False)
        if process.poll() is None:
            process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
        log.close()


if __name__ == '__main__':
    main()
