#!/usr/bin/env python3
"""Small Git/API fixtures for the finite release boundary; no operating writes.
INV repository/bounded-release-automation
INV repository/release-tag-contract
INV repository/promotion-source
"""
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

sys.dont_write_bytecode = True

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
        for domain in ('unixlike', 'windows'):
            Path(domain).mkdir()
            self.write(domain + '/release.json', {'previous': seed, 'version': '1.0.0', 'summary': 'First release',
                       'compatibility': 'breaking', 'migration': 'Explicit consumer adoption.'})
        Path('.githooks').mkdir()
        shutil.copy(ROOT / '.githooks/commit-msg', '.githooks/commit-msg')
        self.write('unixlike/automatic-refresh-inputs.json', ['nixpkgs'])
        self.commit('feat(repository): initial fixture')
        self.write('unixlike/flake.lock', self.lock)
        self.base = self.commit('chore(unixlike-deps): initial fixture lock')
        r.git('tag', '-a', 'unixlike-v1.0.0', '-m', '\n'.join(r.annotation_fields('unixlike', self.base, r.declaration(self.base, 'unixlike'))))
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

    def test_schedule_waits_for_active_manual_run(self):
        with patch.object(r, 'manual_active', return_value=True), patch.object(r, 'api') as remote:
            self.assertEqual(r.inspect(), {'action': 'wait', 'reason': 'manual input patch is active'})
            remote.assert_not_called()
        # Completed/cancelled runs do not strand future scheduled operation.
        with patch.object(r, 'api', return_value={'workflow_runs': []}):
            self.assertFalse(self.real_manual_active())
        with patch.object(r, 'api', side_effect=lambda path: {'workflow_runs': [{'status': 'waiting'}] if 'status=waiting' in path else []}):
            self.assertTrue(self.real_manual_active())

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
        Path('unreleased-development').write_text('Unrelated work stays on dev.')
        dev = self.commit('feat(repository): independent development')
        r.git('push', '--quiet', 'origin', 'HEAD:refs/heads/dev')
        r.git('checkout', '-q', '--detach', self.base)
        lock = json.loads(json.dumps(self.lock))
        lock['nodes']['n']['locked']['rev'] = 'new-upstream'
        self.write('.git/manual-lock.json', lock)
        with patch.dict(os.environ, {'CONFIGS_RELEASE_ENABLED': '1', 'GH_TOKEN': 'fixture-only'}), patch.object(r, 'api', side_effect=remote.api), patch.object(r, 'request', side_effect=remote.request), patch.object(r.time, 'sleep', side_effect=remote.complete_ci):
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
            self.assertNotIn('unreleased-development', r.git('ls-tree', '--name-only', source))
            r.write_guard()
            before = list(remote.writes)
            self.assertEqual(r.refresh_pr(source, '.git/manual-lock.json'), {'action': 'none'})
            self.assertEqual(r.prepare_manual(), {'action': 'none'})
            self.assertEqual(remote.writes, before)
            # CI source admission permits the narrow branch, not arbitrary sources.
            env = dict(os.environ, PROMOTION_BASE_REF='master', PROMOTION_HEAD_REF=r.PATCH_BRANCH+self.base[:12], PROMOTION_BASE_REPOSITORY='fixture/configs', PROMOTION_HEAD_REPOSITORY='fixture/configs', PROMOTION_BASE_SHA=self.base, PROMOTION_HEAD_SHA=candidate)
            subprocess.check_call([str(ROOT/'tool/version-control/check-promotion')],env=env,stdout=subprocess.DEVNULL)
            # Stale development cannot promote until patch history is incorporated.
            env.update(PROMOTION_HEAD_REF='dev', PROMOTION_BASE_SHA=source, PROMOTION_HEAD_SHA=dev)
            self.assertNotEqual(subprocess.call([str(ROOT/'tool/version-control/check-promotion')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),0)
            r.git('checkout','-q','independent-dev')
            r.git('merge','--no-ff','-q',source,'-m','Merge master input patch into development')
            env['PROMOTION_HEAD_SHA']=r.git('rev-parse','HEAD')
            subprocess.check_call([str(ROOT/'tool/version-control/check-promotion')],env=env,stdout=subprocess.DEVNULL)
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
        with patch.dict(os.environ, PROMOTION_BASE_REF='master', PROMOTION_HEAD_REF=r.PATCH_BRANCH+'fake', PROMOTION_BASE_REPOSITORY='fixture/configs', PROMOTION_HEAD_REPOSITORY='fixture/configs', PROMOTION_BASE_SHA=self.base, PROMOTION_HEAD_SHA=extra):
            self.assertNotEqual(subprocess.call([str(ROOT/'tool/version-control/check-promotion')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),0)
        with patch.object(r,'inspect',return_value={'action':'patch-merge','base':self.base,'head':self.head}),patch.object(r,'request') as writer:
            with self.assertRaisesRegex(ValueError,'candidate changed'):
                r.advance('f'*40,self.base,manual=True)
            writer.assert_not_called()

    def test_publication_recovery_and_delayed_association(self):
        r.git('checkout','-q','--detach',self.base)
        remote=LocalGitHub()
        lock=json.loads(json.dumps(self.lock));lock['nodes']['n']['locked']['rev']='new'
        self.write('.git/manual-lock.json',lock)
        with patch.dict(os.environ,CONFIGS_RELEASE_ENABLED='1',GH_TOKEN='fixture-only'),patch.object(r,'api',side_effect=remote.api),patch.object(r,'request',side_effect=remote.request),patch.object(r.time,'sleep',side_effect=remote.complete_ci):
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
        with patch.dict(os.environ,CONFIGS_RELEASE_ENABLED='1',GH_TOKEN='fixture-only'),patch.object(r,'api',side_effect=remote.api),patch.object(r,'request',side_effect=remote.request):
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
        env=dict(os.environ,PROMOTION_BASE_REF='master',PROMOTION_HEAD_REF=r.PATCH_BRANCH+'fixture',PROMOTION_BASE_REPOSITORY='fixture/configs',PROMOTION_HEAD_REPOSITORY='fork/configs',PROMOTION_BASE_SHA=self.base,PROMOTION_HEAD_SHA=self.head)
        self.assertNotEqual(subprocess.call([str(ROOT/'tool/version-control/check-promotion')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),0)

    def test_general_publication_and_promotion_are_not_automated(self):
        r.git('checkout','-q','--detach',self.base)
        remote=LocalGitHub()
        with patch.object(r,'api',side_effect=remote.api):
            self.assertEqual(r.inspect(),{'action':'none'})
            remote.prs.append({'head':{'ref':'dev','repo':{'full_name':'fixture/configs'}},'base':{'ref':'master'},'merged_at':None})
            self.assertEqual(r.inspect()['action'],'wait')
            with self.assertRaisesRegex(ValueError,'development promotion'):
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
        with patch.object(r,'api',side_effect=[[],subprocess.CalledProcessError(1,'gh'),[pr]]):
            self.assertEqual(r.ensure_pr(pr['head']['ref'],'master','title','body'),pr)
        with patch.object(r,'api',side_effect=[[],subprocess.CalledProcessError(1,'gh'),[]]):
            with self.assertRaises(ValueError):r.ensure_pr(pr['head']['ref'],'master','title','body')

    def test_schedule_steps_and_lost_merge_response(self):
        r.git('checkout','-q','--detach',self.base)
        remote=LocalGitHub()
        lock=json.loads(json.dumps(self.lock));lock['nodes']['n']['locked']['rev']='scheduled'
        self.write('.git/manual-lock.json',lock)
        with patch.dict(os.environ,CONFIGS_RELEASE_ENABLED='1',GH_TOKEN='fixture-only'),patch.object(r,'api',side_effect=remote.api),patch.object(r,'request',side_effect=remote.request):
            r.write_guard()
            start=r.inspect(start=True)
            self.assertEqual(start['head'],self.base)
            r.refresh_pr(start['base'],'.git/manual-lock.json')
            r.write_guard()
            self.assertEqual(r.inspect()['action'],'wait')
            remote.complete_ci(0)
            plan=r.inspect()
            def lost_response(path,method,data):
                remote.request(path,method,data)
                raise subprocess.CalledProcessError(1,'gh')
            with patch.object(r,'request',side_effect=lost_response):
                r.advance(plan['head'],plan['base'])
            r.write_guard()
            self.assertEqual(r.inspect(),{'action':'none'})
            self.assertEqual(len(remote.prs),1)
            self.assertEqual(remote.remote_git('rev-parse','windows-v1.0.0'),self.windows_tag)

    def test_branch_creation_resume_and_noop(self):
        r.git('checkout','-q','--detach',self.base)
        remote=LocalGitHub()
        self.write('.git/manual-lock.json',self.lock)
        with patch.object(r,'api',side_effect=remote.api),patch.object(r,'request',side_effect=remote.request):
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
