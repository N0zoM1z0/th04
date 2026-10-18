"""Attest host keyboard/PIC layout with the emulator's exact recorded compiler."""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--emulator-receipt',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
    if args.output_dir.exists():parser.error('output directory must be absent')
    available=os.sched_getaffinity(0);os.sched_setaffinity(0,{1 if 1 in available else min(available)});os.nice(max(0,19-os.getpriority(os.PRIO_PROCESS,0)))
    receipt=json.loads(args.emulator_receipt.read_text());compiler=Path(receipt['compilers']['g++']['path']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(compiler)==receipt['compilers']['g++']['sha256']
    engine=Path(receipt['binary']);assert sha(engine)==receipt['binary_sha256']=='6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1';source=engine.parent.parent
    assert sha(source/'config.h')==receipt['config_header_sha256']
    keyboard=source/'src/hardware/keyboard.cpp';pic=source/'src/hardware/pic.cpp';body=keyboard.read_text();a=body.index('enum AuxCommands {');b=body.index('} keyb;',a)+len('} keyb;');keyboard_fragment=body[a:b]
    body=pic.read_text();a=body.index('struct PICEntry {');b=body.index('} pic_queue;',a)+len('} pic_queue;');pic_fragment=body[a:b]
    out=args.output_dir.resolve();out.mkdir(parents=True);probe=out/'probe.cpp'
    text='''#include "config.h"
    #include "dosbox.h"
    #include "keyboard.h"
    #include "pic.h"
    #include <cstdio>
    #include <cstddef>
    #define KEYBUFSIZE (32*3)
    #define PIC_QUEUESIZE 8192
    '''+keyboard_fragment+'\n'+pic_fragment+'''
    int main() {
     using K=decltype(keyb);using R=decltype(keyb.repeat);using Q=decltype(pic_queue);
     std::printf("{\\"keyb_size\\":%zu,\\"repeat_key\\":%zu,\\"repeat_wait\\":%zu,\\"repeat_pause\\":%zu,\\"repeat_rate\\":%zu,\\"enum_size\\":%zu,\\"bitu_size\\":%zu,\\"pic_entry_size\\":%zu,\\"pic_entry_next\\":%zu,\\"pic_entry_handler\\":%zu,\\"pic_queue_size\\":%zu,\\"pic_queue_next\\":%zu,\\"pic_index_size\\":%zu,\\"z_enum\\":%d,\\"enter_enum\\":%d}\\n",
     sizeof(K),offsetof(K,repeat)+offsetof(R,key),offsetof(K,repeat)+offsetof(R,wait),offsetof(K,repeat)+offsetof(R,pause),offsetof(K,repeat)+offsetof(R,rate),sizeof(KBD_KEYS),sizeof(Bitu),sizeof(PICEntry),offsetof(PICEntry,next),offsetof(PICEntry,pic_event),sizeof(Q),offsetof(Q,next_entry),sizeof(pic_tickindex_t),int(KBD_z),int(KBD_enter));
    }
    ''';probe.write_text(text)
    command=[str(compiler),'-std=gnu++11','-O2','-I'+str(source),'-I'+str(source/'include'),'-I/usr/include/SDL2',str(probe),'-o',str(out/'probe')]
    with (out/'build.log').open('wb') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    run=subprocess.run([str(out/'probe')],capture_output=True,check=True);layout=json.loads(run.stdout);assert layout==dict(keyb_size=0x160,repeat_key=0xf0,repeat_wait=0xf8,repeat_pause=0x100,repeat_rate=0x108,enum_size=4,bitu_size=8,pic_entry_size=48,pic_entry_next=32,pic_entry_handler=24,pic_queue_size=0x60010,pic_queue_next=0x60008,pic_index_size=16,z_enum=30,enter_enum=52)
    inputs={str(p):sha(p) for p in [keyboard,pic,source/'config.h',source/'include/keyboard.h',source/'include/pic.h',source/'include/dosbox.h',probe]}
    nm={}
    for line in subprocess.check_output(['nm','-S',str(engine)],text=True).splitlines():
     cells=line.split()
     if len(cells)==4:nm[cells[3]]=(int(cells[0],16),int(cells[1],16))
    assert nm['_ZL4keyb'][1]==layout['keyb_size'] and nm['_ZL9pic_queue'][1]==layout['pic_queue_size']
    disassembly={}
    for name,wanted in [('_ZL20KEYBOARD_TickHandlerv',{layout['repeat_key'],layout['repeat_wait']}),('_Z20KEYBOARD_PC98_AddKey8KBD_KEYSb',{layout['repeat_key'],layout['repeat_wait'],layout['repeat_pause'],layout['repeat_rate']})]:
     address,size=nm[name];command_dis=['objdump','-d','--start-address='+hex(address),'--stop-address='+hex(address+size),str(engine)]
     observed=subprocess.check_output(command_dis,text=True);offsets={int(v,16) for v in re.findall(r'<_ZL4keyb\+0x([0-9a-f]+)>',observed)};assert wanted<=offsets
     path=out/(name+'.txt');path.write_text(observed);disassembly[name]=dict(command=command_dis,sha256=sha(path),required_offsets=sorted(wanted))
    report=dict(passed=True,disassembly=disassembly,compiler=receipt['compilers']['g++'],command=command,engine_sha256=sha(engine),inputs=inputs,layout=layout,probe_sha256=sha(out/'probe'),stdout_sha256=hashlib.sha256(run.stdout).hexdigest(),scope='Pinned GCC8.4 compiler reproduces host structs extracted from the exact emulator source andheaders. Actual ELF symbol sizes andTickHandler/PC98_AddKey operands independently bind key/wait/pause/rate offsets. These are x86_64 emulator host offsets,not TH04 DGROUP orhardware registers. Raw runtime keyb snapshots can nowbedecoded without fitted repeatphase.')
    (out/'layout.json').write_text(json.dumps(report,indent=2)+'\n');print('PINNED KEYBOARD/PIC HOST LAYOUT PASS',layout,flush=True)


if __name__ == '__main__':
    main()
