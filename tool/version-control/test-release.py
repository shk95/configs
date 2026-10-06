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
import sys
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
                  'base': {'ref': data['base'], 'sha': base}, 'merged': False, 'merged_at': None, 'ready': False,
                  'tree': self.remote_git('merge-tree', '--write-tree', base, head).splitlines()[0]}
            self.prs.append(pr)
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
        if path.startswith('actions/runs/'):
            pr = self.pr(int(path.split('/')[2]))
            if path.endswith('/artifacts'):
                return {'artifacts': [{'name': 'ci-source', 'expired': False, 'id': pr['number']}]}
            return {'path': '.github/workflows/ci.yml', 'event': 'pull_request', 'conclusion': 'success' if pr['ready'] else None}
        if path.startswith('actions/artifacts/'):
            pr = self.pr(int(path.split('/')[2]))
            return archive({'event': 'pull_request', 'base': pr['base']['sha'], 'head': pr['head']['sha'], 'tree': pr['tree']})
        raise AssertionError(path)

    def request(self, path, method, data):
        self.writes.append(path)
        if path.startswith('git/refs/heads/'):
            self.remote_git('update-ref', 'refs/heads/' + path.removeprefix('git/refs/heads/'), data['sha'])
            return {}
        pr = self.pr(int(path.split('/')[1]))
        if data['sha'] != pr['head']['sha'] or not pr['ready']:
            return {'merged': False}
        base = self.remote_git('rev-parse', 'refs/heads/' + pr['base']['ref'])
        if base != pr['base']['sha']:
            return {'merged': False}
        source = self.remote_git('commit-tree', pr['tree'], '-p', base, '-p', data['sha'], data=b'Merge checked fixture PR\n')
        self.remote_git('update-ref', 'refs/heads/' + pr['base']['ref'], source, base)
        pr.update(merged=True, merged_at='2026-10-06T00:00:00Z', merge_commit_sha=source)
        return {'merged': True}


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

    def promotion(self):
        self.write('windows/release.json', {'previous': 'windows-v1.0.0', 'version': '1.0.1',
                   'summary': 'Windows change', 'compatibility': 'patch', 'migration': ''})
        head = self.commit('feat(windows): update fixture')
        r.git('checkout', '-q', '--detach', self.base)
        r.git('merge', '--no-ff', '-q', head, '-m', 'Merge fixture promotion')
        source = r.git('rev-parse', 'HEAD')
        r.git('update-ref', 'refs/remotes/origin/master', source)
        return source

    def test_partial_publication_precedes_next_promotion(self):
        source = self.promotion()
        with patch.object(r, 'tag_state', side_effect=['done', 'missing']):
            action = r.inspect()
        self.assertEqual(action['action'], 'publish')
        self.assertEqual(action['source'], source)
        self.assertFalse(action['approval'])

    def test_partial_publish_creates_only_missing_tag(self):
        source = self.promotion()
        calls = []
        def fake(path, data=None, **kwargs):
            if path.startswith('commits/'):
                return [{'merged_at': '2026-10-06T00:00:00Z', 'base': {'ref': 'master'},
                         'head': {'ref': 'dev', 'repo': {'full_name': 'fixture/configs'}},
                         'merge_commit_sha': source}]
            calls.append((path, data))
            return {'sha': 'f' * 40}
        with patch.object(r, 'tag_state', side_effect=['done', 'missing', 'done']), patch.object(r, 'checked', return_value=True), patch.object(r, 'api', side_effect=fake):
            r.publish(source)
        self.assertEqual([path for path, _ in calls], ['git/tags', 'git/refs'])
        self.assertEqual(calls[0][1]['tag'], 'windows-v1.0.1')
        self.assertEqual(calls[0][1]['object'], source)
        self.assertEqual(calls[1][1]['ref'], 'refs/tags/windows-v1.0.1')

    def test_lost_source_stops_instead_of_searching_history(self):
        with patch.object(r, 'api', return_value=[]), patch.object(r, 'tag_state', return_value='done'):
            with self.assertRaisesRegex(ValueError, 'original SHA'):
                r.inspect()

    def test_existing_environment_wait_is_reused(self):
        action = {'head': self.head, 'base': self.base, 'approval': True}
        name = f'Approve {self.head} on {self.base}'
        with patch.object(r, 'api', side_effect=[{'workflow_runs': [{'id': 7, 'path': '.github/workflows/release.yml'}]}, {'jobs': [{'name': name, 'conclusion': None}]}]):
            self.assertTrue(r.pending_review(action))
        with patch.object(r, 'api', side_effect=[{'workflow_runs': [{'id': 7, 'path': '.github/workflows/manual-release.yml'}]}, {'jobs': [{'name': name, 'conclusion': 'success'}]}]):
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

    def test_manual_start_and_continuation_ignore_only_schedule(self):
        refresh = {'number': 1, 'head': {'ref': 'feature/unixlike-automatic-refresh', 'sha': self.head,
                   'repo': {'full_name': 'fixture/configs'}}}
        promotion = {'number': 2, 'head': {'ref': 'dev', 'sha': self.head,
                     'repo': {'full_name': 'fixture/configs'}}}
        opened = {'refresh': [], 'promotion': []}
        def fake(path):
            if path.startswith('pulls?state=closed'):
                return [{'head': {'ref': 'dev', 'repo': {'full_name': 'fixture/configs'}},
                         'merged_at': '2026-10-06T00:00:00Z'}]
            if 'base=dev' in path:
                return opened['refresh']
            if 'base=master' in path:
                return opened['promotion']
            if 'matching-refs' in path:
                return [{'ref': 'refs/tags/' + path.rsplit('/', 1)[1], 'object': {'type': 'tag', 'sha': 'f' * 40}}]
            return {'object': {'sha': self.base}}
        now = dt.datetime(2026, 10, 6, 16, tzinfo=ZoneInfo('Asia/Seoul'))
        with patch.object(r, 'api', side_effect=fake), patch.object(r, 'tag_state', return_value='done'), patch.object(r, 'checked', return_value=True):
            self.assertEqual(r.inspect(now)['action'], 'wait')
            self.assertEqual(r.inspect(now, manual=True, start=True)['action'], 'refresh')
            opened['refresh'] = [refresh]
            r.git('update-ref', 'refs/remotes/origin/dev', self.base)
            self.assertEqual(r.inspect(now, manual=True, start=True)['action'], 'refresh-merge')
            r.git('update-ref', 'refs/remotes/origin/dev', self.head)
            opened['refresh'] = []
            opened['promotion'] = [promotion]
            action = r.inspect(now, manual=True, start=True)
            self.assertEqual(action['action'], 'promote')
            self.assertFalse(action['approval'])
            Path('README.md').write_text('Human change pending release.\n')
            human = self.commit('docs(repository): human fixture change')
            r.git('update-ref', 'refs/remotes/origin/dev', human)
            self.assertTrue(r.inspect(now, manual=True)['approval'])
            with patch.object(r, 'checked', return_value=False):
                self.assertEqual(r.inspect(now, manual=True)['action'], 'wait')
                with self.assertRaisesRegex(ValueError, 'candidate changed'):
                    r.advance(self.head, self.base, manual=True)

    def test_schedule_waits_for_active_manual_run(self):
        with patch.object(r, 'manual_active', return_value=True), patch.object(r, 'api') as remote:
            self.assertEqual(r.inspect(), {'action': 'wait', 'reason': 'manual release is active'})
            remote.assert_not_called()
        # Completed/cancelled runs do not strand future scheduled operation.
        with patch.object(r, 'api', return_value={'workflow_runs': []}):
            self.assertFalse(self.real_manual_active())
        with patch.object(r, 'api', side_effect=lambda path: {'workflow_runs': [{'status': 'waiting'}] if 'status=waiting' in path else []}):
            self.assertTrue(self.real_manual_active())

    def test_manual_wait_advances_to_separate_review_in_one_call(self):
        refresh_wait = {'action': 'wait', 'base': self.base, 'head': self.head}
        refresh_merge = {'action': 'refresh-merge', 'base': self.base, 'head': self.head, 'approval': False}
        promotion_pr = {'action': 'promotion-pr', 'base': self.base, 'head': self.head, 'approval': False}
        promote = {'action': 'promote', 'base': self.base, 'head': self.head, 'approval': True}
        actions = [refresh_wait, refresh_merge, promotion_pr, refresh_wait, promote]
        with patch.object(r, 'write_guard') as guard, patch.object(r, 'inspect', side_effect=actions), patch.object(r, 'advance', side_effect=[refresh_merge, promotion_pr]) as advance, patch.object(r, 'api', return_value={'check_runs': []}), patch.object(r, 'pending_review', return_value=False), patch.object(r.time, 'sleep') as sleep:
            self.assertEqual(r.prepare_manual(), promote)
            self.assertEqual(guard.call_count, 5)
            self.assertEqual(sleep.call_count, 2)
            self.assertEqual(advance.call_count, 2)
            for call in advance.call_args_list:
                self.assertEqual(call.kwargs, {'manual': True})
        # The preparation loop never approves/promotes its own candidate.
        with patch.object(r, 'write_guard'), patch.object(r, 'inspect', return_value=promote), patch.object(r, 'pending_review', return_value=True):
            with self.assertRaisesRegex(ValueError, 'Environment review'):
                r.prepare_manual()

    def test_manual_wait_failure_timeout_and_candidate_change_stop(self):
        waiting = {'action': 'wait', 'base': self.base, 'head': self.head}
        failed = {'id': 1, 'name': 'Required checks', 'app': {'id': 15368}, 'conclusion': 'failure'}
        with patch.object(r, 'write_guard'), patch.object(r, 'inspect', return_value=waiting), patch.object(r, 'advance') as writer, patch.object(r, 'api', return_value={'check_runs': [failed]}):
            with self.assertRaisesRegex(ValueError, 'Required checks failed'):
                r.prepare_manual()
            writer.assert_not_called()
        with patch.object(r, 'write_guard'), patch.object(r, 'inspect', return_value=waiting), patch.object(r, 'advance') as writer, patch.object(r, 'api', return_value={'check_runs': []}):
            with self.assertRaisesRegex(ValueError, 'wait expired'):
                r.prepare_manual(timeout=0)
            writer.assert_not_called()
        with patch.object(r, 'write_guard'), patch.object(r, 'inspect', side_effect=[waiting, {**waiting, 'head': 'f' * 40}]), patch.object(r, 'api', return_value={'check_runs': []}), patch.object(r.time, 'sleep'):
            with self.assertRaisesRegex(ValueError, 'candidate changed'):
                r.prepare_manual()
        with patch.object(r, 'write_guard'), patch.object(r, 'inspect', return_value={'action': 'none'}), patch.object(r, 'advance') as writer:
            self.assertEqual(r.prepare_manual(), {'action': 'none'})
            writer.assert_not_called()
        # A failed old check does not override the newer queued rerun.
        latest = {**failed, 'id': 2, 'conclusion': None}
        with patch.object(r, 'write_guard'), patch.object(r, 'inspect', side_effect=[waiting, {'action': 'none'}]), patch.object(r, 'api', return_value={'check_runs': [failed, latest]}), patch.object(r.time, 'sleep') as sleep:
            with self.assertRaisesRegex(ValueError, 'candidate changed'):
                r.prepare_manual()
            sleep.assert_called_once()

    def test_manual_final_cli_never_reports_wait_as_completed_release(self):
        args = ['release', 'advance', '--manual', '--head', self.head, '--base', self.base]
        with patch.object(sys, 'argv', args), patch.object(r, 'write_guard'), patch.object(r, 'advance', return_value={'action': 'wait'}), patch.object(sys, 'stderr', io.StringIO()) as error:
            self.assertEqual(r.main(), 1)
            self.assertIn('Required checks changed', error.getvalue())
        with patch.object(sys, 'argv', args), patch.object(r, 'write_guard'), patch.object(r, 'advance', return_value={'action': 'none'}), patch.object(sys, 'stdout', io.StringIO()) as output:
            self.assertEqual(r.main(), 0)
            self.assertEqual(json.loads(output.getvalue()), {'action': 'none'})

    def test_one_call_cycle_with_actual_remote_git_merges_checks_and_tags(self):
        # Start with equal accepted branches and published declarations.
        r.git('checkout', '-q', '--detach', self.base)
        remote = LocalGitHub()
        lock = json.loads(json.dumps(self.lock))
        lock['nodes']['n']['locked']['rev'] = 'new-upstream'
        self.write('.git/manual-lock.json', lock)
        with patch.dict(os.environ, {'CONFIGS_RELEASE_ENABLED': '1', 'GH_TOKEN': 'fixture-only'}), patch.object(r, 'api', side_effect=remote.api), patch.object(r, 'request', side_effect=remote.request), patch.object(r.time, 'sleep', side_effect=remote.complete_ci):
            r.write_guard()
            start = r.inspect(manual=True, start=True)
            self.assertEqual(start['action'], 'refresh')
            r.refresh_pr(start['base'], '.git/manual-lock.json')
            # The remote API created this object; a new runner starts without it.
            candidate = remote.prs[0]['head']['sha']
            self.assertNotEqual(subprocess.call(['git', 'cat-file', '-e', candidate], stderr=subprocess.DEVNULL), 0)
            plan = r.prepare_manual()
            self.assertEqual(plan['action'], 'promote')
            self.assertFalse(plan['approval'])
            result = r.advance(plan['head'], plan['base'], manual=True)
            self.assertEqual(result['action'], 'promote')
            self.assertEqual(len(remote.prs), 2)
            self.assertTrue(all(pr['merged'] for pr in remote.prs))
            self.assertEqual(remote.sleeps, 2)
            source = remote.remote_git('rev-parse', 'refs/heads/master')
            self.assertEqual(r.git('show', '-s', '--format=%P', source).split(), [plan['base'], plan['head']])
            self.assertEqual(remote.remote_git('rev-parse', 'unixlike-v1.0.1^{commit}'), source)
            self.assertEqual(remote.remote_git('rev-parse', 'windows-v1.0.0^{commit}'), self.base)
            self.assertEqual(r.tag_state('unixlike', source, r.declaration(source, 'unixlike')), 'done')
            # Rerunning with unchanged upstreams publishes nothing and adds no PR.
            r.write_guard()
            before = list(remote.writes)
            self.assertEqual(r.refresh_pr(r.git('rev-parse', 'origin/dev'), '.git/manual-lock.json'), {'action': 'none'})
            self.assertEqual(r.prepare_manual(), {'action': 'none'})
            self.assertEqual(remote.writes, before)

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
        manual = (ROOT / '.github/workflows/manual-release.yml').read_text()
        candidate = manual.split('\n  refresh:\n')[1].split('\n  integrate:')[0]
        approval = manual.split('\n  approval:\n')[1].split('\n  writer:')[0]
        self.assertNotIn('secrets.', candidate)
        self.assertIn('persist-credentials: false', candidate)
        self.assertIn('environment: release-approval', approval)
        self.assertNotIn('concurrency:', approval)
        self.assertNotIn('secrets.', approval)
        self.assertIn('timeout-minutes: 65', manual)
        self.assertIn('prepare-manual', manual)
        self.assertIn('advance --manual', manual)
        self.assertIn('test "$DISPATCH_REF" = refs/heads/master', manual)
        self.assertNotIn('pull_request_target', manual)


if __name__ == '__main__':
    unittest.main(verbosity=2)
