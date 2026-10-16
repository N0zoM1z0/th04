"""Pin four source products and derive OP's menu counter from its own MAP/bytes."""
import json
from pathlib import Path
import tomllib

from capture_th04_dos_demos import map_symbols, parse_mz, sha
from compare_th04_dos_demos import require

ROOT = Path(__file__).resolve().parents[2]
PRODUCTS = dict(main='MAIN.EXE', op='OP.EXE', maine='MAINE.EXE', zun='ZUN.COM')
COUNTER = bytes.fromhex('6626ff4714')


def attest_surface(build_dir):
    manifest_path = build_dir/'build.json'
    manifest = json.loads(manifest_path.read_text())
    require(manifest['schema_version'] == 1 and manifest['variant'] == 'normal' and
            set(manifest['products']) == set(PRODUCTS), 'complete normal four-product manifest')
    require(all(Path(record['build_receipt']).parent.name == manifest['run_id']+'-'+name
                for name,record in manifest['products'].items()), 'same-run four-product cohort')
    products = {}
    for name, filename in PRODUCTS.items():
        record = manifest['products'][name]
        path = build_dir/filename
        image = path.read_bytes()
        producer = Path(record['build_receipt'])
        require(record['file'] == filename and len(image) == record['size'] and sha(image) == record['sha256'] and
                parse_mz(image).valid and producer.is_file(), 'four-product file/producer identity: '+name)
        details = json.loads(producer.read_text())
        if name in ('op','maine'):
            require(details['link_complete'] is True and details['link_exit'] == 0 and
                    not details['link_errors'] and not details['unresolved'], 'four-product link: '+name)
        elif name == 'main':
            require(details['link']['exit'] == 0 and not details['link']['errors'] and details['link']['mz'],
                    'four-product MAIN link')
        else:
            require(details['cold_equal'] is True, 'four-product ZUN cold component replay')
            packed_path = producer.parent.with_name(producer.parent.name+'-diet')/'receipt.json'
            packed = json.loads(packed_path.read_text())
            require(packed['artifact'] == 'th04-zun' and packed['candidate_inputs_identical'] is True and
                    packed['packed_outputs_identical'] is True and len(packed['builds']) == 2 and
                    {row['label'] for row in packed['builds']} == {'a','b'} and
                    all(row['packed_sha256'] == sha(image) for row in packed['builds']), 'four-product ZUN packing replay')
        products['th04-'+name] = dict(path=str(path.resolve()), size=len(image), sha256=sha(image),
                                      producer_path=str(producer.resolve()), producer_sha256=sha(producer.read_bytes()))
    op_map = Path(manifest['products']['op']['build_receipt']).parent/'source/obj/product/op-native.map'
    require(op_map.is_file(), 'four-product OP MAP present')
    return dict(schema_version=1, manifest_path=str(manifest_path.resolve()),
                manifest_sha256=sha(manifest_path.read_bytes()), products=products,
                op_map_path=str(op_map.resolve()), op_map_sha256=sha(op_map.read_bytes()),
                origin='TH04-maintained-source', scope='Four maintained source-product identities; runtime and exactness are separate')


def op_counter_profile(image, map_path=None):
    require(parse_mz(image).valid, 'OP counter MZ integrity')
    if map_path is None:
        target = next(row for row in tomllib.loads((ROOT/'config/targets.toml').read_text())['artifacts']
                      if row['id'] == 'th04-op')
        require(len(image) == target['size'] and sha(image) == target['sha256'], 'original OP counter identity')
        return dict(schema_version=1, artifact='th04-op', file_sha256=sha(image),
                    segment=0x0a74, ip=0x0d2f, dgroup=0x0f34, opcode_hex=COUNTER.hex(),
                    provenance='pinned original OP runtime counter boundary')
    symbols = map_symbols(map_path)
    segment, begin = symbols['_main']
    dgroup, resident = symbols['_resident']
    end = min((offset for seg,offset in symbols.values() if seg == segment and offset > begin), default=65536)
    module = image[int.from_bytes(image[8:10], 'little')*16:]
    require(0 <= begin < end <= 65536 and segment*16+end <= len(module), 'OP mapped main extent')
    pattern = b'\xc4\x1e'+resident.to_bytes(2,'little')+COUNTER
    locations = [at for at in range(begin,end-len(pattern)+1)
                 if module[segment*16+at:segment*16+at+len(pattern)] == pattern]
    require(len(locations) == 1, 'OP unique MAP-owned resident rand increment')
    ip = locations[0]+4
    return dict(schema_version=1, artifact='th04-op', file_sha256=sha(image), segment=segment,
                ip=ip, dgroup=dgroup, opcode_hex=COUNTER.hex(), setup_hex=pattern.hex(), setup_ip=locations[0], resident_offset=resident,
                main_begin=begin, main_end=end, map_sha256=sha(map_path.read_bytes()),
                provenance='compiler MAP and raw candidate instruction bytes')
