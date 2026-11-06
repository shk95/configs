#!/usr/bin/env python3
"""Real disposable index/hook cases; optional fixed-source comparison output."""
# INV repository/staged-checks-use-index
# INV repository/evidence-three-states
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT
CHECK = '''#!/bin/sh
root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
if [ -n "${CASE_TRACE:-}" ]; then printf '%s\\n' "$root" >>"$CASE_TRACE"; fi
for file in "$root"/modules/*; do
  [ -f "$file" ] || continue
  if [ "$(cat "$file")" = bad ]; then exit 1; fi
done
exit "${CASE_CHECK_STATUS:-0}"
'''


def environment():
    result = subprocess.run(
        ['sh', '-c', '. "$1"; env -0', 'sh',
         str(ROOT / 'tool/version-control/fixture-git-environment.sh')],
        stdout=subprocess.PIPE, check=True)
    value = dict(item.split('=', 1) for item in result.stdout.decode().split('\0') if item)
    value.pop('REQUIRE_NATIVE', None)
    return value


class StagedChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='configs-staged-case-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.env = environment()
        self.bin = self.base / 'bin'
        self.bin.mkdir()
        self.env['PATH'] = str(self.bin) + os.pathsep + self.env['PATH']
        self.env['CASE_TRACE'] = str(self.base / 'checks.log')
        self.write(self.bin / 'gitleaks', '#!/bin/sh\nexit 0\n', executable=True)
        for name in ('pre-commit', 'evidence'):
            self.copy('.githooks/' + name)
        for name in ('dispatch/select', 'version-control/classify', 'version-control/hooks.sh'):
            if (SOURCE / 'tool' / name).exists():
                self.copy('tool/' + name)
        for name in ('authoring', 'hygiene', 'domain-reads', 'design-citations',
                     'records', 'work', 'invariants', 'provisional'):
            self.write(self.repo / 'tool/version-control' / name,
                       '#!/bin/sh\nexit 0\n', executable=True)
        for name in ('format', 'lint', 'payloads'):
            self.write(self.repo / 'unixlike/tool/checks' / name, CHECK, executable=True)
        self.target = self.repo / 'unixlike/modules/probe.lua'
        self.write(self.target, 'good\n')
        self.git('init', '-q', '-b', 'master')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('add', '.')
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'test(repository): seed fixture')

    def write(self, path, content, executable=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        if executable:
            path.chmod(0o755)

    def copy(self, name):
        target = self.repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SOURCE / name, target)

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, env=self.env,
                                       text=True, stderr=subprocess.PIPE).strip()

    def stage(self, content):
        self.write(self.target, content + '\n')
        self.git('add', 'unixlike/modules/probe.lua')

    def hook(self, expected):
        index = Path(self.git('rev-parse', '--path-format=absolute', '--git-path', 'index'))
        index = Path(self.env.get('GIT_INDEX_FILE', index))
        before = index.read_bytes()
        source = self.target.read_bytes() if self.target.exists() else None
        refs = self.git('show-ref')
        result = subprocess.run([str(self.repo / '.githooks/pre-commit')], cwd=self.repo,
                                env=self.env, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(index.read_bytes(), before, 'hook changed caller index')
        self.assertEqual(self.target.read_bytes() if self.target.exists() else None,
                         source, 'hook changed caller worktree')
        self.assertEqual(self.git('show-ref'), refs, 'hook changed caller refs')
        self.assertEqual(result.returncode == 0, expected, result.stdout)
        return result.stdout

    def test_bad_staged_content_cannot_hide_behind_clean_worktree(self):
        self.stage('bad')
        self.write(self.target, 'good\n')
        self.hook(False)

    def test_clean_staged_content_survives_bad_unstaged_content(self):
        self.stage('good staged')
        self.write(self.target, 'bad\n')
        self.hook(True)

    def test_checker_implementation_also_comes_from_index(self):
        self.stage('good staged')
        checker = self.repo / 'unixlike/tool/checks/payloads'
        self.write(checker, '#!/bin/sh\nexit 1\n', executable=True)
        self.git('add', 'unixlike/tool/checks/payloads')
        self.write(checker, CHECK, executable=True)
        self.hook(False)

    def test_unstaged_checker_failure_does_not_replace_staged_checker(self):
        self.stage('good staged')
        self.write(self.repo / 'unixlike/tool/checks/payloads',
                   '#!/bin/sh\nexit 1\n', executable=True)
        self.hook(True)

    def test_untracked_files_do_not_join_staged_checks(self):
        self.stage('good staged')
        self.write(self.target.with_name('untracked.lua'), 'bad\n')
        self.hook(True)

    def test_staged_deletion_does_not_read_untracked_replacement(self):
        self.git('rm', '-q', 'unixlike/modules/probe.lua')
        self.write(self.target, 'bad\n')
        self.hook(True)

    def test_linked_hook_context_preserves_source_and_index(self):
        linked = self.base / 'linked'
        self.git('worktree', 'add', '-qb', 'feature/unixlike-fixture', str(linked))
        self.repo = linked
        self.target = linked / 'unixlike/modules/probe.lua'
        self.stage('bad')
        self.write(self.target, 'good\n')
        self.env['GIT_DIR'] = self.git('rev-parse', '--absolute-git-dir')
        self.env['GIT_WORK_TREE'] = str(linked)
        self.hook(False)

    def test_alternate_index_is_honored_without_changing_either_index(self):
        ordinary = self.repo / '.git/index'
        ordinary_before = ordinary.read_bytes()
        alternate = self.base / 'alternate-index'
        shutil.copy(ordinary, alternate)
        self.env['GIT_INDEX_FILE'] = str(alternate)
        self.stage('bad')
        self.write(self.target, 'good\n')
        self.hook(False)
        self.assertEqual(ordinary.read_bytes(), ordinary_before)

    def test_unverified_local_check_and_required_native_remain_distinct(self):
        self.stage('good staged')
        self.env['CASE_CHECK_STATUS'] = '69'
        self.assertIn('unverified', self.hook(True))
        self.env['REQUIRE_NATIVE'] = '1'
        self.hook(False)

    def test_repository_only_change_runs_no_domain_check(self):
        self.write(self.repo / 'README.md', 'repository prose\n')
        self.git('add', 'README.md')
        self.write(self.target, 'bad\n')
        self.hook(True)
        self.assertFalse(Path(self.env['CASE_TRACE']).exists())

    def test_doctor_names_missing_candidate_prerequisite(self):
        # INV repository/evidence-three-states
        self.copy('tool/doctor.sh')
        self.git('config', 'core.hooksPath', '.githooks')
        only = self.base / 'doctor-bin'
        only.mkdir()
        for name in ('dirname', 'git', 'python3', 'sed', 'grep', 'head', 'awk', 'sort'):
            path = shutil.which(name)
            if path:
                (only / name).symlink_to(path)
        self.env['PATH'] = str(only)
        result = subprocess.run([str(self.repo / 'tool/doctor.sh'), 'repository'],
                                cwd=self.repo, env=self.env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('candidate verification unavailable', result.stdout.lower())
        self.assertNotIn('Ready.', result.stdout)


def main():
    global SOURCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=ROOT)
    parser.add_argument('--probe', action='store_true', help='Report each fixed case, including failures, as JSON')
    args = parser.parse_args()
    SOURCE = args.source_root.resolve()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StagedChecks)
    if not args.probe:
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(not result.wasSuccessful())
    cases = []
    started = time.perf_counter()
    for case in suite:
        result = unittest.TestResult()
        before = time.perf_counter()
        case.run(result)
        cases.append(dict(case=case._testMethodName, passed=result.wasSuccessful(),
                          seconds=round(time.perf_counter() - before, 6),
                          errors=[message for _, message in result.errors + result.failures]))
    paths = ('.githooks/pre-commit', '.githooks/evidence', 'tool/doctor.sh',
             'tool/dispatch/select', 'tool/version-control/classify', 'tool/version-control/hooks.sh')
    digest = hashlib.sha256()
    for name in paths:
        path = SOURCE / name
        digest.update(name.encode() + b'\0' + (path.read_bytes() if path.exists() else b'<absent>') + b'\0')
    print(json.dumps(dict(source=str(SOURCE), source_sha256=digest.hexdigest(),
                          seconds=round(time.perf_counter() - started, 6), cases=cases)))


if __name__ == '__main__':
    main()
