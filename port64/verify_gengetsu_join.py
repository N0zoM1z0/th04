#!/usr/bin/env python3
"""Actual OP/Extra/two dialogues/Mugetsu/Gengetsu actor controls across hosts.

Compare complete native captures and ordered original dialog/resource requests.
The actor controls suppress player-hit consumption and adapt the unlock bit.
The original script producer uses explicit graphics/input/wait/sound/file
adapters. This is not original complete MAIN pixels, ordinary survival, third
Extra dialogue/completion/unlock/save, audio or physical timing acceptance.
"""
import argparse,hashlib,itertools,json
from pathlib import Path
from datetime import datetime,timezone
from verify import source_manifest
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def validate(frontend,original,extra_clear=False,extra_maine=False):
 producer=json.loads((original/'receipt.json').read_text());assert producer['passed'] and producer['resource_cases']==512 and producer['loads']==['1000','2000']
 assert producer['target_sha256']=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
 assert sha(original/'resource-original.txt')==producer['resource_trace_sha256']
 resources=(original/'resource-original.txt').read_text().splitlines();wanted=None
 for load in ('1000','2000'):
  path=original/f'script-{load}-0.txt';record=next(r for r in producer['scripts'] if r['load']==load and r['held']==0);assert sha(path)==record['trace_sha256']
  scenes=[[],[],[]];scene=0
  for line in path.read_text().splitlines():
   if line.startswith('END '):assert int(line.split()[1])==[987,1736,1961][scene];scene+=1;continue
   fields=line.split()
   if fields[-1]!='-':fields[-1]=bytes.fromhex(fields[-1]).decode('ascii')
   scenes[scene].append(' '.join(fields))
  assert wanted is None or wanted==scenes;wanted=scenes
 result=[]
 for character,shot,shooting,paint in itertools.product(range(2),range(2),(1,) if extra_clear else range(2),range(2)):
  name=f'{character}-{shot}-{shooting}-{paint}';lines=(frontend/(name+'.txt')).read_text().splitlines()
  for owner in range(3 if extra_clear else 2):
   actual=[line.split(' ',1)[1] for line in lines if line.startswith(f'dialog{owner} ')]
   assert actual==wanted[owner],f'{name}: dialogue{owner} requests differ'
  expected=[]
  for calls in (0,1):
   row=resources[character*256+calls].split();assert row[0]==str(calls+1)
   expected.extend(row[i:i+4] for i in range(2,len(row),4))
  actual=[line.split()[1:] for line in lines if line.startswith('resource ')]
  assert actual==expected,f'{name}: original resource requests differ'
  states=[list(map(int,line.split()[1:])) for line in lines if line.startswith('state ')]
  for owner in range(2):
   records=[r for r in states if r[0]==owner];phases=[r[2] for i,r in enumerate(records) if not i or r[2]!=records[i-1][2]]
   assert phases==([0,1,2,3,4,5,6,7,254,255] if not owner else [0,1,2,3,4,5,6,7,8,9,254,255]),f'{name}: phases differ'
   if not owner:assert records[0][1:4]==[11197,0,1]
   else:assert records[0][2:4]==[0,0] and records[0][5:7]==[3072,1536]
  pending=next(line for line in lines if line.startswith('pending ')).split();assert pending[0]=='pending' and int(pending[10])==1736
  numbers=list(map(int,pending[1:]));assert numbers[12]>0 and numbers[13]>0 and numbers[14]>0
  assert numbers[1]>1000 and numbers[2]>1000
  if shooting:assert numbers[5]>0 and numbers[6]>0 and numbers[7:9]==[227,227]
  else:assert numbers[5:9]==[0,0,0,0]
  if extra_clear:
   clear=next(line for line in lines if line.startswith('extra_clear ')).split();assert clear[0]=='extra_clear' and list(map(int,clear[2:4]))==[416,1] and int(clear[5])==1961
   expected3=[]
   for calls in (0,1,2):
    row=resources[character*256+calls].split();assert row[0]==str(calls+1)
    expected3.extend(row[i:i+4] for i in range(2,len(row),4))
   assert [line.split()[1:] for line in lines if line.startswith('resource3 ')]==expected3,f'{name}: third resource requests differ'
  if extra_maine:
   maine=lines[-1].split();assert maine[0]=='extra_maine' and list(map(int,maine[3:5]))==[273,373] and maine[6:]==['fresh_op=1','second_main=1','muted=1']
   flow=[list(map(int,line.split()[1:])) for line in lines if line.startswith('extra_flow ')];assert [k for k,t in flow]==list(range(10))
   assert flow[2][1]==flow[3][1]==273 and flow[4][1]==373 and flow[5][1]==flow[6][1] and flow[8][1]==flow[9][1]
   fade=[list(map(int,line.split()[1:])) for line in lines if line.startswith('mainfade ')]
   assert fade==[[tick,100-((tick-1)//16)*6] for tick in range(1,273)]+[[273,0]]
   assert sha(frontend/(name+'-GENSOU.SCR'))==sha(frontend/name/'save/GENSOU.SCR')
  captures=list(frontend.glob(name+'-*.bmp'));assert len(captures)==(39 if extra_maine else 32 if extra_clear else 28)
  result.append(dict(extra_maine=maine[1:] if extra_maine else None,extra_clear=list(map(int,clear[1:])) if extra_clear else None,name=name,frames=numbers[0],mugetsu_frames=numbers[1],gengetsu_frames=numbers[2],dialog_frames=numbers[3:5],hits=numbers[5:7],bomb_frames=numbers[7:9],wave_frames=numbers[12],laser_frames=numbers[13],column_frames=numbers[14]))
 files={p.name:sha(p) for p in sorted(frontend.iterdir()) if p.is_file()};assert len(files)==(328 if extra_maine else 264 if extra_clear else 464)
 for character,shot,shooting in itertools.product(range(2),range(2),(1,) if extra_clear else range(2)):
  prefix=f'{character}-{shot}-{shooting}-'
  for name,digest in files.items():
   if name.startswith(prefix+'0'):assert files[prefix+'1'+name[len(prefix)+1:]]==digest,'repaint control differs'
 return result,files

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('original-dir','linux-dir','ubsan-dir','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--extra-clear',action='store_true')
 p.add_argument('--extra-maine',action='store_true')
 a=p.parse_args();a.extra_clear=a.extra_clear or a.extra_maine;out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
 left,lf=validate(a.linux_dir,a.original_dir,a.extra_clear,a.extra_maine);right,rf=validate(a.ubsan_dir,a.original_dir,a.extra_clear,a.extra_maine);assert left==right and lf==rf,'GNU/UBSan frontend differs'
 r=dict(passed=True,source_manifest=source_manifest(Path(__file__).resolve().parents[1])[0],scenes=left,files=lf,bmp_count=sum(n.endswith('.bmp') for n in lf),dialog_events=[len([line for line in (a.linux_dir/('0-0-1-0.txt' if a.extra_clear else '0-0-0-0.txt')).read_text().splitlines() if line.startswith(f'dialog{i} ')]) for i in range(3 if a.extra_clear else 2)],original_producer_receipt_sha256=sha(a.original_dir/'receipt.json'),executed_hosts=['GNU8.4','optimized UBSan'],utc=datetime.now(timezone.utc).isoformat(),scope=("Actual OP/Extra two bosses/three dialogues/allclear/MAIN blackout16/fresh Extra MAINE/registration writer-close/congratulations/verdict/freshOP/secondMAIN.8actorcontrols;hit/unlock adapters;nativecrosshost captures and original3dialog/resource requests. No savedOPunlockreading/natural survival/fullroutes/originalwholepixels/Windowsruntime/audio/timing/exact acceptance." if a.extra_maine else "Actual two bosses and third dialogue/all-clear to frozen end_extra entry; original three-dialogue/resource requests, complete native host/paint equality. Actor hit/unlock adapters; no MAIN blackout/MAINE/unlock/full survival/routes/audio/timing/exact acceptance." if a.extra_clear else __doc__))
 (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('Extra clear frontend:' if a.extra_clear else 'Gengetsu frontend:', 'PASS',len(left),'scenes',len(lf),'files',r['bmp_count'],'BMPs; original ordered dialogue/resource requests agree')
if __name__=='__main__':main()
