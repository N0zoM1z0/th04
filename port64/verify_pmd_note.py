#!/usr/bin/env python3
"""Original PMD note rotation and integrated FM/SSG boundary requests.

The unchanged flat COM transpose entry executes at two PSPs for all 256 note
bytes and 256 signed transpose sums, plus wrapped part/master decompositions.
Raw note-byte coverage is an arithmetic-unit claim, not legal music admission.
Authored legal boundary phrases independently compare every configured FM3
player field and ordered write. DOS/board/IRQ adapters remain explicit; muted.
No physical clock/chip, complete game route or DOS exactness is accepted.
"""
import argparse,gzip,hashlib,json,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
import unicorn as U
from unicorn.x86_const import UC_X86_REG_AX,UC_X86_REG_CS,UC_X86_REG_DS,UC_X86_REG_SS,UC_X86_REG_SP,UC_X86_REG_DI,UC_X86_REG_IP,UC_X86_REG_EFLAGS
from verify import source_manifest,require_elf_x86_64
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_cutscene import ending_assets
from verify_pmd_fm3 import resource,target_profile,original_row
from verify_pmd_fm_player import PublishedView
from verify_pmd_musical_fm import mirror
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'PMD.COM':0x1762,'PMD86.COM':0x2502,'PMDB2.COM':0x2104}
EXTENT=87
EXTENT_SHA='127dac85164d65334c9766fe0a8ac0335f86d8368d57b07d62e4d06a1b026646'
CORNERS=(0,11,12,13,14,15,16,31,63,112,123,127,128,255)
def inputs():
    for note in range(256):
        for amount in range(256):yield note,0,amount
    for part in (17,128,255):
        for note in CORNERS:
            for amount in range(256):yield note,part,(amount-part)&255
def phrases():
    phrase=[255,7,253,100]
    for part,master in ((2,253),(255,2),(0,244),(0,12),(128,128),(127,129),(0,232),(0,24)):
        phrase += [245,part,178,master]
        for note in (0,1,11,16,27,64,112,123,15,12):phrase += [note,1]
    phrase += [128]
    result={f'NOTE{p}':resource({p:bytes(phrase)}) for p in (0,2,6,8)}
    extras=[bytes([207,32<<n]+phrase) for n in range(3)]
    result['NOTE3']=resource({2:bytes([255,7,207,17,198,254,255,253,255,252,255,64,100,128])},extras)
    return result
def arithmetic(binary,name,load):
    at=ENTRIES[name];span=binary[at-256:at-256+EXTENT]
    assert hashlib.sha256(span).hexdigest()==EXTENT_SHA
    u=U.Uc(U.UC_ARCH_X86,U.UC_MODE_16);u.mem_map(0,0x110000);base=load*16;u.mem_write(base+256,binary)
    for reg in (UC_X86_REG_CS,UC_X86_REG_DS,UC_X86_REG_SS):u.reg_write(reg,load)
    u.reg_write(UC_X86_REG_DI,0xe000);result=bytearray()
    for note,part,master in inputs():
        u.mem_write(base+0xe013,bytes([part]));u.mem_write(base+0xe05f,bytes([master]));u.mem_write(base+0xfe00,struct.pack('<H',0xf000))
        u.reg_write(UC_X86_REG_SP,0xfe00);u.reg_write(UC_X86_REG_AX,0xa500|note);u.reg_write(UC_X86_REG_EFLAGS,2)
        u.emu_start(base+at,base+0xf000,count=256)
        assert u.reg_read(UC_X86_REG_IP)==0xf000 and u.reg_read(UC_X86_REG_SP)==0xfe02
        result.append(u.reg_read(UC_X86_REG_AX)&255)
    assert bytes(u.mem_read(base+256,len(binary)))==binary
    assert len(result)==76288
    return bytes(result)
def produce(a,out):
    binaries=directory_files(a.hdi);assert sha(a.hdi)==HDI_SHA;assets=ending_assets(a.hdi);anchors=target_profile(binaries)
    matrices=[];cases=[];first={};ops=[('R',0)]+[('I',3)]*110+[('M',0)]+[('I',3)]*8
    (out/'operations.txt').write_text(''.join(f'{op} {v}\n' for op,v in ops));(out/'MIKO.EFC').write_bytes(assets['MIKO.EFC'])
    for load in (0x1000,0x2000):
        for name,(_,_,board,ext,_) in DRIVERS.items():
            data=arithmetic(binaries[name],name,load);matrix=out/f'{name}-{load:04x}-notes.bin';matrix.write_bytes(data)
            matrices.append(dict(driver=name,load=load,entry=f'PSP:{ENTRIES[name]:04X}',extent_size=EXTENT,extent_sha256=EXTENT_SHA,output=matrix.name,rows=len(data),raw_sha256=sha(matrix)))
            for label,data in phrases().items():
                song=label+'.'+ext;path=out/song
                if path.exists():assert path.read_bytes()==data
                else:path.write_bytes(data)
                d=install(binaries[name],name,load);address=d.write_resource(0xb00,assets['MIKO.EFC'])['offset'];d.write_resource(0x600,data);view=PublishedView(d,address)
                initial=out/(name+'-mirror.txt');raw=(' '.join(map(str,mirror(d,name)))+'\n').encode()
                if initial.exists():assert initial.read_bytes()==raw
                else:initial.write_bytes(raw)
                trace=out/f'{name}-{load:04x}-{song}.txt.gz';digest=hashlib.sha256()
                with gzip.open(trace,'wb',compresslevel=1) as stream:
                    for tick,(op,v) in enumerate(ops):
                        d.ticks=tick;d.ports=[]
                        if op=='I':d.irq(v)
                        else:d.service(0 if op=='R' else 0x100)
                        row=original_row(view,name,address,binaries[name],anchors)
                        if op!='I' or tick%53==0:assert row==original_row(d,name,address,binaries[name],anchors)
                        raw=(' '.join(map(str,row))+'\n').encode();digest.update(raw);stream.write(raw)
                key=name,song
                if key in first:assert first[key]==digest.hexdigest()
                first[key]=digest.hexdigest();cases.append(dict(driver=name,board=board,song=song,load=load,mirror=initial.name,reference=trace.name,operations='operations.txt',rows=len(ops),raw_sha256=digest.hexdigest()))
            print('original note unit/boundary',name,f'{load:04x}',flush=True)
    assert len({m['raw_sha256'] for m in matrices})==1 and len(cases)==30
    assert sha(a.hdi)==HDI_SHA
    return dict(matrices=matrices,cases=cases,arithmetic_rows=sum(m['rows'] for m in matrices),rows=sum(c['rows'] for c in cases),hdi_sha256=HDI_SHA,driver_profiles=anchors,outputs={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name not in ('source.tar.gz','source-profile.json')})
