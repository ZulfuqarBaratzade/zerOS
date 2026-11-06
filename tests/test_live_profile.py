"""Fixture-only tests: no real account, locale or privilege commands execute."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'config/includes.chroot/usr/lib/zeros/live_profile.py'
spec = importlib.util.spec_from_file_location('live_profile', HELPER)
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'etc/default').mkdir(parents=True)
        (self.root / 'etc/passwd').write_text('root:x:0:0:root:/root:/bin/bash\n')

    def test_cli_refuses_host_execution_without_build_marker(self):
        with patch('sys.argv', ['live_profile.py', 'accounts']), patch.object(profile.Path, 'is_dir', return_value=False), patch.object(profile, 'configure_accounts') as configure:
            with self.assertRaises(SystemExit) as result:
                profile.main()
            self.assertEqual(result.exception.code, 2)
            configure.assert_not_called()

    def test_locale_overrides_standard_reset_idempotently(self):
        (self.root / 'etc/default/locale').write_text('LANG=C.UTF-8\nLC_ALL=C\n')
        (self.root / 'etc/locale.gen').write_text('# az_AZ.UTF-8 UTF-8\nen_US.UTF-8 UTF-8\naz_AZ.UTF-8 UTF-8\n')
        run = Mock()
        profile.configure_locale(self.root, run)
        before = (self.root / 'etc/locale.gen').read_bytes()
        profile.configure_locale(self.root, run)
        self.assertEqual(before, (self.root / 'etc/locale.gen').read_bytes())
        self.assertEqual(before.count(b'az_AZ.UTF-8 UTF-8'), 1)
        self.assertIn(b'en_US.UTF-8 UTF-8', before)
        self.assertEqual((self.root / 'etc/default/locale').read_text(),
                         'LANG=az_AZ.UTF-8\nLANGUAGE=az:en\n')
        run.assert_called_with(['locale-gen'], check=True)

    def test_locale_generator_failure_propagates(self):
        with self.assertRaises(subprocess.CalledProcessError):
            profile.configure_locale(self.root, Mock(side_effect=subprocess.CalledProcessError(1, 'locale-gen')))

    def test_locale_hook_runs_after_vendor_reset(self):
        names = sorted(p.name for p in (ROOT / 'config/hooks/normal').glob('*'))
        self.assertNotIn('0006-locale.hook.chroot', names)
        self.assertGreater(names.index('1100-zeros-locale.hook.chroot'),
                           names.index('1020-create-locales-files.hook.chroot'))

    def test_new_account_has_no_usable_password_or_admin_groups(self):
        run = Mock()
        profile.configure_accounts(self.root, run)
        commands = [c.args[0] for c in run.call_args_list]
        self.assertIn(['useradd', '--uid', '1000', '--user-group', '--create-home',
                       '--shell', '/bin/bash', '--password', '!', 'zeros'], commands)
        self.assertIn(['usermod', '--password', '!', 'zeros'], commands)
        self.assertIn(['usermod', '--password', '!', 'root'], commands)
        self.assertIn(['usermod', '--gid', 'zeros', '--groups', '', 'zeros'], commands)
        self.assertNotIn('chpasswd', str(commands))
        self.assertNotIn('zeros:zeros', str(commands))

    def test_existing_account_is_restricted_without_recreating(self):
        with (self.root / 'etc/passwd').open('a') as f:
            f.write('zeros:x:1000:1000::/home/zeros:/bin/bash\n')
        run = Mock()
        profile.configure_accounts(self.root, run)
        self.assertFalse(any(c.args[0][0] == 'useradd' for c in run.call_args_list))
        self.assertIn(['usermod', '--password', '!', 'zeros'], [c.args[0] for c in run.call_args_list])

    def test_uid_collision_fails_before_account_commands(self):
        with (self.root / 'etc/passwd').open('a') as f:
            f.write('other:x:1000:1000::/home/other:/bin/bash\n')
        run = Mock()
        with self.assertRaisesRegex(RuntimeError, 'UID 1000'):
            profile.configure_accounts(self.root, run)
        run.assert_not_called()

    def test_unexpected_zeros_uid_rejected(self):
        with (self.root / 'etc/passwd').open('a') as f:
            f.write('zeros:x:0:0::/root:/bin/bash\n')
        run = Mock()
        with self.assertRaisesRegex(RuntimeError, 'Unexpected zeros UID'):
            profile.configure_accounts(self.root, run)
        run.assert_not_called()

    def test_unexpected_live_sudo_grant_fails_build(self):
        (self.root / 'etc/sudoers.d').mkdir()
        (self.root / 'etc/sudoers.d/live').write_text('zeros ALL=(ALL) NOPASSWD: ALL\n')
        with self.assertRaisesRegex(RuntimeError, 'Unexpected live sudoers'):
            profile.configure_accounts(self.root, Mock())

    def test_account_command_failure_stops(self):
        run = Mock(side_effect=subprocess.CalledProcessError(1, 'useradd'))
        with self.assertRaises(subprocess.CalledProcessError):
            profile.configure_accounts(self.root, run)
        self.assertEqual(run.call_count, 1)

    def test_boot_profiles_share_security_policy(self):
        script = ROOT / 'auto/config'
        # Capture arguments instead of invoking lb/config or touching system config.
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        lb = bin_dir / 'lb'
        lb.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
        lb.chmod(0o755)
        result = subprocess.run(['/bin/sh', str(script)], env={'PATH': str(bin_dir)},
                                capture_output=True, text=True, check=True)
        args = result.stdout.splitlines()
        normal = args[args.index('--bootappend-live') + 1].split()
        failsafe = args[args.index('--bootappend-live-failsafe') + 1].split()
        for arg in ('username=zeros', 'noroot', 'nottyautologin', 'locales=az_AZ.UTF-8',
                    'keyboard-layouts=az,us',
                    'live-config.nocomponents=user-setup,live-debconfig_passwd,sudo,locales,policykit,gdm3,xinit'):
            self.assertIn(arg, normal)
            self.assertIn(arg, failsafe)
        self.assertNotIn('persistence', normal)

    def test_profile_has_graphical_only_autologin_and_polkit_deny(self):
        config = (ROOT / 'config/includes.chroot/etc/gdm3/daemon.conf').read_text()
        self.assertIn('WaylandEnable=false\n', config)
        self.assertIn('AutomaticLogin=zeros', config)
        self.assertIn('AutomaticLoginEnable=true', config)
        self.assertIn('TimedLoginEnable=false', config)
        rule = (ROOT / 'config/includes.chroot/etc/polkit-1/rules.d/00-zeros-live.rules').read_text()
        self.assertIn('subject.user === "zeros"', rule)
        self.assertIn('return polkit.Result.NO;', rule)
        self.assertNotIn('polkit.Result.YES', rule)


if __name__ == '__main__':
    unittest.main()
