# GitHub-centered agent workflow
date: 2026-09-26
scope: repository
status: accepted
issue: #412
reopen-when: A second concurrent integration controller or supported native-stack operation is required.

## Decision

Use project-local planning, execution, integration, inspection and reclamation
skills. Roles can change after a worker checkpoints unfinished work. Separate
roadmap priorities from pickup-ready plans, allow standalone plans and a small
single-criterion direct-worker path. Record plan revision and execution base at
pickup; do not freeze the execution base when a plan is drafted.

One coherent same-scope result is one PR even when verification spans several
lanes. This replaces the lane-per-PR interpretation of the work model without
changing spec/report format, evidence separation or the amendment rule. The
stable pull-request-spans-an-evidence-lane invariant ID remains for references.

GitHub PRs are integration authority; worktrees are disposable execution space.
Draft means work in progress; Ready means worker delivery. A worker cannot arm
auto-merge or merge dev. One authorized maintainer-managed integrator admits a
candidate, refreshes it only if necessary and asks GitHub to merge after fresh
checks. No local queue, PR-state labels, central database or integration lock.
Local notes are ignored checkpoints, not remote-state caches.

The legacy human commit --publish and Windows capture operations retain their
explicitly confirmed publication behavior. Agent workers do not invoke them
for delivery. A later change to these human interfaces requires their owning
scope's contract and tests; no behavior is removed merely because agent roles
have different authority.

## Protection and dependencies

Keep dev PR-only with Required checks, strict base, administrator enforcement,
resolved conversations and no force pushes or deletions. Merge Queue is not
used for the personal-owned repository. Auto-merge is admission convenience,
not a branch updater or a queue. The default is an immediate head-matched
merge after checks; recover outstanding requests from GitHub and cancel them
before worker repair, because an armed request may admit a later worker head. CODEOWNERS requires real reviewer identities;
ordinary changes do not acquire a blanket human review requirement.

A separate public native-stack lab demonstrated layer CI, automatic rebases,
conflicts, remote recovery and shared merge commits. That experiment does not
certify this repository's actual CI and policies. Production stacks remain
unsupported until trunk scope validation and all-layer admission are proven.
Dependent work waits for its prerequisite to merge; independent work starts
from origin/dev. No implicit permission to rewrite published branches.

## Transition and cost

The operating contract takes effect with its dev merge. Existing workers adopt
it at the next recorded handoff; preserve commits and useful local data. Local
role enforcement is procedural, not a credential sandbox. Missing session
metadata and uncertain liveness require operator judgment. GitHub remains
recoverable without the local checkpoint; unpushed local work does not.

Test-efficiency follow-ups separate ownership from effect, remove non-verifying
work and preserve conservative shared-input coverage. Keep repeated post-merge
validation until identical validated inputs and the actual result are proven;
no optimistic reuse based only on PR green status. Historical reports and
completed decisions remain historical; current procedures describe this model.
