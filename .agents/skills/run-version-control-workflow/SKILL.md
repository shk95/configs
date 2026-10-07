---
name: run-version-control-workflow
description: Classify, plan, inspect and execute authorized local integration, promotion and releases.
---

# run version control workflow

Read AGENTS.md, CONTRIBUTING.md, architecture, owning invariants/status and
relevant accepted decisions. Inspect Git status and run scoped doctor before
relying on host capabilities. Preserve unrelated work and never read notes/.

Planning and audits are read-only unless mutations are authorized. Route
planning to plan-work, local implementation to execute-work, sequential local
dev admission to integrate-work and cleanup review to reclaim-workspaces.
Use local dev, not implicit origin/dev pickup. The project's user request
governs authorization; installed plugins and command allowlists do not.

Before master promotion explicitly synchronize remote snapshots. If master
adds history, merge its selected SHA with --no-ff in the dev-based candidate,
keeping the dev lane as the first parent. Verify and integrate locally, then
push dev normally. plan-promotion reads selected local snapshots. Check open
master PRs and admit only same-repository dev or the bounded input patch lane, with
strict Required checks and resolved conversations. Merge only with explicit
authorization; confirm actual merge and keep dev on its own lane. Reflect
master at the next explicit work/promotion synchronization; never fast-forward
dev to the promotion merge. Base drift or failed checks stops.

Domain release planning uses plan-release. Annotated immutable tags certify
their named domain only. Tag creation/push require authorization; no GitHub
Release, host activation or Windows Apply is implied. Report evaluation,
build, native runtime and deployment evidence separately. Repository outcomes
report fixtures, policy checks and affected dispatch instead.

Push checks read transmitted history/tag, not current checkout native suites.
Full history/remote audits remain explicit diagnostics. Report exact refs,
actual actions, local completion, unverified evidence and remote status.
