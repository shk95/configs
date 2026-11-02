"""Verify complete recovery by importing into an independent disposable store."""
# INV repository/workspace-preservation
# INV repository/approved-history-rewrite
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def _validate_bundle(path, head):
    path = Path(path)
    if path.is_symlink(): raise ValueError('Recovery bundle cannot be a symlink')
    with path.open('rb') as stream:
        if stream.readline() not in (b'# v2 git bundle\n', b'# v3 git bundle\n'):
            raise ValueError('Invalid recovery bundle')
        while True:
            line = stream.readline(65537)
            if not line or len(line) > 65536: raise ValueError('Invalid recovery header')
            if line.startswith(b'-'): raise ValueError('Recovery has missing prerequisites')
            if line == b'\n': break
    # No caller repository/configuration/hooks may redirect disposable writes.
    env = {key: value for key, value in os.environ.items()
           if not key.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_SYSTEM=os.devnull,
               GIT_CONFIG_GLOBAL=os.devnull, GIT_TEMPLATE_DIR='', GIT_ALLOW_PROTOCOL='file')
    with tempfile.TemporaryDirectory(prefix='configs-recovery-') as temporary:
        root = Path(temporary)
        snapshot = root / 'snapshot.bundle'
        shutil.copyfile(path, snapshot)
        store = root / 'objects.git'
        subprocess.check_call(['git', 'init', '-q', '--bare', '-b', 'recovery', str(store)], env=env)
        command = ['git', '--git-dir', str(store)]
        advertised = subprocess.check_output(command + ['bundle', 'unbundle', str(snapshot)], env=env, text=True)
        if not any(line.split(' ', 1)[0] == head for line in advertised.splitlines()):
            raise ValueError('Recovery does not advertise the exact reviewed head')
        subprocess.check_call(command + ['update-ref', 'refs/heads/recovered', head], env=env)
        subprocess.check_call(command + ['symbolic-ref', 'HEAD', 'refs/heads/recovered'], env=env)
        subprocess.check_call(command + ['fsck', '--full', '--strict', '--no-reflogs'], env=env,
                              stdout=subprocess.DEVNULL)
        with snapshot.open('rb') as stream: digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    with path.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != digest:
            raise ValueError('Recovery changed during verification')
    return digest


def validate_bundle(path, head):
    try:
        return _validate_bundle(path, head)
    except subprocess.CalledProcessError as error:
        raise ValueError('Recovery bundle failed independent restoration and integrity verification') from error
