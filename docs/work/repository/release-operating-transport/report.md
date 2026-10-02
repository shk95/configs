# Report: authenticated operating transport before manual rollout
kind: report
spec: docs/work/repository/release-operating-transport/spec.md
status: done

## Source delivery and review, 2026-10-02

Issue #477 and PR #478 deliver the repository source lane from pickup dev
`eaf3a394cdf007031d7a5191a6f47287626d1ba3` and separately reviewed plan
`970147ef93ca975514fde81555afa1abf18962ff`. The spec records the dated
finite-library and single-job cancellation clarifications. Root is the sole
continuation owner; authorship remains in its dedicated linked worktree.

The verified implementation is `3bb493524c140e7090f58e911c385e0268ca0413`.
The separate five-file trusted inventory digest is
`dc544a0d6ca9248d7c9168e278976877bbda2d19f43d722045d4d7ca45e9cf5e`.
Historical protocol1/2/3 eight-file semantic packages, original event bytes,
configuration and serializers remain exact. Current configuration controls later
work; outstanding batches retain pinned configuration and independently fresh stop.
An owner's actual master run source is independently observed within approved public
history; it is not confused with the retained package's source.

Source review checked entry/evidence provenance, credential isolation, complete
bounded lookup, intent/ref acknowledgement, preservation of old obligations,
recovery without retry, immutable publication and finite supported cancellation.
The public command is read-only preflight and the writer workflow is disabled.
Start/claim/planning and bounded waiting belong to a future separately reviewed
wrapper; no such provisioned wrapper or selected operating connection is delivered.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Entry independently fetches run/latest attempt/workflow/jobs and binds actual source/ref/event/actor/job. Successful checks bind exact run/attempt/job/source plus reviewed workflow/tool blobs. Wrong actor/ref/Environment/source, failed or stale checks, wrong tool blobs, incomplete/redirected/duplicate/unknown pages and stale attempts refuse. Current-source local and Linux/native Git-for-Windows fixtures and policy/affected dispatch passed in run 36890976797. |
| AC2 | verified | Exact retained replay and original serialization project immutable history/index before writes. Expected-head one-parent/non-force Git publication confirms actual ref; this is not API CAS. Lost acknowledgements join observed success; competing writers, tampering and unknown effects fence progress. Recovery observes confirmed result/absence without retry and requires a foreign old owner's confirmed terminal job. Actual disposable Git fixtures passed locally and in run 36890976797. |
| AC3 | verified | Batch-owned lock-only refresh checks actual commit parents/tree/lock bytes and rejects contamination. Complete all-state PR inventory binds exact repository/head/base/source and original body-operation; closed, conflicting, duplicate or unknown state cannot become false absence. Fresh merge checks/protection/base and actual postmerge parents/tree gate fixed immutable tag objects/refs; duplicate success joins and partial/conflicting/unknown publication refuses unsafe advance. Fixtures and affected dispatch passed in run 36890976797. |
| AC4 | verified | Exact authenticated request binding, approval-source check, stop/resume, wake without ownership/approval, bounded transport timeout, latest attempt/job termination and notification-source receipt are tested. Resume clears stale evidence/approval; current config changes preserve the old batch. Cancellation rejects foreign owners and mixed-job runs; 202/timeout is not termination. Independent owner-source history, lost response, attempt change and wrong authority fixtures passed in run 36890976797. |
| AC5 | verified | 35 isolated fake-endpoint/disposable Git transport tests passed locally and on Linux/native Git for Windows in run 36890976797, alongside retained-controller/release proof and policy checks. The source-bound preflight always emits enabled=false and production_certification=false; workflow permissions are empty and its only job reports disabled. CONTRIBUTING records bootstrap/permission/protection/Environment/rerun/cancellation/recovery prerequisites. No production receipt is inferred. |
| AC6 | verified | release-transport-template.json binds the delivered implementation SHA and separate manifest digest. study.md names unresolved operating connection/ref, source/control/bootstrap, identities, Environment, evidence and permission/protection/manual-authorization inputs, plus expected separately approved effects. Mismatched source/manifest refuses preflight. Actual R-manual0/14 and R-scheduled0/5 remain pending. |

## Source-bound proof

Normal commit and push hooks passed the complete local repository suite, history
and policy scans. Explicit production qualification has 22 tests, retained
controller has 24, and this transport has 35; no fake endpoint contacts production.
CI run [36890976797](https://github.com/shk95/configs/actions/runs/36890976797)
checks exact implementation head `3bb4935`. Its Linux log records 22/24/35 tests
in 32.071s/15.081s/20.014s. Its native Windows log records 22/24/35 tests in
387.214s/121.248s/186.258s. Native Git-for-Windows proof and all affected jobs,
including Required checks, passed on that same head. Final report-head checks
remain integration prerequisites and are independently refreshed before Ready.

Source/API review used the official GitHub REST documentation for
[workflow dispatch](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event),
[workflow runs](https://docs.github.com/en/rest/actions/workflow-runs),
[Git refs](https://docs.github.com/en/rest/git/refs) and
[pull-request merge](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request).
The adapter pins API version 2026-03-10. Run-wide cancellation lacks an atomic
expected-attempt guard; supported future provisioning must isolate a sole writer
job and serialize reruns. Actions failure is a source receipt; inbox delivery is
unverified. A dispatch receipt grants no candidate approval or writer ownership.

## Operating boundaries

Only source and synthetic endpoint/local Git/native CI proof are complete.
Operating repository/connection/bootstrap selection, actual secrets/Environment,
protected source deployment, permission/protection receipts, real dispatch/cancel,
promotion/ref/tag/release, notification delivery and enablement remain unperformed.
No baseline is selected, parent manual/scheduled acceptance stays pending, and no
Unix-like activation or Windows Apply occurred. Domain evaluation/build evidence
comes from affected CI jobs; fixture success is not a domain release certificate.
