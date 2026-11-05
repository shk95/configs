#!/usr/bin/env python3
"""INV unixlike/local-consumer-development: subprocess-only bidirectional fixtures.

Real Git/Nix/local remotes; synthetic activation and synthetic release audit.
No private consumer, privileged command or network publication is used.
"""
import json
import fcntl
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1] / 'dev-host'


def run(argv, cwd, env=None):
    return subprocess.check_output([str(v) for v in argv], cwd=cwd, env=env, text=True).strip()


def write(path, content, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    if executable:
        path.chmod(0o755)


class BidirectionalTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='configs-dev-integration-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.provider = self.base / 'provider'
        self.consumer = self.base / 'consumer'
        self.env = {**os.environ, 'FIXTURE_RUNTIME': str(self.base / 'active'), 'FIXTURE_PROVIDER': str(self.provider),
                    'GIT_AUTHOR_NAME': 'Fixture', 'GIT_COMMITTER_NAME': 'Fixture',
                    'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
                    'GIT_COMMITTER_EMAIL': 'fixture@example.invalid'}
        for root in (self.provider, self.consumer):
            root.mkdir()
            run(['git', 'init', '-q', '-b', 'master'], root)
            remote = self.base / (root.name + '.git')
            run(['git', 'init', '--bare', '-q', '-b', 'master', remote], self.base)
            run(['git', 'remote', 'add', 'origin', remote], root)
        for name in ('main.py', 'run'):
            target = self.provider / 'unixlike/tool/dev-host' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / name, target)
        write(self.provider / 'unixlike/flake.nix',
              '{ outputs = _: { shared = import ./shared.nix; }; }')
        write(self.provider / 'unixlike/shared.nix', '"baseline"')
        write(self.provider / 'unixlike/release.json', '{"version":"1.2.3"}')
        write(self.provider / 'Justfile', 'check:\n    python3 -m json.tool unixlike/release.json > /dev/null\n')
        # A protocol fixture audit, not evidence for the production policy audit.
        write(self.provider / 'tool/configs', """#!/usr/bin/env python3
import subprocess, sys
assert sys.argv[1:3] == ['audit', '--tag']
assert subprocess.check_output(['git', 'cat-file', '-t', sys.argv[3]], text=True).strip() == 'tag'
subprocess.run(['git', 'merge-base', '--is-ancestor', sys.argv[3], 'master'], check=True)
""", True)
        write(self.consumer / 'flake.nix', '''{
  inputs.configs.url = "path:''' + str(self.provider / 'unixlike') + '''";
  outputs = { configs, ... }: let
    value = import ./setting.nix configs;
  in {
    lib.hostDeclarations.fixture-home.constructor = "mkHome";
    homeConfigurations.fixture-home.activationPackage = builtins.derivation {
      name = "configs-development-integration";
      system = builtins.currentSystem or "x86_64-linux";
      builder = "builtin:fetchurl";
      url = "file://${builtins.toFile "fixture-value" value}";
      outputHash = builtins.hashString "sha256" value;
      outputHashAlgo = "sha256";
      outputHashMode = "flat";
    };
  };
}''')
        write(self.consumer / 'setting.nix', 'configs: configs.shared')
        write(self.consumer / 'tool/configs-dev', """#!/usr/bin/env python3
import json, os
from pathlib import Path
import subprocess, sys
args = sys.argv[2:]
def flag(name): return args[args.index(name) + 1]
operation = sys.argv[1]
active = Path(os.environ['FIXTURE_RUNTIME'])
if operation == 'protocol': print('1')
elif operation == 'resolve':
    print(json.dumps({'constructor':'mkHome', 'output':'homeConfigurations.fixture-home.activationPackage'}))
elif operation == 'apply': active.write_text(flag('--package'))
elif operation == 'verify': assert active.read_text() == flag('--package')
elif operation == 'adopt':
    source = flag('--source')
    provider = os.environ['FIXTURE_PROVIDER']
    tag = flag('--release')
    assert subprocess.check_output(['git', '-C', provider, 'rev-parse', tag + '^{}'], text=True).strip() == source
    flake = Path('flake.nix')
    import re
    flake.write_text(re.sub(r'inputs.configs.url = "[^"]+";',
        'inputs.configs.url = "git+file://' + provider + '?rev=' + source + '&dir=unixlike";', flake.read_text()))
    subprocess.run(['nix', 'flake', 'update', 'configs'], check=True)
else: raise SystemExit('unknown operation')
""", True)
        write(self.base / 'publish.py', """import os, subprocess, sys
from pathlib import Path
def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()
git('add', '.')
if git('status', '--porcelain'): git('commit', '-qm', 'accept tested fixture')
if sys.argv[1] == 'provider':
    tag = os.environ['CONFIGS_DEV_RELEASE']
    git('tag', '-am', 'synthetic integration release', tag)
    git('push', 'origin', 'master', tag)
else: git('push', 'origin', 'master')
with Path(os.environ['FIXTURE_RUNTIME'] + '.publications').open('a') as log:
    log.write(sys.argv[1] + '\\n')
""")
        for root in (self.provider, self.consumer):
            run(['git', 'add', '.'], root)
            run(['git', 'commit', '-qm', 'baseline fixture'], root, self.env)
            run(['git', 'push', '-q', 'origin', 'master'], root, self.env)
        run(['nix', 'flake', 'lock'], self.consumer, self.env)
        run(['git', 'add', 'flake.lock'], self.consumer)
        run(['git', 'commit', '-qm', 'pin fixture baseline'], self.consumer, self.env)
        self.command('connect', self.consumer, 'fixture-home')
        self.pins = [(self.consumer / p).read_bytes() for p in ('flake.nix', 'flake.lock')]

    def command(self, *args, success=True):
        argv = [self.provider / 'unixlike/tool/dev-host/run', *args]
        if success:
            return run(argv, self.provider, self.env)
        result = subprocess.run([str(v) for v in argv], cwd=self.provider,
                                env=self.env, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return result.stderr

    def receipt(self):
        return json.loads((self.provider / '.git/configs-dev/session.json').read_text())

    def apply_and_verify(self, value):
        self.command('eval')
        self.command('apply')
        receipt = self.receipt()
        self.assertEqual(Path(receipt['package']).read_text(), value)
        self.assertEqual((self.base / 'active').read_text(), receipt['package'])
        self.command('verify', '--note', 'Automatically checked exact fixture payload: ' + value)
        self.assertTrue(self.receipt()['verified'])
        self.assertEqual(self.pins, [(self.consumer / p).read_bytes() for p in ('flake.nix', 'flake.lock')])
        return receipt['package']

    def promote(self, package):
        recipe = self.base / 'recipe.json'
        recipe.write_text(json.dumps({'version':1, 'release':'unixlike-v1.2.3',
            'provider_publish':[sys.executable, str(self.base / 'publish.py'), 'provider'],
            'consumer_publish':[sys.executable, str(self.base / 'publish.py'), 'consumer'],
            'verify':[]}))
        self.command('configure', recipe)
        self.command('verify', '--note', 'Exact fixture payload checked automatically')
        heads = [run(['git', 'rev-parse', 'HEAD'], p) for p in (self.provider, self.consumer)]
        self.command('promote', '--plan')
        self.assertEqual(heads, [run(['git', 'rev-parse', 'HEAD'], p) for p in (self.provider, self.consumer)])
        self.command('promote', '--execute')
        self.command('promote', '--execute')
        receipt = self.receipt()
        self.assertTrue(receipt['pinned'])
        self.assertEqual(receipt['package'], package)
        self.assertEqual((self.base / 'active').read_text(), package)
        self.assertEqual((self.base / 'active.publications').read_text().splitlines(), ['provider', 'consumer'])
        for root in (self.provider, self.consumer):
            self.assertEqual(run(['git', 'status', '--porcelain'], root), '')
            self.assertEqual(run(['git', 'rev-parse', 'HEAD'], root),
                             run(['git', 'ls-remote', 'origin', 'refs/heads/master'], root).split()[0])

    def test_configs_to_hosts_live_change_then_exact_pinned_promotion(self):
        write(self.provider / 'unixlike/shared.nix', '"provider-candidate"')
        package = self.apply_and_verify('provider-candidate')
        write(self.provider / 'unixlike/shared.nix', '"different"')
        self.assertIn('Provider source changed', self.command('verify', '--note', 'stale', success=False))
        write(self.provider / 'unixlike/shared.nix', '"provider-candidate"')
        self.promote(package)

    def test_hosts_to_configs_extraction_then_exact_pinned_promotion(self):
        write(self.consumer / 'setting.nix', 'configs: "host-owned-candidate"')
        before = self.apply_and_verify('host-owned-candidate')
        write(self.provider / 'unixlike/shared.nix', '"host-owned-candidate"')
        write(self.consumer / 'setting.nix', 'configs: configs.shared')
        self.assertIn('source changed', self.command('verify', '--note', 'stale', success=False))
        after = self.apply_and_verify('host-owned-candidate')
        self.assertEqual(before, after, 'Extraction must preserve the built output')
        self.promote(after)


class ReadOnlyInfoTest(unittest.TestCase):
    """Real CLI/Git/locks; queries need neither Nix nor an adapter invocation."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='configs-dev-info-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.provider = self.base / 'provider'
        self.provider.mkdir()
        self.env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
                        GIT_AUTHOR_NAME='Fixture', GIT_COMMITTER_NAME='Fixture',
                        GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_EMAIL='fixture@example.invalid')
        run(['git', 'init', '-q', '-b', 'master'], self.provider, self.env)
        for name in ('main.py', 'run'):
            target = self.provider / 'unixlike/tool/dev-host' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / name, target)
        write(self.provider / 'tracked', 'same bytes')
        run(['git', 'add', '.'], self.provider, self.env)
        run(['git', 'commit', '-qm', 'fixture'], self.provider, self.env)
        self.local = self.provider / '.git/configs-dev'
        # Force a stat-cache refresh opportunity without changing source bytes.
        path = self.provider / 'tracked'
        os.utime(path, (1, 1))

    def command(self, *args, success=True):
        argv = [self.provider / 'unixlike/tool/dev-host/run', *args]
        result = subprocess.run([str(v) for v in argv], cwd=self.provider, env=self.env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return json.loads(result.stdout) if success and args == ('info',) else result

    def snapshot(self, root=None):
        root = root or self.provider
        return {str(path.relative_to(root)): (path.stat().st_mode, None if path.is_dir() else path.read_bytes())
                for path in root.rglob('*')}

    def connection(self):
        consumer = self.base / 'consumer'
        consumer.mkdir()
        run(['git', 'init', '-q', '-b', 'master'], consumer, self.env)
        write(consumer / 'tracked', 'consumer')
        write(consumer / 'tool/configs-dev', "#!/bin/sh\ncase $1 in protocol) echo 1 ;; resolve) echo '{}' ;; *) exit 1 ;; esac\n", True)
        run(['git', 'add', '.'], consumer, self.env)
        run(['git', 'commit', '-qm', 'fixture consumer'], consumer, self.env)
        self.command('connect', consumer, 'fixture-home')
        # Query must not invoke the adapter, even when a connection exists.
        write(consumer / 'tool/configs-dev', '#!/bin/sh\nexit 99\n', True)
        return consumer

    def test_uninitialized_info_creates_nothing_and_does_not_refresh_index(self):
        before = self.snapshot()
        value = self.command('info')
        self.assertEqual(value['schema'], 1)
        self.assertEqual(value['state'], 'uninitialized')
        self.assertEqual(value['coordination'], 'no-records-observed')
        self.assertIsNone(value['connection'])
        self.assertIsNone(value['consumer_head'])
        self.assertFalse(self.local.exists())
        self.assertEqual(self.snapshot(), before)

    def test_info_works_without_nix_or_consumer_adapter(self):
        tools = self.base / 'query-bin'
        tools.mkdir()
        for name, binary in (('python3', sys.executable), ('git', shutil.which('git')),
                             ('dirname', shutil.which('dirname'))):
            (tools / name).symlink_to(Path(binary).resolve())
        self.env['PATH'] = str(tools)
        before = self.snapshot()
        self.assertEqual(self.command('info')['state'], 'uninitialized')
        self.assertEqual(self.snapshot(), before)

    def test_connected_and_disconnected_info_preserve_all_bytes(self):
        consumer = self.connection()
        before = self.snapshot(), self.snapshot(consumer)
        value = self.command('info')
        self.assertEqual(value['state'], 'connected')
        self.assertEqual(value['coordination'], 'shared-lock')
        self.assertEqual(value['connection']['host'], 'fixture-home')
        self.assertEqual((self.snapshot(), self.snapshot(consumer)), before)
        self.command('disconnect')
        before = self.snapshot()
        self.assertEqual(self.command('info')['state'], 'disconnected')
        self.assertEqual(self.snapshot(), before)

    def test_writer_excludes_info_and_readers_exclude_mutation(self):
        self.connection()
        (self.local / 'lock').write_text('preserved lock contents')
        with (self.local / 'lock').open('r') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            before = self.snapshot()
            result = self.command('info', success=False)
            self.assertIn('Another development operation', result.stderr)
            self.assertEqual(self.snapshot(), before)
        with (self.local / 'lock').open('r') as lock:
            fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
            before = self.snapshot()
            self.assertEqual(self.command('info')['state'], 'connected')
            result = self.command('disconnect', success=False)
            self.assertIn('Another development operation', result.stderr)
            self.assertEqual(self.snapshot(), before)

    def test_unlocked_malformed_or_missing_consumer_state_refuses(self):
        consumer = self.connection()
        path = self.local / 'connection.json'
        valid = path.read_bytes()
        for mode in ('unlocked', 'malformed', 'missing-consumer'):
            path.write_bytes(valid)
            if mode == 'unlocked': (self.local / 'lock').unlink()
            elif mode == 'malformed': path.write_text('{broken')
            else: consumer.rename(self.base / 'moved-consumer')
            before = self.snapshot()
            self.command('info', success=False)
            self.assertEqual(self.snapshot(), before)
            if mode == 'unlocked': (self.local / 'lock').touch()

    def test_invalid_connection_schema_refuses_without_rewriting_records(self):
        self.connection()
        path = self.local / 'connection.json'
        valid = json.loads(path.read_text())
        cases = [{'consumer': valid['consumer']}, {**valid, 'version': 99},
                 {**valid, 'version': True}, {**valid, 'host': '../../invalid'},
                 {**valid, 'host': None}, {**valid, 'consumer': []},
                 {**valid, 'consumer': 'relative'}, {**valid, 'extra': 1}, []]
        for value in cases:
            with self.subTest(record=value):
                path.write_text(json.dumps(value))
                before = self.snapshot()
                self.assertIn('Invalid local consumer connection', self.command('info', success=False).stderr)
                self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
