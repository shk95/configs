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

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tool/version-control'
sys.path.insert(0, str(SOURCE))
import repo_policy
import github_proof
from ci_test import Evidence, archive
import history_rewrite as history


def module(name, path):
    spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, str(path)))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


base_tests = module('workflow_fixtures', SOURCE / 'test-workflow.py')
workspaces = module('workspace_implementation', SOURCE / 'workspaces')


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
        # INV repository/exact-ci-proof
        policy = repo_policy.load()
        ci = (ROOT / policy['ci']['workflow']).read_text()
        maintenance = (ROOT / policy['history_rewrite']['workflow']).read_text()
        release = (ROOT / '.github/workflows/release.yml').read_text()
        github_proof.require_strict_workflow(ci)
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

    def test_start_uses_live_git_state_with_legacy_records_present(self):
        # INV repository/workspace-choice
        administrative = Path(self.git('rev-parse', '--absolute-git-dir'))
        for name in ('configs-work.json', 'configs-work.tmp'):
            (administrative / name).write_text('old operation data\n')
        refs = self.git('show-ref')
        preview = json.loads(self.workflow('start', '--topic', 'example', '--workspace', 'current', '--dry-run'))
        self.assertEqual(preview, dict(base=self.base, branch='topic/example', workspace='current'))
        self.assertEqual(self.git('show-ref'), refs)
        self.workflow('start', '--topic', 'example', '--workspace', 'current')
        state = json.loads(self.workflow('inspect'))
        self.assertEqual((state['branch'], state['head']), ('topic/example', self.base))
        self.assertEqual(self.git('status', '--porcelain'), '')
        for name in ('configs-work.json', 'configs-work.tmp'):
            self.assertEqual((administrative / name).read_text(), 'old operation data\n')

    def test_removal_preserves_unique_dirty_ignored_and_primary_workspaces(self):
        # INV repository/workspace-preservation
        tool = str(self.root / 'tool/version-control/workspaces')
        refs = self.git('show-ref')
        self.call(tool, 'new', 'repository-disposable', ok=False)
        self.assertEqual(self.git('show-ref'), refs)
        self.workflow('start', '--commits', 'many',
                      '--topic', 'disposable', '--workspace', 'linked')
        linked = self.root.parent / 'repo-wt/topic-disposable'
        (linked / 'docs/status/repository.md').write_text('unique\n')
        self.git('add', '.', cwd=linked)
        self.git('commit', '-qm', 'feat(repository): unique work', cwd=linked)
        head = self.git('rev-parse', 'HEAD', cwd=linked)
        review = json.loads(self.call(tool, 'review', str(linked)))
        self.assertEqual(review['unique_commits'], [head])
        self.assertEqual(review['retained_branch'], {'ref': 'refs/heads/topic/disposable', 'head': head})
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
        self.assertEqual(self.git('rev-parse', 'topic/disposable'), head)

    def test_workspace_alias_must_identify_one_branch(self):
        # INV repository/workspace-preservation
        tool = str(self.root / 'tool/version-control/workspaces')
        for branch in ('feature/repository-supply', 'topic/repository-supply'):
            self.git('worktree', 'add', '-qb', branch, str(self.root.parent / branch.replace('/', '-')))
        refs = self.git('show-ref')
        self.call(tool, 'review', 'repository-supply', ok=False)
        self.call(tool, 'done', 'repository-supply', '--expect-head', self.base, ok=False)
        self.assertEqual(self.git('show-ref'), refs)
        for branch in ('feature/repository-supply', 'topic/repository-supply'):
            self.assertEqual(json.loads(self.call(tool, 'review', branch))['branch'], branch)
            self.call(tool, 'done', branch, '--expect-head', self.base)
            self.assertFalse((self.root.parent / branch.replace('/', '-')).exists())
        self.assertEqual(self.git('show-ref'), refs)

    def test_clean_conflicted_revert_still_blocks_workflow_and_removal(self):
        # INV repository/workspace-preservation
        self.workflow('start', '--topic', 'revert', '--workspace', 'linked')
        linked = self.root.parent / 'repo-wt/topic-revert'
        file = 'docs/status/repository.md'
        (linked / file).write_text('first edit\n')
        self.git('commit', '-qam', 'test(repository): first edit', cwd=linked)
        reverted = self.git('rev-parse', 'HEAD', cwd=linked)
        (linked / file).write_text('competing edit\n')
        self.git('commit', '-qam', 'test(repository): competing edit', cwd=linked)
        head = self.git('rev-parse', 'HEAD', cwd=linked)
        self.git('revert', '--no-edit', reverted, cwd=linked, ok=False)
        self.git('checkout', '--ours', '--', file, cwd=linked)
        self.git('add', '--', file, cwd=linked)
        self.assertEqual(self.git('status', '--porcelain', cwd=linked), '')
        tool = str(self.root / 'tool/version-control/workspaces')
        review = json.loads(self.call(tool, 'review', 'topic/revert'))
        self.assertIn('REVERT_HEAD', review['operations'])
        self.assertFalse(review['removable'])
        self.workflow('plan', '--base', self.base, '--head', head, cwd=linked, ok=False)
        self.call(tool, 'done', 'topic/revert', '--expect-head', head, ok=False)
        self.assertEqual(self.git('rev-parse', 'REVERT_HEAD', cwd=linked), reverted)

    def test_optional_external_recovery_is_validated_when_supplied(self):
        # INV repository/workspace-preservation
        tool = str(self.root / 'tool/version-control/workspaces')
        self.workflow('start', '--commits', 'many',
                      '--topic', 'archived', '--workspace', 'linked')
        linked = self.root.parent / 'repo-wt/topic-archived'
        (linked / 'docs/status/repository.md').write_text('cancelled but preserved\n')
        self.git('add', '.', cwd=linked)
        self.git('commit', '-qm', 'feat(repository): preserved cancelled work', cwd=linked)
        head = self.git('rev-parse', 'HEAD', cwd=linked)
        bundle = self.root.parent / 'preserved.bundle'
        self.git('bundle', 'create', str(bundle), 'topic/archived')
        damaged = self.root.parent / 'damaged.bundle'
        damaged.write_bytes(bundle.read_bytes()[:-10])
        self.call(tool, 'done', str(linked), '--expect-head', head, '--preserved-bundle', str(damaged), ok=False)
        self.assertTrue(linked.exists())
        self.call(tool, 'done', str(linked), '--expect-head', self.base, '--preserved-bundle', str(bundle), ok=False)
        self.call(tool, 'done', str(linked), '--expect-head', head, '--preserved-bundle', str(bundle))
        self.assertTrue(bundle.exists())
        self.assertFalse(linked.exists())
        self.assertEqual(self.git('rev-parse', 'topic/archived'), head)

    def test_retained_branch_must_match_reviewed_workspace_identity(self):
        # INV repository/workspace-preservation
        tool = str(self.root / 'tool/version-control/workspaces')
        self.workflow('start', '--commits', 'many',
                      '--topic', 'identity', '--workspace', 'linked')
        linked = self.root.parent / 'repo-wt/topic-identity'
        branch = 'topic/identity'
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

    def proof_fixture(self, units=None):
        self.topic()
        if units is not None:
            (self.root / 'tool/dispatch/select').write_text(
                '#!/bin/sh\ncat >/dev/null\nprintf "%s\\n" ' + ' '.join(units) + '\n')
            self.head = self.commit('test(repository): select requested CI units')
        return Evidence(self.git, self.base, self.head, self.git('rev-parse', 'HEAD^{tree}'),
                        units or ['repository:fixtures'])

    def test_live_ci_proof_accepts_exact_dispatch_and_rejects_mismatches(self):
        # INV repository/exact-ci-proof
        fixture = self.proof_fixture()
        source = fixture.source
        job = fixture.jobs['Version-control policy (Linux)']
        def read():
            return github_proof.verify('7', self.base, self.head, self.git('rev-parse', 'HEAD^{tree}'),
                                       repo='fixture/configs', read=fixture.read)
        # The jobs whose entire bodies run need no step display names.
        for ordinary_job in fixture.jobs.values():
            ordinary_job.pop('steps')
        self.assertEqual(read()['head'], self.head)
        for mapping, key, wrong in [(source, 'base', 'a'*40), (source, 'head', 'b'*40),
                                    (source, 'tree', 'c'*40), (source, 'event', 'push'),
                                    (source, 'checkout', self.base), (source, 'workflow_sha', self.head),
                                    (source, 'workflow_blob', 'd'*40), (source, 'run_id', 8),
                                    (source, 'attempt', 2), (source, 'units', []),
                                    (fixture.run, 'path', '.github/workflows/other.yml'),
                                    (fixture.run, 'head_repository', {'full_name': 'fork/configs'}),
                                    (fixture.run, 'head_branch', 'topic/untrusted'),
                                    (fixture.run, 'head_sha', self.head),
                                    (fixture.run, 'conclusion', 'cancelled'), (fixture.run, 'status', 'in_progress'),
                                    (job, 'labels', ['windows-latest']),
                                    (job, 'run_attempt', 2), (job, 'conclusion', 'skipped'),
                                    (fixture.jobs[github_proof.POLICY_JOB], 'conclusion', 'failure'),
                                    (fixture.artifacts[0], 'name', 'ci-source'),
                                    (fixture.artifacts[0], 'expired', True)]:
            with self.subTest(key=key, wrong=wrong):
                with patch.dict(mapping, {key: wrong}), self.assertRaises(ValueError):
                    read()
        fixture.artifacts.append(copy.deepcopy(fixture.artifacts[0]))
        with self.assertRaises(ValueError):
            read()
        with self.assertRaises(ValueError):
            github_proof.source_record(archive(dict(source, extra='field')))

    def test_changed_workflow_requires_success_of_unconditional_steps(self):
        # INV repository/exact-ci-proof
        # A PR can make an unconditional step skippable while its job stays green.
        self.topic()
        shutil.copy2(ROOT / 'tool/dispatch/select', self.root / 'tool/dispatch/select')
        workflow = self.root / '.github/workflows/ci.yml'
        original = workflow.read_text()
        policy_step = 'Verify incoming history and repository policy'
        policy_header = f'      - name: {policy_step}\n'
        self.assertIn(policy_header, original)
        gate = repo_policy.load()['ci']['gate']
        extra_steps = {**github_proof.WORKFLOW_CHANGE_STEPS, gate: github_proof.GATE_STEPS}

        for case, edit in [('ordinary', '        # Workflow review fixture\n'),
                           ('skip', '        if: ${{ false }}\n'),
                           ('tolerate', '        continue-on-error: true\n')]:
            with self.subTest(case=case):
                workflow.write_text(original.replace(policy_header, policy_header + edit))
                head = self.commit('test(repository): exercise updated CI definition')
                tree = self.git('rev-parse', head + '^{tree}')
                units = github_proof.selected_units(self.base, tree, self.root)
                fixture = Evidence(self.git, self.base, head, tree, units, pull=5, event='pull_request')
                for name, steps in extra_steps.items():
                    job = fixture.jobs[name]
                    if job['conclusion'] == 'success':
                        job['steps'].extend(
                            {'name': step, 'conclusion': 'skipped' if case == 'skip' and step == policy_step else 'success'}
                            for step in steps)
                context = dict(event='pull_request', pull=5, repo='fixture/configs', read=fixture.read)
                if case == 'skip':
                    with self.assertRaisesRegex(ValueError, 'Required CI step.*Incoming history'):
                        github_proof.verify(7, self.base, head, tree, **context)
                elif case == 'tolerate':
                    with self.assertRaisesRegex(ValueError, 'must not use continue-on-error'):
                        github_proof.verify(7, self.base, head, tree, **context)
                else:
                    self.assertEqual(github_proof.verify(7, self.base, head, tree, **context)['head'], head)

    def test_workflow_storage_and_runner_changes_use_the_same_checks(self):
        # INV repository/local-gate-selects-by-effect
        self.topic()
        path = self.root / '.github/workflows/ci.yml'
        workflow = path.read_text()
        shutil.copy2(ROOT / 'tool/dispatch/select', self.root / 'tool/dispatch/select')
        base = self.commit('test(repository): use the real CI selector')
        retained = workflow.replace('retention-days: 90', 'retention-days: 30')
        self.assertNotEqual(retained, workflow)
        path.write_text(retained)
        head = self.commit('test(repository): change source-record retention')
        full = ['repository:fixtures', 'repository:windows-git', 'unixlike:suite',
                'unixlike:tools', 'windows:suite', 'windows:runtime']
        self.assertEqual(github_proof.selected_units(base, head, self.root), full)
        path.write_text(retained.replace('runs-on: ubuntu-latest', 'runs-on: windows-latest', 1))
        head = self.commit('test(repository): also change the CI platform')
        self.assertEqual(github_proof.selected_units(base, head, self.root), full)

    def test_unixlike_check_entry_runs_only_selected_checks(self):
        # INV repository/local-gate-selects-by-effect
        fixture = Path(self.tmp.name) / 'checks'
        fixture.mkdir()
        entry = fixture / 'test'
        shutil.copy(ROOT / 'unixlike/tool/checks/test', entry)
        (fixture / 'prerequisite').write_text('require_command() { return 0; }\n')
        tools = ['just-entry-test', 'dev-host-test', 'refresh-inputs-test', 'karabiner-entry-test',
                 'eval-coverage-test', 'prerequisite-test']
        provider = ['programs-test', 'darwin-capture-test', 'payloads-test', 'karabiner-test',
                    'editable-files-test', 'flake-test', 'composition-test', 'import-order-test', 'evaluate']
        for name in {*tools, *provider, 'payloads'}:
            check = fixture / name
            check.write_text(f'#!/bin/sh\nprintf "%s\\n" {name}\n')
            check.chmod(0o755)
        for args, expected in [(('--tools',), tools), (('--provider',), provider),
                               (('--payloads',), ['payloads', 'karabiner-test']), ((), tools + provider)]:
            with self.subTest(args=args):
                output = subprocess.check_output(['sh', str(entry), *args], text=True)
                self.assertEqual(output.splitlines(), expected)

    def test_only_required_jobs_have_a_veto(self):
        # INV repository/exact-ci-proof
        fixture = self.proof_fixture(['unixlike:suite', 'unixlike:tools', 'windows:suite', 'windows:runtime'])

        def verify():
            return github_proof.verify(7, self.base, self.head, fixture.source['tree'],
                                       repo='fixture/configs', read=fixture.read)

        fixture.jobs.pop('Version-control policy (Linux)')
        fixture.set_job('Informational', 'ubuntu-latest')
        fixture.jobs['Informational']['conclusion'] = 'failure'
        fixture.run['conclusion'] = 'failure'
        self.assertEqual(verify()['units'], fixture.source['units'])
        for unit in ('unixlike:tools', 'windows:suite'):
            name, _, (required_step,) = github_proof.UNITS[unit]
            job = fixture.jobs[name]
            skipped = [dict(step, conclusion='skipped') if step['name'] == required_step else step
                       for step in job['steps']]
            with self.subTest(unit=unit), patch.dict(job, steps=skipped):
                with self.assertRaisesRegex(ValueError, 'Required CI step'):
                    verify()

    def test_hosted_proof_replaces_all_equivalent_checks(self):
        # INV repository/exact-ci-proof
        fixture = self.proof_fixture(['windows:suite', 'windows:runtime'])
        implementation = module('workflow_implementation', SOURCE / 'workflow')
        trace = Path(self.tmp.name) / 'hosted-commands.jsonl'
        with patch.object(implementation, 'verify', side_effect=lambda *a: github_proof.verify(
                *a, repo='fixture/configs', read=fixture.read)), patch.dict(
                os.environ, FIXTURE_EXECUTION_LOG=str(trace),
                PATH=str(self.root / 'tool') + os.pathsep + os.environ['PATH']):
            implementation.check(self.root, self.base, self.head, '7')
            self.assertFalse(trace.exists())
            with patch.dict(os.environ, FIXTURE_CHECK_STATUS='1'):
                implementation.check(self.root, self.base, self.head, '7')
            self.assertFalse(trace.exists())

    def test_master_push_reuses_only_exact_prior_provider_units(self):
        # INV repository/exact-ci-proof
        units = ['repository:fixtures', 'unixlike:suite', 'windows:suite', 'windows:runtime']
        topic = self.proof_fixture(units).source
        base, head, tree = (topic[key] for key in ('base', 'head', 'tree'))
        prior = Evidence(self.git, base, head, tree, units, pull=5, event='pull_request')
        master = self.git('commit-tree', tree, '-p', base, '-p', head, '-m', 'Merge published topic')
        current = Evidence(self.git, base, master, tree, units, run_id=8, event='push')

        def read(path, binary=False):
            if path.startswith(f'commits/{head}/check-runs'):
                return {'check_runs': [{'name': 'Required checks', 'id': 1, 'app': {'id': 15368},
                                        'details_url': prior.run['html_url'] + '/job/3', 'conclusion': 'success'}]}
            fixture = current if '/runs/8' in path or '/artifacts/8/' in path else prior
            return fixture.read(path, binary)

        expected = {'run_id': 7, 'attempt': 1, 'units': ['unixlike:suite', 'windows:suite']}
        primary = dict(repo='fixture/configs', read=read)
        self.assertEqual(github_proof.reusable_provider_units(base, master, units, **primary), expected)
        self.assertIsNone(github_proof.reusable_provider_units(base, head, units, **primary))
        with patch.dict(prior.source, {'tree': 'f' * 40}):
            self.assertIsNone(github_proof.reusable_provider_units(base, master, units, **primary))

        current.source['reuse'] = expected
        current.set_job('Unix-like provider contract', 'ubuntu-latest', selected=False)
        name, runner, steps = github_proof.UNITS['windows:runtime']
        current.set_job(name, runner, *steps)
        self.assertEqual(github_proof.verify(8, base, master, tree, **primary)['reuse'], expected)
        failures = [(prior.artifacts[0], {'expired': True}), (prior.source, {'attempt': 2}),
                    (prior.jobs['Windows desired state'], {'labels': ['ubuntu-latest']}),
                    (current.source, {'reuse': dict(expected, units=['windows:runtime'])}),
                    (current.jobs[name], {'steps': []}),
                    (current.jobs[github_proof.POLICY_JOB], {'conclusion': 'failure'})]
        for item, change in failures:
            with self.subTest(change=change), patch.dict(item, change), self.assertRaises(ValueError):
                github_proof.verify(8, base, master, tree, **primary)

    def test_source_record_uses_the_runner_and_actual_workflow_checkout(self):
        # INV repository/exact-ci-proof
        fixture = self.proof_fixture()
        workflow = Path(self.tmp.name) / 'workflow-definition'
        self.git('worktree', 'add', '-q', '--detach', str(workflow), self.base)
        script = workflow / '.github/scripts/ci-source.py'
        script.parent.mkdir()
        shutil.copy(ROOT / '.github/scripts/ci-source.py', script)
        event = Path(self.tmp.name) / 'event.json'
        event.write_text(json.dumps({'inputs': {'base': self.base, 'head': self.head}}))
        env = dict(os.environ, GITHUB_EVENT_PATH=str(event), GITHUB_EVENT_NAME='workflow_dispatch',
                   GITHUB_WORKFLOW_SHA=self.base, GITHUB_WORKFLOW_REF='fixture/configs/.github/workflows/ci.yml@refs/heads/master',
                   GITHUB_RUN_ID='7', GITHUB_RUN_ATTEMPT='1', CI_BASE=self.base, CI_UNITS='repository:fixtures',
                   RUNNER_TEMP=self.tmp.name)
        self.call(sys.executable, str(script), env=env)
        self.assertEqual(json.loads((Path(self.tmp.name) / 'source.json').read_text()), fixture.source)
        self.call(sys.executable, str(script), env=dict(env, GITHUB_WORKFLOW_SHA=self.head), ok=False)

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
        # history.execute runs in this process, outside Workflow.call's fixture PATH.
        env = dict(PATH=str(self.root / 'tool') + os.pathsep + os.environ['PATH'], FIXTURE_SECRET_STATUS='0',
                   GITHUB_ACTIONS='true', GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_REPOSITORY='fixture/configs',
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
                   DISPATCH_BASE=self.base, DISPATCH_HEAD=self.head, GITHUB_WORKFLOW_SHA=self.base)
        command = str(ROOT / 'tool/dispatch/ci-base')
        self.assertEqual(self.call(command, env=env).strip(), self.base)
        for key, wrong in [('DISPATCH_REF', 'refs/heads/feature/repository-untrusted'),
                           ('GITHUB_WORKFLOW_SHA', self.head),
                           ('DISPATCH_BASE', self.head), ('DISPATCH_HEAD', self.base), ('DISPATCH_HEAD', 'invalid')]:
            self.call(command, env=dict(env, **{key: wrong}), ok=False)

    def test_pr_selection_requires_exact_synthetic_merge(self):
        # INV repository/local-gate-selects-by-effect
        self.topic()
        command = str(ROOT / 'tool/dispatch/ci-base')
        env = dict(os.environ, EVENT_NAME='pull_request', PR_BASE_REF='master', EVENT_BASE_REF='master',
                   PR_BASE=self.base, PR_HEAD=self.head, PR_STACK='null')
        self.call(command, env=env, ok=False)
        merged = self.git('commit-tree', 'HEAD^{tree}', '-p', self.base, '-p', self.head, '-m', 'Merge synthetic')
        self.git('checkout', '-q', '--detach', merged)
        self.assertEqual(self.call(command, env=env).strip(), self.base)
        for key, wrong in [('PR_BASE_REF', 'topic/parent'), ('EVENT_BASE_REF', 'topic/parent'),
                           ('PR_STACK', '{"native":true}'), ('PR_HEAD', self.base), ('PR_BASE', self.head)]:
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
        # INV repository/no-secret-in-history
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
            for status in ('1', '69'):
                with patch.dict(os.environ, FIXTURE_SECRET_STATUS=status):
                    with self.assertRaisesRegex(ValueError, 'successful incoming secret scan'):
                        history.execute(destination)
                self.assertEqual(self.git('--git-dir', str(remote), 'rev-parse', 'master'), inputs['old'])
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
