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
3. Classify the intended scope, then run `tool/doctor.sh <scope>` before relying
   on host-local capabilities. Use the unscoped form only for cross-domain
   inventory. Treat a missing foreign-domain capability as unavailable
   evidence, not as failure of an unrelated domain.
4. Inspect `git status --short --branch` before suggesting or performing any
   action. Preserve unrelated user changes.

## Select one operation

- **Audit**: Run `tool/version-control/audit`,
  `tool/version-control/hygiene`, `tool/version-control/domain-reads` and
  `tool/version-control/provisional`.
  When `gh` is authenticated, also run
  `tool/version-control/audit-remote`. Explain every warning or failure with
  the governing context file. A hygiene finding is fixed by removing or
  declaring the value, never by widening the check; `CONTRIBUTING.md` owns that
  procedure. Do not mutate local or remote Git state.
- **Classify**: Run `tool/version-control/classify` for the requested diff.
  Confirm one owning scope; a document's scope is the directory, or the
  scope-named file, that holds it. `CONTRIBUTING.md`, "Branch and commit
  flow", owns the rule.
- **Start**: Propose `feature/<scope>-<topic>` or `fix/<scope>-<topic>` from
  `dev`. Fetch, create a branch, or add a worktree only after the user
  explicitly requests that mutation. A worktree made for an implementer is kept,
  with the ability to resume that implementer in it, until the pull request
  from its branch has merged: review feedback returns to the same worktree,
  and one removed earlier costs a fresh setup for every fix.
- **Work**: Follow `CONTRIBUTING.md`, "Plan and verify work". Before editing
  implementation for work with more than one acceptance criterion or more
  than one pull request, draft its spec and a report with pending rows under
  `docs/work/<scope>/<slug>/`. Name the decisions, rejected alternatives,
  evidence-lane increments and required lanes, then run
  `tool/version-control/work --working-tree docs/work/<scope>/<slug>` against
  that exact item. Resolve failures before proceeding. If a decision changes,
  update the spec before continuing; once the report exists, follow the dated
  amendment rule. This read-only worktree check is early feedback, not staged
  or committed evidence. The spec and report enter the same commit and
  `tool/version-control/work --staged` checks that proposed commit when
  staging is explicitly authorized. Any other change carries its evidence
  in the pull request body. Open the execution issue only when
  implementation starts, name the spec on its first line, and keep acceptance
  criteria and evidence out of it. Create no GitHub milestone. Cut a spec's
  pull requests at its evidence lanes and scopes, not at its steps, and keep
  the report rows, the status sentence and the report's end in the pull
  request whose evidence they record; propose a bookkeeping-only pull
  request only when its evidence was produced outside the repository, and
  say so in its body. Restate the
  exact issue targets before remote writes, report every created URL, link
  issues with `Refs #<n>`, and never present a finished report or a closed
  issue as release or deployment evidence.
- **Prepare**: Review the complete diff, classification, commit boundaries,
  relevant checks, and evidence. Keep `unixlike/flake.lock` refreshes isolated
  in `chore(unixlike-deps)` commits. Never stage or commit without an explicit
  request.
- **Integrate**: Merge a topic branch into `dev`. Require relevant checks,
  preserve merge commits, and refuse squash or rebase of published work. Catch
  a stale branch up by merging `dev` into it locally and pushing, never with
  `gh pr update-branch`. Do
  not merge, push, or change branches without explicit authorization.
  `tool/worktree.sh done` removes an implementer's worktree and runs only at
  the point Start names; the publish helper prunes the merged branch, never
  the worktree.
- **Promote**: Run `tool/version-control/plan-promotion`. Permit only a
  same-repository `dev` to `master` pull request, ensure no competing promotion
  is open, and introduce no fix in the promotion itself. Require `Required
  checks`, resolved conversations, and explicit authorization before a merge
  commit. Run both audits afterward. Do not reverse-merge the promotion commit
  into `dev`; do not infer release or deployment.
- **Release**: Run `tool/version-control/plan-release <domain> [commit]` first.
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
