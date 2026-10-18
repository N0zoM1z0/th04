"""Observe actual post-load AH values using the sampler's existing hardware slot."""
import hashlib,json
import gdb

class ScalarPoint(gdb.Breakpoint):
    def __init__(self,owner,index,point):
        self.owner,self.index,self.point=owner,index,point;m=owner.polls.m
        self.linear=(m.current.load+m.plan['sampler_scalars']['segment'])*16+point['after_offset']
        host=m.ram.state()[0]+m.ram.physical(self.linear)
        super().__init__('*(unsigned char *)0x%x'%host,type=gdb.BP_WATCHPOINT,wp_class=gdb.WP_READ,internal=True)
        self.enabled=False
    def stop(self):
        s=self.owner;p=s.polls;m=p.m
        try:
            before=m.context();state,regs,segs=before
            cs=int.from_bytes(segs[8:16],'little');ip=int.from_bytes(regs[32:36],'little')&65535
            if (cs,ip)!=(m.current.load+m.plan['sampler_scalars']['segment'],self.point['after_offset']):return False
            assert s.active and p.pending is not None and self.index==s.next_index
            assert int.from_bytes(segs[:8],'little')==0 and int.from_bytes(segs[24:32],'little')==m.current.dgroup
            opcode=m.ram.read_range(self.linear-5,5)[0];assert opcode.hex()==self.point['opcode']
            assert m.ram.read_range(self.linear,6)[0].hex()==self.point['after_opcode']
            value=regs[1]
            event=m.admission.event('sampler-scalar',pair=p.pending['pair'],scalar_index=self.index,
                group=self.point['group'],actual_ah=value,load_offset=self.point['load_offset'],
                after_offset=self.point['after_offset'],load_opcode=opcode.hex())
            row=dict(ordinal=s.ordinal,pair=p.pending['pair'],scalar_index=self.index,
                load_segment=m.current.load,dgroup_segment=m.current.dgroup,segment=m.plan['sampler_scalars']['segment'],
                load_offset=self.point['load_offset'],after_offset=self.point['after_offset'],group=self.point['group'],
                actual_ah=value,event_ordinal=event['ordinal'],time=event['time'],registers=regs.hex(),segments=segs.hex(),
                bios=m.ram.read_range(0x52a,10)[0].hex(),key_det=m.number(p.plan['key_det'],2),load_opcode=opcode.hex())
            assert before==m.context(),'scalar observation changed guest CPU'
            s.stream.write(json.dumps(row)+'\n');s.stream.flush();s.digest.update((json.dumps(row)+'\n').encode());s.ordinal+=1;s.next_index+=1
            self.enabled=False
            if s.next_index==len(s.points):s.active=False;p.returned.enabled=True
            else:s.points[s.next_index].enabled=True
            p.check_budget();return False
        except BaseException as error:return m.admission.fail(error)

class ScalarReads:
    def __init__(self,polls):
        self.polls=polls;self.ordinal=0;self.active=False;self.next_index=0
        self.stream=(polls.m.output/'sampler-scalars.jsonl').open('x');self.digest=hashlib.sha256()
        self.points=[]
    def begin(self):
        assert not self.active and self.polls.pending is not None
        if not self.points:self.points=[ScalarPoint(self,i,point) for i,point in enumerate(self.polls.m.plan['sampler_scalars']['points'])]
        self.active=True;self.next_index=0;self.points[0].enabled=True
    def finish(self):
        assert not self.active and self.ordinal>0 and self.ordinal%8==0
        assert all(not p.enabled for p in self.points)
        self.stream.close()
        (self.polls.m.output/'sampler-scalars.json').write_text(json.dumps(dict(passed=True,records=self.ordinal,sampler_pairs=self.ordinal//8,stream_sha256=self.digest.hexdigest(),plan=self.polls.m.plan['sampler_scalars'],scope='Actual AH after each unchanged original MOV AH,ES:[BIOS byte],recorded at the next opcode fetch. One existing sampler hardware watchpoint slot rotates over all8 loads andthe return;at most4 hardware watchpoints. No original patch,CPU/BIOS/latch/clock assignment or expected input word.'),indent=2)+'\n')
