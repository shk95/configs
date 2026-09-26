---
name: run-version-control-workflow
description: Audit and execute this repository's version-control workflow. Use when starting or classifying a change, planning work and its pull requests, preparing commits, integrating topic branches, promoting dev into master, planning a domain release tag, or verifying that Git history, hooks, CI, and branch protection follow the documented unixlike, windows, common, adoption, and repository-governance rules.
---

# Run Version Control Workflow

Execute repository policy without becoming its source of truth. Keep audit and
planning read-only unless the user explicitly authorizes a Git mutation.

## Establish authority

1. Resolve the repository root with `git rev-parse --show-toplevel` and work
   from it.
2. Read `AGENTS.md`, `CONTRIBUTING.md`, `docs/policy/architecture.md`, the scope's
   current state in `docs/status/<scope>.md` and the decision records it cites,
   `docs/policy/definition-of-done/`, and `docs/policy/invariants/<scope>/` for the classified
   scope, completely enough to apply the requested workflow.
3. Classify the intended scope, then run `tool/configs doctor <scope>` before relying
   on host-local capabilities. Use the unscoped form only for cross-domain
   inventory. Treat a missing foreign-domain capability as unavailable
   evidence, not as failure of an unrelated domain.
4. Inspect `git status --short --branch` before suggesting or performing any
   action. Preserve unrelated user changes.

## Select one operation

- **Audit**: Run `tool/configs audit`,
  `tool/configs hygiene`, `tool/configs domain-reads` and
  `tool/configs provisional`.
  When `gh` is authenticated, also run
  `tool/configs audit-remote`. Explain every warning or failure with
  the governing context file. A hygiene finding is fixed by removing or
  declaring the value, never by widening the check; `CONTRIBUTING.md` owns that
  procedure. Do not mutate local or remote Git state.
- **Classify**: Run `tool/configs classify` for the requested diff.
  Confirm one owning scope; a document's scope is the directory, or the
  scope-named file, that holds it. `CONTRIBUTING.md`, "Branch and commit
  flow", owns the rule.
- **Plan or start**: Route intent through plan-work. It finds existing work or
  recognizes a small unambiguous task for execute-work. Use execute-work for
  a picked-up worker lane, integrate-work for GitHub admission, inspect-work
  for status, and reclaim-workspaces for cleanup review. Each lives beside
  this skill under .agents/skills/. A role switch from unfinished execution
  requires a checkpoint, not forced completion. Existing authorization carries
  through the agreed scope; do not ask again for each permitted mutation.
- **Prepare**: Review the complete diff, classification, commit boundaries,
  relevant checks, and evidence. Keep `unixlike/flake.lock` refreshes isolated
  in `chore(unixlike-deps)` commits. Never stage or commit without an explicit
  request.
- **Integrate**: Use integrate-work. Worker authorization ends at Ready PR
  delivery. GitHub provides candidates and protected dev accepts only PRs.
  Do not infer candidates from local worktree or branch inventories.
- **Promote**: Run `tool/configs plan-promotion`. Permit only a
  same-repository `dev` to `master` pull request, ensure no competing promotion
  is open, and introduce no fix in the promotion itself. Require `Required
  checks`, resolved conversations, and explicit authorization before a merge
  commit. Run both audits afterward. Do not reverse-merge the promotion commit
  into `dev`; do not infer release or deployment.
- **Release**: Run `tool/configs plan-release <domain> [commit]` first.
  Require the Definition of Done evidence and an annotated, new, immutable tag
  reachable from `master`. Creating and pushing the tag are separate mutations
  and each requires explicit authorization. Create no GitHub Release; the
  annotation is the record. Never infer activation or Apply from a release
  tag.

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
