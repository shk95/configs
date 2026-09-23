# Report: check work plans before staging

kind: report
spec: docs/work/repository/worktree-work-preflight/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Codex reviewed commit `72a7c3a` on 2026-09-23: the canonical skill and contribution procedure require a pending pair and exact worktree preflight before implementation, while naming staged evidence separately. The maintainer authorized ending the report after this review. |
| AC2 | verified | `tool/version-control/test` passed on commit `72a7c3a`: the fixture accepts an untracked pair and rejects a missing item, missing mate, unknown lane, unexpected file, unstaged spec change and malformed path. |
| AC3 | verified | `tool/version-control/test` passed on commit `72a7c3a`, including the existing index, staged and range fixtures and the new source-label assertions. Codex reviewed the checker and `docs/work/README.md` at that commit on 2026-09-23. |

## Evidence lanes

- Fixtures: `tool/version-control/test` passed on 2026-09-23, both directly and in the implementation commit's pre-commit and pre-push gates. `tool/version-control/work --working-tree docs/work/repository/worktree-work-preflight` and `tool/version-control/work --staged` passed. The pre-push selector chose `repository:fixtures`.
- Policy checks: `tool/version-control/invariants`, `tool/version-control/design-citations`, `sh -n tool/version-control/work tool/version-control/test`, and `git diff --cached --check` passed; the pre-push audit reported no warnings or failures.
- Review: Codex read the full implementation diff at `72a7c3a` for the preflight sequence, exact target, source labels and preserved index, staged and range paths on 2026-09-23. The maintainer authorized the `done` decision after that review.
