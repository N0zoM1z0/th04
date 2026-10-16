"""Validate actual DOS4B00 child entries and the initial OP counter boundary."""
import gzip
import json
from pathlib import Path

from capture_th04_dos_demos import sha
from compare_th04_dos_demos import require


def validate_counter(row, entry, profile, memory):
    regs, segs = bytes.fromhex(row['cpu_regs']),bytes.fromhex(row['segments'])
    load = entry['load_segment']
    cs,ip = int.from_bytes(segs[8:16],'little'),int.from_bytes(regs[32:36],'little') & 65535
    ds = int.from_bytes(segs[24:32],'little')
    resident = int.from_bytes(segs[:8],'little')*16+(int.from_bytes(regs[12:16],'little') & 65535)
    require((cs,ip,ds) == (load+profile['segment'],profile['ip'],load+profile['dgroup']) and
            row['cs'] == cs and row['ip'] == ip and resident == row['resident_linear'] and
            row['counter'] == int.from_bytes(memory[resident+20:resident+24],'little') and
            memory[cs*16+ip:cs*16+ip+len(bytes.fromhex(profile['opcode_hex']))].hex() ==
            row['counter_opcode_hex'] == profile['opcode_hex'], 'OP counter actual MAP/CPU/bytes/resident binding')
    if 'setup_hex' in profile:
        require(memory[cs*16+profile['setup_ip']:cs*16+profile['setup_ip']+len(bytes.fromhex(profile['setup_hex']))].hex() ==
                profile['setup_hex'], 'OP actual MAP-owned resident pointer load')


def validate_boot(directory, receipt, surface, clock):
    from th04_dos_route import validate_entry, validate_resident_memory
    rows=[json.loads(x) for x in (directory/'process-events.jsonl').read_text().splitlines()]
    metadata=json.loads((directory/'process-events.json').read_text())
    require(metadata['complete_capture'] is True and metadata['observe_load_go'] is True and
            metadata['error'] is None and metadata['pending'] is None and metadata['events'] == len(rows) and
            [r['sequence'] for r in rows] == list(range(len(rows))), 'complete actual boot process events')
    entries=[r for r in rows if r['kind']=='entry']
    require(metadata['entries'] == [r['sequence'] for r in entries], 'complete boot entry set')
    boot=[r for r in entries if r['request_ax']==0x4b00]
    overlay=[r for r in entries if r['request_ax']==0x4b03]
    require([r['artifact'] for r in boot] == ['th04-zun']*4+['th04-op'] and entries == boot+overlay and
            overlay and overlay[0]['artifact']=='th04-main' and
            boot[-1]['owner']['psp_segment'] == overlay[0]['owner']['psp_segment'], 'actual ZUN/OP boot generations')
    require(metadata['root_program_mcb'] == boot[0]['owner']['parent_psp']-1, 'actual boot parent PSP allocation anchor')
    names=set()
    for row in entries:
        target=surface['products'][row['artifact']]
        image=Path(target['path']).read_bytes()
        require(len(image)==target['size'] and sha(image)==target['sha256'], 'boot entry file identity')
        name='process-entry-%04d.bin.gz'%row['sequence']
        require(row['ram_file']==name and sha((directory/name).read_bytes())==row['ram_file_sha256']==receipt['files'][name],
                'boot entry dump binding')
        validate_entry(row,rows[row['request_sequence']],image,gzip.decompress((directory/name).read_bytes()),allow_exec=True)
        names.add(name)
    require(names=={n for n in receipt['files'] if n.startswith('process-entry-')}, 'complete actual boot dump set')
    ownership=validate_resident_memory(directory,receipt,rows,entries,root_mcb=metadata['root_program_mcb'])
    menu=json.loads((directory/'initial-op-menu.json').read_text())
    require(menu in rows and menu['kind']=='initial-op-menu' and menu['entry_sequence']==boot[-1]['sequence'] and
            menu['counter']==64 and boot[-1]['sequence'] < menu['sequence'] < overlay[0]['request_sequence'],
            'actual initial OP menu generation')
    memory=gzip.decompress((directory/menu['memory_file']).read_bytes())
    validate_counter(menu,boot[-1],json.loads((directory/'op-counter-profile.json').read_text()),memory)
    action=clock['actions'][0]
    require(action['tick']==menu['tick'] and action['unchanged_guest']['cpu_regs']==menu['cpu_regs'] and
            action['unchanged_guest']['segments']==menu['segments'], 'initial OP key at actual menu boundary')
    return dict(entries=entries,boot_entries=boot,overlay_entries=overlay,ownership=ownership,
                initial_menu=menu,scope='Actual DOS child/overlay entries and parent-anchored resident checkpoints; not continuous lifetime')
