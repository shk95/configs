#!/usr/bin/env python3
"""Small Git/API fixtures for the finite release boundary; no operating writes.
INV repository/bounded-release-automation
INV repository/release-tag-contract
INV repository/topic-source
INV repository/exact-ci-proof
"""
import importlib.util
import json
import os
import shutil
import shlex
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from ci_test import Evidence
from unittest.mock import patch

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('release', ROOT / 'tool/version-control/release.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
REAL_PUSH = r.push_patch_merge


class LocalGitHub:
    """GitHub transport stand-in with actual objects/refs in a local bare repo.

    Release selection, candidate/check binding, merge verification, publication
    and writer acceptance are production code, not mocked controller results.
    INV repository/bounded-release-automation
    INV repository/release-tag-contract
    """
    def __init__(self):
        self.remote = Path.cwd() / '.git' / 'fixture-origin.git'
        subprocess.check_call(['git', 'init', '--bare', '-q', str(self.remote)])
        self.remote_git('config', 'user.name', 'Fixture')
        self.remote_git('config', 'user.email', 'fixture@example.invalid')
        r.git('remote', 'add', 'origin', str(self.remote))
        r.git('push', '--quiet', 'origin', 'HEAD:refs/heads/dev', 'HEAD:refs/heads/master', '--tags')
        self.prs = []
        self.writes = []
        self.sleeps = 0
        self.proofs = {}
        self.writer_enabled = '0'
        self.active = set()

    def remote_git(self, *args, data=None, env=None):
        return subprocess.check_output(['git', '--git-dir', str(self.remote), *args], input=data, env=env).decode().strip()

    def pr(self, number):
        return next(pr for pr in self.prs if pr['number'] == number)

    def complete_ci(self, _):
        self.sleeps += 1
        for pr in self.prs:
            pr['ready'] = True

    def api(self, path, data=None, binary=False):
        if data is not None:
            self.writes.append(path)
        if path.startswith('git/matching-refs/'):
            prefix = 'refs/' + path.removeprefix('git/matching-refs/')
            lines = self.remote_git('for-each-ref', '--format=%(refname) %(objectname) %(objecttype)', prefix)
            return [{'ref': ref, 'object': {'sha': sha, 'type': kind}} for ref, sha, kind in (line.split() for line in lines.splitlines())]
        if path == 'actions/variables/CONFIGS_RELEASE_ENABLED':
            return {'value': self.writer_enabled}
        if path.startswith('actions/workflows/'):
            workflow, query = path.split('/')[2:]
            status = query.split('status=', 1)[1].split('&', 1)[0]
            return {'workflow_runs': [{'id': 1}] if (workflow, status) in self.active else []}
        if path.startswith('git/ref/heads/'):
            return {'object': {'sha': self.remote_git('rev-parse', 'refs/heads/' + path.removeprefix('git/ref/heads/'))}}
        if path == 'git/blobs':
            return {'sha': self.remote_git('hash-object', '-w', '--stdin', data=data['content'].encode())}
        if path == 'git/trees':
            index = self.remote / 'api-index'
            index.unlink(missing_ok=True)
            env = dict(os.environ, GIT_INDEX_FILE=str(index))
            self.remote_git('read-tree', data['base_tree'], env=env)
            for entry in data['tree']:
                self.remote_git('update-index', '--add', '--cacheinfo', entry['mode'], entry['sha'], entry['path'], env=env)
            result = {'sha': self.remote_git('write-tree', env=env)}
            index.unlink()
            return result
        if path == 'git/commits':
            parents = [arg for parent in data['parents'] for arg in ('-p', parent)]
            return {'sha': self.remote_git('commit-tree', data['tree'], *parents, data=data['message'].encode())}
        if path == 'git/tags':
            tag = f"object {data['object']}\ntype commit\ntag {data['tag']}\ntagger Fixture <fixture@example.invalid> 1 +0000\n\n{data['message']}\n"
            return {'sha': self.remote_git('mktag', data=tag.encode())}
        if path.startswith('git/tags/'):
            header, message = self.remote_git('cat-file', 'tag', path.removeprefix('git/tags/')).split('\n\n', 1)
            fields = dict(line.split(' ', 1) for line in header.splitlines())
            return {'tag': fields['tag'], 'object': {'sha': fields['object'], 'type': fields['type']}, 'message': message}
        if path == 'git/refs':
            self.remote_git('update-ref', data['ref'], data['sha'], '0' * 40)
            return {}
        if path.startswith('pulls?'):
            opened = 'state=open' in path
            base = 'dev' if 'base=dev' in path else 'master'
            return [pr for pr in self.prs if pr['base']['ref'] == base and (pr['merged_at'] is None) == opened]
        if path == 'pulls':
            base, head = (self.remote_git('rev-parse', 'refs/heads/' + data[name]) for name in ('base', 'head'))
            pr = {'number': len(self.prs) + 1, 'head': {'ref': data['head'], 'sha': head, 'repo': {'full_name': 'fixture/configs'}},
                  'base': {'ref': data['base'], 'sha': base}, 'state': 'open', 'merged': False, 'merged_at': None, 'ready': False,
                  'tree': self.remote_git('merge-tree', '--write-tree', base, head).splitlines()[0]}
            pr['body'] = data['body']
            self.prs.append(pr)
            self.proofs[pr['number']] = Evidence(self.remote_git, base, head, pr['tree'], ['unixlike:suite'],
                                                 run_id=pr['number'], pull=pr['number'], event='pull_request')
            return pr
        if path.startswith('pulls/'):
            return self.pr(int(path.split('/')[1]))
        if path.startswith('commits/') and path.endswith('/pulls'):
            source = path.split('/')[1]
            return [pr for pr in self.prs if pr.get('merge_commit_sha') == source]
        if path.startswith('commits/') and '/check-runs?' in path:
            head = path.split('/')[1]
            return {'check_runs': [{'id': pr['number'], 'name': 'Required checks', 'app': {'id': 15368},
                    'conclusion': 'success' if pr['ready'] else None,
                    'details_url': f"https://github.com/fixture/configs/actions/runs/{pr['number']}/job/1"}
                    for pr in self.prs if pr['head']['sha'] == head]}
        if path == 'actions/runs?status=waiting&per_page=100':
            return {'workflow_runs': []}
        if path.startswith(('actions/runs/', 'actions/artifacts/')):
            return self.proofs[int(path.split('/')[2])].read(path, binary)
        if path.startswith('git/commits/'):
            sha = path.split('/')[-1]
            return next(proof.commit for proof in self.proofs.values() if proof.commit['sha'] == sha)
        raise AssertionError(path)

    def push_merge(self, base, source):
        # Use the real Git update and tracked pre-push hook. Only the
        # production HTTPS destination and GitHub PR association are simulated.
        with patch.object(r, 'push_target', return_value=str(self.remote)):
            REAL_PUSH(base, source)
        self.writes.append('push master')
        parents = self.remote_git('show', '-s', '--format=%P', source).split()
        assert self.remote_git('rev-parse', 'refs/heads/master') == source
        pr = next(pr for pr in self.prs if pr['head']['sha'] == parents[1])
        pr.update(state='closed', merged=True, merged_at='fixture', merge_commit_sha=source)


class ReleaseFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = os.getcwd()
        os.chdir(self.tmp.name)
        self.env = patch.dict(os.environ, {'GITHUB_REPOSITORY': 'fixture/configs',
                                          'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'})
        self.env.start()
        self.real_manual_active = r.manual_active
        self.manual = patch.object(r, 'manual_active', return_value=False)
        self.manual.start()
        r.git('init', '-q', '-b', 'master')
        r.git('config', 'user.name', 'Fixture')
        r.git('config', 'user.email', 'fixture@example.invalid')
        r.git('config', 'core.hooksPath', os.devnull)
        self.lock = {'version': 7, 'root': 'root', 'nodes': {'root': {'inputs': {'nixpkgs': 'n', 'manual': 'm', 'alias': ['nixpkgs']}},
                     'n': {'original': {'owner': 'NixOS'}, 'locked': {'owner': 'NixOS', 'rev': 'a'}},
                     'm': {'locked': {'rev': 'b'}}}}
        Path('README.md').write_text('Fixture repository.\n')
        for name in ('.github/workflows/ci.yml', 'tool/dispatch/select', 'tool/version-control/classify',
                     'tool/version-control/closing-keywords'):
            target = Path(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        seed = self.commit('chore(repository): seed fixture')
        for domain in ('unixlike', 'windows'):
            Path(domain).mkdir()
            self.write(domain + '/release.json', {'previous': seed, 'version': '1.0.0', 'summary': 'First release',
                       'compatibility': 'breaking', 'migration': 'Explicit consumer adoption.'})
        for name in ('.githooks/commit-msg', '.githooks/pre-push', '.githooks/evidence',
                     'tool/version-control/scan-secrets', 'tool/version-control/incoming-range.sh',
                     'tool/version-control/audit', 'tool/version-control/hooks.sh'):
            target = Path(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        tools = Path('.git/fixture-bin').resolve()
        tools.mkdir()
        scanner = tools / 'gitleaks'
        scanner.write_text('#!/bin/sh\nif [ "$1" = stdin ]; then cat >/dev/null; fi\n')
        scanner.chmod(0o755)
        os.environ['PATH'] = str(tools) + os.pathsep + os.environ['PATH']
        self.write('unixlike/automatic-refresh-inputs.json', ['nixpkgs'])
        self.commit('feat(repository): initial fixture')
        self.write('unixlike/flake.lock', self.lock)
        self.base = self.commit('chore(unixlike-deps): initial fixture lock')
        annotation = r.annotation_fields('unixlike', self.base, r.declaration(self.base, 'unixlike'))
        self.assertIn('Build: passed; provider-owned artifact checks on CI system', annotation)
        self.assertIn('Native runtime: not applicable; host runtime belongs to consumers', annotation)
        self.assertFalse(any(line.startswith('Native runtime: passed') for line in annotation))
        r.git('tag', '-a', 'unixlike-v1.0.0', '-m', '\n'.join(annotation))
        r.git('tag', '-a', 'windows-v1.0.0', '-m', 'Domain: windows\nHost: windows-ci\nEvaluation: passed; fixture\nBuild: not applicable; desired-state\nNative runtime: passed; fixture')
        self.windows_tag = r.git('rev-parse', 'windows-v1.0.0')
        self.write('unixlike/release.json', {'previous': 'unixlike-v1.0.0', 'version': '1.0.1',
                   'summary': r.REFRESH_SUMMARY, 'compatibility': 'patch', 'migration': ''})
        updated = json.loads(json.dumps(self.lock))
        updated['nodes']['n']['locked']['rev'] = 'c'
        self.write('unixlike/flake.lock', updated)
        self.head = self.commit('chore(unixlike-deps): refresh fixture')
        self.tree = r.git('rev-parse', 'HEAD^{tree}')
        r.git('update-ref', 'refs/remotes/origin/master', self.base)
        r.git('update-ref', 'refs/remotes/origin/dev', self.head)

    def tearDown(self):
        self.manual.stop()
        self.env.stop()
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def write(self, path, value):
        Path(path).write_text(json.dumps(value))

    def commit(self, message):
        r.git('add', '.')
        r.git('commit', '-q', '-m', message)
        return r.git('rev-parse', 'HEAD')

    def test_allowed_patch_and_refusals(self):
        self.assertTrue(r.automatic(self.base, self.head))
        lock = json.loads(json.dumps(self.lock))
        lock['nodes']['m']['locked']['rev'] = 'unauthorized'
        with self.assertRaises(ValueError):
            r.validate_lock(self.lock, lock, {'nixpkgs'})
        lock = json.loads(json.dumps(self.lock))
        lock['nodes']['n']['locked']['owner'] = 'other'
        with self.assertRaises(ValueError):
            r.validate_lock(self.lock, lock, {'nixpkgs'})
        self.write('unixlike/release.json', {'previous': 'unixlike-v1.0.0', 'version': '1.0.0',
                   'summary': 'Same version', 'compatibility': 'patch', 'migration': ''})
        changed = self.commit('docs(unixlike): invalid fixture declaration')
        self.assertFalse(r.automatic(self.base, changed))

    def test_nonselected_dependency_graph_and_follows_are_preserved(self):
        before = json.loads(json.dumps(self.lock))
        before['nodes']['m']['inputs'] = {'lib': 'lib'}
        before['nodes']['lib'] = {'locked': {'rev': 'fixed'}}
        before['nodes']['n']['inputs'] = {'upstream': ['manual']}
        after = json.loads(json.dumps(before))
        after['nodes']['n']['locked']['rev'] = 'permitted'
        r.validate_lock(before, after, {'nixpkgs'})
        after['nodes']['lib']['locked']['rev'] = 'forbidden'
        with self.assertRaises(ValueError):
            r.validate_lock(before, after, {'nixpkgs'})
        after = json.loads(json.dumps(before))
        after['nodes']['n']['inputs']['upstream'] = ['nixpkgs']
        with self.assertRaises(ValueError):
            r.validate_lock(before, after, {'nixpkgs'})
        after = json.loads(json.dumps(before))
        after['nodes']['m']['inputs']['lib'] = 'n'
        with self.assertRaises(ValueError):
            r.validate_lock(before, after, {'nixpkgs'})

    def test_checks_bind_actual_base_head_tree_event(self):
        fixture = Evidence(r.git, self.base, self.head, self.tree, ['unixlike:suite'], pull=5, event='pull_request')
        def fake(path, **kwargs):
            if path.startswith('commits/'):
                return {'check_runs': [{'id': 9, 'name': 'Required checks', 'app': {'id': 15368}, 'conclusion': 'success',
                                       'details_url': 'https://github.com/fixture/configs/actions/runs/7/job/8'}]}
            return fixture.read(path, **kwargs)
        with patch.object(r, 'api', side_effect=fake):
            self.assertTrue(r.checked(self.base, self.head, self.tree, 5))
            self.assertIsNone(r.checked('1' * 40, self.head, self.tree, 5))
            self.assertIsNone(r.checked(self.base, self.head, '2' * 40, 5))
            self.assertIsNone(r.checked(self.base, self.head, self.tree, 6))
            for mapping, change in ((fixture.run, {'event': 'workflow_dispatch'}),
                                    (fixture.commit, {'parents': [{'sha': self.head}]}),
                                    (fixture.jobs['Unix-like provider contract'], {'steps': []})):
                with patch.dict(mapping, change):
                    self.assertIsNone(r.checked(self.base, self.head, self.tree, 5))

    def test_existing_tag_checks_content_not_recreated_object_id(self):
        value = r.declaration(self.head, 'unixlike')
        obj = {'tag': 'unixlike-v1.0.1', 'object': {'type': 'commit', 'sha': self.head},
               'message': '\n'.join(r.annotation_fields('unixlike', self.head, value))}
        def fake(path):
            return [{'ref': 'refs/tags/unixlike-v1.0.1', 'object': {'type': 'tag', 'sha': 'f' * 40}}] if 'matching-refs' in path else obj
        with patch.object(r, 'api', side_effect=fake):
            self.assertEqual(r.tag_state('unixlike', self.head, value), 'done')
            obj['message'] = '\n'.join(line for line in obj['message'].splitlines() if not line.startswith('Build:'))
            with self.assertRaises(ValueError):
                r.tag_state('unixlike', self.head, value)
            obj['object']['sha'] = self.base
            with self.assertRaises(ValueError):
                r.tag_state('unixlike', self.head, value)
        with patch.object(r, 'api', return_value=[]):
            self.assertEqual(r.tag_state('unixlike', self.head, value), 'missing')

    def test_existing_publication_recognizes_legacy_without_writes(self):
        # INV repository/bounded-release-automation
        # INV repository/release-tag-contract
        value = r.declaration(self.head, 'unixlike')
        current = r.annotation_fields('unixlike', self.head, value)
        legacy = [
            'Build: passed; selected matching-system provider fixtures'
            if line.startswith('Build:') else
            'Native runtime: passed; provider CI fixtures'
            if line.startswith('Native runtime:') else line
            for line in current
        ]
        obj = {'tag': 'unixlike-v1.0.1', 'object': {'type': 'commit', 'sha': self.head}}
        ref = {'ref': 'refs/tags/unixlike-v1.0.1', 'object': {'type': 'tag', 'sha': 'f' * 40}}
        def reads(path, *args):
            self.assertFalse(args, 'existing publication must make no writes')
            return [ref] if 'matching-refs' in path else obj
        def source_read(*args):
            self.assertIn(args[0], ('rev-parse', 'merge-base'))
            return self.head if args[0] == 'rev-parse' else ''
        with patch.object(r, 'api', side_effect=reads), patch.object(r, 'git', side_effect=source_read), \
                patch.object(r, 'patch_merge', return_value=True), patch.object(r, 'declaration', return_value=value):
            for form in (current, legacy):
                obj['message'] = '\n'.join(form)
                r.publish(self.head)
            invalid = [
                [line for line in legacy if not line.startswith('Build:')],
                [line.replace('Summary: ', 'Summary: altered ') for line in legacy],
                legacy + ['Build: failed; conflicting evidence'],
                legacy + ['  Build: failed; conflicting evidence'],
                legacy + ['Host: unexpected'],
                legacy + ['  Host: unexpected'],
            ]
            for form in invalid:
                obj['message'] = '\n'.join(form)
                with self.assertRaisesRegex(ValueError, 'conflicting required annotation'):
                    r.publish(self.head)
            obj['message'] = '\n'.join(legacy)
            obj['object']['sha'] = self.base
            with self.assertRaisesRegex(ValueError, 'conflicting remote target'):
                r.publish(self.head)
            obj['object']['sha'] = self.head
            # New-write confirmation retains current exact required fields.
            with self.assertRaisesRegex(ValueError, 'conflicting required annotation'):
                r.tag_state('unixlike', self.head, value)

    def test_new_publication_rejects_legacy_write_confirmation(self):
        # INV repository/bounded-release-automation
        # INV repository/release-tag-contract
        value = r.declaration(self.head, 'unixlike')
        ref = {'ref': 'refs/tags/unixlike-v1.0.1', 'object': {'type': 'tag', 'sha': 'f' * 40}}
        obj = {'tag': 'unixlike-v1.0.1', 'object': {'type': 'commit', 'sha': self.head}}
        published = [False]
        def remote(path, *args):
            if path == 'git/ref/heads/master':
                return {'object': {'sha': self.head}}
            if 'matching-refs' in path:
                return [ref] if published[0] else []
            if path == 'git/tags':
                obj['message'] = args[0]['message'].replace(
                    'Build: passed; provider-owned artifact checks on CI system',
                    'Build: passed; selected matching-system provider fixtures').replace(
                    'Native runtime: not applicable; host runtime belongs to consumers',
                    'Native runtime: passed; provider CI fixtures')
                return {'sha': 'f' * 40}
            if path == 'git/refs':
                published[0] = True
                raise subprocess.CalledProcessError(1, 'fixture ambiguous write')
            if path.startswith('git/tags/'):
                return obj
            if path.endswith('/pulls'):
                return [{'number': 5, 'merged_at': 'fixture', 'base': {'ref': 'master'},
                         'head': {'ref': r.PATCH_BRANCH + 'fixture', 'repo': {'full_name': r.repository()}},
                         'merge_commit_sha': self.head}]
            raise AssertionError(path)
        def source_read(*args):
            if args[0] == 'merge-base': return ''
            if args[0] == 'show': return self.base + ' ' + self.head
            return self.tree if args[-1].endswith('^{tree}') else self.head
        with patch.object(r, 'api', side_effect=remote), patch.object(r, 'git', side_effect=source_read), \
                patch.object(r, 'patch_merge', return_value=True), patch.object(r, 'declaration', return_value=value), \
                patch.object(r, 'checked', return_value={'url': 'https://github.com/fixture/configs/actions/runs/7', 'attempt': 1}):
            with self.assertRaisesRegex(ValueError, 'conflicting required annotation'):
                r.publish(self.head)

    def test_schedule_waits_for_active_manual_run(self):
        with patch.object(r, 'manual_active', return_value=True), patch.object(r, 'api') as remote:
            self.assertEqual(r.inspect(), {'action': 'wait', 'reason': 'manual input patch is active'})
            remote.assert_not_called()
        # Completed/cancelled runs do not strand future scheduled operation.
        with patch.object(r, 'api', return_value={'workflow_runs': []}):
            self.assertFalse(self.real_manual_active())
        with patch.object(r, 'api', side_effect=lambda path: {'workflow_runs': [{'status': 'waiting'}] if 'status=waiting' in path else []}):
            self.assertTrue(self.real_manual_active())

    def test_developer_release_is_a_published_refresh_baseline(self):
        # INV repository/bounded-release-automation
        # INV repository/release-tag-contract
        # A general release records actual evidence; the next input patch still
        # needs its own checked merge and exact generated publication evidence.
        r.git('checkout', '-q', '--detach', self.base)
        remote = LocalGitHub()
        self.write('unixlike/release.json', {'previous': 'unixlike-v1.0.0', 'version': '1.1.0',
                   'summary': 'Developer-owned configuration change.', 'compatibility': 'minor', 'migration': ''})
        Path('unixlike/general-config').write_text('Released configuration.')
        general = self.commit('feat(unixlike): released development')
        lines = r.annotation_fields('unixlike', general, r.declaration(general, 'unixlike'))
        lines = [line.rstrip() for line in lines if not line.startswith(('Evaluation:', 'Build:', 'Native runtime:', 'Evidence:'))]
        lines += ['Evaluation: passed; reviewed PR checks',
                  'Build: passed; matching-system provider fixture',
                  'Native runtime: passed; generated fixture reproduction',
                  'Evidence: https://github.com/fixture/configs/pull/42']
        r.git('tag', '-a', 'unixlike-v1.1.0', '-m', '\n'.join(lines))
        r.git('push', '--quiet', 'origin', 'HEAD:refs/heads/master', '--tags')
        r.git('fetch', '--quiet', 'origin')
        r.git('update-ref', 'refs/heads/master', general)
        subprocess.check_call([str(ROOT / 'tool/version-control/audit'), '--tag', 'unixlike-v1.1.0'], stdout=subprocess.DEVNULL)
        baseline_tag = remote.remote_git('rev-parse', 'unixlike-v1.1.0')
        with patch.dict(os.environ, CONFIGS_RELEASE_ENABLED='1', GH_TOKEN='fixture-only'), patch.object(r, 'api', side_effect=remote.api), patch.object(r, 'push_patch_merge', side_effect=remote.push_merge):
            for manual in (False, True):
                with self.subTest(manual=manual):
                    self.assertEqual(r.inspect(manual=manual, start=True), {'action': 'refresh', 'base': general, 'head': general})
            self.assertEqual(remote.writes, [])
            # plan-release's minimal annotation is also a valid baseline.
            minimal = '\n'.join(line for line in lines if line.startswith(('Domain:', 'Evaluation:', 'Build:', 'Native runtime:', 'Deployment:')))
            original_api = remote.api
            def minimal_tag(path, *args, **kwargs):
                result = original_api(path, *args, **kwargs)
                if path == f'git/tags/{baseline_tag}':
                    return {**result, 'message': minimal}
                return result
            with patch.object(r, 'api', side_effect=minimal_tag):
                self.assertEqual(r.inspect(start=True)['action'], 'refresh')
            lock = json.loads(json.dumps(self.lock))
            lock['nodes']['n']['locked']['rev'] = 'after-development-release'
            self.write('.git/refreshed-lock.json', lock)
            r.refresh_pr(general, '.git/refreshed-lock.json')
            remote.complete_ci(0)
            plan = r.inspect()
            self.assertEqual(plan['action'], 'patch-merge')
            r.advance(plan['head'], plan['base'])
            self.assertEqual(remote.remote_git('rev-parse', 'unixlike-v1.1.0'), baseline_tag)
            self.assertEqual(remote.remote_git('rev-parse', 'windows-v1.0.0'), self.windows_tag)
            source = remote.remote_git('rev-parse', 'master')
            self.assertEqual(remote.remote_git('rev-parse', 'unixlike-v1.1.1^{commit}'), source)
            self.assertEqual(r.tag_state('unixlike', source, r.declaration(source, 'unixlike')), 'done')

    def test_baseline_rejects_invalid_evidence_and_writer_keeps_exact_confirmation(self):
        # INV repository/release-tag-contract
        # INV repository/bounded-release-automation
        value = r.declaration(self.base, 'unixlike')
        message = 'Domain: unixlike\nEvaluation: passed; PR checks\nBuild: unavailable; no matching host\nNative runtime: not applicable; provider only'
        obj = {'tag': 'unixlike-v1.0.0', 'object': {'type': 'commit', 'sha': self.base}, 'message': message}
        ref = {'ref': 'refs/tags/unixlike-v1.0.0', 'object': {'type': 'tag', 'sha': 'f' * 40}}
        with patch.object(r, 'api', side_effect=lambda path: [ref] if 'matching-refs' in path else obj):
            self.assertEqual(r.tag_state('unixlike', self.base, value, generated=False), 'done')
            with self.assertRaisesRegex(ValueError, 'conflicting required annotation'):
                r.tag_state('unixlike', self.base, value)
            invalid = [message.replace('Build: unavailable; no matching host', ''),
                       message.replace('passed; PR checks', 'failed; PR checks'),
                       message.replace('passed; PR checks', 'passed without a separator'),
                       message.replace('Domain: unixlike', 'Domain: windows'),
                       message + '\nBuild: passed; duplicate',
                       message + '\nHost: private-host']
            for annotation in invalid:
                with self.subTest(annotation=annotation):
                    obj['message'] = annotation
                    with self.assertRaisesRegex(ValueError, 'conflicting required annotation'):
                        r.tag_state('unixlike', self.base, value, generated=False)
            obj['message'] = message
            obj['object']['sha'] = self.head
            with self.assertRaisesRegex(ValueError, 'conflicting remote target'):
                r.tag_state('unixlike', self.base, value, generated=False)
            obj['object']['sha'] = self.base
            ref['object']['type'] = 'commit'
            with self.assertRaisesRegex(ValueError, 'remote tag is not annotated'):
                r.tag_state('unixlike', self.base, value, generated=False)

    def test_manual_wait_failure_timeout_and_candidate_change_stop(self):
        waiting = {'action': 'wait', 'base': self.base, 'head': self.head}
        failed = {'id': 1, 'name': 'Required checks', 'app': {'id': 15368}, 'conclusion': 'failure'}
        with patch.object(r, 'write_guard'), patch.object(r, 'inspect', return_value=waiting), patch.object(r, 'advance') as writer, patch.object(r, 'api', return_value={'check_runs': [failed]}):
            with self.assertRaisesRegex(ValueError, 'Required checks failed'):
                r.prepare_manual()
            writer.assert_not_called()
        with patch.object(r, 'write_guard'), patch.object(r, 'inspect', return_value=waiting), patch.object(r, 'api', return_value={'check_runs': []}):
            with self.assertRaisesRegex(ValueError, 'wait expired'):
                r.prepare_manual(timeout=0)
        with patch.object(r, 'write_guard'), patch.object(r, 'inspect', side_effect=[waiting, {**waiting, 'head': 'f' * 40}]), patch.object(r, 'api', return_value={'check_runs': []}), patch.object(r.time, 'sleep'):
            with self.assertRaisesRegex(ValueError, 'candidate changed'):
                r.prepare_manual()
        with patch.object(r, 'write_guard'), patch.object(r, 'inspect', return_value={'action': 'none'}), patch.object(r, 'advance') as writer:
            self.assertEqual(r.prepare_manual(), {'action': 'none'})
            writer.assert_not_called()

    def test_one_call_patch_ignores_dev_and_preserves_windows(self):
        # Actual remote Git objects and CI identity artifacts; only transport fake.
        r.git('checkout', '-q', '--detach', self.base)
        remote = LocalGitHub()
        r.git('checkout', '-q', '-b', 'independent-dev')
        unrelated = Path('docs/reference/unreleased-development.md')
        unrelated.parent.mkdir(parents=True, exist_ok=True)
        unrelated.write_text('Unrelated work stays on dev.')
        dev = self.commit('feat(repository): independent development')
        r.git('push', '--quiet', 'origin', 'HEAD:refs/heads/dev')
        r.git('checkout', '-q', '--detach', self.base)
        lock = json.loads(json.dumps(self.lock))
        lock['nodes']['n']['locked']['rev'] = 'new-upstream'
        self.write('.git/manual-lock.json', lock)
        with patch.dict(os.environ, {'CONFIGS_RELEASE_ENABLED': '1', 'GH_TOKEN': 'fixture-only'}), patch.object(r, 'api', side_effect=remote.api), patch.object(r, 'push_patch_merge', side_effect=remote.push_merge), patch.object(r.time, 'sleep', side_effect=remote.complete_ci):
            r.write_guard()
            start = r.inspect(manual=True, start=True)
            self.assertEqual(start, {'action': 'refresh', 'base': self.base, 'head': self.base})
            r.refresh_pr(start['base'], '.git/manual-lock.json')
            candidate = remote.prs[0]['head']['sha']
            self.assertNotEqual(subprocess.call(['git', 'cat-file', '-e', candidate], stderr=subprocess.DEVNULL), 0)
            self.assertEqual(r.prepare_manual(), {'action': 'none'})
            self.assertEqual(len(remote.prs), 1)
            self.assertEqual(remote.prs[0]['base']['ref'], 'master')
            self.assertTrue(remote.prs[0]['merged'])
            self.assertEqual(remote.remote_git('rev-parse', 'refs/heads/dev'), dev)
            self.assertEqual(remote.remote_git('rev-parse', 'windows-v1.0.0'), self.windows_tag)
            subprocess.check_call([str(ROOT/'tool/version-control/audit'),'--history'],stdout=subprocess.DEVNULL)
            source = remote.remote_git('rev-parse', 'refs/heads/master')
            self.assertEqual(r.git('show', '-s', '--format=%P', source).split(), [self.base, candidate])
            self.assertEqual(remote.remote_git('rev-parse', 'unixlike-v1.0.1^{commit}'), source)
            self.assertEqual(r.tag_state('unixlike', source, r.declaration(source, 'unixlike')), 'done')
            self.assertIn('CI run: https://github.com/fixture/configs/actions/runs/1 (attempt 1)',
                          remote.remote_git('cat-file', 'tag', 'unixlike-v1.0.1'))
            self.assertNotIn(unrelated.as_posix(), r.git('ls-tree', '-r', '--name-only', source).splitlines())
            r.write_guard()
            before = list(remote.writes)
            self.assertEqual(r.refresh_pr(source, '.git/manual-lock.json'), {'action': 'none'})
            self.assertEqual(r.prepare_manual(), {'action': 'none'})
            self.assertEqual(remote.writes, before)
            # CI source admission permits the narrow branch, not arbitrary sources.
            env = dict(os.environ, TOPIC_BASE_REF='master', TOPIC_HEAD_REF=r.PATCH_BRANCH+self.base[:12], TOPIC_BASE_REPOSITORY='fixture/configs', TOPIC_HEAD_REPOSITORY='fixture/configs', TOPIC_BASE_SHA=self.base, TOPIC_HEAD_SHA=candidate)
            subprocess.check_call([str(ROOT/'tool/version-control/topic-source')],env=env,stdout=subprocess.DEVNULL)
            # Dev is retired even after incorporating patch history.
            env.update(TOPIC_HEAD_REF='dev', TOPIC_BASE_SHA=source, TOPIC_HEAD_SHA=dev)
            self.assertNotEqual(subprocess.call([str(ROOT/'tool/version-control/topic-source')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL), 0)
            env.update(TOPIC_HEAD_REF='feature/repository-example')
            subprocess.check_call([str(ROOT/'tool/version-control/topic-source')], env=env, stdout=subprocess.DEVNULL)
            # One more patch increments only the patch component.
            r.git('checkout','-q','--detach',source)
            lock['nodes']['n']['locked']['rev']='second-upstream'
            self.write('.git/manual-lock.json',lock)
            r.refresh_pr(source,'.git/manual-lock.json')
            r.prepare_manual()
            self.assertEqual(remote.remote_git('rev-parse','unixlike-v1.0.2^{commit}'),remote.remote_git('rev-parse','refs/heads/master'))

    def test_stale_and_nonpatch_candidates_refused(self):
        self.assertTrue(r.automatic(self.base,self.head))
        Path('unexpected').write_text('Forbidden payload')
        extra=self.commit('feat(repository): forbidden patch payload')
        self.assertFalse(r.automatic(self.base,extra))
        with patch.dict(os.environ, TOPIC_BASE_REF='master', TOPIC_HEAD_REF=r.PATCH_BRANCH+'fake', TOPIC_BASE_REPOSITORY='fixture/configs', TOPIC_HEAD_REPOSITORY='fixture/configs', TOPIC_BASE_SHA=self.base, TOPIC_HEAD_SHA=extra):
            self.assertNotEqual(subprocess.call([str(ROOT/'tool/version-control/topic-source')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),0)
        with patch.object(r,'inspect',return_value={'action':'patch-merge','base':self.base,'head':self.head}),patch.object(r,'push_patch_merge') as writer:
            with self.assertRaisesRegex(ValueError,'candidate changed'):
                r.advance('f'*40,self.base,manual=True)
            writer.assert_not_called()

    def test_publication_recovery_and_delayed_association(self):
        r.git('checkout','-q','--detach',self.base)
        remote=LocalGitHub()
        lock=json.loads(json.dumps(self.lock));lock['nodes']['n']['locked']['rev']='new'
        self.write('.git/manual-lock.json',lock)
        with patch.dict(os.environ,CONFIGS_RELEASE_ENABLED='1',GH_TOKEN='fixture-only'),patch.object(r,'api',side_effect=remote.api),patch.object(r,'push_patch_merge',side_effect=remote.push_merge),patch.object(r.time,'sleep',side_effect=remote.complete_ci):
            r.write_guard();r.refresh_pr(self.base,'.git/manual-lock.json')
            remote.complete_ci(0);r.write_guard()
            plan=r.inspect(manual=True)
            with patch.object(r,'publish',side_effect=ValueError('interrupted publication')):
                with self.assertRaisesRegex(ValueError,'interrupted'):
                    r.advance(plan['head'],plan['base'],manual=True)
            r.write_guard();recovery=r.inspect(manual=True,start=True)
            self.assertEqual(recovery['action'],'publish')
            lag=[0]
            def delayed(path,*args,**kwargs):
                if path.startswith('commits/') and path.endswith('/pulls') and lag[0]==0:
                    lag[0]+=1;return []
                return remote.api(path,*args,**kwargs)
            with patch.object(r,'api',side_effect=delayed):
                self.assertEqual(r.prepare_manual(),{'action':'none'})
            self.assertEqual(lag[0],1)
            self.assertEqual(len(remote.prs),1)

    def test_master_move_stops_existing_patch_and_old_refresh(self):
        r.git('checkout','-q','--detach',self.base)
        remote=LocalGitHub()
        lock=json.loads(json.dumps(self.lock));lock['nodes']['n']['locked']['rev']='next'
        self.write('.git/manual-lock.json',lock)
        with patch.dict(os.environ,CONFIGS_RELEASE_ENABLED='1',GH_TOKEN='fixture-only'),patch.object(r,'api',side_effect=remote.api),patch.object(r,'push_patch_merge',side_effect=remote.push_merge):
            r.write_guard();r.refresh_pr(self.base,'.git/manual-lock.json')
            Path('accepted-doc').write_text('Master advanced independently.')
            advanced=self.commit('docs(repository): move accepted master')
            r.git('push','--quiet','origin','HEAD:refs/heads/master')
            r.write_guard()
            with self.assertRaisesRegex(ValueError,'stale or unpermitted'):
                r.inspect(manual=True)
            with self.assertRaisesRegex(ValueError,'master base changed'):
                r.refresh_pr(self.base,'.git/manual-lock.json')
            self.assertFalse(remote.prs[0]['merged'])
            self.assertEqual(remote.remote_git('rev-parse','refs/heads/master'),advanced)

    def test_merge_rechecks_live_pr_metadata_and_remote_master(self):
        # INV repository/bounded-release-automation
        r.git('checkout', '-q', '--detach', self.base)
        remote = LocalGitHub()
        lock = json.loads(json.dumps(self.lock))
        lock['nodes']['n']['locked']['rev'] = 'fresh-patch'
        self.write('.git/manual-lock.json', lock)
        with patch.dict(os.environ, CONFIGS_RELEASE_ENABLED='1', GH_TOKEN='fixture-only'), \
                patch.object(r, 'api', side_effect=remote.api), patch.object(r, 'push_patch_merge') as writer:
            r.write_guard()
            pr = r.refresh_pr(self.base, '.git/manual-lock.json')
            remote.complete_ci(0)
            action = r.inspect(manual=True)
            with patch.dict(pr, {'body': 'Fixes #42'}), self.assertRaises(subprocess.CalledProcessError):
                r.advance(action['head'], action['base'], manual=True)
            def changed_master(path, *args, **kwargs):
                if path == 'git/ref/heads/master':
                    return {'object': {'sha': self.head}}
                return remote.api(path, *args, **kwargs)
            with patch.object(r, 'api', side_effect=changed_master), self.assertRaisesRegex(ValueError, 'remote master changed'):
                r.advance(action['head'], action['base'], manual=True)
            writer.assert_not_called()

    def test_exact_push_refuses_a_move_before_and_after_advertisement(self):
        # INV repository/bounded-release-automation
        r.git('checkout', '-q', '--detach', self.base)
        remote = LocalGitHub()
        source = r.git('commit-tree', self.tree, '-p', self.base, '-p', self.head, '-m', 'Merge verified fixture')
        r.git('push', '--quiet', 'origin', f'{self.head}:refs/heads/fixture/patch')
        # The racing value is an ancestor of the merge, so an unrestricted
        # fast-forward push would accept it as the receiver's old base.
        remote.remote_git('update-ref', 'refs/heads/master', self.head, self.base)
        with patch.object(r, 'push_target', return_value=str(remote.remote)):
            with self.assertRaises(subprocess.CalledProcessError):
                REAL_PUSH(self.base, source)
            self.assertEqual(remote.remote_git('rev-parse', 'refs/heads/master'), self.head)

            remote.remote_git('update-ref', 'refs/heads/master', self.base, self.head)
            hook = Path('.githooks/pre-push')
            hook.write_text(hook.read_text() + '\nunset GIT_DIR GIT_WORK_TREE\n' + shlex.join([
                'git', '--git-dir', str(remote.remote), 'update-ref', 'refs/heads/master', self.head, self.base]) + '\n')
            with self.assertRaises(subprocess.CalledProcessError):
                REAL_PUSH(self.base, source)
            self.assertEqual(remote.remote_git('rev-parse', 'refs/heads/master'), self.head)

    def test_upgrade_blocks_legacy_unpublished_patch_behind_governance_commits(self):
        # INV repository/bounded-release-automation
        r.git('checkout', '-q', '--detach', self.base)
        remote = LocalGitHub()
        lock = json.loads(json.dumps(self.lock))
        lock['nodes']['n']['locked']['rev'] = 'legacy-patch'
        self.write('.git/manual-lock.json', lock)
        with patch.object(r, 'api', side_effect=remote.api):
            self.assertTrue(r.upgrade_readiness()['ready'])
            remote.writer_enabled = '1'
            remote.active.add(('release.yml', 'waiting'))
            self.assertEqual(len(r.upgrade_readiness()['blockers']), 2)
            remote.writer_enabled = '0'
            remote.active.clear()
            pr = r.refresh_pr(self.base, '.git/manual-lock.json')
            self.assertIn('still open', r.upgrade_readiness()['blockers'][0])
            r.git('fetch', '--quiet', 'origin', pr['head']['sha'])
            source = r.git('commit-tree', pr['tree'], '-p', self.base, '-p', pr['head']['sha'], '-m', 'Merge legacy patch')
            later = r.git('commit-tree', pr['tree'], '-p', source, '-m', 'docs(repository): later governance')
            remote.push_merge(self.base, source)
            r.git('push', '--quiet', 'origin', f'{later}:refs/heads/master')
            before = list(remote.writes)
            readiness = r.upgrade_readiness()
            self.assertEqual(readiness['master'], later)
            self.assertFalse(readiness['ready'])
            self.assertIn('Complete unixlike-v1.0.1 using accepted pre-upgrade tooling', readiness['blockers'][0])
            self.assertEqual(remote.writes, before)

    def test_unpublished_master_development_cannot_be_relabelled_patch(self):
        r.git('checkout','-q','--detach',self.base)
        Path('unixlike/general-config').write_text('Accepted but not released development.')
        general=self.commit('feat(unixlike): unreleased master development')
        r.git('update-ref','refs/remotes/origin/master',general)
        with patch.object(r,'tag_state',return_value='done'):
            with self.assertRaisesRegex(ValueError,'unpublished Unix-like source'):
                r.inspect(manual=True,start=True)
            lock=json.loads(json.dumps(self.lock));lock['nodes']['n']['locked']['rev']='next'
            self.write('.git/manual-lock.json',lock)
            with patch.object(r,'api') as writer:
                with self.assertRaisesRegex(ValueError,'unpublished Unix-like source'):
                    r.refresh_pr(general,'.git/manual-lock.json')
                writer.assert_not_called()

    def test_tampered_actual_merge_is_not_a_patch(self):
        Path('tampered-merge-content').write_text('Not in the checked patch.')
        altered=self.commit('docs(repository): tampered merge fixture')
        tree=r.git('rev-parse',f'{altered}^{{tree}}')
        source=subprocess.check_output(['git','commit-tree',tree,'-p',self.base,'-p',self.head],input=b'Merge tampered fixture').decode().strip()
        self.assertTrue(r.automatic(self.base,self.head))
        self.assertFalse(r.patch_merge(source))
        r.git('update-ref','refs/remotes/origin/master',source)
        with self.assertRaisesRegex(ValueError,'not a bounded'):
            r.publish(source)
        env=dict(os.environ,TOPIC_BASE_REF='master',TOPIC_HEAD_REF=r.PATCH_BRANCH+'fixture',TOPIC_BASE_REPOSITORY='fixture/configs',TOPIC_HEAD_REPOSITORY='fork/configs',TOPIC_BASE_SHA=self.base,TOPIC_HEAD_SHA=self.head)
        self.assertNotEqual(subprocess.call([str(ROOT/'tool/version-control/topic-source')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),0)

    def test_general_publication_and_promotion_are_not_automated(self):
        r.git('checkout','-q','--detach',self.base)
        remote=LocalGitHub()
        with patch.object(r,'api',side_effect=remote.api):
            self.assertEqual(r.inspect(),{'action':'none'})
            remote.prs.append({'head':{'ref':'dev','repo':{'full_name':'fixture/configs'}},'base':{'ref':'master'},'merged_at':None})
            self.assertEqual(r.inspect()['action'],'wait')
            with self.assertRaisesRegex(ValueError,'master topic PR'):
                r.inspect(manual=True,start=True)
            remote.prs.clear()
            self.write('unixlike/release.json',{'previous':'unixlike-v1.0.0','version':'2.0.0','summary':'General change','compatibility':'breaking','migration':'Review.'})
            general=self.commit('feat(unixlike)!: general development')
            r.git('update-ref','refs/remotes/origin/master',general)
            self.assertEqual(r.inspect()['action'],'wait')
            with self.assertRaisesRegex(ValueError,'not a bounded'):
                r.publish(general)

    def test_lost_pr_create_response_requires_remote_confirmation(self):
        pr={'head':{'ref':r.PATCH_BRANCH+'fixture','repo':{'full_name':'fixture/configs'}}}
        expected = {'expected_base': self.base, 'expected_head': self.head}
        heads = [{'object': {'sha': sha}} for sha in (self.head, self.base)]
        error = subprocess.CalledProcessError(1, 'gh')
        with patch.object(r, 'api', side_effect=[[], *heads, error, [pr]]):
            self.assertEqual(r.ensure_pr(pr['head']['ref'], 'master', 'title', 'body', **expected), pr)
        with patch.object(r, 'api', side_effect=[[], *heads, error, []]):
            with self.assertRaises(ValueError):
                r.ensure_pr(pr['head']['ref'], 'master', 'title', 'body', **expected)

    def test_schedule_steps_and_lost_merge_response(self):
        r.git('checkout','-q','--detach',self.base)
        remote=LocalGitHub()
        lock=json.loads(json.dumps(self.lock));lock['nodes']['n']['locked']['rev']='scheduled'
        self.write('.git/manual-lock.json',lock)
        with patch.dict(os.environ,CONFIGS_RELEASE_ENABLED='1',GH_TOKEN='fixture-only'),patch.object(r,'api',side_effect=remote.api),patch.object(r,'push_patch_merge',side_effect=remote.push_merge):
            r.write_guard()
            start=r.inspect(start=True)
            self.assertEqual(start['head'],self.base)
            r.refresh_pr(start['base'],'.git/manual-lock.json')
            r.write_guard()
            self.assertEqual(r.inspect()['action'],'wait')
            remote.complete_ci(0)
            plan=r.inspect()
            def lost_response(base, source):
                remote.push_merge(base, source)
                raise subprocess.CalledProcessError(1,'gh')
            with patch.object(r,'push_patch_merge',side_effect=lost_response):
                r.advance(plan['head'],plan['base'])
            r.write_guard()
            self.assertEqual(r.inspect(),{'action':'none'})
            self.assertEqual(len(remote.prs),1)
            self.assertEqual(remote.remote_git('rev-parse','windows-v1.0.0'),self.windows_tag)

    def test_branch_creation_resume_and_noop(self):
        r.git('checkout','-q','--detach',self.base)
        remote=LocalGitHub()
        self.write('.git/manual-lock.json',self.lock)
        with patch.object(r,'api',side_effect=remote.api),patch.object(r,'push_patch_merge',side_effect=remote.push_merge):
            self.assertEqual(r.refresh_pr(self.base,'.git/manual-lock.json'),{'action':'none'})
            self.assertEqual(remote.writes,[])
            lock=json.loads(json.dumps(self.lock));lock['nodes']['n']['locked']['rev']='next'
            self.write('.git/manual-lock.json',lock)
            with patch.object(r,'ensure_pr',side_effect=ValueError('interrupted before PR')):
                with self.assertRaises(ValueError):r.refresh_pr(self.base,'.git/manual-lock.json')
            r.refresh_pr(self.base,'.git/manual-lock.json')
            self.assertEqual(len(remote.prs),1)
            self.assertTrue(r.automatic(self.base,remote.prs[0]['head']['sha']))

    def test_credentials_and_shared_workflow_boundary(self):
        with patch.dict(os.environ,CONFIGS_RELEASE_ENABLED='',GH_TOKEN=''):
            with self.assertRaises(ValueError):r.write_guard()
        workflow=(ROOT/'.github/workflows/release.yml').read_text()
        candidate=workflow.split('\n  refresh:\n')[1].split('\n  writer:')[0]
        self.assertNotIn('secrets.',candidate)
        self.assertIn('persist-credentials: false',candidate)
        self.assertNotIn('release-approval',workflow)
        self.assertNotIn('promotion-pr',workflow)
        self.assertNotIn('windows',workflow)
        self.assertIn('CONFIGS_RELEASE_SCHEDULE_ENABLED',workflow)
        self.assertIn('timeout-minutes: 65',workflow)
        manual=(ROOT/'.github/workflows/manual-release.yml').read_text()
        self.assertIn('uses: ./.github/workflows/release.yml',manual)
        self.assertIn('manual: true',manual)
        self.assertNotIn('pull_request_target',workflow+manual)


if __name__ == '__main__':
    unittest.main(verbosity=2)
