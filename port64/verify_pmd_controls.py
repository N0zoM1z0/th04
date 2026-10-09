#!/usr/bin/env python3
"""Check original PMD effects, fade, restart and IRQ/measure negative controls.

Consumes an immutable all-music original producer with its own source identity.
The original driver executes again. Explicit DOS/board/IRQ adapters are those
of verify_pmd_driver.py; no native synthesis or physical timing is accepted.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from verify import source_manifest
from verify_pmd_driver import DRIVERS, directory_files, ending_assets, install, sha


def controls(binaries, assets, load, name):
    driver = install(binaries[name], name, load)
    effects = driver.write_resource(0xb00, assets['MIKO.EFC'])
    records = []
    for effect in range(17):
        driver.ports = []
        driver.ticks = 0
        reply = driver.service(0xc00 | effect)
        for tick in range(32):
            driver.ticks = tick + 1
            driver.irq(3)
        records.append(dict(effect=effect, reply=reply, state=driver.snapshot(),
                            ports=driver.ports))

    # LOGO deliberately has a different measure length from OP. Run original
    # commands rather than deriving the returned measure from elapsed ticks.
    driver.ports = []
    song = 'LOGO.' + DRIVERS[name][3]
    driver.service(0x100)
    address = driver.write_resource(0x600, assets[song])
    driver.service(0)
    for tick in range(96):
        driver.ticks = tick + 1
        driver.irq(3)
    running = driver.snapshot()
    driver.service(0x204)
    faded = []
    for tick in range(128):
        driver.ticks = tick + 1
        driver.irq(1)
        faded.append(driver.snapshot())
    if any(state['measure'] != running['measure'] for state in faded):
        raise ValueError('Timer A fade fabricated song measure advancement')
    if faded[-1]['volume'] == running['volume']:
        raise ValueError('original Timer A fade did not change volume')

    driver.service(0x100)
    stopped = driver.snapshot()
    for _ in range(128):
        driver.irq(3)
    if driver.snapshot()['measure'] != stopped['measure']:
        raise ValueError('stopped original measure advanced')
    driver.service(0)
    restarted = driver.snapshot()
    if restarted['measure'] != 0 or restarted['volume'] & 255:
        raise ValueError('original restart did not reset measure/fade')
    return dict(effects=effects, cases=records, song=song, song_address=address,
                running=running, fade=faded, stopped=stopped,
                restarted=restarted, control_ports=driver.ports)


def negative_controls(binaries, assets, reference):
    name = 'PMD86.COM'
    driver = install(binaries[name], name, 0x2000)
    driver.write_resource(0x600, assets['LOGO.M86'])
    driver.service(0)
    for tick in range(96):
        driver.ticks = tick + 1
        driver.irq(3)
    actual = driver.service(0x500)['ax']
    expected = reference['states'][95]['measure']
    if actual != expected:
        raise ValueError('fresh original CPU does not reproduce LOGO reference')
    fixed_counter = 96 // 96
    if fixed_counter == expected:
        raise ValueError('reference cannot reject fixed96tick measure adapter')

    # Adapter-only variant leaves the timer flag latched despite the original
    # driver's ack writes. The real interrupt handler must exhaust its bounded
    # execution allowance, rather than returning a fabricated successful tick.
    original_output = driver.output
    def missing_ack(u, port, size, value, user):
        status = driver.fm_status
        original_output(u, port, size, value, user)
        driver.fm_status = status
    driver.output = missing_ack
    original_run = driver.run
    driver.run = lambda: original_run(limit=20000)
    rejected = None
    try:
        driver.irq(2)
    except ValueError as error:
        rejected = str(error)
    if rejected is None or 'bounded run exhausted' not in rejected:
        raise ValueError('missing IRQ ack variant was not rejected')
    return dict(fixed96tick=dict(rejected=True, expected=expected,
                                actual=actual, variant=fixed_counter),
                missing_ack=dict(rejected=True, result=rejected,
                                 limit=20000),
                scope='Adapter-only negative controls; no target bytes changed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('hdi', 'reference', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest, files = source_manifest(root)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    producer = json.loads((args.reference / 'receipt.json').read_text())
    if not producer['passed'] or producer['cases'] != 138:
        raise ValueError('all-music original producer is incomplete')
    for name, digest in producer['outputs'].items():
        if sha((args.reference / name).read_bytes()) != digest:
            raise ValueError('immutable music producer output changed: ' + name)
    binaries = directory_files(args.hdi)
    assets = ending_assets(args.hdi)
    groups = {}
    for load in (0x1000, 0x2000):
        rows = {name: controls(binaries, assets, load, name) for name in DRIVERS}
        if groups and rows != groups['1000']:
            raise ValueError('relocated effects/fade/restart control differs')
        groups[f'{load:04x}'] = rows
        print(f'Original PMD controls load{load:04x}: 51SE + 3fade/restarts PASS',
              flush=True)
    reference = json.loads(
        (args.reference / 'PMD86.COM-1000-LOGO.M86.json').read_text())
    negative = negative_controls(binaries, assets, reference)
    path = out / 'controls.json'
    path.write_text(json.dumps(dict(groups=groups, negative=negative),
                               separators=(',', ':')) + '\n')
    if source_manifest(root)[0] != manifest:
        raise ValueError('source changed during original controls')
    receipt = dict(passed=True, utc=datetime.now(timezone.utc).isoformat(),
                   source_manifest=manifest, source_files=len(files),
                   reference_source_manifest=producer['source_manifest'],
                   reference_receipt_sha256=sha(
                       (args.reference / 'receipt.json').read_bytes()),
                   hdi_sha256=producer['hdi_sha256'], effect_cases=102,
                   fade_restart_cases=6, loads=['1000', '2000'],
                   controls_sha256=sha(path.read_bytes()), negative=negative,
                   command=sys.argv, scope=__doc__)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Original PMD controls and two adapter negatives PASS')


if __name__ == '__main__':
    main()
