import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EnvironmentTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / 'user home'
        self.home.mkdir()
        self.project = self.base / 'project with spaces'
        self.project.mkdir()
        for name in ('start.sh', 'stop.sh'):
            shutil.copy2(ROOT / name, self.project / name)
        shutil.copytree(ROOT / 'scripts', self.project / 'scripts')
        (self.project / 'vimrc').write_text('set number\n')
        (self.project / '.vim').mkdir()
        (self.project / 'index.py').write_text('')
        self.env = dict(os.environ, HOME=str(self.home))

    def run_script(self, name, ok=True):
        result = subprocess.run(['bash', str(self.project / name)], cwd=self.base,
                                env=self.env, capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def test_empty_home_and_repeated_calls(self):
        self.run_script('stop.sh')
        self.run_script('start.sh')
        self.run_script('start.sh')
        for name, source in (('.vimrc', 'vimrc'), ('.vim', '.vim'), ('.index.py', 'index.py')):
            self.assertEqual((self.home / name).resolve(), self.project / source)
        self.run_script('stop.sh')
        self.run_script('stop.sh')
        for name in ('.vimrc', '.vim', '.index.py'):
            self.assertFalse(os.path.lexists(self.home / name))

    def test_restore_files_directory_and_broken_symlink(self):
        (self.home / '.vimrc').write_text('original config')
        (self.home / '.vim').mkdir()
        (self.home / '.vim' / 'personal.txt').write_text('personal plugin')
        (self.home / '.index.py').symlink_to('missing-original.py')
        self.run_script('start.sh')
        self.run_script('start.sh')
        self.run_script('stop.sh')
        self.assertEqual((self.home / '.vimrc').read_text(), 'original config')
        self.assertEqual((self.home / '.vim' / 'personal.txt').read_text(), 'personal plugin')
        self.assertEqual(os.readlink(self.home / '.index.py'), 'missing-original.py')

    def test_conflict_preserves_user_change_and_backup(self):
        (self.home / '.vimrc').write_text('original')
        self.run_script('start.sh')
        (self.home / '.vimrc').unlink()
        (self.home / '.vimrc').write_text('new user config')
        self.run_script('stop.sh', ok=False)
        self.assertEqual((self.home / '.vimrc').read_text(), 'new user config')
        self.assertTrue((self.home / '.vim').is_symlink())
        (self.home / '.vimrc').unlink()
        self.run_script('stop.sh')
        self.assertEqual((self.home / '.vimrc').read_text(), 'original')

    def test_project_can_move_before_stop(self):
        (self.home / '.vimrc').write_text('original')
        self.run_script('start.sh')
        renamed = self.base / 'renamed'
        self.project.rename(renamed)
        self.project = renamed
        self.run_script('stop.sh')
        self.assertEqual((self.home / '.vimrc').read_text(), 'original')

    def test_preserve_preexisting_project_link(self):
        (self.home / '.vimrc').symlink_to(self.project / 'vimrc')
        self.run_script('start.sh')
        self.run_script('stop.sh')
        self.assertEqual(os.readlink(self.home / '.vimrc'), str(self.project / 'vimrc'))

    def test_failed_start_rolls_back(self):
        (self.home / '.vimrc').write_text('original')
        (self.project / '.vim/tmp').write_text('not a directory')
        self.run_script('start.sh', ok=False)
        self.assertEqual((self.home / '.vimrc').read_text(), 'original')
        self.assertFalse(os.path.lexists(self.home / '.vim'))
        self.run_script('stop.sh')

    def test_missing_source_changes_nothing(self):
        (self.project / 'vimrc').unlink()
        (self.home / '.vimrc').write_text('original')
        self.run_script('start.sh', ok=False)
        self.assertEqual((self.home / '.vimrc').read_text(), 'original')
        self.assertFalse((self.home / '.vim').exists())


if __name__ == '__main__':
    unittest.main()
