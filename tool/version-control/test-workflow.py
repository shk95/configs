#!/usr/bin/env python3
"""Real master-only repositories exercise operation and refusal boundaries."""
# INV repository/local-development-integration
# INV repository/workspace-choice
# INV repository/local-gate-selects-by-effect
import importlib.util
from importlib.machinery import SourceFileLoader
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


class Workflow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-q', '-b', 'master')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.root / 'docs/status').mkdir(parents=True)
        (self.root / 'docs/status/repository.md').write_text('base\n')
        for name in ['workflow', 'authoring', 'policy', 'policy.json', 'repo_policy.py', 'github_proof.py', 'topic_scope.py', 'topic-source', 'audit', 'classify', 'closing-keywords']:
            dest = self.root / 'tool/version-control' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / 'tool/version-control' / name, dest)
        (self.root / '.githooks').mkdir()
        shutil.copy(ROOT / '.githooks/commit-msg', self.root / '.githooks/commit-msg')
        # Real workflow invokes fixture-owned check commands; failure injection
        # proves checks and identities gate integration, not their semantics.
        for name in ['work', 'hygiene', 'domain-reads', 'design-citations', 'records', 'invariants', 'provisional', 'test']:
            dest = self.root / 'tool/version-control' / name
            dest.write_text('#!/bin/sh\nexit "${FIXTURE_CHECK_STATUS:-0}"\n')
            dest.chmod(0o755)
        dest = self.root / 'tool/dispatch/select'
        dest.parent.mkdir(parents=True)
        dest.write_text('#!/bin/sh\ncat >/dev/null\nprintf "repository:fixtures\\n"\n')
        dest.chmod(0o755)
        dest = self.root / 'tool/gitleaks'
        dest.write_text('#!/bin/sh\nexit "${FIXTURE_SECRET_STATUS:-0}"\n')
        dest.chmod(0o755)
        self.commit('chore(repository): seed fixture')
        self.base = self.git('rev-parse', 'HEAD')

    def call(self, *args, ok=True, env=None, cwd=None):
        env = dict(os.environ if env is None else env)
        env['PATH'] = str(self.root / 'tool') + os.pathsep + env['PATH']
        result = subprocess.run(args, cwd=cwd or self.root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def git(self, *args, **kw):
        return self.call('git', *args, **kw).strip()

    def workflow(self, *args, **kw):
        return self.call(str(self.root / 'tool/version-control/workflow'), *args, **kw)

    def commit(self, subject):
        self.git('add', '.')
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', subject)
        return self.git('rev-parse', 'HEAD')

    def topic(self):
        self.workflow('start', '--scope', 'repository', '--commits', 'many', '--topic', 'example', '--workspace', 'current')
        for n in range(2):
            (self.root / 'docs/status/repository.md').write_text(f'change {n}\n')
            self.head = self.commit(f'feat(repository): change {n}')

    def test_start_requires_workspace_and_preserves_dirty_or_invalid_state(self):
        refs = self.git('show-ref')
        self.workflow('start', '--scope', 'repository', '--commits', 'many', '--topic', 'example', ok=False)
        self.workflow('start', '--scope', 'repository', '--commits', 'many', '--workspace', 'current', ok=False)
        self.workflow('start', '--scope', 'repository', '--commits', 'one', '--workspace', 'current')
        self.assertEqual(self.git('show-ref'), refs)
        self.workflow('start', '--scope', 'repository', '--commits', 'many', '--topic', 'example', '--workspace', 'linked', '--dry-run')
        self.assertEqual(self.git('show-ref'), refs)
        (self.root / 'untracked').write_text('preserve')
        self.workflow('start', '--scope', 'repository', '--commits', 'many', '--topic', 'example', '--workspace', 'current', ok=False)
        self.assertEqual(self.git('show-ref'), refs)
        self.assertEqual((self.root / 'untracked').read_text(), 'preserve')

    def test_master_direct_authoring_without_dev_or_remote(self):
        self.call(str(self.root / 'tool/version-control/authoring'))
        (self.root / 'docs/status/repository.md').write_text('direct\n')
        head = self.commit('feat(repository): direct master change')
        self.workflow('check', '--base', self.base, '--head', head)
        record = Path(self.git('rev-parse', '--path-format=absolute', '--git-path', 'configs-work.json'))
        self.assertFalse(record.exists(), 'Verification must not create persistent operation state')
        record.write_text('legacy operation data; not a verification prerequisite\n')
        self.workflow('check', '--base', self.base, '--head', head)
        self.assertEqual(record.read_text(), 'legacy operation data; not a verification prerequisite\n')
        self.assertEqual(self.git('branch', '--show-current'), 'master')
        self.git('switch', '-qc', 'dev')
        self.call(str(self.root / 'tool/version-control/authoring'), ok=False)
        self.git('checkout', '-q', '--detach')
        self.call(str(self.root / 'tool/version-control/authoring'), ok=False)

    def test_no_ff_merge_exact_parents_and_failure_preservation(self):
        self.topic()
        args = ('merge', '--base', self.base, '--head', self.head)
        refs = self.git('show-ref')
        for status in ['1', '69']:
            self.workflow(*args, ok=False, env=dict(os.environ, FIXTURE_CHECK_STATUS=status))
            self.assertEqual(self.git('show-ref'), refs)
        self.workflow(*args, ok=False, env=dict(os.environ, FIXTURE_SECRET_STATUS='1'))
        self.assertEqual(self.git('show-ref'), refs)
        self.workflow('merge', '--base', self.base[:8], '--head', self.head, ok=False)
        self.workflow(*args)
        self.assertEqual(self.git('show', '-s', '--format=%P', 'HEAD'), f'{self.base} {self.head}')
        self.assertEqual(self.git('branch', '--show-current'), 'master')
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_stale_master_and_head_and_dirty_candidate_refuse(self):
        self.topic()
        self.workflow('merge', '--base', self.base, '--head', self.base, ok=False)
        (self.root / 'docs/status/repository.md').write_text('dirty\n')
        self.workflow('merge', '--base', self.base, '--head', self.head, ok=False)
        self.assertEqual((self.root / 'docs/status/repository.md').read_text(), 'dirty\n')
        self.git('restore', 'docs/status/repository.md')
        self.git('switch', '-q', 'master')
        (self.root / 'docs/status/repository.md').write_text('competing master\n')
        new_base = self.commit('feat(repository): competing result')
        self.git('switch', '-q', 'feature/repository-example')
        self.workflow('merge', '--base', self.base, '--head', self.head, ok=False)
        self.workflow('merge', '--base', new_base, '--head', self.head, ok=False)
        self.assertEqual(self.git('rev-parse', 'master'), new_base)
        # A real conflict stays in the selected workspace for explicit recovery.
        self.git('merge', 'master', ok=False)
        self.workflow('merge', '--base', new_base, '--head', self.head, ok=False)
        self.assertTrue((self.root / '.git/MERGE_HEAD').exists())

    def test_topic_scope_and_foreign_native_selection_refuse(self):
        self.topic()
        self.git('branch', '-m', 'feature/windows-wrong-scope')
        self.workflow('merge', '--base', self.base, '--head', self.head, ok=False)
        self.git('branch', '-m', 'feature/repository-example')
        if os.name != 'nt':
            (self.root / 'tool/dispatch/select').write_text('#!/bin/sh\ncat >/dev/null\necho windows:suite\n')
            head = self.commit('test(repository): select native Windows checks')
            self.workflow('check', '--base', self.base, '--head', head, ok=False)
            self.assertEqual(self.git('rev-parse', 'master'), self.base)

    def test_pr_and_local_topic_scope_agree_without_counting_new_base_work(self):
        # INV repository/topic-source
        self.topic()
        source = str(self.root / 'tool/version-control/topic-source')
        env = dict(os.environ, TOPIC_BASE_REF='master', TOPIC_BASE_SHA=self.base,
                   TOPIC_HEAD_SHA=self.head, TOPIC_HEAD_REF='feature/repository-example',
                   TOPIC_BASE_REPOSITORY='fixture/configs', TOPIC_HEAD_REPOSITORY='fixture/configs')
        self.call(source, env=env)
        self.call(source, env=dict(env, TOPIC_HEAD_REF='feature/windows-wrong-scope'), ok=False)
        self.git('switch', '-q', 'master')
        (self.root / 'windows').mkdir()
        (self.root / 'windows/probe.txt').write_text('unrelated newer base\n')
        newer = self.commit('feat(windows): newer base fixture')
        self.git('switch', '-q', 'feature/repository-example')
        # PR base can advance before the topic reflects it. Its own scope is
        # still repository; local integration separately requires current base.
        self.call(source, env=dict(env, TOPIC_BASE_SHA=newer))
        self.workflow('merge', '--base', newer, '--head', self.head, ok=False)

    def test_incoming_range_rejects_mixed_commit_hidden_by_final_scope(self):
        # INV repository/local-development-integration
        # INV repository/topic-source
        self.topic()
        (self.root / 'unixlike').mkdir()
        path = self.root / 'unixlike/probe.txt'
        path.write_text('temporary cross-scope edit\n')
        (self.root / 'docs/status/repository.md').write_text('mixed commit\n')
        self.commit('feat(repository): mixed source fixture')
        path.unlink()
        head = self.commit('fix(unixlike): remove temporary fixture')
        env = dict(os.environ, TOPIC_BASE_REF='master', TOPIC_BASE_SHA=self.base,
                   TOPIC_HEAD_SHA=head, TOPIC_HEAD_REF='feature/repository-example',
                   TOPIC_BASE_REPOSITORY='fixture/configs', TOPIC_HEAD_REPOSITORY='fixture/configs')
        # The final topic diff has one scope, but every authored source commit
        # must satisfy ownership too. CI and local checks use this same audit.
        self.call(str(self.root / 'tool/version-control/topic-source'), env=env, ok=False)
        result = subprocess.run([str(self.root / 'tool/version-control/audit'), '--range', self.base, head],
                                cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('source commit has mixed or unclassified ownership', result.stderr)
        self.workflow('check', '--base', self.base, '--head', head, ok=False)

    def test_topic_refuses_reverted_foreign_scope_even_when_each_commit_is_pure(self):
        # INV repository/topic-source
        self.topic()
        (self.root / 'windows').mkdir()
        path = self.root / 'windows/probe.txt'
        path.write_text('foreign-scope source\n')
        self.commit('feat(windows): foreign source fixture')
        path.unlink()
        head = self.commit('fix(windows): revert foreign source fixture')
        env = dict(os.environ, TOPIC_BASE_REF='master', TOPIC_BASE_SHA=self.base,
                   TOPIC_HEAD_SHA=head, TOPIC_HEAD_REF='feature/repository-example',
                   TOPIC_BASE_REPOSITORY='fixture/configs', TOPIC_HEAD_REPOSITORY='fixture/configs')
        # Each source commit is scope-pure, but a repository topic cannot carry
        # Windows work merely because the final tree no longer contains it.
        self.call(str(self.root / 'tool/version-control/audit'), '--range', self.base, head)
        self.call(str(self.root / 'tool/version-control/topic-source'), env=env, ok=False)
        self.workflow('check', '--base', self.base, '--head', head, ok=False)

    def test_initial_push_range_accepts_only_empty_tree_and_checks_root_ownership(self):
        # INV repository/local-development-integration
        audit = str(self.root / 'tool/version-control/audit')
        empty = self.git('hash-object', '-t', 'tree', os.devnull)
        # The fixture-only scanner stub is not a repository-owned source path.
        # Build bootstrap trees without it; do not move any fixture ref.
        self.git('rm', '--cached', 'tool/gitleaks')
        pure_tree = self.git('write-tree')
        pure = self.git('commit-tree', pure_tree, '-m', 'test(repository): pure root fixture')
        self.call(audit, '--range', empty, pure)
        # A nonempty tree is not a prior-commit identity or an initial basis.
        self.call(audit, '--range', pure_tree, pure, ok=False)
        (self.root / 'windows').mkdir()
        (self.root / 'windows/probe.txt').write_text('mixed root ownership\n')
        self.git('add', 'windows/probe.txt')
        tree = self.git('write-tree')
        # Preserve the existing hook/check tooling but make a synthetic root
        # commit carrying both scopes, as a first push would transmit it.
        root = self.git('commit-tree', tree, '-m', 'feat(repository): mixed root fixture')
        result = subprocess.run([audit, '--range', empty, root], cwd=self.root,
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('source commit has mixed or unclassified ownership', result.stderr)
        self.assertNotIn('transmitted content has an unclassified path', result.stderr)

    def test_runtime_governance_requires_hosted_proof_even_on_native_windows(self):
        # INV repository/windows-ci-runtime-bound
        self.topic()
        (self.root / 'tool/dispatch/select').write_text('#!/bin/sh\ncat >/dev/null\necho windows:runtime\n')
        head = self.commit('test(repository): native runtime governance selection')
        # The requirement belongs to the selected suite, not host detection.
        # A native Windows checkout cannot substitute domain validate/test for
        # the CI orchestrator's runtime-control fixtures.
        path = self.root / 'tool/version-control/workflow'
        loader = SourceFileLoader('native_workflow_fixture', str(path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        implementation = importlib.util.module_from_spec(spec)
        loader.exec_module(implementation)
        previous = Path.cwd()
        os.chdir(self.root)
        try:
            with patch.object(implementation, 'os', SimpleNamespace(name='nt')), \
                 patch.dict(os.environ, PATH=str(self.root / 'tool') + os.pathsep + os.environ['PATH']):
                with self.assertRaisesRegex(ValueError, 'runtime wiring requires exact hosted evidence'):
                    implementation.check(self.root, self.base, head)
        finally:
            os.chdir(previous)

    def test_remote_contract_accepts_direct_master_and_refuses_unsafe_settings(self):
        # INV repository/local-development-integration
        api = self.root / 'tool/gh'
        api.write_text("""#!/bin/sh
set -eu
case "$1" in
  repo) echo fixture/configs; exit 0 ;;
  api) shift ;;
  *) exit 1 ;;
esac
case "$1" in
  */branches/master/protection) cat "$FIXTURE_PROTECTION" ;;
  */rulesets*|*/rules/branches/master*) echo '[]' ;;
  repos/fixture/configs) echo '{"default_branch":"master","allow_merge_commit":true,"allow_squash_merge":false,"allow_rebase_merge":false}' ;;
  *) exit 1 ;;
esac
""")
        api.chmod(0o755)
        protection = Path(self.tmp.name) / 'protection.json'
        good = {'required_status_checks': None, 'required_pull_request_reviews': None,
                'enforce_admins': {'enabled': True}, 'allow_force_pushes': {'enabled': False},
                'allow_deletions': {'enabled': False}, 'required_conversation_resolution': {'enabled': False},
                'lock_branch': {'enabled': False}, 'required_linear_history': {'enabled': False}, 'restrictions': None}
        env = dict(os.environ, FIXTURE_PROTECTION=str(protection))
        protection.write_text(json.dumps(good))
        self.call(str(ROOT / 'tool/version-control/audit-remote'), env=env)
        for key, value in [('required_status_checks', {}), ('required_pull_request_reviews', {}),
                           ('enforce_admins', {'enabled': False}), ('allow_force_pushes', {'enabled': True}),
                           ('allow_deletions', {'enabled': True})]:
            protection.write_text(json.dumps(dict(good, **{key: value})))
            self.call(str(ROOT / 'tool/version-control/audit-remote'), env=env, ok=False)

    def test_growing_master_work_preserves_changes_and_accepted_commits(self):
        # INV repository/local-development-integration
        for accepted in (False, True):
            with self.subTest(accepted_master_commit=accepted):
                if accepted:
                    (self.root / 'docs/status/repository.md').write_text('accepted direct work\n')
                    self.commit('feat(repository): accepted direct work')
                base = self.git('rev-parse', 'master')
                (self.root / 'docs/status/repository.md').write_text('staged growing work\n')
                self.git('add', 'docs/status/repository.md')
                (self.root / 'docs/status/repository.md').write_text('unstaged growing work\n')
                extra = self.root / 'docs/reference' / f'growth-{accepted}.md'
                extra.parent.mkdir(exist_ok=True)
                extra.write_text('untracked growing work\n')
                before = [self.git('status', '--porcelain'), self.git('diff', '--cached'), self.git('diff')]
                self.git('switch', '-c', f'feature/repository-growth-{str(accepted).lower()}')
                self.assertEqual([self.git('status', '--porcelain'), self.git('diff', '--cached'), self.git('diff')], before)
                self.assertEqual(extra.read_text(), 'untracked growing work\n')
                self.assertEqual(self.git('rev-parse', 'master'), base)
                head = self.commit('feat(repository): complete growing topic')
                self.workflow('merge', '--base', base, '--head', head)
                self.assertEqual(self.git('show', '-s', '--format=%P', 'HEAD'), f'{base} {head}')
                self.assertEqual(self.git('branch', '--show-current'), 'master')

    def test_linked_workspace_base_and_integration_to_existing_master(self):
        self.workflow('start', '--scope', 'repository', '--commits', 'many', '--topic', 'linked', '--workspace', 'linked')
        linked = self.root.parent / 'repo-wt/feature-repository-linked'
        self.assertTrue(linked.is_dir())
        self.assertEqual(self.git('rev-parse', 'HEAD', cwd=linked), self.base)
        self.assertEqual(self.git('branch', '--show-current'), 'master')
        (linked / 'docs/status/repository.md').write_text('linked\n')
        self.git('add', '.', cwd=linked)
        self.git('commit', '-qm', 'feat(repository): linked change', cwd=linked)
        head = self.git('rev-parse', 'HEAD', cwd=linked)
        self.workflow('merge', '--base', self.base, '--head', head, cwd=linked)
        self.assertEqual(self.git('show', '-s', '--format=%P', 'HEAD'), f'{self.base} {head}')


if __name__ == '__main__':
    unittest.main()
