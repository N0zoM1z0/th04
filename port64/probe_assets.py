"""Read pinned private probe assets through the independent Python FAT/PAR path."""
import hashlib
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.probes.prepare_th04_maine_diagnostic_hdi import Fat12
from scripts.probes.probe_th04_pf_archive import ARCHIVES, parse_archive


def main_assets(hdi):
    fat = Fat12(bytearray(Path(hdi).read_bytes()))
    directory = fat.find_entry([fat.root],b'GENSO      ')
    clusters = fat.chain(struct.unpack_from('<H',fat.image,directory+26)[0])
    entry = fat.find_entry([fat.cluster_offset(c) for c in clusters],ARCHIVES['main']['fat_name'])
    blob = fat.file_bytes(struct.unpack_from('<H',fat.image,entry+26)[0],struct.unpack_from('<I',fat.image,entry+28)[0])
    if len(blob) != ARCHIVES['main']['size'] or hashlib.sha256(blob).hexdigest() != ARCHIVES['main']['sha256']:
        raise ValueError('probe MAIN archive identity mismatch')
    return parse_archive(blob,'main',ARCHIVES['main'])[1]
