#!/usr/bin/env python3
"""Compare complete sampled programmed display, including recorded GDC blinking.

Derived from the v1451 live-font reader, which remains frozen for prior replay.
The actual captured master GDC phase controls text visibility. Native rendering
receives no target blink phase. Complete RGB and all 8000 active TRAM bytes are
independent gates; no pixel mask, fitted phase or scanout claim is used.
"""
import argparse,gzip,hashlib,json,struct,sys
from pathlib import Path
import numpy as np
from PIL import Image
from compare_th04_dos_ordinary_prefix import load
from th04_demo_video import OFFSETS,SIZES

def sha(data):return hashlib.sha256(data).hexdigest()
def project(block,font):
    if len(block)!=sum(SIZES.values()):raise ValueError('complete video observation extent')
    if len(font)!=528384:raise ValueError('complete live font extent')
    # The independent native probe's existing GDC decoder consumes raw target
    # pages/partitions, never the native frame being compared.
    from verify_demo_pictures import decode_graphics
    region=lambda name:block[OFFSETS[name]:OFFSETS[name]+SIZES[name]]
    gdc=region('gdc');modes=region('modes');text=region('text')
    if len(gdc)!=464 or gdc[196]>3 or not gdc[198] or gdc[197]>=gdc[198]:raise ValueError('recorded GDC blink extent/phase/count/rate')
    if not (gdc[152:154]==bytes(2) and gdc[154]&3==0 and gdc[172]==16
            and int.from_bytes(gdc[184:186],'little')==80 and gdc[202]==1
            and gdc[203]==0 and modes[6]==0):raise ValueError('unsupported text-controller projection')
    # GDC row_height at172 is a BYTE. Byte173 is live row_line and may be2;
    # treating172:174 as a WORD wrongly rejects a valid16-line text mode.
    analog=np.frombuffer(region('analog'),np.uint8).reshape(256,3)
    def expand(nibble):
        four=int(nibble)&15;six=(four<<2)|(four>>2);return (six<<2)|(six>>4)
    colors=np.array([[expand(p[c]) for c in (1,0,2)] for p in analog],np.uint8)
    indices=np.frombuffer(decode_graphics(region('graphics'),gdc[232:],modes),np.uint8).reshape(400,640)
    expected=colors[indices].copy();ink=np.zeros((400,640),bool);palette=struct.unpack('<8I',region('text_palette'))
    for row in range(25):
        for y in range(16):
            right=False;previous=0
            for col in range(80):
                cell=row*80+col;code=int.from_bytes(text[cell*2:cell*2+2],'little');attribute=int.from_bytes(text[8192+cell*2:8192+cell*2+2],'little')
                if attribute&0x18:raise ValueError('unsupported underline/vertical text attribute')
                if right and code&0x7f7f!=previous&0x7f7f:right=False
                half=int(right)
                if code&0xff00:
                    index=(code&127)+((((code+0x7f00)&0x7f00)+0x100)>>1);offset=(index*16+y)*2+half
                else:offset=code*16+y
                mask=font[offset] if attribute&1 else 0
                if attribute&2 and gdc[196]==0:mask=0
                if attribute&4:mask^=255
                color=palette[(attribute>>5)&7];rgb=(color>>16&255,color>>8&255,color&255)
                for x in range(8):
                    if mask&(128>>x):expected[row*16+y,col*8+x]=rgb;ink[row*16+y,col*8+x]=True
                previous=code;right=bool(code&0xff00) and not right
    return expected,indices,ink

def attest_layout(gdc_layout,emulator_sha256):
    layout=json.loads(gdc_layout.read_text())
    if not layout['passed'] or layout['emulator_sha256']!=emulator_sha256:raise ValueError('GDC layout/emulator identity')
    if layout['layout']!={'gdc_size':232,'blink_offset':196,'blink_count_offset':197,'blink_rate_offset':198,'row_height_offset':172}:raise ValueError('unsupported GDC ABI')
    for name,digest in layout['inputs'].items():
        if sha(Path(name).read_bytes())!=digest:raise ValueError('GDC layout input identity: '+name)
    return layout

