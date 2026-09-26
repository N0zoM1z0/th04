from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prune_analysis


@unittest.skipUnless(shutil.which("zstd"), "zstd is required for replay archives")
class PruneArchiveTests(unittest.TestCase):
    def test_prune_requires_recoverable_matching_result(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            run = root / ".analysis/reconstruction/probes/focused"
            run.mkdir(parents=True)
            receipt = run / "receipt.json"
            receipt.write_bytes(b'{"passed": true}\n')
            relative = receipt.relative_to(root).as_posix()
            digest = sha256(receipt.read_bytes()).hexdigest()

            archive_dir = root / ".analysis/reconstruction/receipt-archive"
            archive_dir.mkdir()
            plain = archive_dir / "focused.tar"
            with tarfile.open(plain, "w") as bundle:
                bundle.add(receipt, arcname=relative)
            archive = archive_dir / "focused.tar.zst"
            subprocess.run(
                ["zstd", "-q", "-o", str(archive), str(plain)], check=True
            )
            archive.with_name(archive.name + ".sha256").write_text(
                f"{sha256(archive.read_bytes()).hexdigest()}  "
                f"{archive.relative_to(root).as_posix()}\n"
            )
            manifest = archive_dir / "focused.files.sha256"
            manifest.write_text(f"{digest}  {relative}\n")

            with patch.object(prune_analysis, "ROOT", root):
                prune_analysis.verify_replay_archive([run], archive, manifest)
                receipt.write_bytes(b'{"passed": false}\n')
                with self.assertRaisesRegex(SystemExit, "unarchived or changed"):
                    prune_analysis.verify_replay_archive([run], archive, manifest)
                receipt.write_bytes(b'{"passed": true}\n')
                archive.write_bytes(archive.read_bytes() + b"changed")
                with self.assertRaisesRegex(SystemExit, "checksum mismatch"):
                    prune_analysis.verify_replay_archive([run], archive, manifest)


if __name__ == "__main__":
    unittest.main()
