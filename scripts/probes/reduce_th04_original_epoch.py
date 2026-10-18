#!/usr/bin/env python3
"""Audit complete timer phases and original V86 UART/PIC/CPU dispatch ordering."""
import argparse
import copy
from collections import Counter
import json
from pathlib import Path

import pc98_keyboard_clock as clock
import reduce_th04_original_pic as pic


def audit(capture,read_data=None,hash_file=None):
    """Use regular files, or explicit exact-byte archive readers after retirement."""
    c=Path(capture)
    read_data=read_data or (lambda path:Path(path).read_bytes())
    sha=hash_file or clock.sha
    read=lambda path:json.loads(read_data(path))
    receipt=read(c/'receipt.json');assert receipt['complete'] and not receipt['timeout'] and receipt['exit']==0
    for batch in [receipt['source_files'],receipt['capsule'],{str(c/name):value for name,value in receipt['files'].items()}]:
     for path,digest in batch.items():assert sha(Path(path))==digest,path
    plan=read(c/'font-plan.json');meta=read(c/'keyboard-admission.json');cm=read(c/'clock-events.json')
    engine=Path(receipt['command'][receipt['command'].index('--args')+1]);elf=clock.attest_timer(engine,plan['keyboard_admission']['symbols'])
    bias=meta['symbols']['_Z13TIMER_AddTickv']-elf['timer_elf_address'];assert cm['timer_address']==meta['symbols']['_Z13TIMER_AddTickv']
    for name,item in plan['keyboard_admission']['symbols'].items():assert meta['symbols'][name]==item['address']+bias,name
    rows=[json.loads(line) for line in read_data(c/'keyboard-admission.jsonl').splitlines()];clocks=[json.loads(line) for line in read_data(c/'clock-events.jsonl').splitlines()]
    assert sha(c/'keyboard-admission.jsonl')==meta['stream_sha256'] and sha(c/'clock-events.jsonl')==cm['stream_sha256']
    assert cm['passed'] and cm['phase']=='observe' and cm['offsets']==clock.OFFSETS and len(clocks)==cm['records']
    assert rows[0]['kind']=='main-image-entry' and 'clock_audit' not in rows[0]['time']
    assert all('clock_audit' in row['time'] for row in rows[1:])
    packet=copy.deepcopy(rows[1:])
    for index,row in enumerate(packet):row['captured_ordinal']=row['ordinal'];row['ordinal']=index
    for row in clocks+packet:clock.audit_pic(row,meta['symbols'])
    a,canonical=clock.audit_rows(clocks,packet,cm['timer_address'])
    p=pic.reduce(rows,meta,read(c/'stage-input.json'));assert p['observed_loops']==8
    moments={row['captured_ordinal']:value for row,value in zip(packet,canonical,strict=True)}
    checks=[];pairs=[];pending=None
    for row in rows[1:]:
     g=row['pic']['cpu_dispatch'];assert g['irq_delay_ns']==406 and g['irq_hacks']==[0]*16
     if row['kind']=='pic-check-entry':
      assert pending is None and g['irq_check']==0 and g['irq_check_pending']==1
      pending=row
     elif row['kind']=='pic-check-return':
      assert pending is not None and g['irq_check']==1 and g['irq_check_pending']==0
      assert moments[row['ordinal']]==moments[pending['ordinal']]
      checks.append(dict(entry=pending['ordinal'],returned=row['ordinal']));pending=None
    assert pending is None
    last_receive=None
    for row in rows[1:]:
     if row['kind']=='rx-return':
      assert last_receive is None and row['pic']['cpu_dispatch']['irq_check']==0 and row['pic']['cpu_dispatch']['irq_check_pending']==1
      last_receive=row
     elif row['kind']=='cpu-irq-accept' and row['vector']==9:
      assert last_receive is not None
      between=rows[last_receive['ordinal']+1:row['ordinal']]
      assert [x['kind'] for x in between]==['pic-check-entry','pic-check-return','pic-dispatch-entry']
      delta=(moments[row['ordinal']]-moments[last_receive['ordinal']])*36000
      assert delta.denominator==1 and delta>=0
      pairs.append(dict(receive=last_receive['ordinal'],check=between[0]['ordinal'],accepted=row['ordinal'],emulated_counter_cycles=int(delta)))
      last_receive=None
    assert last_receive is None and len(pairs)==len(p['bios_boundaries'])
    image=read(c/'original-pic-image.json')
    assert image['passed'] and image['unchanged_context'] and image['module_size']==150114
    assert image['target_main_sha256']==pic.MAIN and image['entry_ip']==0
    assert image['entry_cs']==image['load_segment']==rows[0]['load_segment']
    return dict(passed=True,clock=a,timer_elf=elf,pic=p,pic_checks=checks,
        receive_check_accept=pairs,
        emulated_counter_cycle_intervals=dict(Counter(x['emulated_counter_cycles'] for x in pairs)),
        configured_pic_irq_delay_ns=406,converted_native_quanta_ceiling=(406*72+124)//125,
        entry_snapshot_audited=False,
        scope='Original first8-stage-update packet on one pinned emulator. Complete timer phases establish a canonical observation clock; '
              'delayed PIC checks precede CPU acceptance. Configured406ns is not a fitted serial-to-BIOS delay. '
              'Counter intervals do not establish physical latency, ISR cost, native CPU availability or a common boot epoch.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=audit(args.capture)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('ORIGINAL DISPATCH EPOCH PASS',result['clock']['timer_transactions'],
          'timer transactions;',len(result['receive_check_accept']),'receive/check/accept pairs')


if __name__=='__main__':
    main()
