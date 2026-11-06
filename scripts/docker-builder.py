#!/usr/bin/env python3
"""Prepare/check the Trixie Docker builder. This tool NEVER launches an ISO build."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = 'debian:trixie@sha256:bfc36aecdece0387418759dba474aa856c026ca8087da3606b41b90ab0509c99'
TAG = 'zeros-builder:trixie'


def docker_command(context, *args):
    # Explicit context overrides ambient DOCKER_HOST; only local sockets supported.
    return ['docker', '--context', context, *args]


def environment_command(context, image):
    return docker_command(context, 'run', '--rm', '--read-only', '--user', '65534:65534',
                          '--cap-drop=ALL', '--security-opt=no-new-privileges',
                          '--network=none', '--pids-limit=128', '--memory=512m',
                          '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m',
                          '--mount', f'type=bind,src={ROOT},dst=/src,readonly',
                          image, '--check-environment')


def execute(command, output):
    with output.open('w') as log:
        log.write('$ ' + ' '.join(command) + '\n')
        log.flush()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end='', flush=True)
            log.write(line)
            log.flush()
        code = process.wait()
    if code:
        raise RuntimeError(f'Exit {code}; see {output}')


def capture(context, *args):
    return subprocess.check_output(docker_command(context, *args), text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['host-check', 'prepare', 'check'])
    parser.add_argument('--context', default='default')
    args = parser.parse_args()
    output = Path(tempfile.mkdtemp(prefix='zeros-docker-check-'))
    print(f'Evidence: {output}', flush=True)
    result = {'action': args.action, 'state': 'failed', 'iso_build_started': False}
    try:
        if platform.system() != 'Linux' or platform.machine() not in ('x86_64', 'amd64'):
            raise RuntimeError('Expected Linux amd64 host; host distribution need not be Debian')
        if not shutil.which('docker'):
            raise RuntimeError('Docker CLI missing; no automatic host package installation')
        context = json.loads(capture(args.context, 'context', 'inspect', args.context))[0]
        if not context['Endpoints']['docker']['Host'].startswith('unix://'):
            raise RuntimeError('Only explicit local Unix Docker contexts supported for source binds')
        (output / 'docker-context.json').write_text(json.dumps(context, indent=2) + '\n')
        info = json.loads(capture(args.context, 'info', '--format', '{{json .}}'))
        if info['OSType'] != 'linux' or info['Architecture'] not in ('x86_64', 'amd64'):
            raise RuntimeError('Docker server must be Linux amd64')
        summary = {key: info.get(key) for key in ('OperatingSystem', 'OSType', 'Architecture',
                   'ServerVersion', 'KernelVersion', 'SecurityOptions', 'CgroupVersion', 'Driver')}
        (output / 'docker-info.json').write_text(json.dumps(summary, indent=2) + '\n')
        (output / 'host-os-release').write_text(Path('/etc/os-release').read_text())
        result.update(host_os=platform.system(), docker_os=info['OperatingSystem'], context=args.context)
        if args.action == 'prepare':
            execute(docker_command(args.context, 'build', '--platform', 'linux/amd64',
                                   '--build-arg', 'BASE_IMAGE=' + BASE,
                                   '-f', str(ROOT / 'build/Dockerfile'), '-t', TAG, str(ROOT)),
                    output / 'image-build.log')
        if args.action in ('prepare', 'check'):
            image = json.loads(capture(args.context, 'image', 'inspect', TAG))[0]
            if image['Os'] != 'linux' or image['Architecture'] != 'amd64':
                raise RuntimeError('Builder image must be Linux amd64')
            (output / 'builder-image.json').write_text(json.dumps(image, indent=2) + '\n')
            result['builder_id'] = image['Id']
            # Immutable image ID; no fallback to privileged on failure.
            execute(environment_command(args.context, image['Id']), output / 'environment-check.log')
        result['state'] = 'passed'
    except Exception as error:
        result['error'] = str(error)
        raise
    finally:
        (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
