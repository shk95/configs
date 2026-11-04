#!/usr/bin/env python3
"""INV unixlike/local-consumer-development: real Nix evaluation and safe orchestration fixtures."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
MODULE = Path(__file__).resolve().parents[1] / 'dev-host/main.py'
spec = importlib.util.spec_from_file_location('dev_host', MODULE)
dev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dev)


def git(root, *args):
    return dev.git(root, *args)


def init(root):
    root.mkdir()
    git(root, 'init', '-q', '-b', 'master')


class DevelopmentTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='consumer-development-')
        self.base = Path(self.temporary.name)
        self.provider = self.base / 'provider'
        self.consumer = self.base / 'consumer'
        init(self.provider)
        init(self.consumer)
        (self.provider / 'unixlike').mkdir()
        (self.provider / 'unixlike/flake.nix').write_text('{ outputs = _: { message = import ./value.nix; }; }')
        (self.provider / 'unixlike/value.nix').write_text('"original"')
        (self.provider / 'unixlike/release.json').write_text('{"version": "1.2.3"}')
        (self.consumer / 'flake.nix').write_text('''{
          inputs.configs.url = "path:''' + str(self.provider / 'unixlike') + '''";
          outputs = { configs, ... }: {
            lib.hostDeclarations.fixture-home.constructor = "mkHome";
            homeConfigurations.fixture-home.activationPackage = builtins.derivation {
              name = configs.message;
              system = "x86_64-linux";
              builder = "/fixture-not-built";
            };
          };
        }''')
        self.adapter_path = self.consumer / 'tool/configs-dev'
        self.adapter_path.parent.mkdir()
        self.adapter_path.write_text('''#!/usr/bin/env python3
import json, sys
if sys.argv[1] == 'protocol': print('1')
elif sys.argv[1] == 'resolve':
 print(json.dumps({'constructor':'mkHome', 'output':'homeConfigurations.fixture-home.activationPackage'}))
''')
        self.adapter_path.chmod(0o755)
        (self.provider / '.gitignore').write_text('*.local\nnotes/\n')
        self.work = dev.Development(self.provider)
        dev.write_json(self.work.connection_file, {'version': 1, 'consumer': str(self.consumer), 'host': 'fixture-home'})
        self.recipe = {'version': 1, 'release': 'unixlike-v1.2.3',
                       'provider_publish': ['fixture-publish-provider'],
                       'consumer_publish': ['fixture-publish-consumer'], 'verify': []}
        dev.write_json(self.work.local / 'recipe.json', self.recipe)

    def tearDown(self):
        self.temporary.cleanup()

    def pair(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return self.work.pair()

    def applied(self):
        pair = self.pair()
        pair.update(package='/nix/store/fixture-package', verified=True, runtime_note='fixture check', verification_recipe=self.recipe)
        dev.write_json(self.work.session_file, pair)
        return pair

    def test_local_state_and_sources(self):
        # Positive: new source is included; ignored local information and notes are excluded.
        (self.provider / 'unixlike/new.nix').write_text('{}')
        (self.provider / 'unixlike/private.local').write_text('fixture private')
        (self.provider / 'notes').mkdir()
        (self.provider / 'notes/scratch').write_text('must not become context')
        pair = self.pair()
        source = Path(pair['provider_source'])
        self.assertTrue((source / 'new.nix').is_file())
        self.assertFalse((source / 'private.local').exists())
        self.assertFalse(any('configs-dev' in n for n in dev.inventory(self.provider)))
        self.assertEqual(Path(git(self.provider, 'rev-parse', '--absolute-git-dir')) / 'configs-dev', self.work.local)
        # Negative: any source change makes existing evidence stale.
        (self.provider / 'unixlike/new.nix').write_text('{ changed = true; }')
        with self.assertRaises(dev.Refused):
            self.work.unchanged(pair)

    def test_linked_checkout_has_independent_connection_state(self):
        git(self.provider, 'add', '.')
        git(self.provider, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '-qm', 'fixture')
        linked = self.base / 'linked-provider'
        git(self.provider, 'worktree', 'add', '-q', '-b', 'fixture-topic', str(linked))
        other = dev.Development(linked)
        self.assertNotEqual(self.work.local, other.local)
        self.assertFalse(other.connection_file.exists())
        self.assertTrue(self.work.connection_file.exists())

    def test_symlinks_and_snapshot_tampering(self):
        pair = self.pair()
        (Path(pair['provider_source']) / 'value.nix').write_text('"tampered"')
        with self.assertRaises(dev.Refused):
            self.work.unchanged(pair)
        (self.provider / 'unixlike/link').symlink_to('/fixture-private')
        with self.assertRaises(dev.Refused):
            self.pair()

    def test_real_nix_override_preserves_pin_and_lock(self):
        if not shutil.which('nix'):
            self.skipTest('Nix unavailable; real evaluation not verified')
        dev.run(['nix', 'flake', 'lock', f'path:{self.consumer}'])
        before = {name: (self.consumer / name).read_bytes() for name in ('flake.nix', 'flake.lock')}
        (self.provider / 'unixlike/value.nix').write_text('"candidate"')
        with contextlib.redirect_stdout(io.StringIO()):
            candidate = self.work.evaluate(self.work.pair())
            pinned = self.work.evaluate(self.work.pair(pinned=True))
        self.assertNotEqual(candidate, pinned)
        self.assertEqual(before, {name: (self.consumer / name).read_bytes() for name in before})

    def test_real_nix_build_reads_cli_output_without_result_link(self):
        if not shutil.which('nix'):
            self.skipTest('Nix unavailable; real fixture build not verified')
        flake = self.consumer / 'flake.nix'
        text = flake.read_text().replace('builder = "/fixture-not-built";', '''builder = "builtin:fetchurl";
              url = "file://${builtins.toFile "fixture-data" "fixture payload"}";
              outputHash = builtins.hashString "sha256" "fixture payload";
              outputHashAlgo = "sha256";
              outputHashMode = "flat";''')
        flake.write_text(text)
        with contextlib.redirect_stdout(io.StringIO()):
            package = self.work.build(self.pair())
        self.assertTrue(package.startswith('/nix/store/'))
        self.assertEqual(Path(package).read_text(), 'fixture payload')
        self.assertFalse((self.consumer / 'result').exists())
        self.assertFalse((self.consumer / 'flake.lock').exists())

    def test_failed_apply_invalidates_prior_evidence(self):
        self.applied()
        with patch.object(self.work, 'build', return_value='/nix/store/fixture-package'), \
             patch.object(self.work, 'adapter', side_effect=[json.dumps({'constructor': 'mkHome', 'output': 'fixture'}), dev.Refused('activation failed')]):
            with self.assertRaises(dev.Refused):
                self.work.apply()
        self.assertFalse(self.work.session_file.exists())

    def test_verify_requires_active_package_and_runtime_note(self):
        self.applied()
        with patch.object(self.work, 'adapter', side_effect=dev.Refused('wrong active package')):
            with self.assertRaises(dev.Refused):
                self.work.verify('functional checks')
        self.assertFalse(dev.read_json(self.work.session_file)['verified'])
        with patch.object(self.work, 'adapter', return_value=''):
            with self.assertRaises(dev.Refused):
                self.work.verify('')
            self.work.verify('fixture functionality confirmed')
        self.assertTrue(dev.read_json(self.work.session_file)['verified'])

    def test_plan_is_read_only_and_recipe_change_refuses(self):
        self.applied()
        with patch.object(dev, 'run', wraps=dev.run) as commands, contextlib.redirect_stdout(io.StringIO()):
            self.work.promote()
        self.assertFalse(any(call.args[0][0] in ('fixture-publish-provider', 'fixture-publish-consumer') for call in commands.call_args_list))
        changed = {**self.recipe, 'verify': ['another-check']}
        dev.write_json(self.work.local / 'recipe.json', changed)
        with self.assertRaises(dev.Refused):
            self.work.promote(True)

    def test_promotion_closure_mismatch_stops_before_publish_or_apply(self):
        self.applied()
        with contextlib.redirect_stdout(io.StringIO()):
            self.work.promote()
        commands = []
        pinned_pair = {**self.pair(), 'pinned': True}
        actual_run = dev.run

        def command(argv, **kwargs):
            if argv[0] == 'git':
                return actual_run(argv, **kwargs)
            commands.append(argv)
            return ''

        with patch.object(dev, 'run', side_effect=command), \
             patch.object(self.work, 'release_source', return_value='a' * 40), \
             patch.object(self.work, 'adapter', return_value=''), \
             patch.object(self.work, 'pair', return_value=pinned_pair), \
             patch.object(self.work, 'evaluate', return_value='fixture.drv'), \
             patch.object(self.work, 'build', return_value='/nix/store/different-package'):
            with self.assertRaisesRegex(dev.Refused, 'differs from the tested closure'):
                self.work.promote(True)
        self.assertFalse(any(c[0] == 'fixture-publish-consumer' for c in commands))
        plan = dev.read_json(self.work.promotion_file)
        self.assertEqual(plan['completed'], ['provider-check', 'provider-publish', 'consumer-adopt'])
        with self.assertRaises(dev.Refused):
            self.work.guard_promotion()

    def test_partial_adoption_resumes_without_republishing_provider(self):
        self.applied()
        with contextlib.redirect_stdout(io.StringIO()):
            self.work.promote()
        pair = self.pair()
        calls = []

        def adapter(consumer, action, *args, **kwargs):
            calls.append(action)
            if action == 'adopt':
                (self.consumer / 'flake.lock').write_text('fixture partial adoption')
                raise dev.Refused('fixture network failure')
            return ''

        actual_run = dev.run
        fake_run = lambda argv, **kw: actual_run(argv, **kw) if argv[0] == 'git' else ''
        with patch.object(dev, 'run', side_effect=fake_run), \
             patch.object(self.work, 'release_source', return_value='a' * 40), \
             patch.object(self.work, 'adapter', side_effect=adapter):
            with self.assertRaisesRegex(dev.Refused, 'network failure'):
                self.work.promote(True)
        plan = dev.read_json(self.work.promotion_file)
        self.assertEqual(plan['completed'], ['provider-check', 'provider-publish'])
        self.assertNotEqual(plan['consumer_after_adopt'], pair['consumer_id'])
        calls.clear()
        commands = []
        with patch.object(dev, 'run', side_effect=lambda args, **kw: actual_run(args, **kw) if args[0] == 'git' else commands.append(args) or ''), \
             patch.object(self.work, 'release_source', return_value='a' * 40), \
             patch.object(self.work, 'adapter', side_effect=adapter):
            with self.assertRaisesRegex(dev.Refused, 'network failure'):
                self.work.promote(True)
        self.assertIn('adopt', calls)
        self.assertFalse(any(c[0] == 'fixture-publish-provider' for c in commands))

    def test_complete_promotion_and_retry_do_not_repeat_publication_or_apply(self):
        # Source-only commits in disposable fixtures; no real repository publication.
        git(self.consumer, 'add', '.')
        git(self.consumer, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '-qm', 'fixture')
        self.applied()
        with contextlib.redirect_stdout(io.StringIO()):
            self.work.promote()
        pinned = {**self.pair(), 'pinned': True}
        actual_run = dev.run
        commands = []
        actions = []

        def command(argv, **kwargs):
            if argv[0] == 'git':
                if 'ls-remote' in argv:
                    return git(self.consumer, 'rev-parse', 'HEAD') + '\trefs/heads/master'
                return actual_run(argv, **kwargs)
            commands.append(argv)
            return ''

        def adapter(consumer, action, *args, **kwargs):
            actions.append(action)
            return ''

        with patch.object(dev, 'run', side_effect=command), \
             patch.object(self.work, 'release_source', return_value='a' * 40), \
             patch.object(self.work, 'adapter', side_effect=adapter), \
             patch.object(self.work, 'pair', return_value=pinned), \
             patch.object(self.work, 'evaluate', return_value='fixture.drv'), \
             patch.object(self.work, 'build', return_value='/nix/store/fixture-package'):
            self.work.promote(True)
            self.work.promote(True)
        self.assertEqual(sum(c[0] == 'fixture-publish-provider' for c in commands), 1)
        self.assertEqual(sum(c[0] == 'fixture-publish-consumer' for c in commands), 1)
        self.assertEqual(actions.count('apply'), 1)
        journal = dev.read_json(self.work.promotion_file)
        self.assertEqual(journal['completed'], journal['steps'])

    def test_release_content_must_match_tested_snapshot(self):
        pair = self.applied()
        git(self.provider, 'add', '.')
        git(self.provider, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '-qm', 'fixture')
        tag = self.recipe['release']
        git(self.provider, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
            'tag', '-am', 'synthetic release fixture', tag)
        actual_run = dev.run
        head = git(self.provider, 'rev-parse', 'HEAD')

        def command(argv, **kwargs):
            if argv[0] == 'git':
                if 'ls-remote' in argv:
                    return head + '\trefs/tags/' + tag + '^{}'
                return actual_run(argv, **kwargs)
            return ''  # The repository audit itself has its own fixtures.

        with patch.object(dev, 'run', side_effect=command):
            self.assertEqual(self.work.release_source(pair, self.recipe), head)
            with self.assertRaisesRegex(dev.Refused, 'differs from the tested provider'):
                self.work.release_source({**pair, 'provider_id': 'different'}, self.recipe)

    def test_recipe_rejects_shell_strings(self):
        self.assertEqual(dev.validate_recipe(self.recipe), self.recipe)
        with self.assertRaises(dev.Refused):
            dev.validate_recipe({**self.recipe, 'provider_publish': 'fixture; unintended'})


if __name__ == '__main__':
    unittest.main()
