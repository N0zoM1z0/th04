#!/usr/bin/env python3
"""Prepare portable TH04 runtime data from an installed Japanese full game."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import tempfile
from urllib.request import Request, urlopen

# Public portable main.cpp currently expects this FAT12 layout.
PARTITION = 38912
SECTOR = 1024
CLUSTER = 8 * SECTOR
SECTORS = 20706
FAT_BYTES = 4 * SECTOR
ROOT = PARTITION + SECTOR + 2 * FAT_BYTES
DATA = ROOT + 1536 * 32
IMAGE_BYTES = 21415936
GAME = (
    ('MAIN.EXE', 156258, '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'),
    ('幻想郷ED.DAT', 1120284, 'ca787b8ff66f7b3f10c97b3ecc77cd466772767e3e9e8cf5a0c71dd612b1c8d7'),
    ('東方幻想.郷', 1053177, '4d975850a66b4ec2ca5fd4fba7f3166dd9293d220ba8ab6c1be87ed98b1399be'),
)
FONT_SHA = '91d75314ac4f940ab13b3c33fb260ef1713865d025a94f09f6814a72e47dfa87'
FONT_SHAS = {FONT_SHA, '41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'}
ROM_SHA = '53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8'
FONT_URL = 'https://raw.githubusercontent.com/joncampbell123/dosbox-x/997f616e0886a835fc3660f2b935688f17f20d42/contrib/fonts/FREECG98.BMP'
ROM_URL = 'https://raw.githubusercontent.com/Wohlstand/libOPNMIDI/43b6bee61c943ebf91f50dbea649da04aa87fca2/src/chips/mamefm/fmopn_2608rom.h'
HEADER_SHA = '7453a041b2295018ba63a5c8a61925a7bf49c7e396d891e413446eca5ef2e616'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def short_name(name: str) -> bytes:
    stem, _, extension = name.upper().partition('.')
    a, b = stem.encode('cp932'), extension.encode('cp932')
    if len(a) > 8 or len(b) > 3:
        raise ValueError('not an 8.3 name: ' + name)
    return a.ljust(8, b' ') + b.ljust(3, b' ')


def installed_files(folder: Path) -> dict[str, bytes]:
    if not folder.is_dir():
        raise ValueError('game folder does not exist: ' + str(folder))
    wanted = {(size, sha): name for name, size, sha in GAME}
    found = {}
    for path in sorted(folder.rglob('*')):
        if path.is_file() and path.stat().st_size in {row[1] for row in GAME}:
            data = path.read_bytes()
            name = wanted.get((len(data), digest(data)))
            if name:
                found[name] = data
    missing = [name for name, _, _ in GAME if name not in found]
    if missing:
        raise ValueError('missing full-version Japanese files: ' + ', '.join(missing)
                         + '. Extract both original installer archives into one folder first; the trial is a different data set.')
    return found


def compatible_image(path: Path) -> dict[str, bytes]:
    image = path.read_bytes()
    if len(image) < PARTITION + SECTORS * SECTOR:
        raise ValueError('image is too short; export its installed GENSO files and use --game-dir')
    geometry = struct.unpack_from('<HBHBHHBH', image, PARTITION + 11)
    if geometry != (1024, 8, 1, 2, 1536, 20706, 248, 4):
        raise ValueError('unsupported HDI layout; export its installed GENSO files and use --game-dir')
    fat = image[PARTITION + SECTOR:PARTITION + SECTOR + FAT_BYTES]
    if fat != image[PARTITION + SECTOR + FAT_BYTES:PARTITION + SECTOR + 2 * FAT_BYTES]:
        raise ValueError('HDI FAT mirrors disagree')
    max_cluster = 1 + (SECTORS - 1 - 8 - 48) // 8

    def chain(first):
        result = []
        seen = set()
        c = first
        while c < 0xff8:
            if not 2 <= c <= max_cluster or c in seen:
                raise ValueError('invalid HDI FAT chain')
            seen.add(c)
            result.append(c)
            at = c + c // 2
            word = int.from_bytes(fat[at:at + 2], 'little')
            c = (word >> 4) if c & 1 else word & 0xfff
        return result

    def find(starts, name, width):
        for start in starts:
            for at in range(start, start + width, 32):
                if image[at] == 0:
                    break
                if image[at:at + 11] == name:
                    return struct.unpack_from('<H', image, at + 26)[0], struct.unpack_from('<I', image, at + 28)[0]
        raise ValueError('missing image member: ' + repr(name))

    directory, _ = find([ROOT], b'GENSO      ', 1536 * 32)
    dirs = [DATA + (c - 2) * CLUSTER for c in chain(directory)]
    result = {}
    for name, size, sha in GAME:
        first, length = find(dirs, short_name(name), CLUSTER)
        data = b''.join(image[DATA + (c - 2) * CLUSTER:DATA + (c - 1) * CLUSTER] for c in chain(first))[:length]
        if length != size or len(data) != size or digest(data) != sha:
            raise ValueError('image game data differs: ' + name)
        result[name] = data
    return result


def build_image(files: dict[str, bytes]) -> bytes:
    image = bytearray(IMAGE_BYTES)
    struct.pack_into('<8I', image, 0, 0, 20, 4096, IMAGE_BYTES - 4096, 512, 17, 4, 615)
    image[PARTITION:PARTITION + 11] = b'\xeb\x3c\x90TH04PORT'
    struct.pack_into('<HBHBHHBH', image, PARTITION + 11, 1024, 8, 1, 2, 1536, SECTORS, 248, 4)
    struct.pack_into('<HHII', image, PARTITION + 24, 17, 4, 68, 0)
    struct.pack_into('<BBBI', image, PARTITION + 36, 128, 0, 41, 0x54483034)
    image[PARTITION + 43:PARTITION + 62] = b'TH04PORT   FAT12   '
    image[PARTITION + 510:PARTITION + 512] = b'\x55\xaa'
    fat = bytearray(FAT_BYTES)
    fat[:3] = b'\xf8\xff\xff'

    def entry(at, name, first, size, directory=False):
        image[at:at + 11] = name
        image[at + 11] = 16 if directory else 32
        struct.pack_into('<HHHI', image, at + 22, 0, 33, first, size)

    def link(cluster, value):
        at = cluster + cluster // 2
        old = int.from_bytes(fat[at:at + 2], 'little')
        word = ((old & 15) | (value << 4)) if cluster & 1 else ((old & 0xf000) | value)
        fat[at:at + 2] = word.to_bytes(2, 'little')

    entry(ROOT, b'GENSO      ', 2, 0, True)
    link(2, 0xfff)
    entry(DATA, b'.          ', 2, 0, True)
    entry(DATA + 32, b'..         ', 0, 0, True)
    next_cluster = 3
    for index, (name, _, _) in enumerate(GAME):
        data = files[name]
        first = next_cluster
        count = math.ceil(len(data) / CLUSTER)
        entry(DATA + 64 + index * 32, short_name(name), first, len(data))
        for c in range(first, first + count):
            link(c, c + 1 if c + 1 < first + count else 0xfff)
        start = DATA + (first - 2) * CLUSTER
        image[start:start + len(data)] = data
        next_cluster += count
    image[PARTITION + SECTOR:PARTITION + SECTOR + FAT_BYTES] = fat
    image[PARTITION + SECTOR + FAT_BYTES:PARTITION + SECTOR + 2 * FAT_BYTES] = fat
    return bytes(image)


def fetch(url: str, expected: str) -> bytes:
    print('Fetching ' + url)
    with urlopen(Request(url, headers={'User-Agent': 'TH04-portable-prepare-assets'}), timeout=30) as response:
        data = response.read(2 * 1024 * 1024)
    if digest(data) != expected:
        raise ValueError('download checksum differs: ' + url)
    return data


def rhythm_bytes(header: bytes) -> bytes:
    if digest(header) != HEADER_SHA:
        raise ValueError('rhythm header checksum differs')
    match = re.search(rb'YM2608_ADPCM_ROM\[0x2000\]\s*=\s*\{(.*?)\};', header, re.S)
    if not match:
        raise ValueError('rhythm array missing')
    body = re.sub(rb'/\*.*?\*/', b'', match[1], flags=re.S)
    result = bytes(int(v, 16) for v in re.findall(rb'0x([0-9a-fA-F]{2})\b', body))
    if len(result) != 8192 or digest(result) != ROM_SHA:
        raise ValueError('rhythm ROM checksum differs')
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--game-dir', type=Path, help='installed/extracted full-version game folder')
    source.add_argument('--hdi', type=Path, help='already compatible TH04 HDI; its three files are validated')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--fetch-support', action='store_true', help='download pinned DOSBox-X font and libOPNMIDI rhythm header')
    parser.add_argument('--font', type=Path, help='local FREECG98.BMP instead of downloading')
    parser.add_argument('--rhythm-rom', type=Path, help='local 8192-byte rhythm ROM instead of downloading')
    args = parser.parse_args()
    try:
        files = installed_files(args.game_dir) if args.game_dir else compatible_image(args.hdi)
        font_path = args.font or args.output_dir / 'FREECG98.BMP'
        rom_path = args.rhythm_rom or args.output_dir / 'ym2608_adpcm_rom.bin'
        font = font_path.read_bytes() if font_path.is_file() else fetch(FONT_URL, FONT_SHA) if args.fetch_support else None
        rom = rom_path.read_bytes() if rom_path.is_file() else rhythm_bytes(fetch(ROM_URL, HEADER_SHA)) if args.fetch_support else None
        if font is None or digest(font) not in FONT_SHAS:
            raise ValueError('font missing or different; use --font FILE or --fetch-support')
        if rom is None or digest(rom) != ROM_SHA:
            raise ValueError('rhythm ROM missing or different; use --rhythm-rom FILE or --fetch-support')
        outputs = {'th04.hdi': build_image(files), 'FREECG98.BMP': font, 'ym2608_adpcm_rom.bin': rom}
        receipt = dict(format=1, source=str(args.game_dir or args.hdi), game_files={name: digest(data) for name, data in files.items()},
                       files={name: digest(data) for name, data in outputs.items()}, support_references={'font': FONT_URL, 'rhythm_header': ROM_URL},
                       container='generated portable FAT12 data image; game files unchanged; no source scores/config copied')
        outputs['prepared-assets.json'] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        for name, data in outputs.items():
            target = args.output_dir / name
            if target.exists() and target.read_bytes() != data:
                raise ValueError('existing file differs; choose a fresh output folder: ' + str(target))
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, data in outputs.items():
            target = args.output_dir / name
            if target.exists():
                continue
            with tempfile.NamedTemporaryFile(dir=args.output_dir, delete=False) as temporary:
                temporary.write(data)
                staged = Path(temporary.name)
            try:
                os.replace(staged, target)
            finally:
                staged.unlink(missing_ok=True)
        print('Prepared th04.hdi, FREECG98.BMP and ym2608_adpcm_rom.bin in ' + str(args.output_dir))
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
