# Preserve source approval while validating a moving dev base
kind: spec
date: 2026-10-07
scope: repository
status: approved
review-by: 2026-10-21
issue: #535

## Problem and outcome

Strict protection requires a pull request head to include the current base.
Re-running a pull request workflow does not create new evidence for a later
base. Keep the reviewed source commit immutable while allowing a narrowly
bounded, deterministic integration merge of accepted `dev` history, followed
by CI on that exact integration head and current base. This is a dated
follow-up to `docs/work/repository/conditional-merge/spec.md`; it does not
change master promotion, branch protection, or authorization to enable or run
remote writers.

## Approved contract

The approved source head `H` remains frozen. On a dev-target request, if current
`dev` is not already an ancestor of the PR head, the writer may call GitHub's
pull-request branch-update endpoint with `expected_head_sha` equal to the
inspected PR head. The update must produce an integration commit `I` with
exactly two parents: first parent the previous accepted head, second parent an
accepted `dev` commit. Its tree must equal the deterministic clean merge of
those two parents. The second parent must descend from the originally admitted
base and be an ancestor of current `dev`. Conflicts, extra parents, unexpected
source commits, unapproved ancestry, or a tree mismatch refuse the request.

At most three integration commits are allowed, including a chain recovered
after restart, within the original 60-minute request deadline. A later `dev`
advance may require another update. Before each update, the newest evidence for
the current integration head must not be failed or cancelled. After the final
update, only a newly completed successful Required checks run whose event binds
the latest `dev` base, exact integration head, and computed merge tree is
acceptable. Any later base movement invalidates that evidence and requires a
permitted update and new CI. A rerun whose recorded base, head, or tree is stale
is never fresh evidence; a latest successful run for the exact current
identities may qualify.

The GitHub update API compare-and-swaps the PR head, not the base. Inspect the
actual commit returned or observed after its asynchronous response. Compare its
parents, ancestry and tree, then reread current `dev`; repeat only when the
observed update is accepted and the target advanced. If a write is ambiguous,
inspect remote state and recover a valid chain; never blindly repeat the write.
All update and wait time counts toward the original deadline.

The authorization permits only this structural integration chain from `H`.
Commit metadata alone does not establish provenance. A deterministic merge
commit with the required parent order and tree is within scope even if created
outside the API; no normal source commit, conflict-resolution commit, or other
source content is approved. Validate every link, with at most three links.

Only accepted writer tooling may inspect and write the PR branch. Candidate
source runs in ordinary CI without writer credentials. The dedicated writer token must
trigger the normal `pull_request` CI for the updated head. Never reuse an older
CI artifact. Before entering the writer environment and before every write,
the accepted workflow revision must remain an ancestor of `dev`, and these
safety paths must be unchanged from that revision to current `dev`: `.github/`,
`tool/`, `.agents/`, `AGENTS.md`, `CONTRIBUTING.md`, and `docs/policy/`.
Unrelated `dev` changes do not invalidate accepted tooling. Master retains its
fresh accepted-revision requirement and frozen base/head; it never uses branch
update. Strict protection remains enabled on both branches and no bypass is
permitted.

## Verification

Add focused positive and negative fixtures for a clean A-to-B base advance,
correct integration chain, current-base exact-head evidence, and recovered
chain. Refuse conflicts, arbitrary source advance, malformed or overlong
chains, stale-base evidence, failed newest run, master drift, and a further base
move after evidence. Exercise expected-head races, asynchronous/ambiguous update
recovery, deadline exhaustion, and ensure a failure is never hidden by an
update. Test accepted workflow safety-path changes and allow unrelated dev
advances. Existing conditional-merge tests remain regression coverage, not
evidence for these new criteria. Do not perform live updates or merges in this
work item; affected remote qualification remains pending.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The original source head is immutable, and only a structurally valid chain of at most three deterministic clean dev integration commits can extend it. | fixtures, review |
| AC2 | CI evidence is fresh for the latest dev base and exact integration head/tree; stale, failed, cancelled, or superseded evidence cannot authorize merge. | fixtures, review |
| AC3 | CAS races, asynchronous update, restart recovery, timeout, and ambiguity fail closed without duplicate writes or losing a confirmed accepted chain. | fixtures |
| AC4 | Master remains frozen-base/head and never calls branch update; both branches retain strict protection and no bypass. | fixtures, policy checks |
| AC5 | Only accepted writer tooling with isolated credentials can update; accepted safety paths are unchanged, candidate CI receives no writer credentials, and App update triggers ordinary CI. | fixtures, policy checks, review |
| AC6 | The implementation integrates with the existing conditional-merge flow and reports unperformed live qualification honestly. | policy checks, review |
