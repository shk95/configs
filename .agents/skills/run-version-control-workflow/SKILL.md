---
name: run-version-control-workflow
description: Audit and execute this repository's version-control workflow. Use when starting or classifying a change, preparing commits, checking branch and history policy, integrating dev into master, planning a domain release tag, or verifying that Git history, hooks, and CI follow the documented unixlike, windows, common, adoption, and repository-governance rules.
---

# Run Version Control Workflow

Execute repository policy without becoming its source of truth. Keep audit and
planning read-only unless the user explicitly authorizes a Git mutation.

## Establish authority

1. Resolve the repository root with `git rev-parse --show-toplevel` and work
   from it.
2. Read `AGENTS.md`, `CONTRIBUTING.md`, `docs/architecture.md`, the relevant
   section of `docs/status.md`, and `docs/definition-of-done.md` completely
   enough to apply the requested workflow.
3. Classify the intended scope, then run `tool/doctor.sh <scope>` before relying
   on host-local capabilities. Use the unscoped form only for cross-domain
   inventory. Treat a missing foreign-domain capability as unavailable
   evidence, not as failure of an unrelated domain.
4. Inspect `git status --short --branch` before suggesting or performing any
   action. Preserve unrelated user changes.

## Select one operation

- **Audit**: Run `tool/version-control/audit`. When `gh` is authenticated, also
  run `tool/version-control/audit-remote`. Explain every warning or failure with
  the governing context file. Do not mutate local or remote Git state.
- **Classify**: Run `tool/version-control/classify` for the requested diff.
  Confirm one owning scope. Multiple configuration scopes require an explicit
  adoption or split; `repository` may accompany a domain only for supporting
  documentation or enforcement.
- **Start**: Propose `feature/<scope>-<topic>` or `fix/<scope>-<topic>` from
  `dev`. Fetch, create a branch, or add a worktree only after the user
  explicitly requests that mutation.
- **Prepare**: Review the complete diff, classification, commit boundaries,
  relevant checks, and evidence. Keep `flake.lock` refreshes isolated in
  `chore(unixlike-deps)` commits. Never stage or commit without an explicit
  request.
- **Integrate**: Require relevant checks, preserve merge commits, and refuse
  squash or rebase of published work. Do not merge, push, or change branches
  without explicit authorization.
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
