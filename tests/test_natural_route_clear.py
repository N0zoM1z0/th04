import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'port64'))
from verify_natural_routes import strict_clear

def scores(mask=1, index=1):
    sections=[]
    for i in range(10):
        section=bytearray(196);section[174]=mask if i==index else 0x19
        section[2:4]=sum(section[4:]).to_bytes(2,'little');sections.append(section)
    # Independent inverse cipher over explicit checksummed control sections.
    for section in sections:
        for i in range(194,3,-1):section[i]=(section[i]-(((section[i+1]>>3)|(section[i+1]<<5))&255))&255
    return b''.join(sections)

class NaturalClear(unittest.TestCase):
    def check(self,mask=1,**changes):
        args=dict(result=dict(fresh_op=1,gameover_visits=0,registration_visits=1,ending_visits=1,extra_visits=0),raw_score=scores(mask),rank=1,character=0,shot=0,extra=False,stages=set(range(6)),ending='_ED000.TXT');args.update(changes);return strict_clear(**args)['accepted']
    def test_real_mask_and_both_shots(self):
        self.assertTrue(self.check());self.assertTrue(self.check(3));self.assertTrue(self.check(2,shot=1,ending='_ED010.TXT'))
    def test_sentinel_and_high_bits(self):
        for mask in (0x19,0x41,0xff):self.assertFalse(self.check(mask))
    def test_absent_and_wrong_shot(self):
        self.assertFalse(self.check(0));self.assertFalse(self.check(2))
    def test_bad_ending_even_with_clear(self):
        self.assertFalse(self.check(ending='_ED001.TXT'))
    def test_missing_stage(self):
        self.assertFalse(self.check(stages=set(range(5))))
    def test_other_character_partition(self):
        self.assertFalse(self.check(character=1,ending='_ED100.TXT'))
    def test_partial_and_continue_routes(self):
        result=dict(fresh_op=1,gameover_visits=1,registration_visits=1,ending_visits=1,extra_visits=0)
        self.assertFalse(self.check(result=result));result.update(gameover_visits=0,fresh_op=0);self.assertFalse(self.check(result=result))
    def test_full_checksum(self):
        raw=bytearray(scores());raw[196+3]^=1
        with self.assertRaisesRegex(AssertionError,'full score checksum'):self.check(raw_score=bytes(raw))
    def test_easy_and_extra_have_distinct_extent(self):
        self.assertTrue(self.check(raw_score=scores(1,0),rank=0,stages=set(range(5)),ending='_ED001.TXT'))
        result=dict(fresh_op=1,gameover_visits=0,registration_visits=1,ending_visits=0,extra_visits=1)
        self.assertTrue(self.check(raw_score=scores(1,4),extra=True,stages={6},ending=None,result=result))
        self.assertFalse(self.check(raw_score=scores(1,4),extra=True,stages=set(range(6)),ending=None,result=result))
if __name__=='__main__':unittest.main()
