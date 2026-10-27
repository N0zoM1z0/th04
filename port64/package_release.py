#!/usr/bin/env python3
"""Package one attested Windows x64 product; copyrighted runtime data stays out."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', args.version):
        parser.error('version must be a filename-safe release identifier')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=ROOT, text=True)
    if dirty:
        parser.error('commit maintained source and packaging inputs before packaging')
    exe = args.exe.read_bytes()
    if len(exe) < 256 or exe[:2] != b'MZ':
        parser.error('expected a Windows x64 PE executable')
    pe = struct.unpack_from('<I', exe, 60)[0]
    if (pe + 26 > len(exe) or exe[pe:pe + 4] != b'PE\0\0'
            or struct.unpack_from('<H', exe, pe + 4)[0] != 0x8664
            or struct.unpack_from('<H', exe, pe + 24)[0] != 0x20b):
        parser.error('only AMD64 PE32+ products can be packaged')
    digest = sha(exe)
    helper = (ROOT / 'port64/run_no_life_loss.ps1').read_bytes()
    no_death = helper.decode('utf-8-sig').split('$noDeathBuilds = @{', 1)[1].split('}', 1)[0]
    if digest not in no_death:
        parser.error('attest the no-death launcher mapping for this executable before packaging')
    url = f'https://github.com/N0zoM1z0/th04/blob/{commit}'
    readme = f'''# TH04 Portable 64-bit — Windows x64 preview {args.version}

Add your own `th04.hdi`, `FREECG98.BMP` and `ym2608_adpcm_rom.bin`
beside `th04-port64.exe`, then double-click `Play.bat` to play with sound.
`Play-no-life-loss.bat` starts seamless invincibility with a separate save folder.
Keep `save-normal` and `save-no-life-loss` when updating an existing installation.
The default PMD86 profile uses the external 8192-byte rhythm ROM.

Arrow keys move; Z fires/confirms; X bombs/cancels; Shift slows; Esc pauses.
In name entry, X erases and Esc finishes/saves.

The public package contains no original game image/data/executable, font,
chip ROM or user saves. Supply those separately. The executable is native x64;
a DOS emulator is not required. It uses the Windows system libraries and has
statically linked MinGW runtimes.

Full setup, tested input hashes, builds, audio profiles, saves and limits:
{url}/docs/PORTABLE.md
Source revision: `{commit}`
Program SHA-256: `{digest}`

This is a functional preview. Original DOS pixel/timing identity, physical
PC-98 sound and exhaustive difficulty/controller coverage are not claimed.
Protected clears establish flow rather than ordinary balance.

Repository-authored source/docs: MIT (`LICENSE.txt`).
Vendored ymfm: BSD-3-Clause (`licenses/ymfm-LICENSE.txt`).
The local opt-in key-state API extension is documented in
`port64/vendor/ymfm/UPSTREAM.json` at the source revision above.
'''
    files = {
        'th04-port64.exe': exe,
        'Play.bat': (ROOT / 'port64/Play.bat').read_bytes(),
        'Play-no-life-loss.bat': (ROOT / 'port64/Play-no-life-loss.bat').read_bytes(),
        'run_no_life_loss.ps1': helper,
        'README.md': readme.encode('utf-8'),
        'LICENSE.txt': (ROOT / 'LICENSE').read_bytes(),
        'licenses/ymfm-LICENSE.txt': (ROOT / 'port64/vendor/ymfm/LICENSE').read_bytes(),
    }
    info = dict(format=1, name='TH04 Portable 64-bit', version=args.version,
                platform='windows-x64', source_commit=commit, binary_sha256=digest,
                data_included=False, saves_included=False,
                provenance='Cold Release game build from a public source export; source commit also includes launcher/documentation updates. No byte-identical rebuild claim.',
                files={name: sha(data) for name, data in sorted(files.items())})
    files['BUILD-INFO.json'] = (json.dumps(info, indent=2) + '\n').encode()
    files['SHA256SUMS.txt'] = ''.join(f'{sha(data)}  {name}\n' for name, data in sorted(files.items())).encode()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    archive = args.output_dir / f'th04-portable64-windows-x64-{args.version}.zip'
    if archive.exists() or (args.output_dir / 'SHA256SUMS.txt').exists():
        parser.error('use a fresh output directory; existing release files are preserved')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo('th04-portable64/' + name, (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(entry, data)
    sums = args.output_dir / 'SHA256SUMS.txt'
    sums.write_text(f'{sha(archive.read_bytes())}  {archive.name}\n', encoding='ascii')
    print(json.dumps(dict(archive=str(archive), sha256=sha(archive.read_bytes()),
                          source_commit=commit, binary_sha256=digest, files=len(files))))


if __name__ == '__main__':
    main()
