"""Read-only foundation tests; no lb, package install, root or container needed."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('foundation', ROOT / 'scripts/build.py')
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)


class FoundationTests(unittest.TestCase):
    def test_default_never_starts_build(self):
        with patch('sys.argv', ['build.py']), patch.object(foundation, 'preflight') as check, patch.object(foundation, 'build') as build:
            foundation.main()
            check.assert_called_once_with(False)
            build.assert_not_called()

    def test_build_stops_on_failed_environment_gate(self):
        with patch('sys.argv', ['build.py', '--build']), patch.object(foundation, 'preflight', side_effect=RuntimeError('wrong toolchain')), patch.object(foundation, 'build') as build:
            with self.assertRaisesRegex(RuntimeError, 'wrong toolchain'):
                foundation.main()
            build.assert_not_called()

    def test_local_hooks_match_lock(self):
        with contextlib.redirect_stdout(io.StringIO()):
            lock = foundation.preflight()
        self.assertEqual(lock['suite'], 'trixie')

    def test_pins_match_environment_recipe(self):
        lock = json.loads((ROOT / 'build/versions.json').read_text())
        recipe = (ROOT / 'build/Dockerfile').read_text()
        for name, version in lock['packages'].items():
            self.assertIn(f'{name}={version}', recipe)
        self.assertIn(lock['snapshot'], recipe)

    def test_environment_rejects_missing_dependency(self):
        real_which = foundation.shutil.which
        with patch.object(foundation.shutil, 'which', side_effect=lambda name: None if name == 'lb' else real_which(name)):
            with self.assertRaisesRegex(RuntimeError, 'Missing build dependency: lb'):
                foundation.preflight(environment=True)

    def test_modified_hook_rejected_before_build(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'build').mkdir()
            (root / 'config/hooks').mkdir(parents=True)
            (root / 'build/versions.json').write_bytes((ROOT / 'build/versions.json').read_bytes())
            (root / 'config/hooks/bad').write_text('changed')
            (root / 'build/hooks.lock.json').write_text(json.dumps({'hooks': [
                {'path': 'config/hooks/bad', 'sha256': '0' * 64}]}))
            with patch.object(foundation, 'ROOT', root), patch.object(foundation, 'run', return_value=str(root)):
                with self.assertRaisesRegex(RuntimeError, 'Hook checksum mismatch'):
                    foundation.preflight()


if __name__ == '__main__':
    unittest.main()
