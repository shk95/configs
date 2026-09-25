# Repository tool call cleanup

kind: spec
date: 2026-09-25
scope: repository
status: approved
review-by: 2026-10-25
issue: #393

Root governance callers should use the Windows domain entry point, and root
tooling and documentation should describe paths and behavior that still exist.
This is the repository-owned part of the tool cleanup; the Windows directory
rename and Unix-like comment cleanup have their own scope-specific work items.

## Decisions

Route CI and pre-push Windows validation and tests through the public
`windows/win-env.ps1` verbs. Check each exit status immediately, including
contributor setup and the separate CI Zellij installation. Keep the CI job's
native Windows evidence distinct from repository fixtures.

Remove the unreachable worktree installer branch. Make root guidance and
fixtures independent of the private Windows tool directory name. Retire the
two repository candidates whose entry-point and stale-text observations this
work resolves. Preserve historical records as historical records.

## Increments

1. Repository fixtures and policy checks cover the root call sites and tool.
2. Affected dispatch and review confirm the root hook and CI wiring and the
   current root documentation.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | CI and pre-push invoke the Windows validate and test verbs through the public entry point and stop on each failed status; CI also stops on failed setup and Zellij installation. | fixtures, affected dispatch |
| AC2 | The unreachable worktree installer branch and inaccurate root current-state text are removed, and root references no longer depend on the Windows private tool directory name. | review |
| AC3 | The resolved repository candidates are retired and the repository checker and scope dispatch pass for this change. | policy checks, review |

## Evidence boundary

The repository-only PR does not dispatch the native Windows CI job. Here the
affected-dispatch lane means the root selector and hook's selected check path;
the following Windows-scope PR supplies the native Windows job's runtime
evidence. Repository fixtures do not establish native Windows behavior. No
host Apply or activation is part of this work.
