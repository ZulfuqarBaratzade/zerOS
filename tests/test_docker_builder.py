import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('docker_builder', ROOT / 'scripts/docker-builder.py')
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)
spec2 = importlib.util.spec_from_file_location('runner', ROOT / 'scripts/build.py')
runner = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(runner)


class DockerBoundaryTests(unittest.TestCase):
    def test_environment_check_cannot_escalate(self):
        command = workflow.environment_command('default', 'sha256:test')
        for option in ('--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges', '--network=none'):
            self.assertIn(option, command)
        self.assertEqual(command[command.index('--user') + 1], '65534:65534')
        self.assertNotIn('--privileged', command)
        self.assertNotIn('--build', command)
        self.assertEqual(command[-1], '--check-environment')
        self.assertTrue(command[command.index('--mount') + 1].endswith(',readonly'))

    def test_explicit_context_overrides_ambient_endpoint(self):
        self.assertEqual(workflow.docker_command('default', 'info'),
                         ['docker', '--context', 'default', 'info'])

    def test_build_requires_explicit_acknowledgement(self):
        with patch('sys.argv', ['build.py', '--build']), patch.object(runner, 'preflight', return_value={}), patch.object(runner, 'build') as build:
            with self.assertRaisesRegex(RuntimeError, 'separate approval'):
                runner.main()
            build.assert_not_called()


if __name__ == '__main__':
    unittest.main()