def consume(a,out,mf):
    ref=a.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['matrices'])==6 and len(r['cases'])==30
    for n,h in r['outputs'].items():assert sha(ref/n)==h
    profile=json.loads(a.product_profile.read_text());frozen={a.binary:sha(a.binary),a.musical_binary:sha(a.musical_binary),a.product_profile:sha(a.product_profile),ref/'receipt.json':sha(ref/'receipt.json')}
    for binary in (a.binary,a.musical_binary):
        require_elf_x86_64(binary);assert any(x.get(binary.name)==sha(binary) for x in profile['products'].values())
    matrix=out/'notes.bin';subprocess.run([str(a.binary),'--transpose-bytes',str(matrix)],check=True)
    assert all(matrix.read_bytes()==(ref/m['output']).read_bytes() for m in r['matrices'])
    records=[];done={}
    for c in r['cases']:
        key=c['driver'],c['song']
        if key not in done:
            result=out/(c['driver']+'-'+c['song']+'.txt.gz');digest=hashlib.sha256();count=0
            command=[str(a.musical_binary),str(ref/c['song']),str(ref/'MIKO.EFC'),str(c['board']),str(ref/c['mirror']),str(ref/c['operations']),'/dev/stdout']
            with (out/(c['driver']+'-'+c['song']+'-stderr.txt')).open('wb') as error:
                child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=error)
                try:
                    with gzip.open(ref/c['reference'],'rb') as expected,gzip.open(result,'wb',compresslevel=1) as actual:
                        for want in expected:
                            got=child.stdout.readline();actual.write(got)
                            if got!=want:
                                (out/'mismatch.json').write_text(json.dumps(dict(case=c,row=count,expected=want.decode(),actual=got.decode()),indent=2)+'\n');raise ValueError(f'{key}: row{count}')
                            digest.update(got);count+=1
                        assert not child.stdout.read(1) and child.wait(timeout=30)==0
                finally:
                    if child.poll() is None:child.kill();child.wait()
            done[key]=dict(rows=count,raw_sha256=digest.hexdigest(),output=result.name)
        assert done[key]['raw_sha256']==c['raw_sha256'] and done[key]['rows']==c['rows'];records.append(dict(driver=c['driver'],song=c['song'],load=c['load'],**done[key]))
    for p,h in frozen.items():assert sha(p)==h
    assert source_manifest(Path(__file__).resolve().parents[1])[0]==mf
    return dict(cases=records,rows=sum(c['rows'] for c in records),arithmetic_rows=r['arithmetic_rows'],arithmetic_sha256=sha(matrix),product_producer_manifest=profile['product_producer_manifest'],product_profile_sha256=sha(a.product_profile),reference_receipt_sha256=sha(ref/'receipt.json'),reference_producer_manifest=r['source_manifest'],binary_sha256=sha(a.binary),musical_binary_sha256=sha(a.musical_binary))
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for n in ('hdi','reference','binary','musical-binary','product-profile'):parser.add_argument('--'+n,type=Path)
    parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    if bool(a.hdi)==bool(a.reference):parser.error('choose original HDI or accepted reference')
    for n in ('binary','musical_binary','product_profile'):
        if getattr(a,n):setattr(a,n,getattr(a,n).resolve())
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);self_hash=sha(Path(__file__));out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    with tarfile.open(out/'source.tar.gz','w:gz') as archive:
        for f in files:assert sha(root/f['path'])==f['sha256'];archive.add(root/f['path'],arcname=f['path'])
        if 'port64/verify_pmd_note.py' not in [f['path'] for f in files]:archive.add(Path(__file__),arcname='port64/verify_pmd_note.py')
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files,verifier_sha256=self_hash),indent=2)+'\n')
    r=produce(a,out) if a.hdi else consume(a,out,mf)
    assert sha(Path(__file__))==self_hash
    for f in files:
        if f['path'].endswith(('.py','.ps1')):assert sha(root/f['path'])==f['sha256']
    r.update(passed=True,source_manifest=mf,source_files=len(files),verifier_sha256=self_hash,source_archive_sha256=sha(out/'source.tar.gz'),engine_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)),command=sys.argv,utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('note unit/boundaries PASS',r['arithmetic_rows'],r['rows'],flush=True)
if __name__=='__main__':main()
