"""Presentation snapshots must retain the distinct seam and complete raw data."""
import copy
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'port64'))
import verify_demo_present as reader

def site_fixture():
    bias=0x700000000000
    layout={'symbols':{'vga':{'address':10},'pc98_gdc':{'address':20}}}
    metadata={'video_symbols':{'vga':bias+10,'pc98_gdc':bias+20},'scalar_site':dict(
        core_address=bias+reader.CORE_ENTRY,site_address=bias+reader.CORE_ENTRY+reader.SCALAR_OFFSET,
        elf_offset=reader.SCALAR_OFFSET,instruction_witness=reader.SCALAR_WITNESS)}
    return metadata,layout

def archive_fixture(base,duplicate=False):
    name='gnu-v4/capture/demo1-frame3996.tram';data=b'last-byte\x73'
    with tarfile.open(base/'capture.tar.gz','w:gz') as tar:
        for _ in range(2 if duplicate else 1):
            info=tarfile.TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
    journal=dict(archive='capture.tar.gz',archive_sha256=reader.sha((base/'capture.tar.gz').read_bytes()),
                 files=[dict(path=name,size=len(data),sha256=reader.sha(data))])
    write_journal(base,journal)
    return name,data,journal

def write_journal(base,journal):
    raw=json.dumps(journal).encode();(base/'retention.json').write_bytes(raw)
    (base/'retention-readback.json').write_text(json.dumps(dict(passed=True,journal_sha256=reader.sha(raw))))

class NativeDemoPresentTests(unittest.TestCase):
    def test_old_magic_or_boundary_reject(self):
        reader.attest_format(reader.MAGIC,reader.BOUNDARY)
        for magic,boundary in ((b'TH04VD2\n',reader.BOUNDARY),(reader.MAGIC,'stage_frame write, before mod counters and score update')):
            with self.subTest(magic=magic),self.assertRaisesRegex(ValueError,'seam'):reader.attest_format(magic,boundary)

    def test_projection_changes_only_declared_constant(self):
        raw="prefix\nMAGIC = b'TH04VD2\\n'\nopaque suffix\n"
        projected=reader.project_module('th04_demo_video.py',raw)
        self.assertEqual(projected,"prefix\nMAGIC = b'TH04VP3\\n'\nopaque suffix\n")

    def test_missing_or_duplicate_projection_marker_reject(self):
        marker="MAGIC = b'TH04VD2\\n'"
        for raw in ('',marker+'\n'+marker):
            with self.assertRaisesRegex(ValueError,'drift'):reader.project_module('th04_demo_video.py',raw)

    def test_site_real_bias_and_byte_mutations(self):
        metadata,layout=site_fixture();reader.attest_site(metadata,layout)
        for key,value in (('site_address',metadata['scalar_site']['site_address']+1),('elf_offset',reader.SCALAR_OFFSET+1),('instruction_witness','00')):
            changed=copy.deepcopy(metadata);changed['scalar_site'][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'witness'):reader.attest_site(changed,layout)

    def test_site_mixed_symbol_bias_reject(self):
        metadata,layout=site_fixture();metadata['video_symbols']['pc98_gdc']+=1
        with self.assertRaisesRegex(ValueError,'bias'):reader.attest_site(metadata,layout)

    def test_complete_archive_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);name,data,_=archive_fixture(base)
            self.assertEqual(reader.retained_capture(base),{name:data})

    def test_restored_last_byte_digest_reject(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);_,data,journal=archive_fixture(base)
            journal['files'][0]['sha256']=reader.sha(data[:-1]+b'\x74');write_journal(base,journal)
            with self.assertRaisesRegex(ValueError,'restored capture'):reader.retained_capture(base)

    def test_duplicate_archive_member_reject(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);archive_fixture(base,duplicate=True)
            with self.assertRaisesRegex(ValueError,'duplicate'):reader.retained_capture(base)

if __name__=='__main__':unittest.main()
