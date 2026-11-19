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
import sys
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]


class Workflow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve() / 'repo'
        self.root.mkdir()
        self.git('init', '-q', '-b', 'master')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.root / 'docs/status').mkdir(parents=True)
        (self.root / 'docs/status/repository.md').write_text('base\n')
        trace = ('if [ -n "${FIXTURE_EXECUTION_LOG:-}" ]; then\n'
                 ' python3 -c \'import json,os,sys; '
                 'open(os.environ["FIXTURE_EXECUTION_LOG"],"a").write('
                 'json.dumps(sys.argv[1:])+"\\n")\' "$0" "$@"\nfi\n')
        for name in ['workflow', 'authoring', 'policy', 'policy.json', 'repo_policy.py', 'git_workflow.py', 'github_proof.py',
                     'topic_scope.py', 'topic-source', 'audit', 'classify', 'closing-keywords', 'hooks.sh',
                     'incoming-range.sh', 'scan-secrets']:
            dest = self.root / 'tool/version-control' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / 'tool/version-control' / name, dest)
            if name in ('audit', 'scan-secrets'):
                dest.write_text(dest.read_text().replace('set -eu\n', 'set -eu\n' + trace, 1))
        fixture_workflow = self.root / '.github/workflows/ci.yml'
        fixture_workflow.parent.mkdir(parents=True)
        shutil.copy(ROOT / '.github/workflows/ci.yml', fixture_workflow)
        (self.root / '.githooks').mkdir()
        for name in ('commit-msg', 'pre-push', 'evidence'):
            shutil.copy(ROOT / '.githooks' / name, self.root / '.githooks' / name)
        # Real workflow invokes fixture-owned check commands; failure injection
        # proves checks and identities gate integration, not their semantics.
        for name in ['work', 'hygiene', 'domain-reads', 'design-citations', 'records', 'invariants', 'provisional', 'test']:
            dest = self.root / 'tool/version-control' / name
            dest.write_text('#!/bin/sh\n' + trace + 'exit "${FIXTURE_CHECK_STATUS:-0}"\n')
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
        self.workflow('start', '--commits', 'many', '--topic', 'example', '--workspace', 'current')
        for n in range(2):
            (self.root / 'docs/status/repository.md').write_text(f'change {n}\n')
            self.head = self.commit(f'feat(repository): change {n}')

    def test_start_requires_workspace_and_preserves_dirty_or_invalid_state(self):
        refs = self.git('show-ref')
        self.workflow('start', '--scope', 'repository', '--topic', 'example', '--workspace', 'linked', ok=False)
        self.workflow('start', '--commits', 'many', '--topic', 'example', ok=False)
        self.workflow('start', '--commits', 'many', '--workspace', 'current', ok=False)
        self.workflow('start', '--commits', 'one', '--workspace', 'current')
        self.assertEqual(self.git('show-ref'), refs)
        self.workflow('start', '--commits', 'many', '--topic', 'example', '--workspace', 'linked', '--dry-run')
        preview = json.loads(self.workflow('start', '--commits', 'one', '--topic', 'example',
                                           '--workspace', 'current', '--dry-run'))
        self.assertEqual(preview['branch'], 'topic/example')
        self.assertEqual(self.git('show-ref'), refs)
        (self.root / 'untracked').write_text('preserve')
        self.workflow('start', '--commits', 'many', '--topic', 'example', '--workspace', 'current', ok=False)
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

    def test_topic_keeps_separately_owned_commits_in_one_master_merge(self):
        # INV repository/local-development-integration
        # INV repository/topic-source
        self.workflow('start', '--topic', 'program-supply', '--workspace', 'current')
        branch = 'topic/program-supply'
        self.assertEqual(self.git('branch', '--show-current'), branch)
        self.call(str(self.root / 'tool/version-control/authoring'))

        (self.root / 'unixlike').mkdir()
        (self.root / 'unixlike/probe.txt').write_text('implementation\n')
        implementation = self.commit('feat(unixlike): implement program supply')
        (self.root / 'docs/status/repository.md').write_text('support the implementation\n')
        head = self.commit('docs(unixlike): explain program supply')
        source = str(self.root / 'tool/version-control/topic-source')
        env = dict(os.environ, TOPIC_BASE_REF='master', TOPIC_BASE_SHA=self.base,
                   TOPIC_HEAD_SHA=head, TOPIC_HEAD_REF=branch,
                   TOPIC_BASE_REPOSITORY='fixture/configs', TOPIC_HEAD_REPOSITORY='fixture/configs')
        self.call(source, env=env)
        self.call(source, env=dict(env, TOPIC_HEAD_REF='feature/unixlike-program-supply'), ok=False)
        (self.root / 'unowned').write_text('unclassified fixture\n')
        unclassified = self.commit('test(repository): add unclassified fixture')
        self.call(source, env=dict(env, TOPIC_HEAD_SHA=unclassified), ok=False)
        self.workflow('merge', '--base', self.base, '--head', unclassified, ok=False)
        self.git('reset', '--hard', head)
        self.workflow('merge', '--base', self.base, '--head', head)
        self.assertEqual(self.git('show', '-s', '--format=%P', 'HEAD'), f'{self.base} {head}')
        self.assertEqual(self.git('rev-list', '--no-merges', 'master', '--not', self.base).splitlines(),
                         [head, implementation])

    def test_subtopics_follow_their_immediate_parent(self):
        # INV repository/workspace-choice
        # INV repository/local-development-integration
        # INV repository/topic-source
        topic = 'topic/supply'
        child = topic + '+inventory'
        grandchild = child + '+darwin'
        self.workflow('start', '--commits', 'many', '--topic', 'supply', '--workspace', 'current')
        document = self.root / 'docs/status/repository.md'
        document.write_text('top-level change\n')
        root_head = self.commit('feat(repository): start supply')
        start_child = ('start', '--parent', topic, '--topic', 'inventory', '--workspace', 'current')
        refs = self.git('show-ref')
        self.workflow('start', '--parent', 'master', '--topic', 'inventory',
                      '--commits', 'one', '--workspace', 'linked', ok=False)
        self.workflow('start', '--topic', 'supply+inventory', '--commits', 'many',
                      '--workspace', 'linked', ok=False)
        self.assertEqual(self.git('show-ref'), refs)
        self.workflow(*start_child)
        self.assertEqual(self.git('branch', '--show-current'), child)
        self.assertEqual(self.git('rev-parse', 'HEAD'), root_head)
        document.write_text('inventory change\n')
        child_head = self.commit('feat(repository): inventory source')

        self.workflow('start', '--parent', child, '--topic', 'darwin', '--workspace', 'linked')
        linked = self.root.parent / 'repo-wt/topic-supply+inventory+darwin'
        self.assertEqual(self.git('branch', '--show-current', cwd=linked), grandchild)
        self.assertEqual(self.git('rev-parse', 'HEAD', cwd=linked), child_head)
        inspection = json.loads(self.workflow('inspect', cwd=linked))
        self.assertEqual(inspection['merge_target'], child)
        self.assertEqual(inspection['head'], child_head)
        self.call(str(self.root / 'tool/version-control/authoring'), cwd=linked)
        self.git('config', 'core.hooksPath', '.githooks')
        self.call(str(self.root / 'tool/version-control/audit'), cwd=linked)
        (linked / 'docs/status/repository.md').write_text('darwin change\n')
        self.git('commit', '-qam', 'feat(repository): darwin source', cwd=linked)
        deepest = self.git('rev-parse', 'HEAD', cwd=linked)
        env = dict(os.environ, TOPIC_BASE_REF='master', TOPIC_BASE_SHA=self.base,
                   TOPIC_HEAD_SHA=deepest, TOPIC_HEAD_REF=grandchild,
                   TOPIC_BASE_REPOSITORY='fixture/configs', TOPIC_HEAD_REPOSITORY='fixture/configs')
        self.call(str(self.root / 'tool/version-control/topic-source'), env=env, ok=False)
        self.workflow('merge', '--base', self.base, '--head', deepest, cwd=linked, ok=False)
        self.assertEqual(self.git('rev-parse', 'master'), self.base)

        (self.root / 'README.md').write_text('parallel inventory work\n')
        advanced = self.commit('feat(repository): advance inventory independently')
        refs = self.git('show-ref')
        self.workflow('merge', '--base', child_head, '--head', deepest, cwd=linked, ok=False)
        self.assertEqual(self.git('show-ref'), refs)
        # Intermediate integration audits ownership and history. Full suite
        # execution is deferred to the combined top-level candidate.
        env = dict(os.environ, FIXTURE_CHECK_STATUS='1')
        self.workflow('merge', '--base', advanced, '--head', deepest, cwd=linked, env=env)
        assembled_child = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.git('show', '-s', '--format=%P', 'HEAD'), f'{advanced} {deepest}')
        self.assertEqual(self.git('rev-parse', topic), root_head)
        self.assertEqual(self.git('rev-parse', 'master'), self.base)
        self.workflow('merge', '--base', assembled_child, '--head', deepest, cwd=linked, ok=False)
        self.assertEqual(self.git('rev-parse', child), assembled_child)

        self.workflow('merge', '--base', root_head, '--head', assembled_child, env=env)
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.git('branch', '--show-current'), topic)
        self.assertEqual(self.git('show', '-s', '--format=%P', 'HEAD'), f'{root_head} {assembled_child}')
        self.assertEqual(self.git('show', '-s', '--format=%s', 'HEAD'), f"Merge branch '{child}' into {topic}")
        self.workflow('merge', '--base', self.base, '--head', head, env=env, ok=False)
        self.assertEqual(self.git('rev-parse', 'master'), self.base)
        self.workflow('merge', '--base', self.base, '--head', head)
        self.assertEqual(self.git('show', '-s', '--format=%P', 'master'), f'{self.base} {head}')

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
        # A configured ours strategy could keep master content while recording
        # the correct parents. Integration must preserve the verified tree.
        self.git('config', 'branch.master.mergeOptions', '--strategy=ours')
        self.workflow(*args)
        self.assertEqual(self.git('show', '-s', '--format=%P', 'HEAD'), f'{self.base} {self.head}')
        self.assertEqual(self.git('rev-parse', 'HEAD^{tree}'), self.git('rev-parse', self.head + '^{tree}'))
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
        self.git('switch', '-q', 'topic/example')
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
        self.git('branch', '-m', 'topic/example')
        if os.name != 'nt':
            (self.root / 'tool/dispatch/select').write_text('#!/bin/sh\ncat >/dev/null\necho windows:suite\n')
            head = self.commit('test(repository): select native Windows checks')
            planned = json.loads(self.workflow('plan', '--base', self.base, '--head', head))
            self.assertTrue(planned['blockers'])
            self.assertEqual(planned['steps'][-1]['argv'][:4],
                             ['pwsh', '-NoProfile', '-File', 'windows/win-env.ps1'])
            self.workflow('check', '--base', self.base, '--head', head, ok=False)
            self.assertEqual(self.git('rev-parse', 'master'), self.base)

    def test_pr_and_local_topic_scope_agree_without_counting_new_base_work(self):
        # INV repository/topic-source
        self.topic()
        self.git('branch', '-m', 'feature/repository-example')
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
        # INV repository/scope-ownership
        # INV repository/topic-source
        self.topic()
        self.git('branch', '-m', 'feature/repository-example')
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
        self.git('branch', '-m', 'topic/example')
        # A scope-neutral topic is eligible by name and final path ownership,
        # but the common CI/local range audit still refuses the mixed commit.
        self.call(str(self.root / 'tool/version-control/topic-source'),
                  env=dict(env, TOPIC_HEAD_REF='topic/example'))
        self.workflow('check', '--base', self.base, '--head', head, ok=False)

    def test_topic_refuses_reverted_foreign_scope_even_when_each_commit_is_pure(self):
        # INV repository/topic-source
        self.topic()
        self.git('branch', '-m', 'feature/repository-example')
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

    def test_range_rejects_merge_only_effects_and_commit_bodies(self):
        # INV repository/scope-ownership
        # INV repository/flake-lock-isolated
        # INV repository/no-closing-keyword
        side = self.git('commit-tree', 'HEAD^{tree}', '-p', self.base, '-m', 'test(repository): also in history')
        main = self.git('commit-tree', 'HEAD^{tree}', '-p', self.base, '-m', 'test(repository): integration line')
        merge = self.git('commit-tree', 'HEAD^{tree}', '-p', main, '-p', side, '-m', 'Merge clean side')
        audit = str(self.root / 'tool/version-control/audit')
        self.call(audit, '--range', self.base, merge)

        bad_body = self.git('commit-tree', 'HEAD^{tree}', '-p', main, '-p', side,
                            '-m', 'Merge side', '-m', 'Fixes #23')
        self.call(audit, '--range', self.base, bad_body, ok=False)
        ordinary = self.git('commit-tree', 'HEAD^{tree}', '-p', main,
                            '-m', 'fix(repository): ordinary source', '-m', 'Fixes #23')
        self.call(audit, '--range', self.base, ordinary, ok=False)

        for path, error in (('unowned', 'merge commit has an unclassified path'),
                            ('unixlike/flake.lock', 'merge introduced a lock value')):
            with self.subTest(path=path):
                p = self.root / path
                p.parent.mkdir(exist_ok=True)
                p.write_text('appeared during integration\n')
                self.git('add', path)
                tree = self.git('write-tree')
                bad = self.git('commit-tree', tree, '-p', main, '-p', side, '-m', 'Merge with unexpected content')
                self.git('rm', '-q', '-f', path)
                tip = self.git('commit-tree', 'HEAD^{tree}', '-p', bad, '-m', 'fix(repository): restore tree')
                result = subprocess.run([audit, '--range', self.base, tip], cwd=self.root, text=True, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(error, result.stderr)

    def test_secret_range_passes_merge_diffs_and_side_commits_to_scanner(self):
        # INV repository/no-secret-in-history
        # Scanner stand-in uses the exact patch stream consumed by gitleaks.
        scanner = self.root / 'tool/gitleaks'
        scanner.write_text('''#!/usr/bin/env python3
import subprocess
import sys
if sys.argv[1] == 'stdin':
    sys.stdin.read()
    sys.exit(0)
options = next(arg.split('=', 1)[1].split() for arg in sys.argv if arg.startswith('--log-opts='))
patch = subprocess.check_output(['git', '-C', sys.argv[-1], 'log', '-p', '-U0', *options], text=True)
print(patch)
''')
        file = self.root / 'docs/status/repository.md'
        file.write_text('side observation\n')
        self.commit('test(repository): add side observation')
        file.write_text('base\n')
        side = self.commit('test(repository): remove side observation')
        file.write_text('merge result observation\n')
        self.git('add', str(file))
        tree = self.git('write-tree')
        merge = self.git('commit-tree', tree, '-p', self.base, '-p', side, '-m', 'Merge side with result')
        scan = str(self.root / 'tool/version-control/scan-secrets')
        output = self.call(scan, '--range', self.base, merge)
        self.assertIn('+side observation', output)
        self.assertIn('+merge result observation', output)
        self.assertEqual(self.call(scan, '--range', merge, merge).strip(), '')
        self.assertIn('+side observation', self.call(str(self.root / 'tool/version-control/audit'), '--secrets-history'))

    def test_new_ref_uses_receiver_master_and_secret_refusal_vetoes_push(self):
        # INV repository/no-secret-in-history
        receiver = Path(self.tmp.name) / 'receiver.git'
        self.git('init', '-q', '--bare', str(receiver))
        self.git('push', '-q', '--no-verify', str(receiver), self.base + ':refs/heads/master')
        self.git('config', 'core.hooksPath', '.githooks')
        (self.root / 'docs/status/repository.md').write_text('new local master\n')
        local_master = self.commit('test(repository): new local master')
        env = dict(os.environ, FIXTURE_SECRET_STATUS='69')
        self.git('push', '-q', str(receiver), 'HEAD:refs/heads/topic/new', ok=False, env=env)
        self.assertEqual(self.git('ls-remote', str(receiver), 'refs/heads/topic/new'), '')
        trace = Path(self.tmp.name) / 'push-commands.jsonl'
        env.update(FIXTURE_SECRET_STATUS='0', FIXTURE_EXECUTION_LOG=str(trace))
        self.git('push', '-q', str(receiver), 'HEAD:refs/heads/topic/new', env=env)
        calls = [json.loads(line) for line in trace.read_text().splitlines()]
        self.assertTrue(any(call[0].endswith('/scan-secrets') and call[1:] == ['--range', self.base, local_master] for call in calls))

    def test_release_tag_cannot_publish_unaccepted_master_history(self):
        # INV repository/release-tag-contract
        receiver = Path(self.tmp.name) / 'receiver.git'
        self.git('init', '-q', '--bare', str(receiver))
        self.git('push', '-q', '--no-verify', str(receiver), self.base + ':refs/heads/master')
        self.git('config', 'core.hooksPath', '.githooks')
        (self.root / 'docs/status/repository.md').write_text('unpublished local commit\n')
        self.commit('test(repository): move local master')
        tag = 'unixlike-v0.0.1'
        self.git('tag', '-a', tag, '-m',
                 'Domain: unixlike\nEvaluation: passed\nBuild: unavailable\nNative runtime: unavailable')
        ref = 'refs/tags/' + tag
        self.git('push', '-q', str(receiver), ref, ok=False)
        self.assertEqual(self.git('ls-remote', str(receiver), ref), '')
        self.git('push', '-q', str(receiver), 'refs/heads/master')
        self.git('push', '-q', str(receiver), ref)
        self.assertIn(self.git('rev-parse', ref), self.git('ls-remote', str(receiver), ref))

    def test_push_scans_commit_messages_and_annotated_tags(self):
        # INV repository/no-secret-in-history
        scanner = self.root / 'tool/gitleaks'
        scanner.write_text('''#!/usr/bin/env python3
import sys
if sys.argv[1] == 'stdin' and 'private-fixture-marker' in sys.stdin.read():
    raise SystemExit(1)
''')
        receiver = Path(self.tmp.name) / 'receiver.git'
        self.git('init', '-q', '--bare', str(receiver))
        self.git('push', '-q', '--no-verify', str(receiver), self.base + ':refs/heads/master')
        self.git('config', 'core.hooksPath', '.githooks')
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-q', '--allow-empty',
                 '-m', 'test(repository): metadata fixture', '-m', 'private-fixture-marker')
        self.git('push', '-q', str(receiver), 'master', ok=False)
        self.assertIn(self.base, self.git('ls-remote', str(receiver), 'refs/heads/master'))

        annotation = 'Domain: unixlike\nEvaluation: unavailable\nBuild: unavailable\nNative runtime: unavailable'
        rejected = 'refs/tags/unixlike-v0.0.1'
        accepted = 'refs/tags/unixlike-v0.0.2'
        self.git('tag', '-a', 'unixlike-v0.0.1', self.base, '-m', annotation + '\nprivate-fixture-marker')
        self.git('tag', '-a', 'unixlike-v0.0.2', self.base, '-m', annotation)
        self.git('push', '-q', str(receiver), rejected, ok=False)
        self.assertEqual(self.git('ls-remote', str(receiver), rejected), '')
        self.git('push', '-q', str(receiver), accepted)
        self.assertIn(self.git('rev-parse', accepted), self.git('ls-remote', str(receiver), accepted))

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
            with patch.object(implementation, 'os', SimpleNamespace(name='nt', environ=os.environ)), \
                 patch.dict(os.environ, PATH=str(self.root / 'tool') + os.pathsep + os.environ['PATH']):
                with self.assertRaisesRegex(ValueError, 'runtime wiring requires exact hosted evidence'):
                    implementation.check(self.root, self.base, head)
        finally:
            os.chdir(previous)

    def test_plan_reads_exact_candidate_without_checks_or_git_writes(self):
        # INV repository/local-development-integration
        self.topic()
        def snapshot():
            return {str(path.relative_to(self.root)): (path.stat().st_mode, path.read_bytes())
                    for path in self.root.rglob('*') if path.is_file()}
        before = snapshot()
        result = json.loads(self.workflow('plan', '--base', self.base, '--head', self.head,
                            env=dict(os.environ, FIXTURE_CHECK_STATUS='1', FIXTURE_SECRET_STATUS='1')))
        self.assertEqual(snapshot(), before)
        self.assertEqual((result['state'], result['base'], result['head']),
                         ('not-run', self.base, self.head))
        self.assertEqual(result['tree'], self.git('rev-parse', self.head + '^{tree}'))
        self.assertEqual(result['units'], ['repository:fixtures'])
        self.assertEqual(result['blockers'], [])
        self.assertEqual(result['steps'][-1]['argv'], ['tool/version-control/test'])
        (self.root / 'docs/status/repository.md').write_text('dirty preparation\n')
        self.workflow('plan', '--base', self.base, '--head', self.head, ok=False)

    def test_check_executes_the_ordered_local_plan(self):
        # INV repository/local-gate-selects-by-effect
        self.topic()
        args = ['--base', self.base, '--head', self.head]
        planned = json.loads(self.workflow('plan', *args))
        trace = Path(self.tmp.name) / 'executed.jsonl'
        self.workflow('check', *args, env=dict(os.environ, FIXTURE_EXECUTION_LOG=str(trace)))
        observed = [json.loads(line) for line in trace.read_text().splitlines()]
        expected = []
        for step in planned['steps']:
            command = step['argv'][:]
            if command[0].startswith('tool/'):
                command[0] = str(self.root / command[0])
            else:
                command[0] = str(self.root / 'tool' / command[0])
            expected.append(command)
        self.assertEqual(observed, expected)

    def test_plan_exposes_native_blocker_and_hosted_alternative_without_gh(self):
        # INV repository/windows-ci-runtime-bound
        self.topic()
        bin_dir = Path(self.tmp.name) / 'hosted-spy'
        bin_dir.mkdir()
        gh = bin_dir / 'gh'
        gh.write_text('#!/bin/sh\nexit 97\n')
        gh.chmod(0o755)
        env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'])
        (self.root / 'tool/dispatch/select').write_text('#!/bin/sh\ncat >/dev/null\necho windows:runtime\n')
        head = self.commit('test(repository): select hosted runtime evidence')
        args = ['--base', self.base, '--head', head]
        blocked = json.loads(self.workflow('plan', *args, env=env))
        self.assertIn('runtime wiring', blocked['blockers'][0])
        # A proof identifier is not queried or accepted as successful evidence.
        hosted = json.loads(self.workflow('plan', *args, '--ci-run', '123', env=env))
        self.assertEqual(hosted['blockers'], [])
        self.assertEqual([step['id'] for step in hosted['steps'] if step['source'] == 'hosted'],
                         ['ci-proof', 'windows:runtime'])
        self.assertEqual(['provisional'], [step['id'] for step in hosted['steps'] if step['source'] == 'local'])

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
        self.workflow('start', '--commits', 'many', '--topic', 'linked', '--workspace', 'linked')
        linked = self.root.parent / 'repo-wt/topic-linked'
        self.assertTrue(linked.is_dir())
        self.assertEqual(self.git('rev-parse', 'HEAD', cwd=linked), self.base)
        self.assertEqual(self.git('branch', '--show-current'), 'master')
        (linked / 'docs/status/repository.md').write_text('linked\n')
        self.git('add', '.', cwd=linked)
        self.git('commit', '-qm', 'feat(repository): linked change', cwd=linked)
        head = self.git('rev-parse', 'HEAD', cwd=linked)
        self.git('switch', '-qc', 'topic/parked')
        self.workflow('merge', '--base', self.base, '--head', head, cwd=linked, ok=False)
        self.assertEqual(self.git('branch', '--show-current', cwd=linked), 'topic/linked')
        self.assertEqual(self.git('rev-parse', 'master'), self.base)
        self.git('switch', '-q', 'master')
        self.workflow('merge', '--base', self.base, '--head', head, cwd=linked)
        self.assertEqual(self.git('show', '-s', '--format=%P', 'HEAD'), f'{self.base} {head}')
        self.assertEqual(self.git('show', '-s', '--format=%s', 'HEAD'), "Merge branch 'topic/linked' into master")
        self.assertEqual(self.git('branch', '--show-current', cwd=linked), 'topic/linked')


if __name__ == '__main__':
    unittest.main()
