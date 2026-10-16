"""Validate overlay generations, raw entry images, resident use and Quit input."""
import gzip
import json
import re
from pathlib import Path

from capture_th04_dos_demos import parse_mz, sha
from compare_th04_dos_demos import relocated_module, require
from th04_dos_process import artifact_for_path, resident_allocation


def validate_entry(row, request, image, observed, allow_exec=False):
    require(parse_mz(image).valid, 'route entry MZ integrity')
    load = row['load_segment']
    if allow_exec:
        require(len(bytes.fromhex(request['cpu_regs'])) == 48 and request['opcode'] == 'cd21',
                'entry actual software INT21 request')
        require(request['ax'] == int.from_bytes(bytes.fromhex(request['cpu_regs'])[:2],'little') == row['request_ax'],
                'entry raw DOS request AX')
    if allow_exec and request['ax'] == 0x4b00:
        require(request['kind'] == 'exec-request' and request['requested_artifact'] == row['artifact'],
                'entry actual DOS load-and-go request')
    else:
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
    if allow_exec:
        require(owner['parent_psp'] == int.from_bytes(psp[0x16:0x18],'little'),
                'entry actual parent PSP field')


def validate_keyboard(clock, receipt, first, resident, op_profile=None):
    from compare_th04_dos_ordinary_prefix import validate_keyboard_capture
    actions, waits = clock['actions'], clock['waits']
    initial_actions = actions[:clock['second_main']['action_start']] if clock.get('second_main') else actions
    shots = [i for i, row in enumerate(initial_actions) if row['key'] == 'KBD_z' and row['pressed'] is True]
    require(shots, 'route gameplay Shot')
    initial_clock = dict(clock, actions=actions[:shots[-1] + 1])
    if op_profile is None:
        validate_keyboard_capture(initial_clock, first, resident)
    else:
        validate_keyboard_capture(initial_clock, first, resident, op_profile=op_profile)
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
    if receipt.get('restart_main'):
        validate_restart_keys(clock, quit_wait['action_end'])
    require(not clock['remaining'], 'route pending keyboard events')


def validate_restart_keys(clock, previous_end):
    actions = clock['actions']
    cue = clock['restart']
    start, end = cue['action_start'], cue['action_end']
    require(previous_end <= start < end == (clock['second_main']['action_start'] if clock.get('second_main') else len(actions)) and
            cue['tick'] < cue['entry_tick'] and cue['resident_seed'] == 65,
            'route restart action extent/seed')
    actual = actions[start:end]
    planned = [[cue['tick'] + delta + offset, 'KBD_enter', pressed]
               for delta in (range(0,30001,1000) if cue.get('menu_boundary') else (100,1100,2100)) for offset, pressed in ((0, True), (120, False))]
    require([[event['due'], event['key'], event['pressed']] for event in actual] + cue['cancelled'] == planned and
            all(event['tick'] <= cue['entry_tick'] and event['frame'] is None for event in actual) and
            cue['enter_down'] is actual[-1]['pressed'], 'route actual ordinary restart keys/cancellation')

