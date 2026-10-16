"""Validate overlay generations, raw entry images, resident use and Quit input."""
import gzip
import json
import re
from pathlib import Path

from capture_th04_dos_demos import parse_mz, sha
from compare_th04_dos_demos import relocated_module, require
from th04_dos_process import artifact_for_path


def validate_entry(row, request, image, observed):
    require(parse_mz(image).valid, 'route entry MZ integrity')
    load = row['load_segment']
    require(request['kind'] == 'exec-request' and request['ax'] == 0x4b03 and
            request['requested_artifact'] == row['artifact'] and
            request['overlay_load_segment'] == request['overlay_relocation_factor'] == load,
            'route entry overlay request/load/factor')
    block = bytes.fromhex(request['overlay_parameter_hex'])
    require(block == load.to_bytes(2, 'little') * 2, 'route overlay parameter bytes')
    require(row['file_sha256'] == sha(image) and observed == relocated_module(image, load) and
            row['image_bytes'] == len(observed) and row['relocated_sha256'] == sha(observed),
            'route complete raw relocated image')
    cs, ip = load + int.from_bytes(image[22:24], 'little'), int.from_bytes(image[20:22], 'little')
    registers, segments = bytes.fromhex(row['cpu_regs']), bytes.fromhex(row['segments'])
    require(len(registers) == 48 and len(segments) == 136 and (row['cs'], row['ip']) == (cs, ip) and
            int.from_bytes(registers[32:36], 'little') & 65535 == ip and
            int.from_bytes(segments[8:16], 'little') == cs, 'route actual entry CPU PC')
    owner = row['owner']
    psp, mcb = bytes.fromhex(owner['psp_hex']), bytes.fromhex(owner['mcb_hex'])
    require(len(psp) == 256 and psp[:2] == b'\xcd\x20' and len(mcb) == 16 and mcb[0] in b'MZ' and
            int.from_bytes(mcb[1:3], 'little') == owner['psp_segment'] == owner['mcb_segment'] + 1 and
            owner['load_segment'] == load == owner['psp_segment'] + 16 and
            owner['mcb_paragraphs'] == int.from_bytes(mcb[3:5], 'little') and
            (load * 16 + len(observed)) <= (owner['psp_segment'] + owner['mcb_paragraphs']) * 16 <= 655360 and
            int.from_bytes(psp[0x2c:0x2e], 'little') == owner['environment_segment'] and
            artifact_for_path(bytes.fromhex(owner['executable_hex'])) == row['artifact'],
            'route entry MCB/PSP/environment')


def validate_keyboard(clock, receipt, first, resident):
    from compare_th04_dos_ordinary_prefix import validate_keyboard_capture
    actions, waits = clock['actions'], clock['waits']
    shots = [i for i, row in enumerate(actions) if row['key'] == 'KBD_z' and row['pressed'] is True]
    require(shots, 'route gameplay Shot')
    validate_keyboard_capture(dict(clock, actions=actions[:shots[-1] + 1]), first, resident)
    require(len(waits) == 2 and [row['kind'] for row in waits] == ['dialogue', 'quit'] and
            [row['frame'] for row in waits] == [receipt['dialog_at_frame'], receipt['quit_at_frame']],
            'route dialogue/Quit cue identity')
    previous = -1
    for action in actions:
        guard = action['unchanged_guest']
        require(action['key'] in ('KBD_z', 'KBD_enter', 'KBD_esc') and type(action['pressed']) is bool and
                previous <= action['tick'] and action['due'] <= action['tick'] and
                re.fullmatch('[0-9a-f]{64}', guard['conventional_sha256']) is not None and
                len(bytes.fromhex(guard['cpu_regs'])) == 48 and len(bytes.fromhex(guard['segments'])) == 136,
                'route keyboard order/guest preservation')
        previous = action['tick']
    dialogue, quit_wait = waits
    from th04_ordinary_continue import validate_release_resume
    validate_release_resume(clock, dialogue, 'dialogue', receipt['dialog_at_frame'])
    require(dialogue['resumed_frame'] == receipt['dialog_at_frame'] + 1 and
            quit_wait['outcome'] == 'main-overlay', 'route actual wait outcomes')
    start, end = quit_wait['action_start'], quit_wait['action_end']
    require(dialogue['action_end'] <= start < end <= len(actions), 'route Quit action extent')
    events = actions[start:end]
    require(events[0]['key'] == 'KBD_z' and events[0]['pressed'] is False and
            events[0]['tick'] >= quit_wait['tick'] + 100 and
            all(row['frame'] == receipt['quit_at_frame'] for row in events) and
            any(row['key'] == 'KBD_esc' and row['pressed'] is True for row in events) and
            not any(row['key'] == 'KBD_z' and row['pressed'] is True for row in events),
            'route release-first real Quit keys')
    require(not clock['remaining'], 'route pending keyboard events')


