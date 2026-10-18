"""Feed actual external requests, all timer ticks, RX callbacks and CPU reads to native owners."""
import argparse,collections,hashlib,json,subprocess
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--capture',type=Path,required=True)
p.add_argument('--program',type=Path,required=True)
p.add_argument('--tick-layout',type=Path,required=True)
p.add_argument('--model-header',type=Path,required=True)
p.add_argument('--build-receipt',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();c=a.capture
for path in (a.output,a.output.with_suffix('.input'),a.output.with_suffix('.stdout'),a.output.with_suffix('.stderr')):
 if path.exists():p.error('output or companion exists; use fresh paths')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();receipt=json.loads((c/'receipt.json').read_text());assert receipt['passed'] and not receipt['timeout'] and receipt['exit']==0
for path,digest in receipt['inputs'].items():assert sha(Path(path))==digest,path
meta=json.loads((c/'keyboard-admission.json').read_text());raw=(c/'keyboard-admission.jsonl').read_bytes();assert meta['complete'] and not meta['error'] and hashlib.sha256(raw).hexdigest()==meta['stream_sha256'];events=[json.loads(v) for v in raw.splitlines()];assert len(events)==meta['records']
build=json.loads(a.build_receipt.read_text());assert build['passed']
relative=str(a.program.resolve().relative_to(a.build_receipt.resolve().parent))
assert sha(a.program)==build['programs'][relative]
assert a.program.read_bytes()[:4]==b'\x7fELF','execute GNU/UBSan only;Windows is compile-only'
assert a.model_header.resolve()==Path(build['native_root'])/'port64/pc98_keyboard.hpp'
for item in build['source_files']:
 path=Path(build['native_root'])/item['path'];assert sha(path)==item['sha256'],item['path']
assert next(v['sha256'] for v in build['source_files'] if v['path']=='port64/pc98_keyboard.hpp')==sha(a.model_header)
layout=json.loads(a.tick_layout.read_text());assert layout['passed'];offsets=layout['layout'];pending={};operations=[];ticks=[]
def time(e):return Fraction(e['time']['numerator'],e['time']['denominator'])
def wire_time(e):
 q=time(e)*576000;assert q.denominator==1;return q.numerator
for e in events:
 kind=e['kind']
 if kind in ['request-entry','keyboard-tick-entry','rx-entry','bios-irq-entry']:pending[kind]=e
 if kind in ['request-return','keyboard-tick-return','rx-return','bios-irq-return']:
  before=pending.pop(kind.replace('return','entry'));assert time(before)==time(e)
  if kind=='request-return':
   assert before['key'] in [30,52] and e['unchanged_guest'] and before['context']==e['context'];scan={30:0x29,52:0x1c}[before['key']];line=f"K {wire_time(before)} {before['key']} {scan} {int(before['pressed'])}"
  elif kind=='keyboard-tick-return':
   b=bytes.fromhex(before['keyboard_raw']);assert len(b)==352
   slot=int.from_bytes(b[offsets['pending_key']:offsets['pending_key']+4],'little',signed=True);assert slot==-1,'fixture pending slot outside modeled tick path'
   enabled=not b[offsets['reset']] and b[offsets['active']] and b[offsets['scanning']]
   line=f'T {wire_time(before)} {int(enabled)}';ticks.append(before['time']['raw']['PIC_Ticks'])
  elif kind=='rx-return':line=f'R {wire_time(before)}'
  else:line=f'B {wire_time(before)}'
  operations.append((before['ordinal'],line,e))
assert not pending
operations.sort(key=lambda item:item[0]);commands=''.join(line+'\n' for _,line,e in operations)
wire=a.output.with_suffix('.input');wire.write_text(commands)
process=subprocess.run([str(a.program.resolve()),'--trace'],input=commands,text=True,capture_output=True);a.output.with_suffix('.stdout').write_text(process.stdout);a.output.with_suffix('.stderr').write_text(process.stderr);assert process.returncode==0,process.stderr
lines=process.stdout.splitlines();assert len(lines)==len(operations);errors=[]
for index,(line,(_,command,e)) in enumerate(zip(lines,operations,strict=True)):
 cells=line.split();assert int(cells[0])==index;u=e['uart'];expected=[u['recv_in'],u['recv_out'],u['rx_busy'],u['rx_ready'],u['data'],(u['recv_in']-u['recv_out'])%32]
 observed=list(map(int,cells[3:9]));bios=cells[9]
 if observed!=expected or bios!=e['bios']:errors.append(dict(operation=index,kind=command[0],ordinal=e['ordinal'],observed=observed,expected=expected,observed_bios=bios,expected_bios=e['bios']))
 if 'keyboard_raw' in e:
  b=bytes.fromhex(e['keyboard_raw']);actual=[int.from_bytes(b[248:256],'little'),int.from_bytes(b[240:244],'little')]
  if list(map(int,cells[1:3]))!=actual:errors.append(dict(operation=index,kind=command[0],observed_repeat=cells[1:3],expected_repeat=actual))
assert not errors,errors[:4]
assert all(y==x+1 for x,y in zip(ticks,ticks[1:])),'missing actual ticker call'
counts=collections.Counter(v['kind'] for v in events);emitted=list(map(int,lines[-1].split()[11:]));assert len(emitted)==int(lines[-1].split()[10])
report=dict(passed=True,build_receipt_sha256=sha(a.build_receipt),tick_layout_sha256=sha(a.tick_layout),capture_receipt_sha256=sha(c/'receipt.json'),admission_stream_sha256=hashlib.sha256(raw).hexdigest(),model_source_sha256=sha(a.model_header),program_sha256=sha(a.program),operations=len(operations),actual_timer_ticks=len(ticks),first_last_timer_tick=[ticks[0],ticks[-1]],external_calls=counts['request-entry'],internal_repeat_calls_observed_not_fed=counts['internal-repeat-entry'],rx_callbacks=counts['rx-entry'],irq_bios_reads=counts['bios-irq-entry'],emitted_bytes=emitted,errors=errors,scope='Native Typematic/Receiver/matrix owners start from constructor defaults. Actual external requests and every observed timer tick drive repeats;internal-repeat calls andexpected latches never drive them. Actual receive callbacks andCPU BIOS reads are separate external events. Allpost-event FIFO/data/ready/busy/matrix andrecorded repeat state agree. Captured admission times calibrate the boundary;thisdoesnotestablish a native game clock,guestIRQlatency,original V86/fullcampaign,hardware orNP2 parity.')
a.output.write_text(json.dumps(report,indent=2)+'\n');print('NATIVE DEVICE ORACLE PASS',len(operations),'operations;',len(ticks),'actual ticks;',emitted,flush=True)
