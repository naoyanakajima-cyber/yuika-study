"""Exercise standalone installation with synthetic local Git repositories only."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / 'scripts/cloud/install.sh'


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='yuika-bootstrap-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.git(self.source, 'init', '-q', '-b', 'main')
        self.git(self.source, 'config', 'user.name', 'Synthetic bootstrap test')
        self.git(self.source, 'config', 'user.email', 'cloud-tests@example.test')
        (self.source / 'README.md').write_text('Synthetic main without setup\n')
        self.git(self.source, 'add', 'README.md')
        self.git(self.source, 'commit', '-qm', 'Synthetic main')
        self.main = self.git(self.source, 'rev-parse', 'HEAD')
        self.git(self.source, 'switch', '-qc', 'prepared')
        (self.source / 'scripts/cloud').mkdir(parents=True)
        (self.source / 'scripts/cloud/setup.sh').write_text(
            '#!/usr/bin/env bash\nset -eu\n'
            'cd "$(dirname "$0")/../.."\n'
            'if [[ ${SYNTHETIC_SETUP_FAILURE:-0} == 1 ]]; then exit 17; fi\n'
            'mkdir -p .venv\nprintf "setup\\n" >> .venv/calls\n')
        (self.source / 'scripts/cloud/activate.sh').write_text('# synthetic\n')
        (self.source / 'AGENTS.md').write_text('Synthetic instructions\n')
        (self.source / 'requirements-dev.txt').write_text('# synthetic dependencies\n')
        (self.source / '.gitignore').write_text('.venv/\n')
        self.git(self.source, 'add', '--', 'scripts', 'AGENTS.md', 'requirements-dev.txt', '.gitignore')
        self.git(self.source, 'commit', '-qm', 'Synthetic prepared revision')
        self.revision = self.git(self.source, 'rev-parse', 'HEAD')
        self.git(self.source, 'switch', '-q', 'main')
        self.target = self.root / 'checkout'
        self.logs = self.root / 'logs'

    @staticmethod
    def git(repo, *args):
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True,
                                       stderr=subprocess.PIPE).strip()

    def install(self, revision=None, failure=False):
        env = dict(os.environ, YUIKA_CLOUD_SOURCE_REPO=str(self.source),
                   YUIKA_CLOUD_LOG_DIR=str(self.logs),
                   SYNTHETIC_SETUP_FAILURE='1' if failure else '0')
        return subprocess.run(['bash', str(INSTALL), revision or self.revision, str(self.target)],
                              cwd=self.source, env=env, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('SUCCESS stage=complete', result.stdout)

    def test_main_without_setup_and_original_dirty_changes_are_preserved(self):
        (self.source / 'README.md').write_text('Uncommitted original work\n')
        before = self.git(self.source, 'status', '--porcelain=v1')
        self.assertFalse((self.source / 'scripts/cloud/setup.sh').exists())
        self.assert_success(self.install())
        self.assertEqual(self.git(self.source, 'rev-parse', 'HEAD'), self.main)
        self.assertEqual(self.git(self.source, 'branch', '--show-current'), 'main')
        self.assertEqual(self.git(self.source, 'status', '--porcelain=v1'), before)
        self.assertEqual((self.source / 'README.md').read_text(), 'Uncommitted original work\n')
        self.assertEqual(self.git(self.target, 'rev-parse', 'HEAD'), self.revision)
        receipt = json.loads((self.target / '.venv/yuika-cloud-install.json').read_text())
        self.assertEqual(receipt['required_revision'], self.revision)
        self.assertTrue(receipt['requirements_sha256'])
        self.assertTrue(Path(receipt['install_log']).exists())

    def test_reinstall_preserves_clean_topic_branch_and_commits(self):
        self.assert_success(self.install())
        self.git(self.target, 'switch', '-qc', 'codex/synthetic-work')
        self.git(self.target, 'config', 'user.name', 'Synthetic bootstrap test')
        self.git(self.target, 'config', 'user.email', 'cloud-tests@example.test')
        (self.target / 'README.md').write_text('Committed topic work\n')
        self.git(self.target, 'add', 'README.md')
        self.git(self.target, 'commit', '-qm', 'Keep topic work')
        head = self.git(self.target, 'rev-parse', 'HEAD')
        self.assert_success(self.install())
        self.assertEqual(self.git(self.target, 'rev-parse', 'HEAD'), head)
        self.assertEqual(self.git(self.target, 'branch', '--show-current'), 'codex/synthetic-work')
        self.assertEqual((self.target / '.venv/calls').read_text(), 'setup\nsetup\n')

    def test_dirty_target_is_preserved_without_running_setup(self):
        self.assert_success(self.install())
        (self.target / 'README.md').write_text('Uncommitted topic work\n')
        before = self.git(self.target, 'status', '--porcelain=v1')
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FAIL stage=inspect-checkout', result.stdout)
        self.assertEqual(self.git(self.target, 'status', '--porcelain=v1'), before)
        self.assertEqual((self.target / 'README.md').read_text(), 'Uncommitted topic work\n')
        self.assertEqual((self.target / '.venv/calls').read_text(), 'setup\n')

    def test_untracked_target_files_are_preserved(self):
        self.assert_success(self.install())
        (self.target / 'scratch.txt').write_text('Synthetic untracked work\n')
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.target / 'scratch.txt').exists())
        self.assertEqual((self.target / '.venv/calls').read_text(), 'setup\n')

    def test_existing_unrelated_directory_is_preserved(self):
        self.target.mkdir()
        (self.target / 'keep.txt').write_text('Keep me\n')
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FAIL stage=inspect-checkout', result.stdout)
        self.assertEqual((self.target / 'keep.txt').read_text(), 'Keep me\n')

    def test_wrong_revision_does_not_reset_existing_target(self):
        self.assert_success(self.install())
        result = self.install('f' * 40)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git(self.target, 'rev-parse', 'HEAD'), self.revision)
        self.assertIn('preserved', result.stdout)

    def test_missing_commit_logs_fetch_failure_without_target(self):
        result = self.install('f' * 40)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FAIL stage=fetch-pinned-revision', result.stdout)
        self.assertFalse(self.target.exists())
        self.assertTrue(list(self.root.glob('.yuika-cloud-install.*')))

    def test_setup_failure_has_no_success_receipt_and_can_resume(self):
        result = self.install(failure=True)
        self.assertEqual(result.returncode, 17, result.stdout)
        self.assertIn('FAIL stage=setup exit=17', result.stdout)
        self.assertFalse((self.target / '.venv/yuika-cloud-install.json').exists())
        self.assert_success(self.install())

    def test_invalid_sha_stops_before_creating_target(self):
        result = self.install('main')
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.target.exists())

    def test_failed_retry_invalidates_previous_install_success(self):
        self.assert_success(self.install())
        self.assertTrue((self.target / '.venv/yuika-cloud-install.json').exists())
        result = self.install(failure=True)
        self.assertEqual(result.returncode, 17, result.stdout)
        self.assertFalse((self.target / '.venv/yuika-cloud-install.json').exists())
        self.assert_success(self.install())

    def test_symlink_target_is_preserved(self):
        other = self.root / 'other'
        other.mkdir()
        self.target.symlink_to(other, target_is_directory=True)
        result = self.install()
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertEqual(list(other.iterdir()), [])

    def test_setup_runtime_failure_invalidates_previous_receipts(self):
        env = dict(os.environ, YUIKA_CLOUD_LOG_DIR=str(self.logs),
                   PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH='/missing/synthetic-chromium')
        # Run the actual setup script in a synthetic repository, stopping before
        # venv/package changes. No real environment receipts are touched.
        setup = self.source / 'scripts/cloud/setup.sh'
        setup.parent.mkdir(parents=True, exist_ok=True)
        setup.write_text((ROOT / 'scripts/cloud/setup.sh').read_text())
        (self.source / '.venv').mkdir()
        for name in ('yuika-cloud-setup.json', 'yuika-cloud-install.json'):
            (self.source / '.venv' / name).write_text('{}')
        result = subprocess.run(['bash', str(setup)], env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('FAIL stage=runtime exit=1', result.stdout)
        self.assertFalse(list((self.source / '.venv').glob('yuika-cloud-*.json')))

    def test_setup_log_directory_failure_invalidates_previous_receipts(self):
        # A logging failure must not leave an earlier setup looking current.
        setup = self.source / 'scripts/cloud/setup.sh'
        setup.parent.mkdir(parents=True, exist_ok=True)
        setup.write_text((ROOT / 'scripts/cloud/setup.sh').read_text())
        (self.source / '.venv').mkdir()
        for name in ('yuika-cloud-setup.json', 'yuika-cloud-install.json'):
            (self.source / '.venv' / name).write_text('{}')
        self.logs.write_text('Synthetic file blocking log directory creation\n')
        result = subprocess.run(
            ['bash', str(setup)],
            env=dict(os.environ, YUIKA_CLOUD_LOG_DIR=str(self.logs)),
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertFalse(list((self.source / '.venv').glob('yuika-cloud-*.json')))
        self.assertFalse((self.source / '.venv/bin').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
