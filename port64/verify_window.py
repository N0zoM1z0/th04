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

from PIL import Image, ImageChops


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--hdi', type=Path, required=True)
    parser.add_argument('--runner')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault('WINEDEBUG', '-all')
    command = ([args.runner] if args.runner else []) + [str(args.exe.resolve()), '--hdi', str(args.hdi.resolve()), '--title']
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
        for _ in range(3):
            subprocess.run(['xdotool','key','Return'],check=True)
            time.sleep(0.3)
        time.sleep(1.5)  # Let the startup white-flash interval expire.

        def snapshot(name):
            path = output/(name+'.png')
            subprocess.run(['import','-window',window,str(path)],check=True)
            image = Image.open(path).convert('RGB')
            # Exclude Win32's non-client frame/title bar. The MAIN scene is
            # otherwise black, so the remaining nonblack extent is the player.
            crop = image.crop((20,60,image.width-20,image.height-12))
            box = ImageChops.difference(crop,Image.new('RGB',crop.size)).getbbox()
            if box is None: raise RuntimeError('player sprite was not visible')
            if box[2]-box[0] > 80 or box[3]-box[1] > 110:
                raise RuntimeError('MAIN scene not reached or unexpected rendering')
            return (box[0]+box[2])/2 + 20

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
        subprocess.run(['xdotool','key','Escape'],check=True)
        process.wait(timeout=10)
        if process.returncode != 0: raise RuntimeError('window exit failed')
        receipt = {
            'passed':True,'observed_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'exe_sha256':hashlib.sha256(args.exe.read_bytes()).hexdigest(),
            'runner':args.runner,'normal_delta_display_pixels':normal_delta,
            'shift_delta_display_pixels':slow_delta,
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
