"""Exercise clean checkout, PR range and accidental private-file failures."""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RepositoryChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts/boundary_review").mkdir(parents=True)
        shutil.copyfile(ROOT / "scripts/ci.py", self.root / "scripts/ci.py")
        # Ledger validation has its own tests; isolate Git/syntax behavior here.
        for name in ("validate_tracking.py", "decoded_function_acceptance.py",
                     "boundary_review/validate_function_boundary_ledger.py"):
            (self.root / "scripts" / name).write_text("raise SystemExit(0)\n")
        self.git("init", "-q")
        self.git("config", "user.name", "CI test")
        self.git("config", "user.email", "ci@example.invalid")
        self.commit()
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, text=True,
                              capture_output=True, check=True)

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture", "--allow-empty")

    def ci(self, *args):
        env = os.environ.copy()
        env.pop("CI_BASE_REF", None)
        return subprocess.run([sys.executable, "scripts/ci.py", *args],
                              cwd=self.root, env=env, text=True, capture_output=True)

    def test_clean_checkout_without_private_inputs(self):
        result = self.ci()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_earlier_pr_commit_with_bad_syntax_is_checked(self):
        (self.root / "broken.py").write_text("def broken(\n")
        self.commit()
        (self.root / "later.py").write_text("answer = 42\n")
        self.commit()
        result = self.ci()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("broken.py", result.stderr)

    def test_full_pr_whitespace_range(self):
        (self.root / "earlier.txt").write_text("trailing space \n")
        self.commit()
        (self.root / "later.txt").write_text("clean\n")
        self.commit()
        self.assertEqual(self.ci().returncode, 0)
        result = self.ci("--base", self.base)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("earlier.txt", result.stdout)

    def test_staged_and_untracked_machine_inputs(self):
        (self.root / "staged.json").write_text('{"valid": true}\n')
        self.git("add", "staged.json")
        (self.root / "untracked.toml").write_text("broken = [\n")
        result = self.ci()
        self.assertNotEqual(result.returncode, 0)

    def test_private_directory_and_binary(self):
        for name in (".analysis/target.txt", "src/MAIN.EXE"):
            with self.subTest(name=name):
                path = self.root / name
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(b"private fixture")
                self.git("add", "-f", name)
                result = self.ci()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("must not be committed", result.stderr)
                self.git("rm", "-f", name)

    def test_malformed_csv(self):
        (self.root / "ledger.csv").write_text("id,value\na,b,c\n")
        result = self.ci()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("column count", result.stderr)

    def test_renamed_executable_is_rejected(self):
        (self.root / "target.data").write_bytes(b"MZ\x00\x00fixture")
        result = self.ci()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("executable or archive", result.stderr)

    def test_missing_build_source(self):
        (self.root / "config").mkdir()
        manifest = self.root / "config/native_op_sources.toml"
        manifest.write_text('c_sources = ["src/op/missing.cpp"]\n')
        result = self.ci()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing source", result.stderr)
        manifest.unlink()
        (self.root / "port64").mkdir()
        (self.root / "port64/CMakeLists.txt").write_text("add_executable(game missing.cpp)\n")
        result = self.ci()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing source", result.stderr)


if __name__ == "__main__":
    unittest.main()
