"""Reject erased generation identities and mixed old/new observation streams."""
import gzip
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/probes'))
from th04_ordinary_generation import split_generations, parse_trace
from compare_th04_dos_demos import relocated_module
from th04_ordinary_dgroup import MAGIC, HEADER, records


class GenerationPartitionTests(unittest.TestCase):
    def test_actual_partition_preserves_every_byte_and_literal_ids(self):
        raw = b'L 1 abc\nI 1 a\nR 1 b\nL 2 def\nI 2 c\n'
        a,b = split_generations(raw)
        self.assertEqual(a+b,raw)
        self.assertEqual(b,b'L 2 def\nI 2 c\n')

    def test_missing_relabelled_reordered_and_extra_generations_reject(self):
        for raw in (b'L 1 a\nI 1 b\n', b'L 2 a\nI 2 b\n',
                    b'L 1 a\nI 2 b\nL 2 c\n', b'L 1 a\nL 1 b\n',
                    b'L 1 a\nL 2 b\nL 3 c\n', b'L 1 a\n\nL 2 b\n'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                split_generations(raw)


class LiteralGenerationParserTests(unittest.TestCase):
    def setUp(self):
        header=bytearray(32);header[:2]=b'MZ'
        struct.pack_into('<HHHHHHHHHHHHH',header,2,64,1,0,2,1,0xffff,0,32,0,0,0,28,0)
        self.main=bytes(header)+bytes(32)
        self.profile=dict(fields=[('frame',0,2),('stage',2,1),('resident_pointer',3,4)],
                          hooks=[(1,0x10,0x20),(2,0x10,0x22)],dgroup=0x20,end_after=1)
        resident=bytearray(80);resident[:11]=b'HUMAConfig\0'
        self.text='L 2 0100 00000000 00000000 '+relocated_module(self.main,0x100).hex()+'\n'
        self.text+='I 2 0110 0020 0120 0 0 0000 00 00000000 '+resident.hex()+'\n'

    def test_second_generation_is_admitted_only_with_explicit_generation(self):
        parsed=parse_trace(self.text,self.main,self.profile,generation=2)
        self.assertEqual(parsed['rows'][0]['frame'],'0000')
        with self.assertRaisesRegex(ValueError,'process extent'):
            parse_trace(self.text,self.main,self.profile)

    def test_stale_generation_in_second_sample_rejects(self):
        with self.assertRaisesRegex(ValueError,'frame shape/process'):
            parse_trace(self.text.replace('I 2','I 1'),self.main,self.profile,generation=2)

    def test_second_generation_must_restart_frame_and_rng_counts(self):
        for text in (self.text.replace('0 0 0000','0 0 0100'),self.text.replace('0 0 0000','1 0 0000')):
            with self.subTest(text=text),self.assertRaises(ValueError):
                parse_trace(text,self.main,self.profile,generation=2)


class GenerationDgroupTests(unittest.TestCase):
    def stream(self,generation):
        data=bytearray(65536);data[2:4]=b'\1\0'
        return MAGIC+HEADER.pack(generation,1,0x1000,0x2000,1,0,4096)+data

    def read(self,generation,expected=1):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'records.gz';path.write_bytes(gzip.compress(self.stream(generation)))
            return list(records(path,0x1000,0x2000,[('frame',2,2),('stage',4,1)],1,4096,1,generation=expected))

    def test_actual_generation_two_header_admits(self):
        self.assertEqual(self.read(2,2)[0][0],1)

    def test_default_generation_one_gate_stays_strict(self):
        with self.assertRaisesRegex(ValueError,'order/load'):
            self.read(2)

    def test_generation_one_header_cannot_prove_generation_two(self):
        with self.assertRaisesRegex(ValueError,'order/load'):
            self.read(1,2)


class KeyboardGenerationOwnershipTests(unittest.TestCase):
    def test_second_shot_cannot_extend_initial_op_validation_past_quit(self):
        from unittest.mock import patch
        from th04_dos_route import validate_keyboard
        actions=[dict(key=key,pressed=down) for key,down in
                 [('KBD_z',True),('KBD_z',False),('KBD_z',True),('KBD_z',False),
                  ('KBD_esc',True),('KBD_enter',True),('KBD_z',True)]]
        clock=dict(actions=actions,waits=[],second_main=dict(action_start=6))
        with patch('compare_th04_dos_ordinary_prefix.validate_keyboard_capture',side_effect=RuntimeError('phase probe')) as initial:
            with self.assertRaisesRegex(RuntimeError,'phase probe'):
                validate_keyboard(clock,{},None,None)
        self.assertEqual(initial.call_args.args[0]['actions'],actions[:3])


class SecondShotBoundaryTests(unittest.TestCase):
    def setUp(self):
        from th04_ordinary_second_main import validate_shot_boundary
        self.check=validate_shot_boundary
        self.action=dict(frame=1,tick=1234,due=1234,unchanged_guest=dict(cpu_regs='00'*48,segments='00'*136))
        self.followup=dict(shot_boundary_tick=1234)
        self.snapshot=dict(cpu_regs='00'*48,segments='00'*136)

    def test_actual_first_actor_frame_and_context_admits(self):
        self.check(self.action,self.followup,self.snapshot)

    def test_entry_delay_or_old_frame_cannot_claim_actor_boundary(self):
        for frame in (0,7547,None):
            self.action['frame']=frame
            with self.subTest(frame=frame),self.assertRaises(ValueError):
                self.check(self.action,self.followup,self.snapshot)

    def test_other_cpu_context_or_late_tick_rejects(self):
        for field in ('tick','due'):
            original=self.action[field];self.action[field]+=1
            with self.subTest(field=field),self.assertRaises(ValueError):
                self.check(self.action,self.followup,self.snapshot)
            self.action[field]=original
        self.snapshot['cpu_regs']='01'*48
        with self.assertRaises(ValueError):
            self.check(self.action,self.followup,self.snapshot)
