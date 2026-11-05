"""Exercise the public Just menu in disposable source with inert tool spies."""
# INV unixlike/provider-entry-boundary
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
REFUSALS = ['home-eval', 'home-build', 'home-switch', 'home-bootstrap', 'home-news',
            'darwin-eval', 'darwin-build', 'darwin-check', 'darwin-bootstrap',
            'darwin-switch', 'nixos-eval', 'nixos-build', 'nixos-test',
            'nixos-switch', 'nixos-rollback', 'nixos-generations', 'nixos-tarball']


class JustEntry(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.repo = self.work / 'provider with spaces'
        self.repo.mkdir()
        (self.repo / 'unixlike').mkdir()
        shutil.copyfile(ROOT / 'Justfile', self.repo / 'Justfile')
        self.just = shutil.which('just')
        self.assertIsNotNone(self.just)
        self.bin = self.work / 'bin'
        self.bin.mkdir()
        self.trace = self.work / 'trace.jsonl'
        self.sentinel = self.work / 'argument-executed'
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ['PATH'])
        for name in ['nix', 'sudo', 'nixos-rebuild', 'darwin-rebuild', 'home-manager',
                     'nix-collect-garbage', 'chsh', 'defaults', 'plutil']:
            self.spy(self.bin / name)
        for relative in ['unixlike/tool/dev-host/run', 'unixlike/tool/refresh-inputs',
                         'unixlike/modules/programs/karabiner/tool']:
            self.spy(self.repo / relative)

    def spy(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('#!' + sys.executable + '\nimport json,os,sys\n'
                        'with open(' + repr(str(self.trace)) + ", 'a') as stream:\n"
                        ' stream.write(json.dumps(dict(executable=sys.argv[0], '
                        "argv=sys.argv[1:], cwd=os.getcwd())) + '\\n')\n")
        path.chmod(0o755)

    def invoke(self, *args):
        return subprocess.run([self.just, '--justfile', str(self.repo / 'Justfile'), *args],
                              cwd=self.work, env=self.env, text=True, capture_output=True,
                              timeout=10)

    def calls(self):
        return [json.loads(line) for line in self.trace.read_text().splitlines()] if self.trace.exists() else []

    def snapshot(self):
        return {str(path.relative_to(self.repo)): (path.stat().st_mode,
                None if path.is_dir() else path.read_bytes())
                for path in self.repo.rglob('*')}

    def test_menu_distinguishes_work_and_preserves_compatibility_aliases(self):
        result = self.invoke('--dump', '--dump-format', 'json')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        expected = {'check': 'provider-verification', 'dev-info': 'consumer-development',
                    'up': 'provider-inputs', 'upp': 'provider-inputs', 'fmt': 'source-formatting',
                    'home-generations': 'host-observation', 'darwin-generations': 'host-observation',
                    'karabiner-check': 'host-observation', 'gc': 'host-maintenance',
                    'switch-shell': 'host-maintenance', 'nixos-stage': 'host-transfer'}
        expected.update({name: 'compatibility' for name in REFUSALS})
        for name, group in expected.items():
            self.assertIn({'group': group}, data['recipes'][name]['attributes'])
        self.assertEqual({name: value['target'] for name, value in data['aliases'].items()},
                         dict(bootstrap='home-bootstrap', build='home-build',
                              generations='home-generations', news='home-news', switch='home-switch'))
        self.assertEqual(self.calls(), [])

    def test_named_refresh_and_format_bind_the_domain_flake(self):
        before = self.snapshot()
        result = self.invoke('upp', 'nixpkgs')
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.invoke('fmt')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls()
        self.assertEqual(calls[0]['argv'], ['flake', 'update', 'nixpkgs', '--flake',
                                          str(self.repo / 'unixlike')])
        self.assertEqual(calls[1]['argv'], ['fmt', '.'])
        self.assertEqual(calls[1]['cwd'], str(self.repo / 'unixlike'))
        self.assertEqual(self.snapshot(), before)

    def test_named_refresh_does_not_evaluate_input_text_or_accept_options(self):
        attacks = ['; touch ' + str(self.sentinel), '$(touch ' + str(self.sentinel) + ')',
                   '`touch ' + str(self.sentinel) + '`', 'input with spaces']
        for text in attacks:
            result = self.invoke('upp', text)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.calls()[-1]['argv'][2], text)
            self.assertFalse(self.sentinel.exists())
        count = len(self.calls())
        for text in ['', '--all', '--help']:
            self.assertNotEqual(self.invoke('upp', text).returncode, 0)
        self.assertEqual(len(self.calls()), count)

    def test_compatibility_routes_refuse_before_any_host_tool_or_source_change(self):
        before = self.snapshot()
        for name in [*REFUSALS, 'bootstrap', 'build', 'news', 'switch',
                     '_home-target', '_darwin-target', '_nixos-target', '_nixos-host']:
            args = [name]
            if name in ['nixos-eval', 'nixos-build', 'nixos-tarball', '_nixos-target']:
                args.append('$(touch ' + str(self.sentinel) + ')')
            result = self.invoke(*args)
            self.assertNotEqual(result.returncode, 0, (name, result.stdout, result.stderr))
            self.assertIn('synthetic fixtures only', result.stderr, (name, result.stderr))
            self.assertEqual(self.calls(), [], name)
            self.assertFalse(self.sentinel.exists())
            self.assertEqual(self.snapshot(), before)

    def test_active_local_routes_still_delegate(self):
        for args in [('home-generations',), ('darwin-generations',), ('generations',),
                     ('karabiner-check',), ('dev-info',), ('up',), ('gc',)]:
            result = self.invoke(*args)
            self.assertEqual(result.returncode, 0, (args, result.stderr))
        self.assertEqual([Path(call['executable']).name for call in self.calls()],
                         ['home-manager', 'darwin-rebuild', 'home-manager', 'tool',
                          'run', 'refresh-inputs', 'nix-collect-garbage'])


if __name__ == '__main__':
    unittest.main()
