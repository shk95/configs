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
from unittest.mock import Mock, patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('conditional_merge', ROOT / 'tool/version-control/conditional-merge.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


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
        for field, value in (('head_sha', 'd' * 40), ('base_ref', 'master'), ('repo', 'fork/configs')):
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
        with patch.object(m, 'branch_sha', return_value='d' * 40), self.assertRaisesRegex(ValueError, 'no longer current'):
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
        with patch.object(m, 'branch_sha', return_value='a' * 40), self.assertRaisesRegex(ValueError, 'not active'):
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
    def test_ambiguous_dispatch_is_never_retried(self):
        args = type('Args', (), {'confirm': True, 'pr': 17, 'target': 'dev', 'head': 'b' * 40,
                                 'base': 'a' * 40})()
        api = API()
        api.request = Mock(side_effect=m.urllib.error.URLError('timed out'))
        with patch.dict(os.environ, {'GH_TOKEN': 'fixture'}), patch.object(m, 'repo_name', return_value='shk95/configs'), patch.object(m, 'GitHub', return_value=api), \
             patch.object(m, 'read_pr', return_value={'number': 17}), patch.object(m, 'branch_sha', return_value='a' * 40), \
             patch('builtins.print'):
            with self.assertRaisesRegex(ValueError, 'inspect Actions before retrying'):
                m.submit(args)
        self.assertEqual(api.request.call_count, 1)

    # FIXTURE repository/conditional-protected-merge
    def test_write_orchestration_submits_once_only_after_exact_ci_and_protection(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40}
        args = type('Args', (), {'run_id': '99', **request})()
        active = {'created_at': '2026-10-06T12:00:00Z'}
        open_pr = {'state': 'open', 'merged_at': None, '_conditional_waiting': False}
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
        active = {'created_at': '2026-10-06T12:00:00Z'}
        pr = {'state': 'open', 'merged_at': None, '_conditional_waiting': False}
        base_api = API()
        env = {'GITHUB_RUN_ID': '99', 'GITHUB_REPOSITORY': 'shk95/configs', 'GITHUB_ACTOR': 'maintainer',
               'GH_TOKEN': 'fixture', 'CONFIGS_MERGE_ENABLED': '1'}
        with patch.dict(os.environ, env), patch.object(m, 'repo_name', return_value='shk95/configs'), \
             patch.object(m, 'GitHub', return_value=base_api), patch.object(m, 'verify_accepted_run', return_value=active), \
             patch.object(m, 'validate_actor'), patch.object(m, 'validate_protection'), patch.object(m, 'check_independent_shape'), \
             patch.object(m, 'read_pr', return_value=pr), patch.object(m, 'branch_sha', return_value=request['base']), \
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
             patch.object(m, 'sha256_tree', return_value='d' * 40), patch.dict(os.environ, env):
            with self.assertRaisesRegex(ValueError, '60-minute CI wait expired'):
                m.write_run(args)
        self.assertFalse(any(call[1] == 'PUT' for call in waiting_api.calls))

    # FIXTURE repository/conditional-protected-merge
    def test_changed_target_and_ambiguous_merge_never_retry(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40}
        args = type('Args', (), {'run_id': '99', **request})()
        active = {'created_at': '2026-10-06T12:00:00Z'}
        pr = {'state': 'open', 'merged_at': None, '_conditional_waiting': False}
        env = {'GITHUB_RUN_ID': '99', 'GITHUB_REPOSITORY': 'shk95/configs', 'GITHUB_ACTOR': 'maintainer',
               'GH_TOKEN': 'fixture', 'CONFIGS_MERGE_ENABLED': '1'}
        common = [patch.object(m, 'repo_name', return_value='shk95/configs'),
                  patch.object(m, 'verify_accepted_run', return_value=active), patch.object(m, 'validate_actor'),
                  patch.object(m, 'validate_protection'), patch.object(m, 'check_independent_shape'),
                  patch.object(m, 'read_pr', return_value=pr), patch.object(m, 'sha256_tree', return_value='d' * 40),
                  patch.object(m, 'source_run', return_value=({'id': 10}, 'success')), patch.object(m.time, 'monotonic', return_value=1)]
        moved = API()
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, env))
            stack.enter_context(patch.object(m, 'GitHub', return_value=moved))
            stack.enter_context(patch.object(m, 'branch_sha', side_effect=[request['base'], 'e' * 40]))
            for context in common:
                stack.enter_context(context)
            with self.assertRaisesRegex(ValueError, 'target moved before merge'):
                m.write_run(args)
        self.assertFalse(any(call[1] == 'PUT' for call in moved.calls))

        ambiguous = API()
        ambiguous.request = Mock(side_effect=lambda path, method='GET', data=None, binary=False:
            (_ for _ in ()).throw(m.urllib.error.URLError('connection lost')) if method == 'PUT'
            else {'state': 'open', 'merged_at': None, 'head': {'sha': request['head']}})
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
             patch.object(m, 'finish', return_value='already merged') as finish:
            self.assertEqual(m.write_run(args), 'already merged')
        finish.assert_called_once_with(api, {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40,
                                              'repo': 'shk95/configs'}, merged, 'already merged')
        self.assertFalse(any(call[1] == 'PUT' for call in api.calls))

    # FIXTURE repository/conditional-protected-merge
    def test_finish_binds_merge_parents_tree_and_reports_postmerge_audit_failure(self):
        request = {'pr': 17, 'target': 'dev', 'head': 'b' * 40, 'base': 'a' * 40, 'repo': 'shk95/configs'}
        pr = {'merge_commit_sha': 'c' * 40}
        outputs = []
        audit_ok = type('Result', (), {'returncode': 0, 'stdout': 'passed'})()
        audit_fail = type('Result', (), {'returncode': 1, 'stdout': 'remote audit failed'})()
        with patch.object(m.subprocess, 'run', return_value=audit_ok), \
             patch.object(m.subprocess, 'check_output', side_effect=['a' * 40 + ' ' + 'b' * 40, 'd' * 40]), \
             patch.object(m, 'sha256_tree', return_value='d' * 40), \
             patch('builtins.print', side_effect=lambda *args, **kwargs: outputs.append(args[0])):
            m.finish(API(), request, pr, 'merged')
        self.assertIn('"state": "merged"', outputs[-1])

        outputs.clear()
        with patch.object(m.subprocess, 'run', side_effect=[audit_ok, audit_ok, audit_fail]), \
             patch.object(m.subprocess, 'check_output', side_effect=['a' * 40 + ' ' + 'b' * 40, 'd' * 40]), \
             patch.object(m, 'sha256_tree', return_value='d' * 40), \
             patch('builtins.print', side_effect=lambda *args, **kwargs: outputs.append(args[0])):
            with self.assertRaisesRegex(ValueError, 'merge completed; post-merge'):
                m.finish(API(), request, pr, 'merged')
        self.assertIn('"state": "merged-with-audit-failure"', outputs[0])

        for parents, tree in ((['e' * 40, 'b' * 40], 'd' * 40),
                              (['a' * 40, 'b' * 40], 'f' * 40)):
            with self.subTest(parents=parents, tree=tree), patch.object(m.subprocess, 'run', return_value=audit_ok), \
                 patch.object(m.subprocess, 'check_output', side_effect=[' '.join(parents), tree]), \
                 patch.object(m, 'sha256_tree', return_value='d' * 40), patch('builtins.print'):
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
