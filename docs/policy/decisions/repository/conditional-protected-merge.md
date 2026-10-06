# Conditional protected merge
date: 2026-10-06
scope: repository
status: accepted
issue: #533
source: eaf812d652e462c61fd18ff908b5814ad483c3e4:docs/work/repository/conditional-merge/spec.md § Conditional asynchronous protected merges
reopen-when: A supported writer cannot preserve exact-source checks, target-race safeguards or post-merge recovery under the current GitHub controls.

## Decision

Keep the existing integration and promotion roles. Their canonical skills
orchestrate distinct review steps and explicit merge authorization; the
maintainer retains decision authority. Once the authorized integrator has
admitted a candidate, `tool/configs conditional-merge submit` may create one explicit
Actions request carrying the pull request number, target branch, approved head
SHA and observed target SHA. The operator command requires `--confirm`, checks
the live pull request and target before dispatch, and treats the dispatch API's
returned run identity as confirmation of a request only.

GitHub registers `workflow_dispatch` only after the workflow reaches the
default branch (`master`); requests explicitly select `dev`, and execution
refuses unless the workflow revision is still the current `dev` head. The
ordinary dev PR and explicitly authorized dev-to-master promotion establish
that registration. A separate read-only admission job
checks the request identity, actor allowlist and actor's maintainer/admin role
before the writer environment is entered. The writer runs accepted `dev`
tooling; it never checks out or executes the pull request's source. A dedicated
`merge-control` environment provides a narrowly permissioned GitHub App token,
or a dedicated token, independent of `release-control`; its deployment branch
policy must admit only `dev` before any writer credential is configured. The
environment's writer credential is not available to candidate code and grants
no branch protection bypass. `CONFIGS_MERGE_ENABLED` must be explicitly enabled;
the repository variable is initially `0`, and missing or zero leaves writes
disabled. The repository variable `CONFIGS_MERGE_ACTORS` is a comma-separated
list of allowed GitHub logins. The environment stores either
`CONFIGS_MERGE_APP_ID` and the `CONFIGS_MERGE_APP_PRIVATE_KEY` secret, or the
dedicated `CONFIGS_MERGE_TOKEN` secret. The App requests Contents write, Pull
requests write, and Administration, Actions, Checks and Metadata read; it has
no branch-protection bypass.

Every request freezes both identities. Only same-repository Ready independent
topic pull requests into `dev` and an explicitly admitted same-repository
`dev` promotion into `master` are supported. The promotion path retains the
one-open-master-pull-request rule and runs the existing accepted-patch ancestry
validator. Drafts, forks, stacks, explicit blockers, high-risk metadata,
outstanding changes requested, stale identities, unknown protection and
unsupported sources refuse. High-risk admission remains with the existing
synchronous integrator procedure.

The writer rechecks current strict branch protection and the exact Required
checks app, explicit review and conversation blockers, target/head identity,
current candidate shape and the newest matching CI run. An unknown or changed
protection configuration refuses; a pending aggregate mergeability result is
bounded and may wait. CI evidence must come
from the latest run of the required CI workflow for that head, and its
`ci-source` record must match the frozen base, head and computed merge tree.
A newer pending run waits; a newer failed or cancelled run refuses, regardless
of an older success. Waiting is bounded at 60 minutes from request creation,
including Actions queue time. Each target serializes its writers with
`queue: max`; master shares `configs-release-writes` with the input-patch
writer and dev uses its own group. Active writers are not cancelled and queued
requests are retained. A later request becomes stale after another writer
moves its target.

Immediately before writing, the accepted workflow runner repeats the admission
and evidence checks, then calls GitHub's protected merge API with the exact head and merge
method. The API atomically matches the head; it has no expected-target-SHA
field. Both branches therefore remain strict and up to date. Strict protection
is the final defence against a target movement in the interval between the
last read and the merge. This does not serialize the human `commit --publish`
operation or direct protected manual merges; no absolute target-SHA
compare-and-swap is claimed. Do not enable the writer until live qualification
has exercised this race and confirmed its refusal behavior.

The Actions run is the request and recovery record. Confirmed dispatch is
reported as `requested`; a merge is reported only after GitHub confirms it and
the merge parents and tree match the request. An ambiguous dispatch or merge
is inspected on GitHub before another attempt. An already merged request is
verified without another write. Post-merge identity or audit failure is
reported as `merged-with-audit-failure`; it does not roll back the merge. The
dedicated token preserves normal post-merge workflow triggers. No release tag,
GitHub Release, activation or Apply is created.

## Rollout boundary

This source change does not create the remote environment, restrict its
deployment branches, add its secrets, set the actor allowlist, enable the
writer or qualify an actual merge. Qualification is a separately authorized,
scoped live trial: a designated qualification PR and restricted actor allowlist
are used for a temporary `CONFIGS_MERGE_ENABLED=1`, then it is immediately
returned to `0` while the maintainer reviews run, merge, audit and target-race
evidence. General enablement requires a separate acceptance of that evidence.
Until a trial is authorized, `CONFIGS_MERGE_ENABLED` remains unset or zero and
the established synchronous procedure remains available.
