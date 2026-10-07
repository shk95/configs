# Live qualification of the conditional protected merge
kind: spec
date: 2026-10-07
scope: repository
status: approved
review-by: 2026-10-21
issue: #537

## Outcome and boundary

Collect live GitHub evidence for the adopted conditional writer before general
enablement. The trial is bounded to one normal `dev` request, one `dev` target
race followed by a clean base-drift request using the same candidate PR, and a
later meaningful `dev`-to-`master` promotion after the workflow is registered
on the default branch. The writer remains disabled outside the root-owned
scoped trials.

PR #536 merged into `dev` as `e38f29d886d22b07807211f36eb61799413c2f69`.
The accepted master input patch #534 has since been adopted into `dev` through
protected PR #539. Its topic merge commit is
`76e40f48c95d196ecabd3ff4cbf81c0a32cdac9d`, and the resulting `dev` merge is
`07c4ff8325e38568afa4c0d8845117ff3164909a`. Bootstrap promotion PR #540 has
since merged that accepted `dev` revision to `master` as
`6c60f37d5e8ebb31f7b69c84eb0a65affb57b9bf`; its Required checks passed in
run `37557373470`, and workflow `376977835` is active. This
bootstrap is not the separate meaningful master-promotion trial in AC3. The
workflow dispatch must select the accepted `dev` revision; do not infer
registration from its presence on `dev`.

The repository maintainer owns all remote setup and operations: creating the
dev-only `merge-control` environment, installing the dedicated App
credential, restricting the actor allowlist to the scoped maintainer, keeping
strict branch protection and no-bypass settings, temporarily setting
`CONFIGS_MERGE_ENABLED=1`, requesting runs, and performing protected merges.
The worker only authors candidate documentation and reports live results. The
flag returns to `0` immediately after each scoped trial. No credential or
environment value is written by this work. Any unexpected merge, branch
update, identity mismatch, protection mismatch, or audit failure stops the
trial; the maintainer immediately disables the writer and records the failure.

Candidate source is limited to useful `docs/work/` updates, outside the
accepted workflow's safety paths. Candidate PRs do not modify `.github/`,
`tool/`, `.agents/`, `AGENTS.md`, `CONTRIBUTING.md`, or `docs/policy/`. Before
each request the maintainer reviews the exact PR head, target and current
checks. The work report cites actual PRs, Actions runs, check artifacts, merge
SHAs, and API outcomes. A fixture or a manual API probe is never presented as
a writer dispatch or successful protected merge.

## Qualification sequence

1. **Normal dev request (P).** This spec/report PR is the first useful
   documentation candidate. Its ordinary Required checks and `ci-source`
   record must pass before the maintainer dispatches the request; the App
   token does not trigger this already-completed check run. After the
   maintainer completes workflow registration and scoped setup, submit one
   conditional request at the unchanged source head and base. Confirm the
   workflow run, that pre-existing evidence still binds the exact
   `ci-source` base/head/tree, protected merge result and post-merge audits.
   App-token-triggered fresh `pull_request` CI is proved by the later R update
   in step 2. Reset the flag to `0`.
2. **Target race and dev drift (R then B).** Prepare a useful report-update PR
   R at base B with exact current-head CI passing, and a separate disjoint
   useful `docs/work/` PR B based on the same `dev` commit. Before any writer
   request for R, capture its unchanged source H, target B, Required-checks
   results, `ci-source` base/head/tree, resolved conversations, reviews,
   Ready/mergeable state, and both branch protection settings. The maintainer
   then merges B through the ordinary protected path, advancing `dev` from B
   to C. With R still at H and its old-base checks preserved, the maintainer
   calls the exact-head protected merge API for H without an admin bypass. It
   must refuse because strict protection requires the head to include C. Verify
   R remains open and unmerged, with no head change. If GitHub merges it, stop
   immediately and report the protection failure; do not treat post-merge
   detection as prevention.

   After that refusal, submit a new conditional request for R, preserving H
   and recording C as the current base. The writer may create only the clean
   deterministic integration head I with first parent H and second parent C.
   Confirm the dedicated App token triggered ordinary PR CI; the newest
   `ci-source` artifact must bind C, I and the deterministic merge tree. The
   protected merge must match I. Verify actual parents/tree and post-merge
   audits, then reset the flag to `0`.
