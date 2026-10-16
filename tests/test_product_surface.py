"""Reject mixed product cohorts, foreign OP hooks and filename-only DOS entries."""
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/probes'))
from capture_th04_dos_demos import sha
from th04_product_surface import attest_surface, op_counter_profile, COUNTER, PRODUCTS
from th04_dos_boot import validate_counter
from th04_dos_route import validate_entry
import test_dos_route as route_tests


def mz():
    header=bytearray(32);header[:2]=b'MZ'
    struct.pack_into('<HHHHHHHHHHHHH',header,2,96,1,0,2,1,0xffff,0,32,0,0,0,28,0)
    body=bytearray(64);body[16:25]=bytes.fromhex('c41e2000')+COUNTER
    return bytes(header+body)


class OpCounterProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.map=Path(self.temp.name)/'op.map'
        self.text='0000:0000 _main\n0000:0040 _next\n0020:0020 _resident\n'
        self.map.write_text(self.text);self.image=mz()

    def test_map_owned_increment_uses_executing_eip(self):
        profile=op_counter_profile(self.image,self.map)
        self.assertEqual(profile['ip'],20)
        self.assertEqual(profile['setup_ip'],16)
        self.assertEqual(profile['dgroup'],0x20)

    def test_duplicate_increment_in_main_rejects(self):
        image=bytearray(self.image);image[32+32:32+41]=image[32+16:32+25]
        with self.assertRaisesRegex(ValueError,'unique MAP-owned'):
            op_counter_profile(bytes(image),self.map)

    def test_increment_outside_main_extent_rejects(self):
        self.map.write_text(self.text.replace('0000:0040','0000:0008'))
        with self.assertRaises(ValueError):op_counter_profile(self.image,self.map)

    def test_foreign_resident_pointer_operand_rejects(self):
        self.map.write_text(self.text.replace('0020:0020','0020:0022'))
        with self.assertRaises(ValueError):op_counter_profile(self.image,self.map)

    def test_unmapped_code_or_bad_mz_rejects(self):
        self.map.write_text(self.text.replace('0000:0040','0000:0080'))
        with self.assertRaises(ValueError):op_counter_profile(self.image,self.map)
        with self.assertRaises(ValueError):op_counter_profile(b'no-MZ',self.map)

    def test_arbitrary_candidate_cannot_use_original_op_constants(self):
        with self.assertRaisesRegex(ValueError,'original OP counter identity'):
            op_counter_profile(self.image)


class ProductCohortTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.build=self.root/'build';self.build.mkdir();self.image=mz()
        self.manifest=dict(schema_version=1,variant='normal',run_id='cohort',products={})
        for name,filename in PRODUCTS.items():
            (self.build/filename).write_bytes(self.image);directory=self.root/('cohort-'+name);directory.mkdir();producer=directory/'receipt.json'
            details=(dict(link=dict(exit=0,errors=[],mz=True)) if name=='main' else
                     dict(cold_equal=True) if name=='zun' else
                     dict(link_complete=True,link_exit=0,link_errors=[],unresolved=[]))
            producer.write_text(json.dumps(details));self.manifest['products'][name]=dict(file=filename,size=len(self.image),sha256=sha(self.image),build_receipt=str(producer))
        (self.root/'cohort-op/source/obj/product').mkdir(parents=True)
        (self.root/'cohort-op/source/obj/product/op-native.map').write_text('MAP')
        self.pack=self.root/'cohort-zun-diet/receipt.json';self.pack.parent.mkdir();self.pack.write_text(json.dumps(dict(artifact='th04-zun',candidate_inputs_identical=True,packed_outputs_identical=True,builds=[dict(label=n,packed_sha256=sha(self.image)) for n in ['a','b']])))
        self.write()

    def write(self):
        (self.build/'build.json').write_text(json.dumps(self.manifest))

    def test_complete_same_run_surface_pins_all_four_files(self):
        surface=attest_surface(self.build)
        self.assertEqual(set(surface['products']),{'th04-'+n for n in PRODUCTS})

    def test_missing_product_or_invincible_variant_rejects(self):
        self.manifest['variant']='invincible-main';self.write()
        with self.assertRaises(ValueError):attest_surface(self.build)
        self.manifest['variant']='normal';self.manifest['products'].pop('zun');self.write()
        with self.assertRaises(ValueError):attest_surface(self.build)

    def test_foreign_cohort_receipt_rejects(self):
        self.manifest['products']['op']['build_receipt']=str(self.root/'other-op/receipt.json');self.write()
        with self.assertRaisesRegex(ValueError,'same-run'):attest_surface(self.build)

    def test_changed_executable_rejects(self):
        (self.build/'OP.EXE').write_bytes(self.image[:-1]+b'X')
        with self.assertRaisesRegex(ValueError,'file/producer'):attest_surface(self.build)

    def test_zun_packing_must_name_the_published_digest(self):
        packed=json.loads(self.pack.read_text());packed['builds'][0]['packed_sha256']='0'*64;self.pack.write_text(json.dumps(packed))
        with self.assertRaisesRegex(ValueError,'packing replay'):attest_surface(self.build)


class CounterBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.memory=bytearray(655360);self.profile=dict(segment=0x70,ip=0x123,dgroup=0xf4,opcode_hex=COUNTER.hex())
        self.entry=dict(load_segment=0x1000);self.resident=0x9fef0;self.at=0x1070*16+0x123
        self.memory[self.at:self.at+5]=COUNTER;self.memory[self.resident+20:self.resident+24]=(64).to_bytes(4,'little')
        regs,segs=bytearray(48),bytearray(136);regs[32:36]=(0x123).to_bytes(4,'little');segs[:8]=(0x9fef).to_bytes(8,'little');segs[8:16]=(0x1070).to_bytes(8,'little');segs[24:32]=(0x10f4).to_bytes(8,'little')
        self.row=dict(cs=0x1070,ip=0x123,cpu_regs=regs.hex(),segments=segs.hex(),resident_linear=self.resident,counter=64,counter_opcode_hex=COUNTER.hex())

    def check(self):validate_counter(self.row,self.entry,self.profile,bytes(self.memory))

    def test_actual_store_context_and_bytes_admit(self):self.check()

    def test_next_instruction_pc_cannot_claim_store_boundary(self):
        self.row['ip']+=5;regs=bytearray.fromhex(self.row['cpu_regs']);regs[32:36]=self.row['ip'].to_bytes(4,'little');self.row['cpu_regs']=regs.hex()
        with self.assertRaises(ValueError):self.check()

    def test_wrong_dgroup_or_resident_rejects(self):
        self.row['resident_linear']+=16
        with self.assertRaises(ValueError):self.check()
        self.row['resident_linear']-=16;self.profile['dgroup']+=1
        with self.assertRaises(ValueError):self.check()

    def test_changed_counter_code_or_value_rejects(self):
        self.memory[self.at]^=1
        with self.assertRaises(ValueError):self.check()
        self.memory[self.at]^=1;self.memory[self.resident+20]+=1
        with self.assertRaises(ValueError):self.check()


class LoadAndGoEntryTests(unittest.TestCase):
    def setUp(self):
        fixture=route_tests.OverlayEntryTests();fixture.setUp();self.row=fixture.row;self.request=fixture.request;self.image=fixture.image;self.observed=fixture.observed
        self.request['ax']=0x4b00;self.row['request_ax']=0x4b00;regs=bytearray(48);regs[:2]=b'\0K';self.request['cpu_regs']=regs.hex();self.request['opcode']='cd21';self.row['owner']['parent_psp']=0

    def test_explicit_load_and_go_still_requires_actual_raw_image_and_pc(self):
        validate_entry(self.row,self.request,self.image,self.observed,allow_exec=True)
        with self.assertRaises(ValueError):validate_entry(self.row,self.request,self.image,self.observed)

    def test_raw_request_ax_cannot_be_relabelled(self):
        self.request['ax']=0x4b03
        with self.assertRaisesRegex(ValueError,'raw DOS request AX'):
            validate_entry(self.row,self.request,self.image,self.observed,allow_exec=True)

    def test_same_filename_without_image_identity_rejects(self):
        raw=self.observed[:-1]+b'X';self.row['relocated_sha256']=sha(raw)
        with self.assertRaisesRegex(ValueError,'complete raw'):
            validate_entry(self.row,self.request,self.image,raw,allow_exec=True)

    def test_parent_psp_metadata_must_match_actual_psp_bytes(self):
        self.row['owner']['parent_psp']=0x875
        with self.assertRaisesRegex(ValueError,'parent PSP field'):
            validate_entry(self.row,self.request,self.image,self.observed,allow_exec=True)


class BoundaryMenuPlanTests(unittest.TestCase):
    def setUp(self):
        from th04_dos_route import validate_restart_keys
        self.validate=validate_restart_keys
        self.plan=[[1000+delta+offset,'KBD_enter',down] for delta in range(0,30001,1000) for offset,down in ((0,True),(120,False))]
        self.clock=dict(actions=[dict(due=due,tick=due,key=key,pressed=down,frame=None) for due,key,down in self.plan[:8]],
            restart=dict(action_start=0,action_end=8,tick=1000,entry_tick=4500,resident_seed=65,menu_boundary=True,cancelled=self.plan[8:],enter_down=False))

    def test_verified_entry_may_end_after_fourth_confirmation(self):
        self.validate(self.clock,0)
        self.clock['restart']['menu_boundary']=False
        with self.assertRaises(ValueError):self.validate(self.clock,0)

    def test_missing_prefix_event_is_not_hidden_by_extra_confirmations(self):
        self.clock['actions'].pop(2);self.clock['restart']['action_end']-=1
        with self.assertRaises(ValueError):self.validate(self.clock,0)

    def test_pending_suffix_cancellation_must_remain_complete(self):
        self.clock['restart']['cancelled'].pop()
        with self.assertRaises(ValueError):self.validate(self.clock,0)
