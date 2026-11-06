#!/usr/bin/env python3
"""Non-destructive build staging. Default mode only reads/checks the checkout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    if args[:2] == ('git', '-C'):
        args = ('git', '-c', f'safe.directory={ROOT}', *args[1:])
    return subprocess.check_output(args, text=True, **kwargs).strip()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def preflight(environment=False):
    for tool in ('git', 'bash', 'sha256sum'):
        require(shutil.which(tool), f'Missing dependency: {tool}')
    require(run('git', '-C', str(ROOT), 'rev-parse', '--show-toplevel') == str(ROOT),
            'Script must belong to the repository root')
    lock = json.loads((ROOT / 'build/versions.json').read_text())
    hooks = json.loads((ROOT / 'build/hooks.lock.json').read_text())['hooks']
    for item in hooks:
        path = ROOT / item['path']
        require(not path.is_symlink() and path.is_file(), f'Hook must be local: {path}')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'],
                f'Hook checksum mismatch: {path}')
    for path in (ROOT / 'config').rglob('*'):
        require(not path.is_symlink(), f'Unexpected config symlink: {path}')
    for path in [ROOT / 'auto/config', ROOT / 'scripts/build.sh',
                 *(ROOT / 'config/hooks').glob('*/*')]:
        subprocess.run(['bash', '-n', str(path)], check=True)
    if environment:
        for tool in ('lb', 'debootstrap', 'dpkg-query', 'xorriso', 'mksquashfs',
                     'cpio', 'rsync', 'wget', 'gpgv', 'mount', 'chroot', 'flock'):
            require(shutil.which(tool), f'Missing build dependency: {tool}')
        release = dict(line.split('=', 1) for line in Path('/etc/os-release').read_text().splitlines()
                       if '=' in line)
        require(release.get('ID', '').strip('"') == 'debian' and
                release.get('VERSION_CODENAME', '').strip('"') == lock['suite'],
                'Builder userspace must be Debian Trixie; host OS is checked separately')
        require(run('dpkg', '--print-architecture') == lock['architecture'], 'Expected amd64 environment')
        require(Path('/.dockerenv').is_file(), 'Run the environment check inside the Docker builder')
        require(Path('/etc/zeros-build-environment').is_file(), 'Missing isolated-environment marker')
        require(Path('/opt/zeros/versions.json').read_bytes() == (ROOT / 'build/versions.json').read_bytes(),
                'Environment lock differs from repository; rebuild the environment')
        for package, version in lock['packages'].items():
            actual = run('dpkg-query', '-W', '-f=${Version}', package)
            require(actual == version, f'{package}: expected {version}, found {actual}')
        print(f"Builder userspace: Debian {lock['suite']} / {lock['architecture']} (Docker)", flush=True)
    print('Preflight OK' + (' (environment)' if environment else ' (static only)'), flush=True)
    return lock


def build(lock):
    require(os.geteuid() == 0, 'Build needs root inside the approved Docker builder; preflight does not')
    # Never clean, build in, or overwrite the source checkout or its old ISO.
    output = Path(tempfile.mkdtemp(prefix='zeros-build-'))
    work = output / 'work'
    work.mkdir()
    print(f'Build output: {output}', flush=True)
    shutil.copytree(ROOT / 'config', work / 'config')
    shutil.copytree(ROOT / 'auto', work / 'auto')
    # Generated files contain Bookworm defaults. Only discard disposable copies.
    for name in ('common', 'bootstrap', 'chroot', 'binary', 'source'):
        (work / 'config' / name).unlink(missing_ok=True)
    shutil.copytree(ROOT / 'build', output / 'foundation')
    shutil.copytree(ROOT / 'scripts', output / 'input-scripts',
                    ignore=shutil.ignore_patterns('__pycache__'))
    (output / 'commit.txt').write_text(run('git', '-C', str(ROOT), 'rev-parse', 'HEAD') + '\n')
    (output / 'git-status.txt').write_text(run('git', '-C', str(ROOT), 'status', '--short') + '\n')
    (output / 'working-tree.patch').write_text(run('git', '-C', str(ROOT), 'diff', 'HEAD', '--binary') + '\n')
    shutil.copytree(work / 'config', output / 'input-config')
    shutil.copytree(work / 'auto', output / 'input-auto')
    (output / 'host-packages.tsv').write_text(run('dpkg-query', '-W', '-f=${Package}\t${Version}\n') + '\n')
    (output / 'os-release').write_bytes(Path('/etc/os-release').read_bytes())
    (output / 'base-image.txt').write_bytes(Path('/etc/zeros-build-environment').read_bytes())
    env = dict(os.environ, LC_ALL='C.UTF-8', TZ='UTC',
               SOURCE_DATE_EPOCH=str(lock['source_date_epoch']))
    mirror = f"https://snapshot.debian.org/archive/debian/{lock['snapshot']}/"
    security = f"https://snapshot.debian.org/archive/debian-security/{lock['snapshot']}/"
    options = ['--ignore-system-defaults', '--utc-time', 'true', '--build-with-chroot', 'true',
               '--apt-options', '--yes -o Acquire::Check-Valid-Until=false']
    for key, url in [('bootstrap', mirror), ('chroot', mirror), ('chroot-security', security),
                     ('binary', 'https://deb.debian.org/debian/'),
                     ('binary-security', 'https://security.debian.org/debian-security/')]:
        options.extend([f'--mirror-{key}', url])
    status = {'state': 'running', 'started_utc': time.strftime('%FT%TZ', time.gmtime())}
    try:
        with (output / 'build.log').open('w') as log:
            for command in [['bash', 'auto/config', *options], ['lb', 'build']]:
                log.write('$ ' + ' '.join(command) + '\n')
                log.flush()
                process = subprocess.Popen(command, cwd=work, env=env, stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, text=True)
                for line in process.stdout:
                    print(line, end='', flush=True)
                    log.write(line)
                    log.flush()
                require(process.wait() == 0, f'Command failed; see {output}/build.log')
                if command[0] == 'bash':
                    # lb config must not silently replace our vendored hooks.
                    for item in json.loads((ROOT / 'build/hooks.lock.json').read_text())['hooks']:
                        p = work / item['path']
                        require(not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'],
                                f'Configured hook drift: {p}')
                    shutil.copytree(work / 'config', output / 'resolved-config')
        manifests = list(work.glob('*.packages'))
        require(manifests, 'No final package manifest produced')
        for p in manifests:
            shutil.copy2(p, output / p.name)
        images = list(work.glob('*.iso'))
        require(images, 'No ISO produced')
        with (output / 'SHA256SUMS').open('w') as sums:
            for p in images:
                with p.open('rb') as stream:
                    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                sums.write(f'{digest}  work/{p.name}\n')
        status['state'] = 'build-complete-boot-untested'
    except BaseException as error:
        status.update(state='failed', error=str(error))
        raise
    finally:
        status['finished_utc'] = time.strftime('%FT%TZ', time.gmtime())
        (output / 'result.json').write_text(json.dumps(status, indent=2) + '\n')
        # Keep intermediate manifests for failure diagnosis, too.
        for p in work.glob('chroot.packages.*'):
            shutil.copy2(p, output / p.name)
        print(f'Preserved output: {output}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--preflight', action='store_true', help='Static read-only checks (default)')
    mode.add_argument('--check-environment', action='store_true', help='Also check isolated toolchain; no build')
    mode.add_argument('--build', action='store_true', help='Full build inside approved Docker builder (requires explicit acknowledgement)')
    parser.add_argument('--allow-container-build', action='store_true',
                        help='Acknowledge a separately approved container build; grants no capabilities')
    args = parser.parse_args()
    lock = preflight(args.check_environment or args.build)
    if args.build:
        require(args.allow_container_build,
                'Container build needs separate approval and --allow-container-build')
        build(lock)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f'ERROR: {error}')
