#!/usr/bin/env python3
"""Read functional Windows smoke results; original DOS pixel parity is separate."""
import argparse
import hashlib
import json
from pathlib import Path

from verify_host_window import assess, row
from verify_natural_routes import strict_clear


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def window_case(folder):
    actions = []
    for line in (folder / 'actions.tsv').read_text().splitlines():
        name, begin, end = line.split('\t')
        actions.append(dict(name=name, begin=int(begin), end=int(end)))
    result = assess(folder / 'trace/window.tsv', actions)
    rows = [row(line) for line in (folder / 'trace/window.tsv').read_text().splitlines()
            if line.startswith('R ')]
    by_name = {action['name']: action for action in actions}
    bomb = by_name['bomb']
    selected = [r for r in rows if bomb['begin'] < r['seq'] <= bomb['end']]
    assert any(r['bombing'] for r in selected), 'Bomb did not start'
    assert min(r['bombs'] for r in selected) < rows[bomb['begin'] - 1]['bombs']
    pause, resume = by_name['pause'], by_name['resume']
    frozen = [r for r in rows if pause['end'] < r['seq'] <= resume['begin']]
    assert len(frozen) >= 10 and len({r['frame'] for r in frozen}) == 1
    assert rows[-1]['frame'] > frozen[-1]['frame'], 'Pause did not resume'
    result.update(bomb_spent=True, pause_frozen_refreshes=len(frozen),
                  hook_sha256=sha(folder / 'hook.txt'))
    return result


def natural_case(folder, case):
    route = folder / 'route'
    words = (route / 'result.txt').read_text().split()
    result = {words[i]: int(words[i + 1]) for i in range(0, len(words), 2)}
    states = [line.split() for line in (route / 'state.txt').read_text().splitlines()]
    assert [int(r[0]) for r in states] == list(range(result['ticks'] + 1))
    main = [r for r in states if 'CHILD' not in r]
    stages = {int(r[2]) for r in main}
    ending_path = route / 'ending-name.txt'
    ending = ending_path.read_text().strip() if ending_path.exists() else None
    outcome = strict_clear(result, (folder / 'saves/GENSOU.SCR').read_bytes(),
                           case['rank'], case['character'], case['shot'],
                           case.get('extra', False), stages, ending)
    assert outcome['accepted'], outcome
    if case.get('no_life_loss'):
        patch = (folder / 'life-patch.txt').read_text()
        if case.get('invincible'):
            assert 'no_death_gate' in patch and 'before A4' in patch and 'after A5' in patch
            assert all(int(r[9])==0 and int(r[12])==0 for r in main), 'Death or respawn in no-death mode'
        else:
            assert 'before 83-E8-01-88-42-19' in patch
            assert 'after 83-E8-00-88-42-19' in patch
            assert min(int(r[6]) for r in main) >= (3 if case.get('extra') else 6)
    cfg = (folder / 'saves/MIKO.CFG').read_bytes()
    assert len(cfg) == 10 and sum(cfg[:6]) % 256 == cfg[9]
    return dict(result=result, outcome=outcome,
                minimum_lives=min(int(r[6]) for r in main),
                misses=max(int(r[9]) for r in main),
                state_sha256=sha(route / 'state.txt'),
                inputs_sha256=sha(route / 'inputs.txt'),
                score_sha256=sha(folder / 'saves/GENSOU.SCR'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    assert manifest['version'] == 1 and not args.output.exists()
    for pin in manifest['inputs']:
        assert sha(pin['path']) == pin['sha256'], pin['path']
    cases = []
    for case in manifest['cases']:
        folder = Path(case['path'])
        assert (folder / 'controller-passed.txt').read_text().strip() == 'exit 0'
        if case['kind'] == 'window':
            result = window_case(folder)
        elif case['kind'] == 'natural':
            result = natural_case(folder, case)
        elif case['kind'] == 'ordinary-gameover':
            words = (folder / 'route/result.txt').read_text().split()
            result = {words[i]: int(words[i + 1]) for i in range(0, len(words), 2)}
            assert result['fresh_op'] and result['gameover_visits'] and result['registration_visits']
            assert not result['ending_visits']
            if case.get('reference'):
                reference = Path(case['reference'])
                for name in ('route/inputs.txt', 'route/state.txt',
                             'saves/GENSOU.SCR', 'saves/MIKO.CFG'):
                    assert sha(folder / name) == sha(reference / name), name
                result['gnu_reference_files_equal'] = 4
        else:
            assert case['kind'] == 'controls'
            assert (folder / 'checks').is_dir()
            files = [p for p in (folder / 'checks').rglob('*') if p.is_file()]
            assert files
            result = dict(files=len(files), scope=case['scope'])
        cases.append(dict(name=case['name'], passed=True, result=result))
    report = dict(passed=True, cases=cases, manifest_sha256=sha(args.manifest),
                  scope=manifest['scope'])
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
