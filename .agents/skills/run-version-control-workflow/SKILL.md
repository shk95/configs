---
name: run-version-control-workflow
description: Audit and execute this repository's version-control workflow. Use when starting or classifying a change, planning GitHub milestones, preparing commits, integrating topic branches, promoting dev into master, planning a domain release tag, or verifying that Git history, hooks, CI, and branch protection follow the documented unixlike, windows, common, adoption, and repository-governance rules.
---

# Run Version Control Workflow

Execute repository policy without becoming its source of truth. Keep audit and
planning read-only unless the user explicitly authorizes a Git mutation.

## Establish authority

1. Resolve the repository root with `git rev-parse --show-toplevel` and work
   from it.
2. Read `AGENTS.md`, `CONTRIBUTING.md`, `docs/architecture.md`, the scope's
   current state in `docs/status.md` and the decision records it cites,
   `docs/definition-of-done.md`, and `invariants/<scope>/` for the classified
   scope, completely enough to apply the requested workflow.
3. Classify the intended scope, then run `tool/doctor.sh <scope>` before relying
   on host-local capabilities. Use the unscoped form only for cross-domain
   inventory. Treat a missing foreign-domain capability as unavailable
   evidence, not as failure of an unrelated domain.
4. Inspect `git status --short --branch` before suggesting or performing any
   action. Preserve unrelated user changes.

## Select one operation

- **Audit**: Run `tool/version-control/audit`,
  `tool/version-control/hygiene` and `tool/version-control/domain-reads`.
  When `gh` is authenticated, also run
  `tool/version-control/audit-remote`. Explain every warning or failure with
  the governing context file. A hygiene finding is fixed by removing or
  declaring the value, never by widening the check; `CONTRIBUTING.md` owns that
  procedure. Do not mutate local or remote Git state.
- **Classify**: Run `tool/version-control/classify` for the requested diff.
  Confirm one owning scope. Multiple configuration scopes require an explicit
  adoption or split; `repository` may accompany a domain only for supporting
  documentation or enforcement.
- **Start**: Propose `feature/<scope>-<topic>` or `fix/<scope>-<topic>` from
  `dev`. Fetch, create a branch, or add a worktree only after the user
  explicitly requests that mutation.
- **Milestone**: Search open and closed GitHub milestones before creating one.
  Confirm one owning scope, the `<scope>: <outcome>` title, the required
  description sections, no due date unless the maintainer supplied one, and
  same-scope issue membership. Restate the exact milestone and issue targets
  before remote writes. Keep a final evidence issue, report every created URL,
  and never present milestone closure as release or deployment evidence.
- **Prepare**: Review the complete diff, classification, commit boundaries,
  relevant checks, and evidence. Keep `flake.lock` refreshes isolated in
  `chore(unixlike-deps)` commits. Never stage or commit without an explicit
  request.
- **Integrate**: Merge a topic branch into `dev`. Require relevant checks,
  preserve merge commits, and refuse squash or rebase of published work. Do
  not merge, push, or change branches without explicit authorization.
- **Promote**: Run `tool/version-control/plan-promotion`. Permit only a
  same-repository `dev` to `master` pull request, ensure no competing promotion
  is open, and introduce no fix in the promotion itself. Require `Required
  checks`, resolved conversations, and explicit authorization before a merge
  commit. Run both audits afterward. Do not reverse-merge the promotion commit
  into `dev`; do not infer release or deployment.
- **Release**: Run `tool/version-control/plan-release <domain> [commit]` first.
  Require the Definition of Done evidence and an annotated, new, immutable tag
  reachable from `master`. Creating and pushing the tag are separate mutations
  and each requires explicit authorization. Never infer activation or Apply
  from a release tag.

## Report evidence

Report these lanes separately for each affected configuration domain:

- evaluation;
- build;
- native runtime check;
- activation or Apply.

For `repository`, report fixture tests, policy checks, and affected dispatch
checks instead. Say `unavailable` or `not applicable` rather than upgrading
partial evidence to success.

End with the current branch and worktree state, actions performed, actions not
performed, and the next authorization boundary.
