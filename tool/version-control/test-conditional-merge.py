#!/usr/bin/env python3
"""Finite local fixtures for conditional protected merging; no remote writes.
INV repository/conditional-protected-merge
"""
import importlib.util
from contextlib import ExitStack
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import subprocess
import unittest
import datetime as dt
from unittest.mock import Mock, patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('conditional_merge', ROOT / 'tool/version-control/conditional-merge.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
NOW = lambda: dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')


def archive(record):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as zipped:
        zipped.writestr('source.json', json.dumps(record))
    return out.getvalue()


class API:
    def __init__(self, values=None):
        self.values = values or {}
        self.calls = []

    def request(self, path, method='GET', data=None, binary=False):
        self.calls.append((path, method, data, binary))
        value = self.values.get((method, path), self.values.get(path))
        if isinstance(value, Exception):
            raise value
        return value

    def pages(self, path):
        self.calls.append((path, 'PAGES', None, False))
        return self.values.get(('PAGES', path), self.values.get(path, []))


class ConditionalMergeFixtures(unittest.TestCase):
    # FIXTURE repository/conditional-protected-merge
    def test_sha_and_repository_inputs_require_full_exact_values(self):
        self.assertEqual(m.full_sha('a' * 40, 'head'), 'a' * 40)
        for value in ('a' * 39, 'A' * 40, 'a' * 40 + 'x'):
            with self.assertRaises(ValueError):
                m.full_sha(value, 'head')
        self.assertTrue(m.REPO.fullmatch('shk95/configs'))
        self.assertFalse(m.REPO.fullmatch('shk95/configs/other'))

    # FIXTURE repository/conditional-protected-merge
    def test_protection_check_fetches_repository_settings_without_trailing_slash(self):
        repo_url = f'{m.API}/repos/shk95/configs'
        protection_url = f'{repo_url}/branches/dev/protection'
        pull_url = f'{repo_url}/pulls/17'
        branch = {'required_status_checks': {
            'strict': True, 'contexts': ['Required checks'],
            'checks': [{'context': 'Required checks', 'app_id': m.APP_ID}]},
            'enforce_admins': {'enabled': True},
            'required_conversation_resolution': {'enabled': True},
            'required_pull_request_reviews': {},
            'allow_force_pushes': {'enabled': False}, 'allow_deletions': {'enabled': False}}
        repository = {'allow_merge_commit': True, 'allow_squash_merge': False,
                      'allow_rebase_merge': False}

        class Endpoint:
            def __init__(self):
                self.urls = []

            def open(self, request, timeout):
                self.urls.append(request.full_url)
                if request.full_url.endswith('/'):
                    raise m.urllib.error.HTTPError(request.full_url, 404, 'Not Found', None, io.BytesIO())
                responses = {protection_url: branch, repo_url: repository,
                             pull_url: {'number': 17}}
                if request.full_url not in responses:
                    raise AssertionError(f'unexpected GitHub API URL: {request.full_url}')
                return io.BytesIO(json.dumps(responses[request.full_url]).encode())

        endpoint = Endpoint()
        api = m.GitHub('fixture-token', 'shk95/configs')
        with patch.object(m.urllib.request, 'build_opener', return_value=endpoint):
            m.validate_protection(api, 'dev')
            self.assertEqual(api.request('pulls/17'), {'number': 17})
            with self.assertRaises(m.urllib.error.HTTPError) as error:
                endpoint.open(m.urllib.request.Request(repo_url + '/'), timeout=30)

        self.assertEqual(error.exception.code, 404)
        error.exception.close()
        self.assertEqual(endpoint.urls, [protection_url, repo_url, pull_url, repo_url + '/'])

    # FIXTURE repository/conditional-protected-merge
    def test_source_archive_is_bounded_and_binds_event_base_head_and_tree(self):
        record = {'event': 'pull_request', 'base': 'a' * 40, 'head': 'b' * 40, 'tree': 'c' * 40}
        self.assertEqual(m.source_identity(archive(record)), record)
        with self.assertRaisesRegex(ValueError, 'too large'):
            m.source_identity(b'x' * 65537)
        with self.assertRaisesRegex(ValueError, 'invalid CI source record'):
            m.source_identity(archive({**record, 'event': 'push'}))
        with self.assertRaisesRegex(ValueError, 'full 40-character'):
            m.source_identity(archive({**record, 'head': 'b' * 39}))

    # FIXTURE repository/conditional-protected-merge
    def test_exact_source_run_requires_newest_success_and_matching_artifact(self):
        request = {'pr': 17, 'target': 'dev', 'base': 'a' * 40, 'head': 'b' * 40, 'repo': 'shk95/configs'}
        tree = 'c' * 40
        run = {'id': 20, 'path': '.github/workflows/ci.yml', 'event': 'pull_request',
               'head_sha': request['head'], 'status': 'completed', 'conclusion': 'success'}
        check = {'id': 30, 'name': 'Required checks', 'app': {'id': m.APP_ID}, 'status': 'completed',
                 'conclusion': 'success', 'details_url': 'https://github.com/shk95/configs/actions/runs/20/job/1'}
        good = API({
            ('PAGES', f"actions/workflows/ci.yml/runs?head_sha={request['head']}&event=pull_request&per_page=100"): [run],
            ('PAGES', f"commits/{request['head']}/check-runs?per_page=100"): [check],
            ('PAGES', 'actions/runs/20/artifacts?per_page=100'): [{'id': 40, 'name': 'ci-source', 'expired': False}],
            ('GET', 'actions/artifacts/40/zip'): archive({'event': 'pull_request', 'base': request['base'], 'head': request['head'], 'tree': tree})})
        self.assertEqual(m.source_run(good, request, tree), (run, 'success'))

        stale_base = API({
            ('PAGES', f"actions/workflows/ci.yml/runs?head_sha={request['head']}&event=pull_request&per_page=100"): [run],
            ('PAGES', f"commits/{request['head']}/check-runs?per_page=100"): [check],
            ('PAGES', 'actions/runs/20/artifacts?per_page=100'): [{'id': 40, 'name': 'ci-source', 'expired': False}],
            ('GET', 'actions/artifacts/40/zip'): archive({'event': 'pull_request', 'base': 'e' * 40,
                'head': request['head'], 'tree': tree})})
        with self.assertRaisesRegex(ValueError, 'identity does not match'):
            m.source_run(stale_base, request, tree)

        newer_pending = {**run, 'id': 21, 'status': 'in_progress', 'conclusion': None}
        stale = API({
            ('PAGES', f"actions/workflows/ci.yml/runs?head_sha={request['head']}&event=pull_request&per_page=100"): [run, newer_pending]})
        self.assertEqual(m.source_run(stale, request, tree), (None, 'waiting'))

        newer_failed = {**run, 'id': 22, 'conclusion': 'failure'}
        failed = API({('PAGES', f"actions/workflows/ci.yml/runs?head_sha={request['head']}&event=pull_request&per_page=100"): [run, newer_failed]})
        with self.assertRaisesRegex(ValueError, 'newest matching CI run'):
            m.source_run(failed, request, tree)

    # FIXTURE repository/conditional-protected-merge
    def test_changed_head_draft_fork_and_blocked_pr_cannot_enter_wait(self):
        request = {'pr': 17, 'target': 'dev', 'base': 'a' * 40, 'head': 'b' * 40, 'repo': 'shk95/configs'}
        base_pr = {'number': 17, 'state': 'open', 'draft': False,
                   'base': {'ref': 'dev', 'sha': request['base'], 'repo': {'full_name': request['repo']}},
                   'head': {'ref': 'feature/topic', 'sha': request['head'], 'repo': {'full_name': request['repo']}},
                   'mergeable': True, 'mergeable_state': 'clean', 'labels': []}
        for mutate, message in (
            (lambda p: p['head'].__setitem__('sha', 'd' * 40), 'identity changed'),
            (lambda p: p.__setitem__('draft', True), 'Ready'),
            (lambda p: p['head'].__setitem__('repo', {'full_name': 'fork/configs'}), 'identity changed'),
            (lambda p: p.__setitem__('labels', [{'name': 'blocked'}]), 'explicitly blocked'),
            (lambda p: p.__setitem__('labels', [{'name': 'high-risk'}]), 'synchronous review'),
        ):
            pr = json.loads(json.dumps(base_pr))
            mutate(pr)
            api = API({"pulls/17": pr})
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                m.read_pr(api, request)

    # FIXTURE repository/conditional-protected-merge
    def test_open_pr_ancestor_is_refused_as_a_stack(self):
        request = {'pr': 17, 'target': 'dev', 'base': 'a' * 40, 'head': 'b' * 40, 'repo': 'shk95/configs'}
        api = API({('PAGES', 'pulls?state=open&base=dev&per_page=100'):
                   [{'number': 18, 'head': {'sha': 'c' * 40}}]})
        with patch.object(m.subprocess, 'run', side_effect=[
                type('Result', (), {'returncode': 0})(),
                type('Result', (), {'returncode': 0})(),
                type('Result', (), {'returncode': 0})()]) as run:
            with self.assertRaisesRegex(ValueError, 'stacked on open pull request #18'):
                m.check_independent_shape(api, request)
        self.assertEqual(run.call_count, 3)

    # FIXTURE repository/conditional-protected-merge
    def test_pending_mergeability_waits_but_conflicts_refuse(self):
        request = {'pr': 17, 'target': 'dev', 'base': 'a' * 40, 'head': 'b' * 40, 'repo': 'shk95/configs'}
        pr = {'number': 17, 'state': 'open', 'draft': False,
              'base': {'ref': 'dev', 'sha': request['base'], 'repo': {'full_name': request['repo']}},
              'head': {'ref': 'feature/topic', 'sha': request['head'], 'repo': {'full_name': request['repo']}},
              'mergeable': None, 'mergeable_state': 'unknown', 'labels': []}
        api = API({'pulls/17': pr, 'https://api.github.com/graphql': {'data': {'repository': {'pullRequest': {
            'reviewThreads': {'nodes': [], 'pageInfo': {'hasNextPage': False, 'endCursor': None}}}}}},
            ('PAGES', 'pulls/17/reviews?per_page=100'): [],
            'branches/dev/protection': {'required_pull_request_reviews': {'required_approving_review_count': 0}}})
        self.assertTrue(m.read_pr(api, request)['_conditional_waiting'])
        behind = json.loads(json.dumps(pr))
        behind.pop('_conditional_waiting', None)
        behind['mergeable'] = True
        behind['mergeable_state'] = 'behind'
        self.assertFalse(m.read_pr(API({**api.values, 'pulls/17': behind}), request,
                                   allow_dev_chain=True).get('_conditional_waiting', False))
        with self.assertRaisesRegex(ValueError, 'behind its target'):
            m.read_pr(API({**api.values, 'pulls/17': behind}), request)
        conflict = json.loads(json.dumps(pr))
        conflict['mergeable'] = False
        conflict['mergeable_state'] = 'dirty'
        with self.assertRaisesRegex(ValueError, 'not mergeable'):
            m.read_pr(API({'pulls/17': conflict}), request)

    # FIXTURE repository/conditional-protected-merge
    def test_merged_recovery_checks_head_target_and_repository_but_uses_parents_for_base(self):
        request = {'pr': 17, 'target': 'dev', 'base': 'a' * 40, 'head': 'b' * 40, 'repo': 'shk95/configs'}
        merged = {'number': 17, 'state': 'closed', 'merged_at': '2026-10-06T12:00:00Z',
                  'base': {'ref': 'dev', 'sha': 'c' * 40, 'repo': {'full_name': request['repo']}},
                  'head': {'ref': 'feature/topic', 'sha': request['head'], 'repo': {'full_name': request['repo']}}}
        self.assertEqual(m.read_pr(API({'pulls/17': merged}), request), merged)
        for field, value in (('base_ref', 'master'), ('repo', 'fork/configs')):
            pr = json.loads(json.dumps(merged))
            if field == 'head_sha':
                pr['head']['sha'] = value
            elif field == 'base_ref':
                pr['base']['ref'] = value
            else:
                pr['head']['repo']['full_name'] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.read_pr(API({'pulls/17': pr}), request)

    # FIXTURE repository/conditional-protected-merge
    def test_branch_protection_requires_strict_required_checks_and_admin_safeguards(self):
        required = {'strict': True, 'contexts': ['Required checks'],
                    'checks': [{'context': 'Required checks', 'app_id': m.APP_ID}]}
        branch = {'required_status_checks': required, 'enforce_admins': {'enabled': True},
                  'required_conversation_resolution': {'enabled': True},
                  'required_pull_request_reviews': {}, 'allow_force_pushes': {'enabled': False},
                  'allow_deletions': {'enabled': False}}
        api = API({'branches/dev/protection': branch, '': {'allow_merge_commit': True,
                    'allow_squash_merge': False, 'allow_rebase_merge': False}})
        m.validate_protection(api, 'dev')
        loose = json.loads(json.dumps(branch))
        loose['required_status_checks']['strict'] = False
        with self.assertRaisesRegex(ValueError, 'strict Required checks'):
            m.validate_protection(API({'branches/dev/protection': loose}), 'dev')

    # FIXTURE repository/conditional-protected-merge
    def test_target_move_and_unapproved_actor_fail_closed(self):
        api = API({'git/ref/heads/dev': {'object': {'sha': 'd' * 40}}})
        run = {'event': 'workflow_dispatch', 'path': '.github/workflows/conditional-merge.yml',
               'head_branch': 'dev', 'head_sha': 'a' * 40, 'status': 'in_progress',
               'created_at': '2026-10-06T12:00:00Z'}
        api.values['actions/runs/1'] = run
        with patch.object(m, 'branch_sha', return_value='d' * 40), \
             patch.object(m.subprocess, 'run', return_value=type('Result', (), {'returncode': 0})()), \
             patch.object(m, 'is_ancestor', return_value=False), self.assertRaisesRegex(ValueError, 'not an ancestor'):
            m.verify_accepted_run(api, '1')
        with patch.dict(os.environ, {'CONFIGS_MERGE_ACTORS': 'maintainer'}):
            with self.assertRaisesRegex(ValueError, 'not in CONFIGS_MERGE_ACTORS'):
                m.validate_actor(API({}), {'repo': 'shk95/configs'}, {'actor': {'login': 'worker'}})
        with patch.dict(os.environ, {'CONFIGS_MERGE_ACTORS': 'maintainer'}):
            m.validate_actor(API({'collaborators/maintainer/permission': {
                'permission': 'write', 'role_name': 'maintain'}}), {'repo': 'shk95/configs'},
                {'actor': {'login': 'maintainer'}})
        run['status'] = 'completed'
        api.values['actions/runs/1'] = run
        with patch.object(m, 'branch_sha', return_value='a' * 40), \
             patch.object(m.subprocess, 'run', return_value=type('Result', (), {'returncode': 0})()), \
             self.assertRaisesRegex(ValueError, 'not active'):
            m.verify_accepted_run(api, '1')

    # FIXTURE repository/conditional-protected-merge
    def test_preflight_recovers_old_completed_run_only_after_same_pr_is_merged(self):
        now_old = '2026-10-06T09:00:00Z'
        run = {'event': 'workflow_dispatch', 'path': '.github/workflows/conditional-merge.yml',
               'head_branch': 'dev', 'head_sha': 'a' * 40, 'status': 'completed', 'created_at': now_old,
               'actor': {'login': 'maintainer'}}
        pr = {'number': 17, 'state': 'closed', 'merged_at': '2026-10-06T09:30:00Z',
              'base': {'ref': 'dev', 'repo': {'full_name': 'shk95/configs'}},
              'head': {'sha': 'b' * 40, 'repo': {'full_name': 'shk95/configs'}}}
        api = API({'actions/runs/99': run, 'git/ref/heads/dev': {'object': {'sha': 'd' * 40}},
                   'pulls/17': pr, 'collaborators/maintainer/permission': {'permission': 'admin'}})
        args = type('Args', (), {'run_id': '99', 'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'c' * 40})()
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '99', 'GITHUB_REPOSITORY': 'shk95/configs',
                                     'GH_TOKEN': 'fixture', 'CONFIGS_MERGE_ENABLED': '1',
                                     'CONFIGS_MERGE_ACTORS': 'maintainer'}), \
             patch.object(m, 'repo_name', return_value='shk95/configs'), patch.object(m, 'GitHub', return_value=api), \
             patch.object(m, 'branch_sha', return_value='d' * 40), \
             patch.object(m.subprocess, 'run', return_value=type('Result', (), {'returncode': 0})()), \
             patch('builtins.print'):
            m.preflight(args)

    # FIXTURE repository/conditional-protected-merge
    def test_comment_does_not_clear_a_current_head_change_request(self):
        request = {'pr': 17, 'target': 'dev', 'base': 'a' * 40, 'head': 'b' * 40, 'repo': 'shk95/configs'}
        api = API({('PAGES', 'pulls/17/reviews?per_page=100'): [
            {'user': {'login': 'reviewer'}, 'state': 'CHANGES_REQUESTED', 'commit_id': request['head'],
             'submitted_at': '2026-10-06T10:00:00Z'},
            {'user': {'login': 'reviewer'}, 'state': 'COMMENTED', 'commit_id': request['head'],
             'submitted_at': '2026-10-06T11:00:00Z'}],
            'branches/dev/protection': {'required_pull_request_reviews': {'required_approving_review_count': 0}}})
        with self.assertRaisesRegex(ValueError, 'outstanding change request'):
            m.check_reviews(api, request, {}, set())

    # FIXTURE repository/conditional-protected-merge
    def test_approval_on_original_head_does_not_satisfy_integration_head_and_changes_request_persists(self):
        request = {'pr': 17, 'target': 'dev', 'base': 'a' * 40, 'head': 'b' * 40, 'repo': 'shk95/configs'}
        current_pr = {'head': {'sha': 'c' * 40}}
        old_approval = {'user': {'login': 'reviewer'}, 'state': 'APPROVED',
                        'commit_id': request['head'], 'submitted_at': '2026-10-06T09:00:00Z'}
        api = API({('PAGES', 'pulls/17/reviews?per_page=100'): [old_approval],
                   'branches/dev/protection': {'required_pull_request_reviews': {'required_approving_review_count': 1}}})
        with self.assertRaisesRegex(ValueError, 'approvals'):
            m.check_reviews(api, request, current_pr, set())
        api.values[('PAGES', 'pulls/17/reviews?per_page=100')] = [
            {**old_approval, 'state': 'CHANGES_REQUESTED', 'submitted_at': '2026-10-06T10:00:00Z',
             'commit_id': 'c' * 40},
            {'user': old_approval['user'], 'state': 'COMMENTED', 'commit_id': 'c' * 40,
             'submitted_at': '2026-10-06T11:00:00Z'}]
        with self.assertRaisesRegex(ValueError, 'outstanding change request'):
            m.check_reviews(api, request, current_pr, set())

    # FIXTURE repository/conditional-protected-merge
    def test_submit_refuses_any_source_head_other_than_reviewed_SHA(self):
        args = type('Args', (), {'confirm': True, 'pr': 17, 'target': 'dev', 'head': 'b' * 40,
                                 'base': 'a' * 40})()
        api = API()
        with patch.dict(os.environ, {'GH_TOKEN': 'fixture'}), patch.object(m, 'repo_name', return_value='shk95/configs'), \
             patch.object(m, 'GitHub', return_value=api), \
             patch.object(m, 'read_pr', return_value={'head': {'sha': 'c' * 40}}):
            with self.assertRaisesRegex(ValueError, 'reviewed source SHA'):
                m.submit(args)
        self.assertFalse(any(call[1] == 'POST' for call in api.calls))

    # FIXTURE repository/conditional-protected-merge
    def test_ambiguous_dispatch_is_never_retried(self):
        args = type('Args', (), {'confirm': True, 'pr': 17, 'target': 'dev', 'head': 'b' * 40,
                                 'base': 'a' * 40})()
        api = API()
        api.request = Mock(side_effect=m.urllib.error.URLError('timed out'))
        with patch.dict(os.environ, {'GH_TOKEN': 'fixture'}), patch.object(m, 'repo_name', return_value='shk95/configs'), patch.object(m, 'GitHub', return_value=api), \
             patch.object(m, 'read_pr', return_value={'number': 17, 'head': {'sha': 'b' * 40}}), \
             patch.object(m, 'branch_sha', return_value='a' * 40), \
             patch('builtins.print'):
            with self.assertRaisesRegex(ValueError, 'inspect Actions before retrying'):
                m.submit(args)
        self.assertEqual(api.request.call_count, 1)

    # FIXTURE repository/conditional-protected-merge
    def test_write_orchestration_submits_once_only_after_exact_ci_and_protection(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40}
        args = type('Args', (), {'run_id': '99', **request})()
        active = {'created_at': NOW()}
        open_pr = {'state': 'open', 'merged_at': None, '_conditional_waiting': False,
                   'head': {'sha': request['head']}, 'base': {'sha': request['base']}}
        merged_pr = {'state': 'closed', 'merged_at': '2026-10-06T12:02:00Z',
                     'head': {'sha': request['head']}, 'merge_commit_sha': 'c' * 40}
        api = API({'pulls/17': merged_pr})
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '99', 'GITHUB_REPOSITORY': 'shk95/configs',
                                     'GITHUB_ACTOR': 'maintainer', 'GH_TOKEN': 'fixture',
                                     'CONFIGS_MERGE_ENABLED': '1'}), \
             patch.object(m, 'repo_name', return_value='shk95/configs'), \
             patch.object(m, 'GitHub', return_value=api), \
             patch.object(m, 'verify_accepted_run', return_value=active), \
             patch.object(m, 'validate_actor'), patch.object(m, 'validate_protection'), \
             patch.object(m, 'check_independent_shape'), \
             patch.object(m, 'read_pr', side_effect=[open_pr, open_pr, open_pr]), \
             patch.object(m, 'branch_sha', return_value=request['base']), \
             patch.object(m, 'validate_dev_chain', return_value=0), patch.object(m, 'is_ancestor', return_value=True), \
             patch.object(m, 'sha256_tree', return_value='d' * 40), \
             patch.object(m, 'source_run', return_value=({'id': 10}, 'success')), \
             patch.object(m, 'finish', return_value='confirmed'), patch.object(m.time, 'monotonic', return_value=1):
            self.assertEqual(m.write_run(args), 'confirmed')
        writes = [call for call in api.calls if call[1] == 'PUT']
        self.assertEqual(len(writes), 1)
        self.assertEqual(writes[0][2], {'sha': request['head'], 'merge_method': 'merge'})

    # FIXTURE repository/conditional-protected-merge
    def test_write_orchestration_refuses_new_ci_failure_and_timeout_without_merge(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40}
        args = type('Args', (), {'run_id': '99', **request})()
        active = {'created_at': NOW()}
        pr = {'state': 'open', 'merged_at': None, '_conditional_waiting': False,
              'head': {'sha': request['head']}, 'base': {'sha': request['base']}}
        base_api = API()
        env = {'GITHUB_RUN_ID': '99', 'GITHUB_REPOSITORY': 'shk95/configs', 'GITHUB_ACTOR': 'maintainer',
               'GH_TOKEN': 'fixture', 'CONFIGS_MERGE_ENABLED': '1'}
        with patch.dict(os.environ, env), patch.object(m, 'repo_name', return_value='shk95/configs'), \
             patch.object(m, 'GitHub', return_value=base_api), patch.object(m, 'verify_accepted_run', return_value=active), \
             patch.object(m, 'validate_actor'), patch.object(m, 'validate_protection'), patch.object(m, 'check_independent_shape'), \
             patch.object(m, 'read_pr', return_value=pr), patch.object(m, 'branch_sha', return_value=request['base']), \
             patch.object(m, 'validate_dev_chain', return_value=0), patch.object(m, 'is_ancestor', return_value=True), \
             patch.object(m, 'sha256_tree', return_value='d' * 40), patch.object(m, 'source_run', side_effect=ValueError('newest CI failed')):
            with self.assertRaisesRegex(ValueError, 'newest CI failed'):
                m.write_run(args)
        self.assertFalse(any(call[1] == 'PUT' for call in base_api.calls))

        waiting_api = API()
        with patch.object(m, 'GitHub', return_value=waiting_api), patch.object(m, 'source_run', return_value=(None, 'waiting')), \
             patch.object(m.time, 'monotonic', side_effect=[1, 3602]), patch.object(m.time, 'sleep'), \
             patch.object(m, 'repo_name', return_value='shk95/configs'), patch.object(m, 'verify_accepted_run', return_value=active), \
             patch.object(m, 'validate_actor'), patch.object(m, 'validate_protection'), patch.object(m, 'check_independent_shape'), \
             patch.object(m, 'read_pr', return_value=pr), patch.object(m, 'branch_sha', return_value=request['base']), \
             patch.object(m, 'validate_dev_chain', return_value=0), patch.object(m, 'is_ancestor', return_value=True), \
             patch.object(m, 'sha256_tree', return_value='d' * 40), patch.dict(os.environ, env):
            with self.assertRaisesRegex(ValueError, '60-minute request deadline expired'):
                m.write_run(args)
        self.assertFalse(any(call[1] == 'PUT' for call in waiting_api.calls))

    # FIXTURE repository/conditional-protected-merge
    def test_dev_base_drift_A_to_B_updates_same_approved_head_and_gates_latest_base(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40}
        args = type('Args', (), {'run_id': '99', **request})()
        active_run = {'created_at': NOW()}
        first = {'state': 'open', 'merged_at': None, '_conditional_waiting': False,
                 'head': {'sha': request['head']}, 'base': {'sha': request['base']}}
        integrated = {'state': 'open', 'merged_at': None, '_conditional_waiting': False,
                      'head': {'sha': 'c' * 40}, 'base': {'sha': 'd' * 40}}
        merged = {'state': 'closed', 'merged_at': '2026-10-07T01:05:00Z',
                  'head': {'sha': 'c' * 40}, 'merge_commit_sha': 'e' * 40}
        api = API({('PUT', 'pulls/17/merge'): {'merged': True}, 'pulls/17': merged})
        reads = [first, first, integrated, integrated]
        update = Mock(return_value=integrated)
        source = Mock(return_value=({'id': 501}, 'success'))
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '99', 'GITHUB_REPOSITORY': 'shk95/configs',
                                     'GITHUB_ACTOR': 'maintainer', 'GH_TOKEN': 'fixture',
                                     'CONFIGS_MERGE_ENABLED': '1'}), \
             patch.object(m, 'repo_name', return_value='shk95/configs'), \
             patch.object(m, 'GitHub', return_value=api), \
             patch.object(m, 'verify_accepted_run', return_value=active_run), patch.object(m, 'validate_actor'), \
             patch.object(m, 'validate_protection'), patch.object(m, 'check_independent_shape'), \
             patch.object(m, 'read_pr', side_effect=reads), \
             patch.object(m, 'branch_sha', return_value='d' * 40), \
             patch.object(m, 'validate_dev_chain', side_effect=[0, 1, 1]), \
             patch.object(m, 'is_ancestor', side_effect=[False, True]), \
             patch.object(m, 'refuse_latest_ci_failure'), patch.object(m, 'update_dev_branch', update), \
             patch.object(m, 'sha256_tree', return_value='f' * 40), patch.object(m, 'source_run', source), \
             patch.object(m, 'finish', return_value='confirmed'), patch.object(m.time, 'monotonic', return_value=2):
            self.assertEqual(m.write_run(args), 'confirmed')
        update.assert_called_once()
        self.assertEqual(update.call_args.args[2], request['head'])
        self.assertEqual(request['head'], 'b' * 40)
        self.assertEqual(source.call_args.args[1]['base'], 'd' * 40)
        self.assertEqual(source.call_args.args[1]['head'], 'c' * 40)
        self.assertEqual([call[2] for call in api.calls if call[1] == 'PUT'],
                         [{'sha': 'c' * 40, 'merge_method': 'merge'}])

    # FIXTURE repository/conditional-protected-merge
    def test_change_request_on_integrated_head_stops_without_a_second_update_or_merge(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40}
        args = type('Args', (), {'run_id': '99', **request})()
        active = {'created_at': NOW()}
        pr = {'state': 'open', 'merged_at': None, '_conditional_waiting': False,
              'head': {'sha': request['head']}, 'base': {'sha': request['base']}}
        api = API()
        update = Mock(return_value={'head': {'sha': 'c' * 40}})
        read = Mock(side_effect=[pr, pr, ValueError('candidate has an outstanding change request')])
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '99', 'GITHUB_REPOSITORY': 'shk95/configs',
                                     'GITHUB_ACTOR': 'maintainer', 'GH_TOKEN': 'fixture',
                                     'CONFIGS_MERGE_ENABLED': '1'}), \
             patch.object(m, 'repo_name', return_value='shk95/configs'), patch.object(m, 'GitHub', return_value=api), \
             patch.object(m, 'verify_accepted_run', return_value=active), patch.object(m, 'validate_actor'), \
             patch.object(m, 'validate_protection'), patch.object(m, 'check_independent_shape'), \
             patch.object(m, 'read_pr', read), patch.object(m, 'branch_sha', return_value='d' * 40), \
             patch.object(m, 'validate_dev_chain', return_value=0), patch.object(m, 'is_ancestor', return_value=False), \
             patch.object(m, 'refuse_latest_ci_failure'), patch.object(m, 'update_dev_branch', update), \
             patch.object(m.time, 'monotonic', return_value=2):
            with self.assertRaisesRegex(ValueError, 'outstanding change request'):
                m.write_run(args)
        update.assert_called_once()
        self.assertFalse(any(call[1] == 'PUT' for call in api.calls))

    # FIXTURE repository/conditional-protected-merge
    def test_branch_update_uses_head_CAS_and_refuses_conflicts_before_api_write(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'source_head': 'b' * 40,
                   'base': 'a' * 40, 'source_base': 'a' * 40, 'repo': 'shk95/configs'}
        old = {'state': 'open', 'draft': False, 'head': {'sha': request['head'], 'ref': 'feature/topic'},
               'base': {'sha': request['base']}, '_conditional_waiting': False}
        updated = {**old, 'head': {'sha': 'c' * 40, 'ref': 'feature/topic'}}
        api = API()
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '99'}), \
             patch.object(m, 'verify_accepted_run', return_value={'head_sha': 'x' * 40}), \
             patch.object(m, 'validate_accepted_revision'), patch.object(m, 'validate_protection'), \
             patch.object(m, 'read_pr', side_effect=[old, updated]), patch.object(m, 'branch_sha', return_value='d' * 40), \
             patch.object(m, 'validate_dev_chain', return_value=1), patch.object(m, 'sha256_tree', return_value='e' * 40), \
             patch.object(m, 'refuse_latest_ci_failure'), patch.object(m, 'check_independent_shape'), \
             patch.object(m.time, 'monotonic', return_value=5):
            self.assertEqual(m.update_dev_branch(api, request, request['head'], 100), updated)
        puts = [call for call in api.calls if call[1] == 'PUT']
        self.assertEqual(len(puts), 1)
        self.assertEqual(puts[0][0], 'pulls/17/update-branch')
        self.assertEqual(puts[0][2], {'expected_head_sha': request['head']})

        exhausted = API()
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '99'}), \
             patch.object(m, 'verify_accepted_run', return_value={'head_sha': 'x' * 40}), \
             patch.object(m, 'validate_accepted_revision'), patch.object(m, 'validate_protection'), \
             patch.object(m, 'read_pr', return_value=old), patch.object(m, 'branch_sha', return_value='d' * 40), \
             patch.object(m, 'validate_dev_chain', return_value=3), patch.object(m, 'is_ancestor', return_value=False), \
             patch.object(m.time, 'monotonic', return_value=5):
            with self.assertRaisesRegex(ValueError, 'three dev integration updates exhausted'):
                m.update_dev_branch(exhausted, request, request['head'], 100)
        self.assertFalse(any(call[1] == 'PUT' for call in exhausted.calls))

        protection_changed = API()
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '99'}), \
             patch.object(m, 'verify_accepted_run', return_value={'head_sha': 'x' * 40}), \
             patch.object(m, 'validate_accepted_revision'), \
             patch.object(m, 'validate_protection', side_effect=ValueError('strict protection changed')), \
             patch.object(m.time, 'monotonic', return_value=5), \
             self.assertRaisesRegex(ValueError, 'strict protection changed'):
            m.update_dev_branch(protection_changed, request, request['head'], 100)
        self.assertFalse(any(call[1] == 'PUT' for call in protection_changed.calls))

        blocked = API()
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '99'}), \
             patch.object(m, 'verify_accepted_run', return_value={'head_sha': 'x' * 40}), \
             patch.object(m, 'validate_accepted_revision'), patch.object(m, 'validate_protection'), \
             patch.object(m, 'read_pr', return_value=old), patch.object(m, 'branch_sha', return_value='d' * 40), \
             patch.object(m, 'validate_dev_chain', return_value=1), patch.object(m, 'sha256_tree', side_effect=ValueError('conflict')), \
             patch.object(m.time, 'monotonic', return_value=5):
            with self.assertRaisesRegex(ValueError, 'conflict'):
                m.update_dev_branch(blocked, request, request['head'], 100)
        self.assertFalse(any(call[1] == 'PUT' for call in blocked.calls))

        ambiguous = API()
        ambiguous.request = Mock(side_effect=m.urllib.error.URLError('response lost'))
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '99'}), \
             patch.object(m, 'verify_accepted_run', return_value={'head_sha': 'x' * 40}), \
             patch.object(m, 'validate_accepted_revision'), patch.object(m, 'validate_protection'), \
             patch.object(m, 'read_pr', side_effect=[old, updated]), patch.object(m, 'branch_sha', return_value='d' * 40), \
             patch.object(m, 'validate_dev_chain', return_value=1), patch.object(m, 'sha256_tree', return_value='e' * 40), \
             patch.object(m, 'refuse_latest_ci_failure'), patch.object(m, 'check_independent_shape'), \
             patch.object(m.time, 'monotonic', return_value=5):
            self.assertEqual(m.update_dev_branch(ambiguous, request, request['head'], 100), updated)
        self.assertEqual(ambiguous.request.call_count, 1)

    # FIXTURE repository/conditional-protected-merge
    def test_latest_failed_required_check_refuses_before_dev_update(self):
        head = 'b' * 40
        api = API({('PAGES', f"actions/workflows/ci.yml/runs?head_sha={head}&event=pull_request&per_page=100"): [],
                   ('PAGES', f"commits/{head}/check-runs?per_page=100"): [
                       {'id': 42, 'name': 'Required checks', 'app': {'id': m.APP_ID},
                        'status': 'completed', 'conclusion': 'cancelled'}]})
        with self.assertRaisesRegex(ValueError, 'newest Required checks run did not pass'):
            m.refuse_latest_ci_failure(api, head)

    # FIXTURE repository/conditional-protected-merge
    def test_accepted_dev_tooling_allows_unrelated_move_but_refuses_safety_path_change(self):
        api = API()
        run = {'head_sha': 'a' * 40}
        with patch.object(m, 'branch_sha', return_value='b' * 40), \
             patch.object(m, 'is_ancestor', return_value=True), \
             patch.object(m.subprocess, 'run', side_effect=[type('R', (), {'returncode': 0})(),
                                                             type('R', (), {'returncode': 1})()]) as calls:
            with self.assertRaisesRegex(ValueError, 'safety paths changed'):
                m.validate_accepted_revision(api, run, 'dev')
        self.assertEqual(calls.call_args.args[0][-len(m.SAFETY_PATHS):], list(m.SAFETY_PATHS))
        with patch.object(m, 'branch_sha', return_value='b' * 40), patch.object(m, 'is_ancestor', return_value=True), \
             patch.object(m.subprocess, 'run', return_value=type('R', (), {'returncode': 0})()) as calls:
            self.assertEqual(m.validate_accepted_revision(api, run, 'dev', allow_recovery=True), 'b' * 40)
            self.assertEqual(calls.call_count, 1)  # fetch only; recovery does not reinterpret old execution safety

    # FIXTURE repository/conditional-protected-merge
    def test_dev_integration_chain_is_clean_bounded_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / 'repo'
            subprocess.run(['git', 'init', '-q', '-b', 'dev', str(repo)], check=True)
            def git(*args, **kwargs):
                return subprocess.run(['git', *args], cwd=repo, check=True, text=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs).stdout.strip()
            git('config', 'user.name', 'Fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            (repo / 'shared.txt').write_text('base\n')
            git('add', 'shared.txt')
            git('commit', '-qm', 'base')
            source_base = git('rev-parse', 'HEAD')
            git('switch', '-qc', 'topic')
            (repo / 'shared.txt').write_text('topic\n')
            git('commit', '-qam', 'approved source')
            source_head = git('rev-parse', 'HEAD')
            git('switch', '-q', 'dev')
            (repo / 'dev.txt').write_text('accepted dev change\n')
            git('add', 'dev.txt')
            git('commit', '-qm', 'accepted dev change')
            base_b = git('rev-parse', 'HEAD')
            clean_tree = git('merge-tree', '--write-tree', source_head, base_b).splitlines()[0]
            env = {**os.environ, 'GIT_AUTHOR_NAME': 'Fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
                   'GIT_COMMITTER_NAME': 'Fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid'}
            integrated = subprocess.run(['git', 'commit-tree', clean_tree, '-p', source_head, '-p', base_b],
                                        cwd=repo, env=env, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
            (repo / 'later.txt').write_text('later accepted dev\n')
            git('add', 'later.txt')
            git('commit', '-qm', 'later accepted dev')
            current_dev = git('rev-parse', 'HEAD')
            def merge_commit(first, second):
                tree = git('merge-tree', '--write-tree', first, second).splitlines()[0]
                return subprocess.run(['git', 'commit-tree', tree, '-p', first, '-p', second],
                                      cwd=repo, env=env, check=True, text=True,
                                      stdout=subprocess.PIPE).stdout.strip()
            integrated2 = merge_commit(integrated, current_dev)
            integrated3 = merge_commit(integrated2, current_dev)
            integrated4 = merge_commit(integrated3, current_dev)
            extra_source = subprocess.run(['git', 'commit-tree', git('rev-parse', f'{integrated}^{{tree}}'),
                                           '-p', integrated], cwd=repo, env=env, check=True, text=True,
                                          stdout=subprocess.PIPE).stdout.strip()
            (repo / 'shared.txt').write_text('dev conflict\n')
            git('add', 'shared.txt')
            git('commit', '-qm', 'conflicting dev update')
            conflict_dev = git('rev-parse', 'HEAD')
            conflict_result = subprocess.run(['git', 'merge-tree', '--write-tree', source_head, conflict_dev],
                                             cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            conflict_tree = conflict_result.stdout.splitlines()[0]
            conflict_merge = subprocess.run(['git', 'commit-tree', conflict_tree, '-p', source_head,
                                              '-p', conflict_dev], cwd=repo, env=env, check=True, text=True,
                                             stdout=subprocess.PIPE).stdout.strip()
            git('remote', 'add', 'origin', str(repo))
            request = {'source_base': source_base, 'base': source_base,
                       'source_head': source_head, 'head': source_head}
            previous = Path.cwd()
            os.chdir(repo)
            try:
                self.assertEqual(m.validate_dev_chain(request, integrated, current_dev), 1)
                self.assertEqual(m.validate_dev_chain(request, integrated3, current_dev), 3)
                with self.assertRaisesRegex(ValueError, 'exceeds three updates'):
                    m.validate_dev_chain(request, integrated4, current_dev)
                with self.assertRaisesRegex(ValueError, 'malformed integration'):
                    m.validate_dev_chain(request, extra_source, current_dev)
                with self.assertRaisesRegex(ValueError, 'not conflict-free'):
                    m.validate_dev_chain(request, conflict_merge, conflict_dev)
                bad_tree = subprocess.run(['git', 'commit-tree', git('rev-parse', f'{source_head}^{{tree}}'),
                                           '-p', source_head, '-p', base_b], cwd=repo, env=env, check=True,
                                          text=True, stdout=subprocess.PIPE).stdout.strip()
                with self.assertRaisesRegex(ValueError, 'non-deterministic tree'):
                    m.validate_dev_chain(request, bad_tree, current_dev)
                arbitrary = subprocess.run(['git', 'commit-tree', git('rev-parse', f'{source_head}^{{tree}}'),
                                             '-p', source_head], cwd=repo, env=env, check=True,
                                            text=True, stdout=subprocess.PIPE).stdout.strip()
                with self.assertRaisesRegex(ValueError, 'malformed integration'):
                    m.validate_dev_chain(request, arbitrary, current_dev)
            finally:
                os.chdir(previous)

    # FIXTURE repository/conditional-protected-merge
    def test_finish_recovers_only_approved_integration_and_uses_actual_tested_base(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / 'repo'
            subprocess.run(['git', 'init', '-q', '-b', 'dev', str(repo)], check=True)
            def git(*args):
                return subprocess.run(['git', *args], cwd=repo, check=True, text=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()
            git('config', 'user.name', 'Fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            (repo / 'base.txt').write_text('A\n')
            git('add', 'base.txt')
            git('commit', '-qm', 'admitted base A')
            source_base = git('rev-parse', 'HEAD')
            git('switch', '-qc', 'topic')
            (repo / 'topic.txt').write_text('approved source H\n')
            git('add', 'topic.txt')
            git('commit', '-qm', 'approved source')
            source_head = git('rev-parse', 'HEAD')
            git('switch', '-q', 'dev')
            (repo / 'dev.txt').write_text('accepted dev B\n')
            git('add', 'dev.txt')
            git('commit', '-qm', 'accepted dev B')
            base_b = git('rev-parse', 'HEAD')
            tree_i = git('merge-tree', '--write-tree', source_head, base_b).splitlines()[0]
            env = {**os.environ, 'GIT_AUTHOR_NAME': 'Fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
                   'GIT_COMMITTER_NAME': 'Fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid'}
            integration = subprocess.run(['git', 'commit-tree', tree_i, '-p', source_head, '-p', base_b],
                                          cwd=repo, env=env, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
            merge_commit = subprocess.run(['git', 'commit-tree', tree_i, '-p', base_b, '-p', integration],
                                          cwd=repo, env=env, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
            (repo / 'later.txt').write_text('later dev C\n')
            git('add', 'later.txt')
            git('commit', '-qm', 'later dev C')
            current_dev = git('rev-parse', 'HEAD')
            git('remote', 'add', 'origin', str(repo))
            request = {'pr': 17, 'target': 'dev', 'head': source_head, 'source_head': source_head,
                       'base': source_base, 'source_base': source_base, 'repo': 'shk95/configs'}
            request['head'] = integration
            pr = {'merge_commit_sha': merge_commit, 'head': {'sha': integration}}
            api = API({'git/ref/heads/dev': {'object': {'sha': current_dev}}})
            original_run = m.subprocess.run
            def run(command, *args, **kwargs):
                if command[0] == 'tool/version-control/audit' or command == ['tool/version-control/audit-remote']:
                    return type('Result', (), {'returncode': 0, 'stdout': 'passed'})()
                if command[:3] == ['git', 'fetch', '--quiet'] and 'dev' in command and 'master' in command:
                    return type('Result', (), {'returncode': 0, 'stdout': ''})()
                return original_run(command, *args, **kwargs)
            previous = Path.cwd()
            os.chdir(repo)
            outputs = []
            source_evidence = Mock(return_value=({'id': 20}, 'success'))
            try:
                with patch.object(m.subprocess, 'run', side_effect=run), \
                     patch.object(m, 'source_run', source_evidence), \
                     patch('builtins.print', side_effect=lambda *args, **kwargs: outputs.append(args[0])):
                    m.finish(api, request, pr, 'already merged')
                record = json.loads(outputs[-1])
                self.assertEqual(record['approved_source_head'], source_head)
                self.assertEqual(record['integration_head'], integration)
                self.assertEqual(record['tested_base'], base_b)
                self.assertEqual(source_evidence.call_args.args[1]['base'], base_b)
                self.assertEqual(source_evidence.call_args.args[1]['head'], integration)
                wrong = dict(request, source_head=base_b)
                with patch.object(m.subprocess, 'run', side_effect=run), patch.object(m, 'source_run', source_evidence), \
                     patch('builtins.print'):
                    with self.assertRaisesRegex(ValueError, 'post-merge identity or audit failed'):
                        m.finish(api, wrong, pr, 'already merged')
            finally:
                os.chdir(previous)

    # FIXTURE repository/conditional-protected-merge
    def test_changed_target_and_ambiguous_merge_never_retry(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40}
        args = type('Args', (), {'run_id': '99', **request})()
        active = {'created_at': NOW()}
        pr = {'state': 'open', 'merged_at': None, '_conditional_waiting': False,
              'head': {'sha': request['head']}, 'base': {'sha': request['base']}}
        env = {'GITHUB_RUN_ID': '99', 'GITHUB_REPOSITORY': 'shk95/configs', 'GITHUB_ACTOR': 'maintainer',
               'GH_TOKEN': 'fixture', 'CONFIGS_MERGE_ENABLED': '1'}
        common = [patch.object(m, 'repo_name', return_value='shk95/configs'),
                  patch.object(m, 'verify_accepted_run', return_value=active), patch.object(m, 'validate_actor'),
                  patch.object(m, 'validate_protection'), patch.object(m, 'check_independent_shape'),
                  patch.object(m, 'read_pr', return_value=pr), patch.object(m, 'sha256_tree', return_value='d' * 40),
                  patch.object(m, 'validate_dev_chain', return_value=0), patch.object(m, 'is_ancestor', return_value=True),
                  patch.object(m, 'source_run', return_value=({'id': 10}, 'success')), patch.object(m.time, 'monotonic', return_value=1)]
        moved = API()
        master_request = {'pr': 17, 'target': 'master', 'head': 'b' * 40, 'base': 'a' * 40}
        master_args = type('Args', (), {'run_id': '99', **master_request})()
        master_pr = {'state': 'open', 'merged_at': None, '_conditional_waiting': False,
                     'head': {'sha': master_request['head']}, 'base': {'sha': master_request['base']}}
        master_common = [patch.object(m, 'repo_name', return_value='shk95/configs'),
                         patch.object(m, 'verify_accepted_run', return_value=active), patch.object(m, 'validate_actor'),
                         patch.object(m, 'read_pr', return_value=master_pr), patch.object(m, 'validate_protection'),
                         patch.object(m, 'check_independent_shape')]
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, env))
            stack.enter_context(patch.object(m, 'GitHub', return_value=moved))
            stack.enter_context(patch.object(m, 'branch_sha', return_value='e' * 40))
            for context in master_common:
                stack.enter_context(context)
            with self.assertRaisesRegex(ValueError, 'master target or source head moved'):
                m.write_run(master_args)
        self.assertFalse(any(call[1] == 'PUT' for call in moved.calls))

        ambiguous = API()
        ambiguous.request = Mock(side_effect=lambda path, method='GET', data=None, binary=False:
            (_ for _ in ()).throw(m.urllib.error.URLError('connection lost')) if method == 'PUT'
            else {'state': 'open', 'merged_at': None, 'head': {'sha': request['head']},
                  'base': {'sha': request['base']}, '_conditional_waiting': False})
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, env))
            stack.enter_context(patch.object(m, 'GitHub', return_value=ambiguous))
            stack.enter_context(patch.object(m, 'branch_sha', return_value=request['base']))
            for context in common:
                stack.enter_context(context)
            with self.assertRaisesRegex(ValueError, 'inspect GitHub before retrying'):
                m.write_run(args)
        put_calls = [call for call in ambiguous.request.call_args_list if call.kwargs.get('method') == 'PUT']
        self.assertEqual(len(put_calls), 1)

    # FIXTURE repository/conditional-protected-merge
    def test_merged_recovery_verifies_result_without_another_write(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40}
        args = type('Args', (), {'run_id': '99', **request})()
        api = API()
        merged = {'state': 'closed', 'merged_at': '2026-10-06T12:02:00Z',
                  'head': {'sha': request['head']}, 'merge_commit_sha': 'c' * 40}
        with patch.dict(os.environ, {'GITHUB_RUN_ID': '99', 'GITHUB_REPOSITORY': 'shk95/configs',
                                     'GITHUB_ACTOR': 'maintainer', 'GH_TOKEN': 'fixture', 'CONFIGS_MERGE_ENABLED': '1'}), \
             patch.object(m, 'repo_name', return_value='shk95/configs'), patch.object(m, 'GitHub', return_value=api), \
             patch.object(m, 'verify_accepted_run', return_value={'created_at': '2026-10-06T10:00:00Z'}), \
             patch.object(m, 'validate_actor'), patch.object(m, 'read_pr', return_value=merged), \
             patch.object(m, 'validate_dev_chain', return_value=0), patch.object(m, 'branch_sha', return_value='c' * 40), \
             patch.object(m, 'finish', return_value='already merged') as finish:
            self.assertEqual(m.write_run(args), 'already merged')
        self.assertEqual(finish.call_args.args[1]['source_head'], 'b' * 40)
        self.assertEqual(finish.call_args.args[3], 'already merged')
        self.assertFalse(any(call[1] == 'PUT' for call in api.calls))

    # FIXTURE repository/conditional-protected-merge
    def test_finish_binds_merge_parents_tree_and_reports_postmerge_audit_failure(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40, 'repo': 'shk95/configs'}
        pr = {'merge_commit_sha': 'c' * 40, 'head': {'sha': 'b' * 40}}
        outputs = []
        audit_ok = type('Result', (), {'returncode': 0, 'stdout': 'passed'})()
        audit_fail = type('Result', (), {'returncode': 1, 'stdout': 'remote audit failed'})()
        with patch.object(m.subprocess, 'run', return_value=audit_ok), \
             patch.object(m.subprocess, 'check_output', side_effect=['a' * 40 + ' ' + 'b' * 40, 'd' * 40]), \
             patch.object(m, 'sha256_tree', return_value='d' * 40), patch.object(m, 'source_run', return_value=({'id': 1}, 'success')), \
             patch.object(m, 'branch_sha', return_value='a' * 40), \
             patch.object(m, 'is_ancestor', return_value=True), patch.object(m, 'validate_dev_chain', return_value=0), \
             patch('builtins.print', side_effect=lambda *args, **kwargs: outputs.append(args[0])):
            m.finish(API(), request, pr, 'merged')
        self.assertIn('"state": "merged"', outputs[-1])

        outputs.clear()
        with patch.object(m.subprocess, 'run', side_effect=[audit_ok, audit_ok, audit_ok, audit_fail]), \
             patch.object(m.subprocess, 'check_output', side_effect=['a' * 40 + ' ' + 'b' * 40, 'd' * 40]), \
             patch.object(m, 'sha256_tree', return_value='d' * 40), patch.object(m, 'source_run', return_value=({'id': 1}, 'success')), \
             patch.object(m, 'branch_sha', return_value='a' * 40), \
             patch.object(m, 'is_ancestor', return_value=True), patch.object(m, 'validate_dev_chain', return_value=0), \
             patch('builtins.print', side_effect=lambda *args, **kwargs: outputs.append(args[0])):
            with self.assertRaisesRegex(ValueError, 'merge completed; post-merge'):
                m.finish(API(), request, pr, 'merged')
        self.assertIn('"state": "merged-with-audit-failure"', outputs[0])

        for parents, tree in ((['e' * 40, 'b' * 40], 'd' * 40),
                              (['a' * 40, 'b' * 40], 'f' * 40)):
            with self.subTest(parents=parents, tree=tree), patch.object(m.subprocess, 'run', return_value=audit_ok), \
                 patch.object(m.subprocess, 'check_output', side_effect=[' '.join(parents), tree]), \
                 patch.object(m, 'sha256_tree', return_value='d' * 40), patch.object(m, 'source_run', return_value=({'id': 1}, 'success')), \
                 patch.object(m, 'branch_sha', return_value='a' * 40), \
                 patch.object(m, 'is_ancestor', return_value=True), patch.object(m, 'validate_dev_chain', return_value=0), \
                 patch('builtins.print'):
                with self.assertRaisesRegex(ValueError, 'post-merge identity or audit failed'):
                    m.finish(API(), request, pr, 'merged')

    # FIXTURE repository/conditional-protected-merge
    def test_workflow_serializes_writers_without_replacing_pending_runs(self):
        workflow = (ROOT / '.github/workflows/conditional-merge.yml').read_text()
        release = (ROOT / '.github/workflows/release.yml').read_text()
        self.assertIn("queue: max", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn("'configs-release-writes'", workflow)
        self.assertIn('group: configs-release-writes', release)
        self.assertIn('queue: max', release)
        self.assertIn('environment: merge-control', workflow)
        self.assertIn('CONFIGS_MERGE_ENABLED', workflow)
        self.assertIn('ref: ${{ github.sha }}', workflow)
        self.assertNotIn('ref: ${{ inputs.head }}', workflow)
        self.assertIn('permission-contents: write', workflow)
        self.assertIn('Recheck queued request before minting writer token', workflow)
        self.assertIn('test "$accepted" = "$ACCEPTED_SHA"', workflow)
        self.assertNotIn('  members: read', workflow)

    # FIXTURE repository/conditional-protected-merge
    def test_remote_audit_accepts_strict_protection_on_both_targets_and_refuses_false_master(self):
        with tempfile.TemporaryDirectory() as name:
            temp = Path(name)
            bindir = temp / 'bin'
            bindir.mkdir()
            script = temp / 'audit-remote'
            shutil.copy(ROOT / 'tool/version-control/audit-remote', script)
            (temp / 'work').write_text('#!/bin/sh\nexit 0\n')
            (temp / 'work').chmod(0o755)
            gh = bindir / 'gh'
            gh.write_text('''#!/bin/sh
set -eu
case "$1" in
  auth) exit 0 ;;
  repo)
    case "$*" in *defaultBranchRef*) echo master ;; *) echo shk95/configs ;; esac
    exit 0 ;;
  api)
    query=
    path=
    previous=
    for arg in "$@"; do
      if [ "$previous" = jq ]; then query=$arg; fi
      [ "$arg" = --jq ] && previous=jq || previous=
      case "$arg" in repos/*) path=$arg ;; esac
    done
    case "$path:$query" in
      *branches/dev/protection*contexts*) echo 'Required checks' ;;
      *branches/master/protection*contexts*) echo 'Required checks' ;;
      *branches/dev/protection*strict*) echo true ;;
      *branches/master/protection*strict*) echo "${STRICT_MASTER:-true}" ;;
      *branches/*/protection*allow_force_pushes*) echo true ;;
      *branches/*/protection*) echo '{}' ;;
      *pulls?state=*) : ;;
      *allow_merge_commit*) echo true ;;
      *) echo '[]' ;;
    esac
    ;;
  *) exit 2 ;;
esac
''')
            gh.chmod(0o755)
            environment = dict(os.environ, PATH=f'{bindir}:{os.environ["PATH"]}')
            passed = subprocess.run([str(script)], cwd=ROOT, env={**environment, 'STRICT_MASTER': 'true'},
                                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertEqual(passed.returncode, 0, passed.stdout)
            failed = subprocess.run([str(script)], cwd=ROOT, env={**environment, 'STRICT_MASTER': 'false'},
                                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('master strict status-check setting is false, expected true', failed.stdout)


if __name__ == '__main__':
    unittest.main()
