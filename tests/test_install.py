import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install.py')
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dest = Path(self.tmp.name) / 'space in path' / 'sun-ge'

    def run_cli(self, *args, success=True):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'),
                                 '--dest', str(self.dest), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_install_payload_and_noop(self):
        self.run_cli()
        self.assertEqual((self.dest / 'SKILL.md').read_bytes(), (ROOT / 'SKILL.md').read_bytes())
        self.assertTrue((self.dest / 'references/quotes.md').is_file())
        self.assertTrue((self.dest / 'agents/openai.yaml').is_file())
        self.assertFalse((self.dest / '.git').exists())
        self.assertFalse((self.dest / 'scripts').exists())
        before = (self.dest / 'SKILL.md').stat().st_mtime_ns
        self.run_cli()
        self.assertEqual((self.dest / 'SKILL.md').stat().st_mtime_ns, before)
        self.assertFalse(list(self.dest.parent.glob('*.zip')))

    def test_preview_writes_nothing(self):
        self.run_cli('--dry-run')
        self.assertFalse(self.dest.parent.exists())

    def test_collision_and_backup_restore(self):
        self.run_cli()
        (self.dest / 'local.txt').write_text('my edits')
        old = installer.snapshot(self.dest)
        self.run_cli(success=False)
        self.run_cli('--update', '--dry-run')
        self.assertEqual(installer.snapshot(self.dest), old)
        self.assertFalse(list(self.dest.parent.glob('*.zip')))
        self.run_cli('--update')
        self.assertFalse((self.dest / 'local.txt').exists())
        backups = list(self.dest.parent.glob('*.zip'))
        self.assertEqual(len(backups), 1)
        restored = Path(self.tmp.name) / 'restore'
        with zipfile.ZipFile(backups[0]) as archive:
            self.assertIsNone(archive.testzip())
            archive.extractall(restored)
        self.assertEqual(installer.snapshot(restored / 'sun-ge'), old)

    @unittest.skipIf(os.name == 'nt', 'Symlinks require special Windows privileges')
    def test_symlink_destination_and_nested_link_rejected(self):
        self.dest.parent.mkdir(parents=True)
        target = Path(self.tmp.name) / 'real'
        target.mkdir()
        self.dest.symlink_to(target, target_is_directory=True)
        self.run_cli('--update', success=False)
        self.assertTrue(self.dest.is_symlink())
        self.dest.unlink()
        self.run_cli()
        (self.dest / 'link').symlink_to(target, target_is_directory=True)
        self.run_cli('--update', success=False)
        self.assertTrue((self.dest / 'link').is_symlink())

    def test_file_destination_rejected(self):
        self.dest.parent.mkdir(parents=True)
        self.dest.write_text('keep')
        self.run_cli('--update', success=False)
        self.assertEqual(self.dest.read_text(), 'keep')

    def test_source_overlap_rejected(self):
        for target in (ROOT, ROOT.parent, ROOT / 'inside'):
            with self.assertRaises(ValueError):
                installer.install(target, update=True, dry_run=True)

    def test_failed_readback_rolls_back(self):
        self.run_cli()
        (self.dest / 'local.txt').write_text('keep')
        previous = installer.snapshot(self.dest)
        real_snapshot = installer.snapshot
        calls = 0

        def fail_readback(root):
            nonlocal calls
            if root == self.dest:
                calls += 1
                if calls == 2:
                    raise OSError('simulated readback failure')
            return real_snapshot(root)

        with patch.object(installer, 'snapshot', side_effect=fail_readback):
            with self.assertRaises(OSError):
                installer.install(self.dest, update=True)
        self.assertEqual(installer.snapshot(self.dest), previous)

    def test_agent_targets(self):
        import argparse
        for agent, folder in [('codex', '.agents'), ('claude', '.claude'), ('openclaw', '.openclaw')]:
            args = argparse.Namespace(agent=agent, dest=None)
            with patch.object(Path, 'home', return_value=Path(self.tmp.name)):
                self.assertEqual(installer.destination(args), Path(self.tmp.name) / folder / 'skills/sun-ge')


if __name__ == '__main__':
    unittest.main()
