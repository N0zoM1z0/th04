"""Shared tool selector paths preserve target/worktree boundaries."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lib.analysis import AnalysisError, repository_path


class SharedToolPathTests(unittest.TestCase):
    def test_only_provisioned_tool_paths_can_leave_the_worktree(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root, tool, foreign = base / 'game', base / 'shared', base / 'foreign'
            (root / '.tools').mkdir(parents=True)
            tool.mkdir()
            foreign.mkdir()
            (root / '.tools/ghidra').symlink_to(tool, target_is_directory=True)
            (root / 'target').symlink_to(foreign, target_is_directory=True)
            with self.assertRaises(AnalysisError):
                repository_path(root, '.tools/ghidra')
            (root / '.tools/factory-runtime.py').write_text('# provisioned')
            self.assertEqual(repository_path(root, '.tools/ghidra').resolve(), tool)
            with self.assertRaises(AnalysisError):
                repository_path(root, 'target')
            (root / '.tools/escape').symlink_to(foreign, target_is_directory=True)
            with self.assertRaises(AnalysisError):
                repository_path(root, '.tools/escape')
            for path in ('../shared', str(tool)):
                with self.assertRaises(AnalysisError):
                    repository_path(root, path)
