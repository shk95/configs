# GitHub-centered agent workflow
kind: spec
date: 2026-09-26
scope: repository
status: approved
review-by: 2026-10-26
issue: #412

## Goal

Separate planning, worker execution, integration admission, inspection and
workspace reclamation. GitHub PRs preserve integration state; dev is canonical.
The maintainer approved this design and test-efficiency follow-up on 2026-09-26.
No merge, promotion, release, activation or Apply is authorized by this work.

## Decisions

Use project skills and small existing-tool extensions, not an orchestration
framework. Roles may change after a worker checkpoints its unfinished work.
Roadmap participation is optional; standalone plans are valid; only a small
single-criterion task may bypass planning. A plan is reviewed at worker pickup;
record its revision and the current dev base separately. Local session notes
hold execution handoff only, never a duplicate PR/check/merge state.
One coherent same-scope result is one PR even with multiple evidence lanes.
A single maintainer-operated integrator selects GitHub Ready PRs; Merge Queue
is unavailable for this personal repository. Keep strict protected dev and
refresh only an admitted candidate when necessary. Native stacks were tested
in a separate public lab but automatic rebases and trunk CI must be handled
before enabling them in production. Default to independent PRs or wait for a
dependency to merge. Never infer merge candidates from local branch lists.

## Execution slices and dependencies

| Slice | Owner | Dependency | Delivery |
| --- | --- | --- | --- |
| Operating contract and skills | repository | none | this work item and PR |
| Local worker checkpoint, inspection and reclaim procedure | repository | operating contract | same coherent PR |
| GitHub integration procedure and protection audit | repository | operating contract | same PR; no dev merge |
| Effect-based CI selection | repository | operating contract adopted before activation | ci-effect-selection work item |
| Unix-like test internal efficiency | unixlike | retain current guarantees; CI selection may land separately | test-efficiency work item |
| Windows test measurement and efficiency | windows | native CI evidence | test-efficiency work item |
| Repeated integration validation | repository | CI selection and exact-result safety review | decision documented with CI selection; retain post-merge checks until equivalence is proven |

Implementation branches may be prepared in parallel, but the integrator lands
the operating contract first. Domain outcomes own separate specs. Historical
records stay historical; current procedures point to the adopted contract.

## Test-efficiency follow-up

Baseline on 2026-09-26: Actions run 36109055733 checked only Unix-like documents
but ran a 782-second Unix job; run 36216060416 changed the lock and ran a
762-second job (flake-test 342s, test 250s, import-order-test 116s). Run
36207658666 spent 107.16s in Pester, including 106.44s in WinEnv.Tests.ps1.
Remove irrelevant suite execution first, then non-verifying size calculations,
duplicate scans and repeated evaluation. Keep runtime versus evaluation and
external consumer versus internal contract evidence distinct. Do not skip
post-merge checks merely because a PR once passed. Unknown impact stays broad.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Canonical skills route implicit requests and implement planning, worker handoff, integration, inspection and reclamation with dynamic role boundaries. | review |
| AC2 | Current policy and procedures agree on same-scope coherent PRs, optional roadmap, plan pickup, interruption and GitHub integration authority. | policy checks, review |
| AC3 | Local session support refuses primary-checkout writes and invalid transitions, preserves handoff, and reports local state without treating it as PR state. | fixtures |
| AC4 | Integration and reclaim procedures cover strict-base refresh, conflicts, remote recovery, uncertain liveness and unpushed or ignored data; dev protection is observed and remaining manual controls stated. | review |
| AC5 | Test-efficiency work is assigned to owning scopes with measured baselines, conservative selection and explicit limits on validation reuse. | review |
| AC6 | Repository fixtures and policy checks pass and the delivery PR passes Required checks before Ready. | fixtures, policy checks, affected dispatch |

## Governance decomposition

Failure: local execution state previously doubled as integration authority,
and lane-based splitting duplicated verification. Owner: repository maintainer.
Policy lives in AGENTS, architecture, decision and invariants; CONTRIBUTING is
the human procedure; project skills perform orchestration; local session
commands handle deterministic checkpoints; GitHub protects dev. The report
records evidence, not authority. Remote settings already enforce PR/checks,
strict base, administrator coverage, no force push/deletion and conversations.
Risk-specific reviews remain explicit admission decisions until code-owner
identities are supplied; no invented reviewer or broad mandatory review.
