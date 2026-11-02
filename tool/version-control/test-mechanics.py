#!/usr/bin/env python3
"""Positive/refusal cases for repository-owned mechanics and remote evidence."""
# INV repository/mechanical-policy
# INV repository/workspace-preservation
# INV repository/exact-ci-proof
# INV repository/approved-history-rewrite
import sys
sys.dont_write_bytecode = True
import copy
import importlib.util
from importlib.machinery import SourceFileLoader
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tool/version-control'
sys.path.insert(0, str(SOURCE))
import repo_policy
import github_proof
import history_rewrite as history


def module(name, path):
    spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, str(path)))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


base_tests = module('workflow_fixtures', SOURCE / 'test-workflow.py')
workspaces = module('workspace_implementation', SOURCE / 'workspaces')


def archive(value):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as zipped:
        zipped.writestr('source.json', json.dumps(value))
    return stream.getvalue()


class Mechanics(unittest.TestCase):
    call = base_tests.Workflow.call
    git = base_tests.Workflow.git
    workflow = base_tests.Workflow.workflow
    commit = base_tests.Workflow.commit
    topic = base_tests.Workflow.topic

    def setUp(self):
        base_tests.Workflow.setUp(self)
        for name in ('workspaces', 'history-rewrite', 'history_rewrite.py', 'recovery.py'):
            shutil.copy(SOURCE / name, self.root / 'tool/version-control' / name)
        previous = Path.cwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)
        # Copying support tools is fixture setup, not an uncommitted candidate.
        self.base = self.commit('test(repository): mechanics fixture tools')

    def test_static_policy_refuses_unknown_schema_and_unsafe_commands(self):
        # INV repository/mechanical-policy
        policy = repo_policy.load()
        self.assertEqual(policy['base_branch'], 'master')
        path = self.root / 'tool/version-control/policy.json'
        for bad in [dict(policy, schema=8), dict(policy, private_override=True),
                    dict(policy, workspace_choices=['implicit']),
                    dict(policy, ci=dict(policy['ci'], suite_commands={'repository:fixtures': [['../escape']]}))]:
            path.write_text(json.dumps(bad))
            with patch.object(repo_policy, '__file__', str(path.with_name('repo_policy.py'))):
                with self.assertRaises(ValueError): repo_policy.load()

    def test_static_workflow_wiring_matches_the_declared_capabilities(self):
        # INV repository/mechanical-policy
        policy = repo_policy.load()
        ci = (ROOT / policy['ci']['workflow']).read_text()
        maintenance = (ROOT / policy['history_rewrite']['workflow']).read_text()
        release = (ROOT / '.github/workflows/release.yml').read_text()
        self.assertIn('branches: [' + policy['base_branch'] + ']', ci)
        self.assertIn('workflow_dispatch:', ci)
        self.assertIn('name: ' + policy['ci']['gate'], ci)
        self.assertIn('name: ' + policy['ci']['artifact'], ci)
        self.assertIn('accepted-tools/.github/scripts/ci-source.py', ci)
        rules = policy['history_rewrite']
        # Workflow-only wiring is declared in YAML, not mirrored in JSON.
        # Both remote writers must still serialize against each other.
        for text in [maintenance, release]: self.assertIn('group: configs-release-writes', text)
        self.assertIn('environment: ' + rules['environment'], maintenance)
        self.assertIn('vars.' + rules['app_id_variable'], maintenance)
        self.assertIn('secrets.CONFIGS_HISTORY_APP_PRIVATE_KEY', maintenance)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = ' + str(rules['attempts']), maintenance)
        self.assertNotIn('gh api --method', maintenance)
        for permission, access in history.APP_PERMISSIONS.items():
            if permission == 'variables':
                self.assertIn(f'INPUT_PERMISSION-VARIABLES: {access}', maintenance)
                self.assertNotIn('permission-variables:', maintenance)
            else:
                self.assertIn(f'permission-{permission}: {access}', maintenance)
        self.assertIn('permissions:\n  contents: read\n', ci)
        self.assertIn('permissions:\n      contents: read\n      pull-requests: read', ci)
        candidate_checkouts = ci.split('ref: ${{ inputs.head || github.sha }}')[1:]
        self.assertTrue(candidate_checkouts)
        for checkout in candidate_checkouts:
            self.assertIn('persist-credentials: false', checkout.split('\n      -', 1)[0])

    def test_start_record_is_inspectable_and_preview_does_not_replace_it(self):
        # INV repository/mechanical-policy
        self.workflow('start', '--scope', 'repository', '--commits', 'one', '--workspace', 'current')
        state = json.loads(self.workflow('inspect'))['work_record']
        self.assertEqual(state['base'], self.base)
        self.assertEqual(state['workspace'], 'current')
        self.workflow('start', '--scope', 'repository', '--commits', 'many', '--topic', 'preview', '--workspace', 'linked', '--dry-run')
        self.assertEqual(json.loads(self.workflow('inspect'))['work_record'], state)
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_removal_preserves_unique_dirty_ignored_and_primary_workspaces(self):
        # INV repository/workspace-preservation
        tool = str(self.root / 'tool/version-control/workspaces')
        refs = self.git('show-ref')
        self.call(tool, 'new', 'repository-disposable', ok=False)
        self.assertEqual(self.git('show-ref'), refs)
        self.workflow('start', '--scope', 'repository', '--commits', 'many',
                      '--topic', 'disposable', '--workspace', 'linked')
        linked = self.root.parent / 'repo-wt/feature-repository-disposable'
        (linked / 'docs/status/repository.md').write_text('unique\n')
        self.git('add', '.', cwd=linked)
        self.git('commit', '-qm', 'feat(repository): unique work', cwd=linked)
        head = self.git('rev-parse', 'HEAD', cwd=linked)
        review = json.loads(self.call(tool, 'review', str(linked)))
        self.assertEqual(review['unique_commits'], [head])
        self.assertEqual(review['retained_branch'], {'ref': 'refs/heads/feature/repository-disposable', 'head': head})
        self.assertTrue(review['removable'], 'The retained exact branch preserves unique Git history')
        self.call(tool, 'done', str(linked), '--expect-head', self.base, ok=False)
        exclude = self.root / '.git/info/exclude'
        exclude.parent.mkdir(exist_ok=True)
        exclude.write_text((exclude.read_text() if exclude.exists() else '') + '\ncache/\nnotes/\n')
        (linked / 'cache').mkdir()
        (linked / 'cache/data').write_text('preserve ignored')
        review = json.loads(self.call(tool, 'review', str(linked)))
        self.assertIn('cache/data', review['ignored'])
        self.call(tool, 'done', str(linked), '--expect-head', head, ok=False)
        (linked / 'cache/data').unlink()
        (linked / 'cache').rmdir()
        (linked / 'notes').mkdir()
        (linked / 'notes/do-not-read').write_text('private fixture scratch')
        review = self.call(tool, 'review', str(linked))
        self.assertNotIn('do-not-read', review)
        self.call(tool, 'done', str(linked), '--expect-head', head, ok=False)
        (linked / 'notes/do-not-read').unlink()
        (linked / 'notes').rmdir()
        (linked / 'untracked').write_text('preserve')
        self.call(tool, 'done', str(linked), '--expect-head', head, ok=False)
        (linked / 'untracked').unlink()
        (linked / 'docs/status/repository.md').write_text('dirty')
        self.call(tool, 'done', str(linked), '--expect-head', head, ok=False)
        self.git('restore', 'docs/status/repository.md', cwd=linked)
        operation = Path(self.git('rev-parse', '--path-format=absolute', '--git-path', 'MERGE_HEAD', cwd=linked))
        operation.write_text(head + '\n')
        self.call(tool, 'done', str(linked), '--expect-head', head, ok=False)
        self.assertTrue(operation.exists())
        operation.unlink()
        self.call(tool, 'done', str(self.root), '--expect-head', self.git('rev-parse', 'HEAD'), ok=False)
        self.call(tool, 'done', str(linked), '--expect-head', head)
        self.assertFalse(linked.exists())
        self.assertEqual(self.git('rev-parse', 'feature/repository-disposable'), head)

    def test_optional_external_recovery_is_validated_when_supplied(self):
        # INV repository/workspace-preservation
        tool = str(self.root / 'tool/version-control/workspaces')
        self.workflow('start', '--scope', 'repository', '--commits', 'many',
                      '--topic', 'archived', '--workspace', 'linked')
        linked = self.root.parent / 'repo-wt/feature-repository-archived'
        (linked / 'docs/status/repository.md').write_text('cancelled but preserved\n')
        self.git('add', '.', cwd=linked)
        self.git('commit', '-qm', 'feat(repository): preserved cancelled work', cwd=linked)
        head = self.git('rev-parse', 'HEAD', cwd=linked)
        bundle = self.root.parent / 'preserved.bundle'
        self.git('bundle', 'create', str(bundle), 'feature/repository-archived')
        damaged = self.root.parent / 'damaged.bundle'
        damaged.write_bytes(bundle.read_bytes()[:-10])
        self.call(tool, 'done', str(linked), '--expect-head', head, '--preserved-bundle', str(damaged), ok=False)
        self.assertTrue(linked.exists())
        self.call(tool, 'done', str(linked), '--expect-head', self.base, '--preserved-bundle', str(bundle), ok=False)
        self.call(tool, 'done', str(linked), '--expect-head', head, '--preserved-bundle', str(bundle))
        self.assertTrue(bundle.exists())
        self.assertFalse(linked.exists())
        self.assertEqual(self.git('rev-parse', 'feature/repository-archived'), head)

    def test_retained_branch_must_match_reviewed_workspace_identity(self):
        # INV repository/workspace-preservation
        tool = str(self.root / 'tool/version-control/workspaces')
        self.workflow('start', '--scope', 'repository', '--commits', 'many',
                      '--topic', 'identity', '--workspace', 'linked')
        linked = self.root.parent / 'repo-wt/feature-repository-identity'
        branch = 'feature/repository-identity'
        ref = 'refs/heads/' + branch
        (linked / 'docs/status/repository.md').write_text('unique retained work\n')
        self.git('add', '.', cwd=linked)
        self.git('commit', '-qm', 'feat(repository): retained source', cwd=linked)
        head = self.git('rev-parse', 'HEAD', cwd=linked)
        self.git('update-ref', '-d', ref)
        self.call(tool, 'done', str(linked), '--expect-head', head, ok=False)
        self.assertTrue(linked.exists(), 'A missing branch must not permit workspace removal')
        self.git('update-ref', ref, head)
        self.git('update-ref', ref, self.base)
        self.call(tool, 'done', str(linked), '--expect-head', head, ok=False)
        self.assertTrue(linked.exists(), 'A moved branch must not permit removal at the old reviewed SHA')
        self.git('update-ref', ref, head)
        self.git('checkout', '--detach', '-q', head, cwd=linked)
        self.call(tool, 'done', str(linked), '--expect-head', head, ok=False)
        self.assertTrue(linked.exists(), 'Detached HEAD has no retained named branch guarantee')
        self.git('switch', '-q', branch, cwd=linked)
        records = workspaces.registered()
        for item in records:
            if Path(item['worktree']).resolve() == linked.resolve():
                item['branch'] = 'refs/heads/feature/repository-other'
        with patch.object(workspaces, 'registered', return_value=records):
            review = workspaces.inventory(linked)
        self.assertFalse(review['removable'])
        self.assertIn('registered workspace identity differs from live HEAD/branch', review['blockers'])
        # A change during the two inventories stops before removal.
        inventory = workspaces.inventory
        calls = []
        def changed_inventory(*args, **kwargs):
            value = inventory(*args, **kwargs)
            if not calls:
                (linked / 'docs/status/repository.md').write_text('changed during review\n')
            calls.append(value)
            return value
        with patch.object(workspaces, 'inventory', side_effect=changed_inventory), \
             patch.object(sys, 'argv', ['workspaces', 'done', str(linked), '--expect-head', head]), \
             patch('sys.stdout', io.StringIO()):
            with self.assertRaisesRegex(ValueError, 'changed during preservation review'):
                workspaces.main()
        self.assertTrue(linked.exists())
        self.assertEqual(self.git('rev-parse', ref), head)
        self.git('restore', 'docs/status/repository.md', cwd=linked)
        self.call(tool, 'done', str(linked), '--expect-head', head, cwd=linked)
        self.assertEqual(self.git('rev-parse', ref), head)

    def proof_fixture(self):
        self.topic()
        tree = self.git('rev-parse', 'HEAD^{tree}')
        source = dict(base=self.base, head=self.head, tree=tree, event='workflow_dispatch')
        run = dict(repository={'full_name': 'fixture/configs'}, path='.github/workflows/ci.yml',
                   head_branch='master', head_sha=self.base, run_attempt=1, status='completed',
                   conclusion='success', event='workflow_dispatch', html_url='https://github.com/fixture/configs/actions/runs/7')
        jobs = {'jobs': [{'name': 'Required checks', 'conclusion': 'success'}]}
        artifacts = {'artifacts': [{'id': 8, 'name': 'ci-source', 'expired': False}]}
        def api(path, binary=False):
            if path.endswith('/runs/7'): return run
            if path.endswith('/attempts/1/jobs?per_page=100'): return jobs
            if path.endswith('/runs/7/artifacts?per_page=100'): return artifacts
            if path.endswith('/artifacts/8/zip'): return archive(source)
            raise AssertionError('Unexpected remote read: ' + path)
        return source, run, jobs, artifacts, api

    def test_live_ci_proof_accepts_exact_dispatch_and_rejects_mismatches(self):
        # INV repository/exact-ci-proof
        source, run, jobs, artifacts, api = self.proof_fixture()
        with patch.object(github_proof, 'api', api), patch.object(github_proof, 'repository', return_value='fixture/configs'):
            proof = github_proof.verify('7', self.base, self.head, source['tree'])
            self.assertEqual(proof['head'], self.head)
            for mapping, key, wrong in [(source, 'base', 'a'*40), (source, 'head', 'b'*40),
                                        (source, 'tree', 'c'*40), (source, 'event', 'push'),
                                        (run, 'path', '.github/workflows/other.yml'),
                                        (run, 'repository', {'full_name': 'fork/configs'}),
                                        (run, 'head_branch', 'feature/repository-untrusted'),
                                        (run, 'conclusion', 'failure'), (run, 'status', 'in_progress'),
                                        (jobs['jobs'][0], 'conclusion', 'failure'),
                                        (artifacts['artifacts'][0], 'expired', True)]:
                old = mapping[key]
                mapping[key] = wrong
                with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                    github_proof.verify('7', self.base, self.head, self.git('rev-parse', 'HEAD^{tree}'))
                mapping[key] = old
            artifacts['artifacts'].append(copy.deepcopy(artifacts['artifacts'][0]))
            with self.assertRaises(ValueError): github_proof.verify('7', self.base, self.head, source['tree'])
        with self.assertRaises(ValueError): github_proof.source_record(archive(dict(source, extra='field')))

    def test_hosted_proof_supplies_selected_suite_but_global_scans_still_run(self):
        # INV repository/exact-ci-proof
        source, run, jobs, artifacts, api = self.proof_fixture()
        implementation = module('workflow_implementation', SOURCE / 'workflow')
        # Select native Windows, unavailable on this host, without executing it.
        (self.root / 'tool/dispatch/select').write_text('#!/bin/sh\ncat >/dev/null\nprintf "windows:suite\\nwindows:runtime\\n"\n')
        head = self.commit('test(repository): native selection')
        source.update(head=head, tree=self.git('rev-parse', 'HEAD^{tree}'))
        with patch.object(implementation, 'verify', side_effect=lambda *a: github_proof.verify(*a)), \
             patch.object(github_proof, 'api', api), patch.object(github_proof, 'repository', return_value='fixture/configs'), \
             patch.dict(os.environ, PATH=str(self.root / 'tool') + os.pathsep + os.environ['PATH']):
            implementation.check(self.root, self.base, head, '7')
            with patch.dict(os.environ, FIXTURE_CHECK_STATUS='1'):
                with self.assertRaises(subprocess.CalledProcessError): implementation.check(self.root, self.base, head, '7')

    def history_fixture(self):
        (self.root / 'docs/status/repository.md').write_text('old unreleased result\n')
        old = self.commit('feat(repository): unreleased old result')
        remote = self.root.parent / 'remote.git'
        self.git('init', '-q', '--bare', str(remote))
        self.git('remote', 'add', 'origin', str(remote))
        self.git('push', '-q', 'origin', 'master')
        inputs = dict(old=old, new=self.base, reason='explicit fixture correction')
        event = self.root.parent / 'event.json'
        event.write_text(json.dumps({'inputs': inputs}))
        env = dict(GITHUB_ACTIONS='true', GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_REPOSITORY='fixture/configs',
                   GITHUB_REF='refs/heads/master', GITHUB_WORKFLOW_REF='fixture/configs/.github/workflows/history-rewrite.yml@refs/heads/master',
                   GITHUB_RUN_ATTEMPT='1', GITHUB_SHA=old, GITHUB_WORKFLOW_SHA=old,
                   GITHUB_EVENT_PATH=str(event), GITHUB_RUN_ID='9', CONFIGS_HISTORY_APP_SLUG='fixture-writer')
        environment = dict(id=3, can_admins_bypass=False, deployment_branch_policy={'protected_branches': False, 'custom_branch_policies': True}, protection_rules=[{'type': 'required_reviewers', 'reviewers': [{'type': 'User', 'reviewer': {'id': 4}}]}])
        reviews = [{'state': 'approved', 'user': {'id': 4}, 'environments': [{'id': 3}]}]
        artifacts = {'artifacts': [{'name': 'history-recovery', 'expired': False}]}
        rule = dict(id=41, name=repo_policy.load()['history_rewrite']['ruleset'], source_type='Repository',
                    source='fixture/configs', target='branch', enforcement='active',
                    bypass_actors=[{'actor_type': 'Integration', 'actor_id': 17, 'bypass_mode': 'always'}],
                    conditions={'ref_name': {'include': ['refs/heads/master'], 'exclude': []}},
                    rules=[{'type': 'non_fast_forward'}])
        def api(path, binary=False):
            if '/git/ref/heads/master' in path:
                return {'object': {'sha': self.git('--git-dir', str(remote), 'rev-parse', 'master')}}
            if path.endswith('/runs/9'): return {'path': '.github/workflows/history-rewrite.yml', 'head_sha': old, 'run_attempt': 1, 'event': 'workflow_dispatch', 'head_branch': 'master', 'status': 'in_progress', 'conclusion': None}
            if path.endswith('/environments/history-rewrite'): return environment
            if path.endswith('/deployment-branch-policies'): return {'branch_policies': [{'name': 'master', 'type': 'branch'}]}
            if path.endswith('/approvals'): return reviews
            if path.endswith('/protection'): return {'enforce_admins': {'enabled': True}, 'allow_deletions': {'enabled': False}, 'allow_force_pushes': {'enabled': True}}
            if path == 'apps/fixture-writer': return {'node_id': 'APP_fixture', 'id': 17, 'permissions': dict(history.APP_PERMISSIONS)}
            if path.endswith('/variables/CONFIGS_HISTORY_APP_ID'): return {'value': '17'}
            if path.endswith('/variables/CONFIGS_HISTORY_APP_NODE_ID'): return {'value': 'APP_fixture'}
            if path.endswith('/rulesets?includes_parents=true&per_page=100&page=1'): return [rule]
            if path.endswith('/rulesets/41?includes_parents=true'): return rule
            if path.endswith('/rules/branches/master?per_page=100&page=1'):
                return [dict(type='non_fast_forward', ruleset_source_type='Repository', ruleset_source='fixture/configs', ruleset_id=41)]
            if path.endswith('/artifacts'): return artifacts
            raise AssertionError(path)
        return inputs, env, environment, reviews, artifacts, remote, api

    def test_recovery_tampering_and_remote_lease_race_never_overwrite_peer_work(self):
        # INV repository/approved-history-rewrite
        inputs, env, environment, reviews, artifacts, remote, api = self.history_fixture()
        with patch.dict(os.environ, env), patch.object(history, 'api', api), \
             patch.object(history, 'repository', return_value='fixture/configs'):
            destination = self.root.parent / 'recovery'
            history.prepare(str(destination), **inputs)
            bundle = destination / 'recovery.bundle'
            original = bundle.read_bytes()
            bundle.write_bytes(original + b'tampered')
            with self.assertRaises(ValueError): history.execute(destination)
            bundle.write_bytes(original)
            (self.root / 'docs/status/repository.md').write_text('peer work\n')
            peer = self.commit('feat(repository): peer work')
            real_call = subprocess.check_call
            def race(command, *args, **kwargs):
                if 'push' in command:
                    real_call(['git', '--git-dir', str(remote), 'fetch', '-q', str(self.root), peer])
                    real_call(['git', '--git-dir', str(remote), 'update-ref', 'refs/heads/master', peer])
                return real_call(command, *args, **kwargs)
            with patch.object(history.subprocess, 'check_call', side_effect=race):
                with self.assertRaises(ValueError): history.execute(destination)
            self.assertEqual(self.git('--git-dir', str(remote), 'rev-parse', 'master'), peer)

    def test_candidate_dispatch_requires_exact_current_master_and_candidate(self):
        # INV repository/exact-ci-proof
        self.topic()
        self.git('update-ref', 'refs/remotes/origin/master', self.base)
        env = dict(os.environ, EVENT_NAME='workflow_dispatch', DISPATCH_REF='refs/heads/master',
                   DISPATCH_BASE=self.base, DISPATCH_HEAD=self.head)
        command = str(ROOT / 'tool/dispatch/ci-base')
        self.assertEqual(self.call(command, env=env).strip(), self.base)
        for key, wrong in [('DISPATCH_REF', 'refs/heads/feature/repository-untrusted'),
                           ('DISPATCH_BASE', self.head), ('DISPATCH_HEAD', self.base), ('DISPATCH_HEAD', 'invalid')]:
            self.call(command, env=dict(env, **{key: wrong}), ok=False)

    def test_history_approval_rejects_missing_replayed_wrong_or_bypassed_authority(self):
        # INV repository/approved-history-rewrite
        inputs, env, environment, reviews, artifacts, remote, api = self.history_fixture()
        value = dict(inputs, repository='fixture/configs', branch='master')
        with self.assertRaises(ValueError): history.authorization(value)
        with patch.dict(os.environ, env), patch.object(history, 'api', api):
            self.assertEqual(history.authorization(value)['reviewer_id'], 4)
            for mapping, key, wrong in [(os.environ, 'GITHUB_RUN_ATTEMPT', '2'),
                                        (os.environ, 'GITHUB_WORKFLOW_SHA', self.base),
                                        (environment, 'can_admins_bypass', True),
                                        (environment, 'deployment_branch_policy', None),
                                        (reviews[0], 'state', 'rejected'),
                                        (reviews[0], 'user', {'id': 999})]:
                original = mapping[key]
                mapping[key] = wrong
                with self.assertRaises(ValueError): history.authorization(value)
                mapping[key] = original
            changed = dict(value, reason='not the approved reason')
            with self.assertRaises(ValueError): history.authorization(changed)

    def test_approved_lease_has_recovery_and_never_changes_protection(self):
        # INV repository/approved-history-rewrite
        inputs, env, environment, reviews, artifacts, remote, api = self.history_fixture()
        with patch.dict(os.environ, env), patch.object(history, 'api', api), \
             patch.object(history, 'repository', return_value='fixture/configs'):
            destination = self.root.parent / 'recovery'
            value = history.prepare(str(destination), **inputs)
            self.assertTrue((destination / 'recovery.bundle').exists())
            artifacts['artifacts'].clear()
            with self.assertRaises(ValueError): history.execute(destination)
            self.assertEqual(self.git('--git-dir', str(remote), 'rev-parse', 'master'), inputs['old'])
            artifacts['artifacts'].append({'name': 'history-recovery', 'expired': False})
            result = history.execute(destination)
            self.assertEqual(result['new'], inputs['new'])
            self.assertEqual(result['protection'], 'unchanged')
            self.assertIn('bundle_sha256', value)

    def test_force_ruleset_refuses_other_actors_targets_sources_or_unconfigured_permission(self):
        # INV repository/approved-history-rewrite
        ruleset = dict(id=41, name=repo_policy.load()['history_rewrite']['ruleset'], source_type='Repository',
                       source='fixture/configs', target='branch', enforcement='active',
                       bypass_actors=[dict(actor_type='Integration', actor_id=17, bypass_mode='always')],
                       conditions={'ref_name': {'include': ['refs/heads/master'], 'exclude': []}},
                       rules=[{'type': 'non_fast_forward'}])
        summary = {key: ruleset[key] for key in ('id', 'name', 'source_type', 'source', 'enforcement')}
        inventory = [summary]
        effective = [dict(type='non_fast_forward', ruleset_source_type='Repository', ruleset_source='fixture/configs', ruleset_id=41)]
        protection = {'allow_force_pushes': {'enabled': True}}
        def api(path, binary=False):
            if path.endswith('/rulesets?includes_parents=true&per_page=100&page=1'): return inventory
            if path.endswith('/rulesets/41?includes_parents=true'): return ruleset
            if path.endswith('/rules/branches/master?per_page=100&page=1'): return effective
            if path.endswith('/variables/CONFIGS_HISTORY_APP_ID'): return {'value': '17'}
            if path.endswith('/variables/CONFIGS_HISTORY_APP_NODE_ID'): return {'value': 'APP_fixture'}
            raise AssertionError(path)
        with patch.object(history, 'api', api):
            self.assertEqual(history.audit_force_actor('fixture/configs', protection),
                             dict(enabled=True, actor='APP_fixture', app_id=17, ruleset_id=41))
            for key, wrong in [('bypass_actors', []), ('bypass_actors', None),
                               ('bypass_actors', [dict(actor_type='User', actor_id=17, bypass_mode='always')]),
                               ('bypass_actors', ruleset['bypass_actors'] + [dict(actor_type='Integration', actor_id=18, bypass_mode='always')]),
                               ('bypass_actors', [dict(actor_type='Integration', actor_id=17, bypass_mode='pull_request')]),
                               ('bypass_actors', [dict(actor_type='Integration', actor_id=17, bypass_mode='exempt')]),
                               ('conditions', {'ref_name': {'include': ['~ALL'], 'exclude': []}}),
                               ('conditions', {'ref_name': {'include': ['refs/heads/master'], 'exclude': ['refs/heads/master']}}),
                               ('rules', []), ('rules', [{'type': 'non_fast_forward'}, {'type': 'deletion'}]),
                               ('source_type', 'Organization'), ('source', 'other/configs'),
                               ('target', 'tag'), ('enforcement', 'disabled')]:
                previous = ruleset[key]
                ruleset[key] = wrong
                with self.assertRaises(ValueError): history.audit_force_actor('fixture/configs', protection)
                ruleset[key] = previous
            actors = ruleset.pop('bypass_actors')  # API hides this without sufficient visibility.
            with self.assertRaises(ValueError): history.audit_force_actor('fixture/configs', protection)
            ruleset['bypass_actors'] = actors
            for key, wrong in [('source_type', 'Organization'), ('source', 'other/configs'),
                               ('name', 'unknown'), ('enforcement', 'future-state')]:
                previous = summary[key]
                summary[key] = wrong
                with self.assertRaises(ValueError): history.audit_force_actor('fixture/configs', protection)
                summary[key] = previous
            inventory.append(dict(summary))
            with self.assertRaises(ValueError): history.audit_force_actor('fixture/configs', protection)
            inventory.pop()
            effective.append(dict(type='pull_request', ruleset_source_type='Organization', ruleset_source='org', ruleset_id=42))
            with self.assertRaises(ValueError): history.audit_force_actor('fixture/configs', protection)
            effective.pop()
            protection['allow_force_pushes']['enabled'] = False
            with self.assertRaises(ValueError): history.audit_force_actor('fixture/configs', protection)
            inventory.clear()
            effective.clear()
            self.assertEqual(history.audit_force_actor('fixture/configs', protection, require_enabled=False), {'enabled': False})
            with self.assertRaises(ValueError): history.audit_force_actor('fixture/configs', protection)
            protection['allow_force_pushes']['enabled'] = True
            with self.assertRaises(ValueError): history.audit_force_actor('fixture/configs', protection, require_enabled=False)

    def test_ruleset_inventory_reads_every_page(self):
        # INV repository/approved-history-rewrite
        first = [dict(enforcement='disabled') for _ in range(100)]
        with patch.object(history, 'api', side_effect=[first, [dict(enforcement='active', source_type='Organization')], []]) as api:
            with self.assertRaises(ValueError):
                history.audit_force_actor('fixture/configs', {'allow_force_pushes': {'enabled': False}}, require_enabled=False)
            self.assertIn('page=2', api.call_args_list[1].args[0])

    def test_remote_audit_accepts_closed_baseline_or_exact_ruleset_exception(self):
        # INV repository/mechanical-policy
        # INV repository/approved-history-rewrite
        implementation = module('remote_audit', SOURCE / 'audit-remote')
        policy = repo_policy.load()
        remote = dict(default_branch='master', **{key: policy['remote'][key] for key in
                      ('allow_merge_commit', 'allow_squash_merge', 'allow_rebase_merge')})
        protection = dict(policy['remote'], allow_force_pushes={'enabled': False})
        inputs, env, environment, reviews, artifacts, origin, admitted = self.history_fixture()
        def api(path, binary=False):
            if path == 'repos/fixture/configs': return remote
            if path.endswith('/protection'): return protection
            if not protection['allow_force_pushes']['enabled'] and ('/rulesets?' in path or '/rules/branches/' in path): return []
            return admitted(path, binary=binary)
        with patch.object(implementation, 'api', api), patch.object(history, 'api', api), \
             patch.object(implementation, 'repository', return_value='fixture/configs'), patch('sys.stdout', new_callable=io.StringIO) as output:
            implementation.audit()
            self.assertEqual(json.loads(output.getvalue())['history_rewrite'], {'enabled': False})
            output.seek(0)
            output.truncate(0)
            protection['allow_force_pushes']['enabled'] = True
            implementation.audit()
            self.assertTrue(json.loads(output.getvalue())['history_rewrite']['enabled'])
            environment['can_admins_bypass'] = True
            with self.assertRaises(ValueError): implementation.audit()

    def test_preflight_is_read_only_and_reports_app_permission_or_visibility_failures(self):
        # INV repository/approved-history-rewrite
        inputs, env, environment, reviews, artifacts, remote, api = self.history_fixture()
        refs = self.git('show-ref')
        with patch.object(history, 'api', api), patch.object(history, 'repository', return_value='fixture/configs'):
            result = history.preflight('fixture-writer')
            self.assertEqual(result['writes'], 'none')
            self.assertEqual(result['approval'], 'not granted')
            self.assertEqual(self.git('show-ref'), refs)
            for permission in history.APP_PERMISSIONS:
                def denied(path, binary=False):
                    value = api(path, binary=binary)
                    if path == 'apps/fixture-writer':
                        value['permissions'][permission] = 'none'
                    return value
                with patch.object(history, 'api', denied):
                    with self.assertRaises(ValueError): history.preflight('fixture-writer')
            for permissions in [dict(history.APP_PERMISSIONS, administration='write'),
                                dict(history.APP_PERMISSIONS, issues='write'),
                                dict(history.APP_PERMISSIONS, actions='write'),
                                dict(history.APP_PERMISSIONS, metadata='write')]:
                def elevated(path, binary=False):
                    value = api(path, binary=binary)
                    if path == 'apps/fixture-writer': value['permissions'] = permissions
                    return value
                with patch.object(history, 'api', elevated):
                    with self.assertRaises(ValueError): history.preflight('fixture-writer')
            def implicit_metadata(path, binary=False):
                value = api(path, binary=binary)
                if path == 'apps/fixture-writer': value['permissions']['metadata'] = 'read'
                return value
            with patch.object(history, 'api', implicit_metadata):
                self.assertEqual(history.preflight('fixture-writer')['writes'], 'none')

    def test_pre_push_refuses_non_fast_forward_without_reading_agent_approval_flags(self):
        # INV repository/approved-history-rewrite
        self.topic()
        for name in ('pre-push', 'evidence'):
            shutil.copy(ROOT / '.githooks' / name, self.root / '.githooks' / name)
        line = f'refs/heads/master {self.base} refs/heads/master {self.head}\n'
        result = subprocess.run([str(self.root / '.githooks/pre-push')], input=line, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Non-fast-forward', result.stderr)
        self.assertEqual(self.git('rev-parse', 'master'), self.base)


if __name__ == '__main__':
    unittest.main()
