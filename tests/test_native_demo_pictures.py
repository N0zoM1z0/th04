"""Guard diagnostic display decoding without claiming physical scanout equality."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'port64'))
import verify_demo_pictures as reader

def controller(start=0):
    g=bytearray(232)
    for offset,value in ((184,40),(180,400),(182,40)):
        g[offset:offset+2]=value.to_bytes(2,'little')
    g[172]=g[202]=1
    g[152:156]=bytes((start&255,start>>8,0,0))
    return g

class NativeDemoPictureTests(unittest.TestCase):
    def test_page_plane_and_bit_order(self):
        raw=bytearray(262144)
        for plane in range(4):raw[plane*65536+32768]=0x80>>plane
        actual=reader.decode_graphics(raw,controller(),bytes((16,1,1,0,1,1,0,0)))
        self.assertEqual(actual[:8],bytes((1,2,4,8,0,0,0,0)))
        self.assertEqual(len(actual),256000)
        self.assertEqual(sum(actual[8:]),0)

    def test_partition_and_address_wrap(self):
        raw=bytearray(262144);raw[32760]=128;raw[0]=64
        g=controller(16380);g[154]=16 # first partition exactly one row
        pixels=reader.decode_graphics(raw,g,bytes((16,0,0,0,1,1,0,0)))
        self.assertEqual(pixels[0],1)
        self.assertEqual(pixels[65],1) # first row wraps after eight bytes
        self.assertEqual(pixels[641],1) # next partition starts at zero

    def test_unsupported_pitch_and_im_reject(self):
        for offset,value in ((184,39),(155,64),(172,2),(207,1),(202,0)):
            g=controller();g[offset]=value
            with self.subTest(offset=offset),self.assertRaises(ValueError):
                reader.decode_graphics(bytes(262144),g,bytes((16,0,0,0,1,1,0,0)))

    def test_raw_extent_reject(self):
        with self.assertRaisesRegex(ValueError,'extent'):
            reader.decode_graphics(bytes(262143),controller(),bytes(8))

    def test_tram_attribute_bank_and_last_byte(self):
        raw=bytearray(16384);raw[3999]=17;raw[8192]=5;raw[12191]=73;raw[4000]=99
        text=reader.canonical_tram(raw)
        self.assertEqual((len(text),text[3999],text[4000],text[-1]),(8000,17,5,73))
        self.assertNotIn(99,text)

    def test_difference_keeps_invisible_and_last_byte(self):
        a=bytes(256000);b=bytearray(a);b[-1]=15
        row=reader.differences(a,b)
        self.assertEqual(row['differing_bytes'],1)
        self.assertEqual(row['first_difference']['offset'],255999)
        with self.assertRaisesRegex(ValueError,'extent'):reader.differences(a,b[:-1])

    def test_label_both_halves_and_attribute_tail(self):
        raw=bytearray(8000);start=2*(12*80+18)
        raw[start]=87;raw[start+35]=194;raw[4000+start+35]=195
        actual=reader.label_cells(raw)
        self.assertEqual((len(actual),actual[0],actual[35],actual[-1]),(72,87,194,195))
        empty=reader.label_cells(bytes(8000))
        self.assertEqual(reader.differences(actual,empty)['differing_bytes'],3)

    def test_metadata_complete_order_and_duplicate_reject(self):
        lines=[f'{n} {frame} {[3,0,2,1][n-1]} demo{n}-frame{frame} 100 0'
               for n in range(1,5) for frame in reader.SAMPLES]
        self.assertEqual(len(reader.display_rows('\n'.join(lines).encode())),40)
        for mutated in (lines[:-1],lines+[lines[-1]],lines[:1]+lines):
            with self.assertRaises(ValueError):reader.display_rows('\n'.join(mutated).encode())
        changed=lines.copy();changed[-1]=lines[-2]
        with self.assertRaisesRegex(ValueError,'order'):reader.display_rows('\n'.join(changed).encode())

if __name__=='__main__':unittest.main()
