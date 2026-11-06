#!/usr/bin/env python3
"""Build-time profile setup; run inside the target chroot, never on the host."""
import argparse
from pathlib import Path
import re
import subprocess


def configure_locale(root, run):
    """root/run are explicit test seams; the CLI always uses the chroot root."""
    path = root / 'etc/locale.gen'
    lines = path.read_text().splitlines() if path.exists() else []
    lines = [line for line in lines
             if not re.fullmatch(r'\s*#?\s*az_AZ\.UTF-8\s+UTF-8\s*', line)]
    path.write_text('\n'.join([*lines, 'az_AZ.UTF-8 UTF-8']) + '\n')
    run(['locale-gen'], check=True)
    # No global LC_ALL: preserve the ability to override individual categories.
    (root / 'etc/default/locale').write_text('LANG=az_AZ.UTF-8\nLANGUAGE=az:en\n')


def configure_accounts(root, run):
    entries = {line.split(':', 1)[0]: line.split(':')
               for line in (root / 'etc/passwd').read_text().splitlines() if line}
    # Fail closed if a fresh build unexpectedly contains a live sudo grant.
    live_sudo = root / 'etc/sudoers.d/live'
    if live_sudo.exists() and live_sudo.read_text().strip():
        raise RuntimeError('Unexpected live sudoers grant; review the image inputs')
    if 'root' not in entries or entries['root'][2] != '0':
        raise RuntimeError('Expected root account missing')
    if 'zeros' in entries:
        if entries['zeros'][2] != '1000':
            raise RuntimeError('Unexpected zeros UID; refusing to repurpose an account')
    else:
        if any(entry[2] == '1000' for entry in entries.values()):
            raise RuntimeError('UID 1000 already belongs to another account')
        run(['useradd', '--uid', '1000', '--user-group', '--create-home',
             '--shell', '/bin/bash', '--password', '!', 'zeros'], check=True)
    # Replace hashes, rather than prefixing ! onto a reusable known password hash.
    run(['usermod', '--password', '!', 'zeros'], check=True)
    run(['usermod', '--gid', 'zeros', '--groups', '', 'zeros'], check=True)
    run(['usermod', '--password', '!', 'root'], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['locale', 'accounts'])
    args = parser.parse_args()
    # This marker is exposed only by live-build during chroot hook execution.
    if not Path('/live-build/config').is_dir():
        parser.error('Run only in a live-build target chroot')
    action = configure_locale if args.action == 'locale' else configure_accounts
    action(Path('/'), subprocess.run)


if __name__ == '__main__':
    main()
