# Check work plans before staging

kind: spec
date: 2026-09-23
scope: repository
status: approved
review-by: 2026-10-23
issue: #346

The maintainer asked to implement the first two levels of the work-planning
improvement: an agent entry check and a read-only check of an unstaged work
item. The existing index and commit-range gates remain authoritative.

## Problem

The canonical workflow describes spec and report creation, but does not make
their local preflight an explicit step before implementation. The work checker
reads the Git index by default. When a new spec and report are still untracked,
that check can pass over older items without examining the new pair, and its
success line does not name the inspected Git state.

## Decisions

The canonical skill will direct agents to draft a spec and pending report for
multi-criterion work before editing implementation files, then run a check
against that exact work item. It will distinguish a local worktree result from
the staged and committed evidence gates. A changed direction is reflected in
the spec before work continues, using the existing amendment rule once the
report exists.

`tool/version-control/work --working-tree docs/work/<scope>/<slug>` will read
the named item from the filesystem, including files not added to Git. It will
apply the existing W1-W6 rules, fail when the item is absent, and name its
target and source in the result. The existing index, `--staged` and `--range`
modes keep their current subjects and W7 history check. The default success
line will explicitly say it checked the index.

Rejected: automatically staging draft documents for a check. Staging is a Git
mutation and the index is a proposed commit, not a scratch validation area.
Rejected: making the early check a second policy authority or a new CI gate.
Pre-commit and CI already validate committed state.

## Increments

1. The repository fixture lane verifies the new working-tree mode and the
   existing index and range behavior after the skill and checker change.
2. The review lane checks that the skill states the early sequence, the
   command reports its subject precisely, and the documentation describes
   the difference between local feedback and commit evidence.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The canonical workflow makes the spec and pending report a local preflight for multi-criterion work and names the worktree command without treating it as commit evidence. | review |
| AC2 | The checker reads a specified unstaged or untracked item, accepts a valid pair, and refuses a missing target, a missing mate, an unknown lane and a malformed path. | fixtures |
| AC3 | Success identifies the inspected target and source, and the existing index, staged and range behavior continues to pass its fixtures. | fixtures, review |

## Excluded

No new approval gate, automatic staging, branch change, GitHub issue, PR,
deployment, or alteration of the committed-state invariant belongs here.