def validate_route(directory, receipt, capture):
    metadata = json.loads((directory / 'process-events.json').read_text())
    rows = [json.loads(s) for s in (directory / 'process-events.jsonl').read_text().splitlines()]
    require(metadata['schema_version'] == 1 and metadata['complete_capture'] is True and
            metadata['complete_route'] is True and metadata['boundary'] == 'fresh-op-menu' and
            metadata['error'] is None and metadata['pending'] is None and metadata['events'] == len(rows),
            'route complete process metadata')
    require([row['sequence'] for row in rows] == list(range(len(rows))) and
            all(a['tick'] <= b['tick'] for a, b in zip(rows, rows[1:])), 'route event sequence/clock')
    entries = [row for row in rows if row['kind'] == 'entry']
    require([row['artifact'] for row in entries] == ['th04-main', 'th04-maine', 'th04-op'] and
            metadata['entries'] == [row['sequence'] for row in entries], 'route executable generations')
    targets = json.loads((directory / 'process-targets.json').read_text())
    dump_names = set()
    for row in entries:
        spec = targets[row['artifact']]
        image = Path(spec['path']).read_bytes()
        require(sha(image) == spec['sha256'] and len(image) == spec['size'], 'route target file identity')
        require(row['request_sequence'] < row['sequence'], 'route request before entry')
        name = row['ram_file']
        require(name == 'process-entry-%04d.bin.gz' % row['sequence'] and
                sha((directory / name).read_bytes()) == row['ram_file_sha256'] == receipt['files'][name],
                'route entry dump identity/extent')
        observed = gzip.decompress((directory / name).read_bytes())
        validate_entry(row, rows[row['request_sequence']], image, observed)
        dump_names.add(name)
    require(dump_names == {name for name in receipt['files'] if name.startswith('process-entry-')},
            'route complete entry dump set')
    require(len({row['owner']['psp_segment'] for row in entries}) == 1 and
            [rows[row['request_sequence']]['caller_artifact'] for row in entries[1:]] == ['th04-main', 'th04-maine'],
            'route retained PSP/predecessor generations')
    for artifact in ('th04-op', 'th04-maine', 'th04-zun'):
        # The initial image gate separately attests these original products.
        require(targets[artifact]['sha256'] == capture['original_product_hashes'][artifact],
                'route original supporting image identity')
    require(targets['th04-main']['sha256'] == receipt['main_sha256'], 'route MAIN producer binding')
    handoff = json.loads((directory / 'main-handoff.json').read_text())
    request = rows[handoff['request_sequence']]
    resident = bytes.fromhex(request['resident_hex'])
    count = receipt['main_frames']
    require(handoff['schema_version'] == 1 and handoff['natural_game_exit'] is False and
            handoff['completed_updates'] == handoff['incomplete_update_frame'] == count == receipt['quit_at_frame'] and
            handoff['requested_limit'] == receipt['end_after'] and
            handoff['request_sequence'] == entries[1]['request_sequence'] and
            handoff['resident_hex'] == request['resident_hex'] and len(resident) == 256 and
            resident[:11] == b'HUMAConfig\0' and resident[48] == 0 and
            resident[29:37].hex() == capture['rows'][-1]['score_digits'], 'route published MAIN resident/score')
    retired = [row for row in rows if row['kind'] == 'main-observer-retired']
    require(len(retired) == 1 and retired[0]['request_sequence'] == request['sequence'] and
            request['sequence'] < retired[0]['sequence'] < entries[1]['sequence'] and
            retired[0]['unchanged_guest']['cpu_regs'] == request['cpu_regs'] == retired[0]['cpu_regs'] and
            retired[0]['unchanged_guest']['segments'] == request['segments'] == retired[0]['segments'] and
            retired[0]['tick'] == request['tick'], 'route old MAIN observer retirement')
    menu = json.loads((directory / 'fresh-op-menu.json').read_text())
    require(menu == rows[-1] and menu['kind'] == 'fresh-op-menu' and
            menu['entry_sequence'] == entries[2]['sequence'], 'route fresh OP activity boundary')
    registers, segments = bytes.fromhex(menu['cpu_regs']), bytes.fromhex(menu['segments'])
    load = entries[2]['load_segment']
    base = menu['resident_linear']
    require(menu['cs'] == int.from_bytes(segments[8:16], 'little') == load + 0x0a74 and
            menu['ip'] == int.from_bytes(registers[32:36], 'little') & 65535 == 0x0d2f and
            int.from_bytes(segments[24:32], 'little') == load + 0x0f34 and
            int.from_bytes(segments[:8], 'little') * 16 + (int.from_bytes(registers[12:16], 'little') & 65535) == base,
            'route fresh OP menu/resident CPU ownership')
    require(all(row['resident_linear'] == base and bytes.fromhex(row['resident_hex'])[:11] == b'HUMAConfig\0'
                for row in (request, *entries[1:], menu)), 'route shared resident address/identity')
    before, after = bytes.fromhex(entries[2]['resident_hex']), bytes.fromhex(menu['resident_hex'])
    require(after[:20] + after[24:] == before[:20] + before[24:] and
            menu['counter'] == int.from_bytes(after[20:24], 'little') ==
            (int.from_bytes(before[20:24], 'little') + 1) & 0xffffffff, 'route fresh OP resident counter store')
    return dict(entries=entries, handoff=request, menu=menu, resident_pointer=base,
                completed_updates=count, partial_update=count, natural_game_exit=False,
                scope='Actual overlay entries, published/shared resident bytes and fresh OP menu use; resident allocation-owner MCB not sampled')


def decode_score_sections(data):
    require(len(data) == 1960, 'route score file extent')
    sections = []
    for number in range(10):
        encoded = data[number * 196:(number + 1) * 196]
        plain = bytearray(encoded)
        for i in range(4, 195):
            next_byte = encoded[i + 1]
            plain[i] = (encoded[0] + ((((next_byte >> 3) | (next_byte << 5)) & 255) ^ encoded[1]) + encoded[i]) & 255
        plain[195] = (encoded[195] + encoded[0]) & 255
        require(int.from_bytes(plain[2:4], 'little') == sum(plain[4:]) & 65535,
                'route full 16-bit score checksum section %d' % number)
        sections.append(bytes(plain[4:]))
    return sections
