#!/usr/bin/env python3
"""Small Git/API fixtures for the finite release boundary; no operating writes.
INV repository/bounded-release-automation
INV repository/release-tag-contract
"""
import datetime as dt
import importlib.util
import io
import json
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('release', ROOT / 'tool/version-control/release.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def archive(record):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as stream:
        stream.writestr('source.json', json.dumps(record))
    return output.getvalue()


class ReleaseFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = os.getcwd()
        os.chdir(self.tmp.name)
        self.env = patch.dict(os.environ, {'GITHUB_REPOSITORY': 'fixture/configs', 'CONFIGS_RELEASE_BOOTSTRAP_SOURCE': '',
                                          'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'})
        self.env.start()
        r.git('init', '-q', '-b', 'master')
        r.git('config', 'user.name', 'Fixture')
        r.git('config', 'user.email', 'fixture@example.invalid')
        r.git('config', 'core.hooksPath', os.devnull)
        self.lock = {'version': 7, 'root': 'root', 'nodes': {'root': {'inputs': {'nixpkgs': 'n', 'manual': 'm', 'alias': ['nixpkgs']}},
                     'n': {'original': {'owner': 'NixOS'}, 'locked': {'owner': 'NixOS', 'rev': 'a'}},
                     'm': {'locked': {'rev': 'b'}}}}
        Path('README.md').write_text('Fixture repository.\n')
        seed = self.commit('chore(repository): seed fixture')
        for domain in r.DOMAINS:
            Path(domain).mkdir()
            self.write(domain + '/release.json', {'previous': seed, 'version': '1.0.0', 'summary': 'First release',
                       'compatibility': 'breaking', 'migration': 'Explicit consumer adoption.'})
        Path('.githooks').mkdir()
        shutil.copy(ROOT / '.githooks/commit-msg', '.githooks/commit-msg')
        self.write('unixlike/automatic-refresh-inputs.json', ['nixpkgs'])
        self.commit('feat(repository): initial fixture')
        self.write('unixlike/flake.lock', self.lock)
        self.base = self.commit('chore(unixlike-deps): initial fixture lock')
        for domain in r.DOMAINS:
            r.git('tag', '-a', domain + '-v1.0.0', '-m', '\n'.join(r.annotation_fields(domain, self.base, r.declaration(self.base, domain))))
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
        self.assertEqual(r.validate_versions(self.base, self.head), ['unixlike'])
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
        with self.assertRaises(ValueError):
            r.validate_versions(self.base, changed)
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
        record = {'base': self.base, 'head': self.head, 'tree': self.tree, 'event': 'pull_request'}
        def fake(path, **kwargs):
            if path.startswith('commits/'):
                return {'check_runs': [{'id': 9, 'name': 'Required checks', 'app': {'id': 15368}, 'conclusion': 'success',
                                       'details_url': 'https://github.com/fixture/configs/actions/runs/7/job/8'}]}
            if path == 'actions/runs/7':
                return {'path': '.github/workflows/ci.yml', 'event': 'pull_request', 'conclusion': 'success'}
            if path.endswith('/artifacts'):
                return {'artifacts': [{'name': 'ci-source', 'expired': False, 'id': 10}]}
            return archive(record)
        with patch.object(r, 'api', side_effect=fake):
            self.assertTrue(r.checked(self.base, self.head, self.tree, 'pull_request'))
            self.assertFalse(r.checked('1' * 40, self.head, self.tree, 'pull_request'))
            self.assertFalse(r.checked(self.base, self.head, '2' * 40, 'pull_request'))
            self.assertFalse(r.checked(self.base, self.head, self.tree, 'push'))
        with self.assertRaises(ValueError):
            r.identity_from_zip(archive({**record, 'verified': True}))
        with self.assertRaises(ValueError):
            r.identity_from_zip(archive({**record, 'head': 'invalid'}))

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

    def test_approval_cannot_survive_candidate_change(self):
        prepared = {'action': 'promote', 'head': self.head, 'base': self.base, 'approval': True}
        with patch.object(r, 'inspect', return_value=prepared):
            with self.assertRaises(ValueError):
                r.advance(self.head, self.base)
            with self.assertRaises(ValueError):
                r.advance('f' * 40, self.base, approved=True)
            with self.assertRaises(ValueError):
                r.advance(self.head, 'f' * 40, approved=True)

    def test_partial_publication_precedes_next_promotion(self):
        with patch.dict(os.environ, {'CONFIGS_RELEASE_BOOTSTRAP_SOURCE': self.head}), patch.object(r, 'tag_state', side_effect=['done', 'missing']):
            action = r.inspect()
        self.assertEqual(action['action'], 'publish')
        self.assertEqual(action['source'], self.head)
        self.assertTrue(action['approval'])

    def test_partial_publish_creates_only_missing_tag(self):
        r.git('update-ref', 'refs/remotes/origin/master', self.head)
        calls = []
        def fake(path, data=None, **kwargs):
            calls.append((path, data))
            return {'sha': 'f' * 40}
        with patch.dict(os.environ, {'CONFIGS_RELEASE_BOOTSTRAP_SOURCE': self.head}), patch.object(r, 'tag_state', side_effect=['done', 'missing', 'done']), patch.object(r, 'checked', return_value=True), patch.object(r, 'api', side_effect=fake):
            r.publish(self.head)
        self.assertEqual([path for path, _ in calls], ['git/tags', 'git/refs'])
        self.assertEqual(calls[0][1]['tag'], 'windows-v1.0.0')
        self.assertEqual(calls[0][1]['object'], self.head)
        self.assertEqual(calls[1][1]['ref'], 'refs/tags/windows-v1.0.0')

    def test_lost_source_stops_instead_of_searching_history(self):
        with patch.object(r, 'api', return_value=[]), patch.object(r, 'tag_state', return_value='done'):
            with self.assertRaisesRegex(ValueError, 'original SHA'):
                r.inspect()

    def test_existing_environment_wait_is_reused(self):
        action = {'head': self.head, 'base': self.base, 'approval': True}
        name = f'Approve {self.head} on {self.base}'
        with patch.object(r, 'api', side_effect=[{'workflow_runs': [{'id': 7}]}, {'jobs': [{'name': name, 'conclusion': None}]}]):
            self.assertTrue(r.pending_review(action))
        with patch.object(r, 'api', side_effect=[{'workflow_runs': [{'id': 7}]}, {'jobs': [{'name': name, 'conclusion': 'success'}]}]):
            self.assertFalse(r.pending_review(action))

    def test_clock_releases_runner_and_stops_refresh_wait_at_seven(self):
        patch_head = self.head
        r.git('checkout', '-q', self.base)
        Path('README.md').write_text('Accepted repository change.\n')
        dev = self.commit('docs(repository): accepted fixture change')
        r.git('cherry-pick', patch_head)
        self.head = r.git('rev-parse', 'HEAD')
        r.git('update-ref', 'refs/remotes/origin/dev', dev)
        refresh = {'number': 1, 'head': {'ref': 'feature/unixlike-automatic-refresh', 'sha': self.head,
                   'repo': {'full_name': 'fixture/configs'}}}
        def fake(path):
            if path.startswith('pulls?state=closed'):
                return []
            if 'base=dev' in path:
                return [refresh]
            if 'base=master' in path:
                return []
            if 'matching-refs' in path:
                return [{'ref': 'refs/tags/' + path.rsplit('/', 1)[1], 'object': {'type': 'tag', 'sha': 'f' * 40}}]
            return {'object': {'sha': self.base}}
        with patch.object(r, 'api', side_effect=fake), patch.object(r, 'tag_state', return_value='done'), patch.object(r, 'checked', return_value=False):
            actions = [r.inspect(dt.datetime(2026, 10, 6, hour, tzinfo=ZoneInfo('Asia/Seoul')))['action'] for hour in (4, 5, 6, 7)]
        self.assertEqual(actions, ['wait', 'wait', 'wait', 'promotion-pr'])
        with patch.object(r, 'api', side_effect=lambda path: [] if path.startswith('pulls?') else fake(path)), patch.object(r, 'tag_state', return_value='done'):
            self.assertEqual(r.inspect(dt.datetime(2026, 10, 6, 5, tzinfo=ZoneInfo('Asia/Seoul')))['action'], 'refresh')

    def test_lost_pr_create_response_requires_remote_confirmation(self):
        pr = {'head': {'ref': 'dev', 'repo': {'full_name': 'fixture/configs'}}}
        with patch.object(r, 'api', side_effect=[[], subprocess.CalledProcessError(1, 'gh'), [pr]]):
            self.assertEqual(r.ensure_pr('dev', 'master', 'title', 'body'), pr)
        with patch.object(r, 'api', side_effect=[[], subprocess.CalledProcessError(1, 'gh'), []]):
            with self.assertRaises(ValueError):
                r.ensure_pr('dev', 'master', 'title', 'body')

    def test_lost_merge_response_checks_remote_source(self):
        action = {'action': 'promote', 'number': 1, 'head': self.head, 'base': self.base, 'tree': self.tree, 'approval': False}
        remote = {'merged': True, 'head': {'sha': self.head}, 'merge_commit_sha': 'e' * 40}
        real_git = r.git
        def fake_git(*args):
            if args[0] == 'fetch':
                return ''
            if args[:3] == ('show', '-s', '--format=%P'):
                return self.base + ' ' + self.head
            if args[0] == 'rev-parse':
                return self.tree
            return real_git(*args)
        with patch.object(r, 'inspect', return_value=action), patch.object(r, 'request', side_effect=subprocess.CalledProcessError(1, 'gh')), patch.object(r, 'api', return_value=remote), patch.object(r, 'git', side_effect=fake_git), patch.object(r, 'planned', return_value=['unixlike']), patch.object(r, 'publish') as publication:
            r.advance(self.head, self.base)
            publication.assert_called_once_with('e' * 40)
            publication.reset_mock()
            with patch.object(r, 'planned', return_value=[]):
                r.advance(self.head, self.base)
            publication.assert_not_called()
            remote['head']['sha'] = 'f' * 40
            with self.assertRaises(ValueError):
                r.advance(self.head, self.base)

    def test_refresh_second_cycle_and_actual_base_move(self):
        # The small API fake creates real objects in this disposable Git DB.
        r.git('remote', 'add', 'origin', '.')
        branch = 'feature/unixlike-automatic-refresh'
        commits = []
        def fake(path, data=None, **kwargs):
            if path.startswith('git/matching-refs/heads/'):
                sha = subprocess.run(['git', 'rev-parse', '--verify', 'refs/heads/' + branch], capture_output=True, text=True)
                return [] if sha.returncode else [{'ref': 'refs/heads/' + branch, 'object': {'sha': sha.stdout.strip()}}]
            if path == 'git/blobs':
                sha = subprocess.check_output(['git', 'hash-object', '-w', '--stdin'], input=data['content'].encode()).decode().strip()
            elif path == 'git/trees':
                index = Path(self.tmp.name, '.git', 'api-index')
                if index.exists():
                    index.unlink()
                env = dict(os.environ, GIT_INDEX_FILE=str(index))
                subprocess.check_call(['git', 'read-tree', data['base_tree']], env=env)
                for entry in data['tree']:
                    subprocess.check_call(['git', 'update-index', '--add', '--cacheinfo', entry['mode'], entry['sha'], entry['path']], env=env)
                sha = subprocess.check_output(['git', 'write-tree'], env=env).decode().strip()
            elif path == 'git/commits':
                args = ['git', 'commit-tree', data['tree']]
                for parent in data['parents']:
                    args += ['-p', parent]
                sha = subprocess.check_output(args, input=data['message'].encode()).decode().strip()
                commits.append((sha, data))
            elif path == 'git/refs':
                r.git('update-ref', data['ref'], data['sha'])
                return {}
            elif path == 'git/ref/heads/' + branch:
                return {'object': {'sha': r.git('rev-parse', 'refs/heads/' + branch)}}
            else:
                raise AssertionError(path)
            return {'sha': sha}
        def write_ref(path, method, data):
            r.git('update-ref', 'refs/heads/' + branch, data['sha'])
            return {}
        def refresh(base, revision):
            lock = r.source_json(base, 'unixlike/flake.lock')
            lock['nodes']['n']['locked']['rev'] = revision
            self.write('.git/candidate-lock.json', lock)
            with patch.object(r, 'api', side_effect=fake), patch.object(r, 'request', side_effect=write_ref), patch.object(r, 'tag_state', return_value='done'), patch.object(r, 'ensure_pr', return_value={'number': 1}):
                r.refresh_pr(base, '.git/candidate-lock.json')
            return r.git('rev-parse', 'refs/heads/' + branch)
        first = refresh(self.head, 'next')
        self.assertEqual(r.git('show', '-s', '--format=%P', first), self.head)
        r.git('merge', '--no-ff', '-q', branch, '-m', 'Merge accepted refresh')
        dev = r.git('rev-parse', 'HEAD')
        r.git('update-ref', 'refs/remotes/origin/dev', dev)
        r.git('update-ref', 'refs/remotes/origin/master', dev)
        r.git('tag', '-a', 'unixlike-v1.0.1', '-m', '\n'.join(r.annotation_fields('unixlike', dev, r.declaration(dev, 'unixlike'))))
        second = refresh(dev, 'second')
        self.assertEqual(r.git('show', '-s', '--format=%P', second), dev)
        self.assertEqual(r.git('diff-tree', '--no-commit-id', '--name-only', '-r', second).splitlines(), ['unixlike/flake.lock', 'unixlike/release.json'])
        # A real base update gets a synchronization merge, then a pure refresh.
        Path('README.md').write_text('Actual integration update.\n')
        advanced = self.commit('docs(repository): move fixture dev')
        r.git('update-ref', 'refs/remotes/origin/dev', advanced)
        third = refresh(advanced, 'second')
        self.assertEqual(r.git('show', '-s', '--format=%P', third).split(), [second, advanced])
        self.assertEqual(r.source_json(third, 'unixlike/flake.lock'), r.source_json(second, 'unixlike/flake.lock'))
        self.assertEqual(r.git('show', f'{third}:README.md'), 'Actual integration update.')
        # Audit the generated graph with the same entry used by CI.
        r.git('update-ref', 'refs/remotes/origin/dev', third)
        subprocess.check_call([str(ROOT / 'tool/version-control/audit'), '--history', third], stdout=subprocess.DEVNULL)

    def test_credentials_and_workflow_boundary(self):
        with patch.dict(os.environ, {'CONFIGS_RELEASE_ENABLED': '', 'GH_TOKEN': ''}):
            with self.assertRaises(ValueError):
                r.write_guard()
        workflow = (ROOT / '.github/workflows/release.yml').read_text()
        candidate = workflow.split('\n  refresh:\n')[1].split('\n  refresh-writer:')[0]
        approval = workflow.split('\n  approval:\n')[1].split('\n  writer:')[0]
        self.assertNotIn('secrets.', candidate)
        self.assertIn('persist-credentials: false', candidate)
        self.assertIn('environment: release-approval', approval)
        self.assertNotIn('concurrency:', approval)
        self.assertIn('CONFIGS_RELEASE_ENABLED', workflow)
        self.assertIn("github.event_name != 'schedule' || vars.CONFIGS_RELEASE_SCHEDULE_ENABLED == '1'", workflow)
        self.assertNotIn('pull_request_target', workflow)


if __name__ == '__main__':
    unittest.main(verbosity=2)