def compare(original,native,target,native_root,phase,gdc_layout,output_images=None):
    sys.path.insert(0,str(native_root/'port64'));load(original,target)
    receipt=json.loads((original/'receipt.json').read_text());terminal=json.loads((original/'ordinary-terminal.json').read_text())
    attest_layout(gdc_layout,receipt['emulator_sha256'])
    plans=[Path(path) for path in receipt['source_files'] if Path(path).name=='font-plan.json']
    if len(plans)!=1:raise ValueError('unique captured font plan required')
    plan_bytes=plans[0].read_bytes();plan=json.loads(plan_bytes);frames=plan['frames'];layout_bytes=Path(plan['layout_path']).read_bytes()
    if sha(layout_bytes)!=plan['layout_sha256']:raise ValueError('font layout identity')
    folder='post-score-checkpoints' if phase=='after-score' else 'font-checkpoints';ip=0x207 if phase=='after-score' else 0x1b3
    samples=[];inputs={str(plans[0]):sha(plan_bytes),str(gdc_layout):sha(gdc_layout.read_bytes())}
    if output_images is not None:output_images.mkdir(parents=True,exist_ok=False)
    for frame in frames:
        stem=original/folder/str(frame);metadata_path=Path(str(stem)+'.json');row=json.loads(metadata_path.read_text());blocks={name:gzip.decompress(Path(str(stem)+'-'+name+'.bin.gz').read_bytes()) for name in ('font','video','dgroup')}
        if any(sha(data)!=row[name+'_sha256'] for name,data in blocks.items()):raise ValueError('checkpoint content digest')
        if row['plan_sha256']!=sha(plan_bytes) or row['layout_sha256']!=sha(layout_bytes) or not row['unchanged_context']:raise ValueError('checkpoint plan/read-only context')
        registers=bytes.fromhex(row['registers']);segments=bytes.fromhex(row['segments']);cs=terminal['load_segment']+0xaaf;ds=terminal['dgroup_segment'];group=blocks['dgroup']
        if len(registers)!=48 or len(segments)!=136 or len(group)!=65536:raise ValueError('checkpoint raw CPU/DGROUP extent')
        if (int.from_bytes(registers[32:36],'little')&65535,int.from_bytes(segments[8:16],'little'),int.from_bytes(segments[24:32],'little'))!=(ip,cs,ds):raise ValueError('checkpoint phase CS:IP/DS')
        if (row['frame'],row['load_segment'],row['dgroup_segment'],int.from_bytes(group[0x538a:0x538c],'little'))!=(frame,terminal['load_segment'],ds,frame):raise ValueError('checkpoint frame/load identity')
        expected,indices,ink=project(blocks['video'],blocks['font']);picture=native/('title-'+str(frame)+'.bmp');actual=np.asarray(Image.open(picture).convert('RGB'))
        if actual.shape!=(400,640,3):raise ValueError('complete native picture extent')
        graphics_path=native/('title-'+str(frame)+'-graphics.bin');native_graphics=np.frombuffer(graphics_path.read_bytes(),np.uint8)
        if native_graphics.size!=256000:raise ValueError('native graphics observation extent')
        native_graphics=native_graphics.reshape(400,640);sample=dict(frame=frame,original_font_sha256=sha(blocks['font']),original_checkpoint_sha256=sha(metadata_path.read_bytes()),native_picture_sha256=sha(picture.read_bytes()),regions={})
        gdc=blocks['video'][OFFSETS['gdc']:OFFSETS['gdc']+SIZES['gdc']]
        sample['recorded_blink']=dict(phase=gdc[196],count=gdc[197],rate=gdc[198])
        text_path=native/('title-'+str(frame)+'-text.bin');actual_text=text_path.read_bytes()
        if len(actual_text)!=16384:raise ValueError('native complete TRAM extent')
        original_text=blocks['video'][OFFSETS['text']:OFFSETS['text']+SIZES['text']]
        active=lambda data:data[:4000]+data[8192:12192]
        wanted,got=active(original_text),active(actual_text)
        sample['active_tram']=dict(bytes=8000,differing_bytes=sum(a!=b for a,b in zip(wanted,got,strict=True)),original_sha256=sha(wanted),native_sha256=sha(got))
        inputs[str(text_path)]=sha(actual_text)
        for name,(left,top,right,bottom) in {'stage-bands':(32,160,416,240),'BGM-band':(32,352,416,400),'playfield':(32,16,416,384),'whole-picture':(0,0,640,400)}.items():
            a=expected[top:bottom,left:right];b=actual[top:bottom,left:right];bad=np.any(a!=b,axis=2);coordinates=np.argwhere(bad)
            sample['regions'][name]=dict(pixels=bad.size,differing_pixels=int(bad.sum()),graphics_index_differences=int((indices[top:bottom,left:right]!=native_graphics[top:bottom,left:right]).sum()),differing_expected_text_ink=int((bad&ink[top:bottom,left:right]).sum()),original_sha256=sha(a.tobytes()),native_sha256=sha(b.tobytes()),first=[dict(x=left+int(x),y=top+int(y),original=a[y,x].tolist(),native=b[y,x].tolist()) for y,x in coordinates[:8]])
        if output_images is not None:Image.fromarray(expected).save(output_images/(str(frame)+'.png'))
        inputs[str(picture)]=sha(picture.read_bytes());inputs[str(graphics_path)]=sha(graphics_path.read_bytes());samples.append(sample)
    verdicts={key:all(not sample['regions'][key]['differing_pixels'] for sample in samples) for key in samples[0]['regions']}
    verdicts['active-tram']=all(not sample['active_tram']['differing_bytes'] for sample in samples)
    return dict(passed=all(verdicts.values()),verdicts=verdicts,phase=phase,samples=samples,sample_count=len(samples),original_receipt_sha256=sha((original/'receipt.json').read_bytes()),reader_sha256=sha(Path(__file__).read_bytes()),inputs=inputs,numpy_version=np.__version__,scope=__doc__+' Original capture is DOSBox-X with complete live font,raw planar video,DGROUP and unchanged CPU context at each declared phase. Full80-column text sequencing and attributes project independently of native pixels. Graphics-index/text-ink classifications are diagnostic; only complete RGB determines verdicts. All declared frames are explicit samples,not every update or a campaign. NP2 cross-emulator validation remains open.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('original','native','target','native-root','gdc-layout','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--phase',choices=('after-actor','after-score'),default='after-score');parser.add_argument('--output-images',type=Path);args=parser.parse_args()
    result=compare(args.original.resolve(),args.native.resolve(),args.target.read_bytes(),args.native_root.resolve(),args.phase,args.gdc_layout.resolve(),args.output_images)
    with args.output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(passed=result['passed'],verdicts=result['verdicts'],phase=result['phase'],samples=result['sample_count'])));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