def validate_route(directory, receipt, capture):
    restart = receipt.get('restart_main', False)
    expected_artifacts = ['th04-main', 'th04-maine', 'th04-op'] + (['th04-main'] if restart else [])
    expected_boundary = 'second-main-prefix' if receipt.get('restart_updates') else 'second-main-entry' if restart else 'fresh-op-menu'
    metadata = json.loads((directory / 'process-events.json').read_text())
    rows = [json.loads(s) for s in (directory / 'process-events.jsonl').read_text().splitlines()]
    require(metadata['schema_version'] == 1 and metadata['complete_capture'] is True and
            metadata['complete_route'] is True and metadata['boundary'] == expected_boundary and
            metadata['error'] is None and metadata['pending'] is None and metadata['events'] == len(rows),
            'route complete process metadata')
    require([row['sequence'] for row in rows] == list(range(len(rows))) and
            all(a['tick'] <= b['tick'] for a, b in zip(rows, rows[1:])), 'route event sequence/clock')
    all_entries = [row for row in rows if row['kind'] == 'entry']
    entries = [row for row in all_entries if row['request_ax'] == 0x4b03] if receipt.get('all_products') else all_entries
    require([row['artifact'] for row in entries] == expected_artifacts and
            metadata['entries'] == [row['sequence'] for row in all_entries], 'route executable generations')
    targets = json.loads((directory / 'process-targets.json').read_text())
    dump_names = set()
    for row in all_entries:
        spec = targets[row['artifact']]
        image = Path(spec['path']).read_bytes()
        require(sha(image) == spec['sha256'] and len(image) == spec['size'], 'route target file identity')
        require(row['request_sequence'] < row['sequence'], 'route request before entry')
        name = row['ram_file']
        require(name == 'process-entry-%04d.bin.gz' % row['sequence'] and
                sha((directory / name).read_bytes()) == row['ram_file_sha256'] == receipt['files'][name],
                'route entry dump identity/extent')
        observed = gzip.decompress((directory / name).read_bytes())
        validate_entry(row, rows[row['request_sequence']], image, observed, allow_exec=receipt.get('all_products',False))
        dump_names.add(name)
    require(dump_names == {name for name in receipt['files'] if name.startswith('process-entry-')},
            'route complete entry dump set')
    require(len({row['owner']['psp_segment'] for row in entries}) == 1 and
            [rows[row['request_sequence']]['caller_artifact'] for row in entries[1:]] == ['th04-main', 'th04-maine'] + (['th04-op'] if restart else []),
            'route retained PSP/predecessor generations')
    for artifact in ('th04-op', 'th04-maine', 'th04-zun'):
        # The initial image gate separately attests these original products.
        require(targets[artifact]['sha256'] == capture['executed_product_hashes'][artifact],
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
    require(menu in rows and (restart or menu == rows[-1]) and menu['kind'] == 'fresh-op-menu' and
            menu['entry_sequence'] == entries[2]['sequence'], 'route fresh OP activity boundary')
    registers, segments = bytes.fromhex(menu['cpu_regs']), bytes.fromhex(menu['segments'])
    load = entries[2]['load_segment']
    base = menu['resident_linear']
    if receipt.get('all_products'):
        from th04_dos_boot import validate_counter
        profile = json.loads((directory/'op-counter-profile.json').read_text())
        memory = gzip.decompress((directory/menu['memory_file']).read_bytes())
        validate_counter(menu,entries[2],profile,memory)
    else:
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
    ownership = validate_resident_memory(directory, receipt, rows, all_entries,
        root_mcb=metadata.get('root_program_mcb') if receipt.get('all_products') else None) if receipt.get('resident_ownership') else None
    if restart:
        cue = capture['clock']['restart']
        require(bool(cue.get('menu_boundary')) == bool(receipt.get('restart_menu_boundary')),
                'route restart menu input policy')
        if receipt.get('restart_menu_boundary'):
            action = capture['clock']['actions'][cue['action_start']]
            require(action['tick'] == menu['tick'] and action['unchanged_guest']['cpu_regs'] == menu['cpu_regs'] and
                    action['unchanged_guest']['segments'] == menu['segments'], 'actual fresh-menu confirmation boundary')
        require(cue['menu_sequence'] == menu['sequence'] and cue['tick'] == menu['tick'] and
                cue['entry_sequence'] == entries[-1]['sequence'] and cue['entry_tick'] == entries[-1]['tick'] and
                menu['sequence'] < entries[-1]['request_sequence'] < entries[-1]['sequence'] and
                (receipt.get('restart_updates') or entries[-1] == rows[-1]) and entries[-1]['resident_linear'] == base,
                'route actual fresh-menu/second-MAIN generation')
    if receipt.get('restart_updates'):
        armed = [row for row in rows if row['kind'] == 'second-main-observer-armed']
        end = json.loads((directory/'second-main-prefix.json').read_text())
        require(len(armed) == 1 and armed[0]['entry_sequence'] == entries[-1]['sequence'] and
                armed[0]['expected_generation'] == 2 and armed[0]['observer_generation'] == 1 and
                entries[-1]['sequence'] < armed[0]['sequence'] < end['sequence'] and
                armed[0]['tick'] == entries[-1]['tick'] and
                armed[0]['unchanged_guest']['cpu_regs'] == armed[0]['cpu_regs'] == entries[-1]['cpu_regs'] and
                armed[0]['unchanged_guest']['segments'] == armed[0]['segments'] == entries[-1]['segments'],
                'second MAIN observer generation/unchanged entry context')
        require(end == rows[-1] and end['kind'] == 'second-main-prefix' and end['generation'] == 2 and
                end['completed_updates'] == receipt['restart_updates'] and
                end['entry_sequence'] == entries[-1]['sequence'] and end['resident_linear'] == base,
                'second MAIN real update boundary')
        followup = capture['clock']['second_main']
        require(followup['entry_sequence'] == entries[-1]['sequence'] and
                followup['armed_sequence'] == armed[0]['sequence'] and
                followup['prefix_sequence'] == end['sequence'] and followup['prefix_tick'] == end['tick'] and
                followup['completed_updates'] == followup['requested_updates'] == receipt['restart_updates'],
                'second MAIN clock/update binding')
    return dict(entries=entries, handoff=request, menu=menu, resident_pointer=base,
                resident_ownership=ownership, restart_main=restart,
                completed_updates=count, partial_update=count, natural_game_exit=False,
                scope='Actual overlay entries and resident use; checkpoint allocation proof only when resident_ownership is present; no continuous lifetime or second-MAIN gameplay acceptance')


def validate_resident_memory(directory, receipt, rows, entries, root_mcb=None):
    samples, names = [], set()
    for row in rows:
        if row['resident_linear'] is None and not receipt.get('all_products'):
            continue
        name = 'process-memory-%04d.bin.gz' % row['sequence']
        require(row['memory_file'] == name and sha((directory / name).read_bytes()) ==
                row['memory_file_sha256'] == receipt['files'][name], 'route ownership memory identity')
        memory = gzip.decompress((directory / name).read_bytes())
        require(len(memory) == 655360 and sha(memory) == row['conventional_sha256'],
                'route complete conventional memory')
        if row['resident_linear'] is not None:
            allocation = row['resident_allocation']
            require(allocation == resident_allocation(memory, allocation['program_mcb'], row['resident_linear']) and
                    allocation['program_mcb'] == (root_mcb if root_mcb is not None else entries[0]['owner']['mcb_segment']) and
                    memory[row['resident_linear']:row['resident_linear'] + 256].hex() == row['resident_hex'],
                    'route actual resident allocation/content')
        if row['kind'] == 'entry':
            owner = row['owner']
            psp, mcb = owner['psp_segment'] * 16, owner['mcb_segment'] * 16
            require(memory[psp:psp + 256].hex() == owner['psp_hex'] and
                    memory[mcb:mcb + 16].hex() == owner['mcb_hex'], 'route actual full PSP/MCB readback')
            start = row['load_segment'] * 16
            module = gzip.decompress((directory / row['ram_file']).read_bytes())
            require(memory[start:start + len(module)] == module, 'route entry/conventional image agreement')
        if row['resident_linear'] is not None:
            samples.append(dict(sequence=row['sequence'], kind=row['kind'], allocation=allocation['allocation']))
        names.add(name)
    require(samples and names == {name for name in receipt['files'] if name.startswith('process-memory-')},
            'route complete ownership dump set')
    require(all(row['allocation'] == samples[0]['allocation'] for row in samples),
            'route persistent allocation checkpoint identity')
    return dict(passed=True, checkpoints=samples,
                scope='Actual MCB chain/owner field and allocated resident extent at captured checkpoints; no continuous lifetime claim')


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