3. **Master promotion.** Once the accepted workflow revision and patch source
   adoption are on `master`, prepare a meaningful same-repository `dev` to
   `master` promotion with accepted-patch ancestry. Submit one explicit
   conditional master request while head and base remain unchanged. Confirm
   exact-source required CI, a protected merge matching the frozen dev head,
   actual merge ancestry/tree and post-merge audits. Confirm no branch-update
   endpoint was called for master. Reset the flag to `0`.

The candidate PR contents and the exact source/base SHAs are reviewed by the
maintainer before requests. Integration and promotions are separate
maintainer-owned GitHub operations; a worker Ready PR or a successful local
check is not merge authorization.

## Evidence limits and stop conditions

The local fixture suite already exercises unexpected source commits, merge
conflicts, failed/cancelled newest checks, the three-update limit, CAS races,
ambiguous update responses, recovery, and the 60-minute deadline. This trial
does not inject fake transport failures, deliberately corrupt tracked work
documents to manufacture a CI failure, wait past the 60-minute deadline, or
claim a live CAS/ambiguity result without observing one. Those cases remain
fixture evidence unless a natural production event occurs and is captured.
The stale-base protected merge in step 2 is the controlled live target-race
qualification; the exact API request and refusal must be preserved as remote
evidence.

Stop before dispatch if the `merge-control` environment can deploy from any
ref except `dev`, the dedicated token or actor role cannot be confirmed, a
required branch protection is not strict, a bypass is enabled, the accepted
writer revision differs from the reviewed source, or the candidate's state is
not clear. Stop after dispatch on any unexpected source or target identity,
failed latest check, additional dev movement beyond the bounded sequence,
missing exact `ci-source` identity, ambiguous write without safe recovery, or
post-merge audit mismatch. Keep general enablement off until the maintainer
reviews all evidence and separately accepts rollout.

## Acceptance

Amended 2026-10-07, successor candidate after the stopped first trial: PR #538
was merged, but both conditional-run attempts ended in post-merge audit
failure because the pinned REST API version no longer returned
`merge_commit_sha`. It is not a successful AC1 trial and cannot be repeated.
The documentation PR carrying this continuation is the successor normal
`dev` candidate (P2). Its exact head must pass fresh required checks and
review before the maintainer considers a new scoped request. AC1–AC4 and their
evidence requirements below are unchanged; the remaining qualification
sequence stays gated until that candidate's result is recorded. The writer
remains disabled outside maintainer-owned trials.

Amended 2026-10-07, AC1: the normal request reuses Required-check evidence
that passed before dispatch; it does not claim the App triggered that
pre-existing run. The App-triggered fresh CI evidence belongs to the later R
base-update test in AC2.

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The normal `dev` trial proves accepted dispatch against unchanged identities, exact pre-dispatch Required-check evidence, protected merge and post-merge audits. | affected dispatch, review |
| AC2 | With R at H/base B and B merged to advance `dev` to C, strict protection refuses the stale exact-H merge; the new request then creates only deterministic H→I(C), triggers new exact C/I/tree CI, and merges I. | affected dispatch, review |
| AC3 | After workflow registration on `master`, a meaningful `dev` promotion passes accepted-patch ancestry and merges with frozen source/base; master receives no branch update. | affected dispatch, policy checks, review |
| AC4 | The report distinguishes live remote evidence from fixtures and confirms the scoped flag is reset to zero after each trial; no general enablement or bypass is inferred. | policy checks, review |
