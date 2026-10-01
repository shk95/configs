"""Finite retirement proof; all repositories, readers and originals are synthetic."""
# INV repository/retired-capture-publication
# INV repository/fixture-git-isolation
import itertools
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

SOURCE = Path(__file__).resolve().parents[2]


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def snapshot(root, original):
    # The unreadable case uses mode 000 on POSIX. Do not read its content while
    # protected; its bytes were known before protection and cannot be rewritten
    # without changing the before/after filesystem snapshot or executing a spy.
    result = {}
    common = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip())
    for directory, prefix in ((root, 'tree/'), (common, 'git/')):
        for path in sorted(directory.rglob('*')):
            if path.is_file():
                mode = path.stat().st_mode
                result[prefix + str(path.relative_to(directory))] = (mode, None if path == original and mode & 0o777 == 0 else path.read_bytes())
    return result


def main():
    with tempfile.TemporaryDirectory(prefix='retired-capture-') as temporary:
        base = Path(temporary)
        root = base / 'repo'
        root.mkdir()
        git(root, 'init', '-q', '-b', 'dev')
        git(root, 'config', 'user.name', 'Fixture')
        git(root, 'config', 'user.email', 'fixture@example.invalid')
        for name in ('tool/configs', 'tool/version-control/commit', 'tool/version-control/require-linked-worktree', '.githooks/evidence'):
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / name, destination)
        payload = root / 'unixlike/modules/programs/karabiner/karabiner.json'
        payload.parent.mkdir(parents=True)
        payload.write_bytes(b'{"synthetic":"desired"}\n')
        hotkeys = payload.with_name('symbolic-hotkeys.json')
        hotkeys.write_bytes(b'{"synthetic":"hotkeys"}\n')
        git(root, 'add', '.')
        git(root, 'commit', '-qm', 'synthetic initial state')
        remote = base / 'remote.git'
        subprocess.check_call(['git', 'init', '-q', '--bare', str(remote)])
        git(root, 'remote', 'add', 'origin', str(remote))
        git(root, 'push', '-q', 'origin', 'dev')
        # Normal unknown-group parsing also passes the real linked-worktree gate.
        git(root, 'worktree', 'add', '-q', '-b', 'feature/repository-synthetic', str(base / 'linked'))
        root = base / 'linked'
        payload = root / 'unixlike/modules/programs/karabiner/karabiner.json'
        hotkeys = payload.with_name('symbolic-hotkeys.json')
        spies = base / 'spies'
        spies.mkdir()
        log = base / 'spy.log'
        for command in ('git', 'uname', 'jq', 'defaults', 'plutil', 'nix', 'gh', 'mktemp', 'cat', 'awk'):
            spy = spies / command
            spy.write_text('#!/bin/sh\nprintf "%s\\n" "$0" >>"$RETIREMENT_SPY_LOG"\nexit 97\n')
            spy.chmod(0o755)
        projection = payload.with_name('tool')
        projection.write_text('#!/bin/sh\nprintf "projection\\n" >>"$RETIREMENT_SPY_LOG"\nexit 97\n')
        projection.chmod(0o755)
        environment = dict(os.environ, PATH=str(spies) + os.pathsep + os.environ['PATH'],
                           RETIREMENT_SPY_LOG=log.as_posix(), KARABINER_PLATFORM='darwin')
        expected = ['capture karabiner is retired; no host reads or Git changes were performed.',
                    'Use the pinned host-document preview/review/save workflow in CONTRIBUTING.md.']
        count = 0
        for state in ('matching', 'drift', 'missing', 'unreadable'):
            original = root / 'synthetic-original.json'
            original_hotkeys = root / 'synthetic-hotkeys.json'
            body = payload.read_bytes() if state == 'matching' else b'{"synthetic":"observed"}\n'
            original.write_bytes(body)
            original_hotkeys.write_bytes(hotkeys.read_bytes())
            if state == 'missing':
                original.unlink()
            elif state == 'unreadable':
                original.chmod(0)
            before = snapshot(root, original)
            refs = git(remote, 'show-ref')
            for entry, flags in itertools.product(('internal', 'operator'),
                    ([], ['--dry-run'], ['--publish'], ['--publish', '--dry-run'])):
                for paths in ([], ['--host', str(original)], ['--hotkeys-host', str(original_hotkeys)],
                              ['--host', str(original), '--hotkeys-host', str(original_hotkeys)]):
                    for separator in ([], ['--']):
                        command = root / ('tool/version-control/commit' if entry == 'internal' else 'tool/configs')
                        args = (['commit'] if entry == 'operator' else []) + flags + paths + separator + ['capture', 'karabiner']
                        result = subprocess.run(['sh', command.as_posix(), *args], cwd=root, env=environment,
                                                input=b'y\nyes\n', capture_output=True, timeout=10)
                        assert result.returncode == 1, (state, args, result.stderr)
                        assert result.stdout == b'', result.stdout
                        assert result.stderr.decode().splitlines() == expected, result.stderr
                        assert not log.exists(), 'reader/projection/Git/scratch spy executed'
                        assert snapshot(root, original) == before, 'payload/original/index/HEAD/refs changed'
                        assert git(remote, 'show-ref') == refs, 'remote refs changed'
                        count += 1
            # Also exercise the actual ordinary parser using isolated Git,
            # independently of the early-refusal spies. These arguments stop at
            # help/usage before classification or any edit operation.
            for args, status in ((['--unknown', 'capture', 'karabiner'], 2),
                                 (['capture', 'other'], 2), (['--help'], 0),
                                 (['--host'], 2),
                                 (['--host', str(original), 'brew', 'add', 'example'], 2)):
                before_grammar = snapshot(root, original)
                result = subprocess.run(['sh', (root / 'tool/version-control/commit').as_posix(), *args],
                                        cwd=root, env=os.environ.copy(), capture_output=True, timeout=10)
                assert result.returncode == status, (args, result.returncode, result.stderr)
                assert b'capture karabiner is retired' not in result.stderr
                assert b'usage: tool/configs commit' in result.stdout + result.stderr
                assert snapshot(root, original) == before_grammar
                assert git(remote, 'show-ref') == refs
            if state == 'unreadable':
                original.chmod(0o600)
                assert original.read_bytes() == body, 'protected original bytes changed'
        print(f'retired capture: {count} refusal/no-effect cases and 20 grammar boundary cases passed')
        print('POSIX mode-000 protection is platform-specific; Windows proves refusal before any reader execution.')


if __name__ == '__main__':
    main()
