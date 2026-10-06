# Master input patch verification
kind: report
spec: docs/work/repository/master-input-patch/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Fixtures: production selection, refresh, checking, merge confirmation and tag publication run against real local Git objects with GitHub transport/artifacts simulated. An unrelated dev commit stays on dev; one master patch PR is created and successive patches publish 1.0.1/1.0.2. Windows tag object remains exact. Affected dispatch: actionlint passes shared/thin entry points and CI; wiring fixtures prove shared patch-only execution and candidate credential separation. |
| AC2 | verified | Fixtures: master gate accepts a permitted single-commit patch and rejects extra content/forks/stale bases; dev promotion refuses missing accepted patch ancestry and accepts reviewed incorporation. Audit accepts actual bounded patch merge history while dev remains independent. Policy checks: invariant registry, repository classification, design-citation and work preflight pass; full repository fixture suite passes. |
| AC3 | verified | Fixtures: exact CI event/base/head/tree binding, failed/expired waiting and moved master refusal, immutable tag target/annotation checking, unchanged no-op, orphan branch/PR resume, lost merge response and interrupted publication recovery pass. Delayed merge association is rechecked without weakening proof; tampered actual merge is refused. Seventeen final release fixtures pass, including refusal to relabel unpublished master development as an input patch. Affected dispatch: writer-only credentials and 60-minute manual wait are covered by workflow wiring and actionlint. |
| AC4 | verified | Review: this lane reviewed AGENTS, architecture, the master-input-patch decision, invariants, CONTRIBUTING, README, status and agent routing for independent developer promotion, reviewed patch incorporation, Unix-like-only scope and separate host consumers. |

## Limits

Local proof uses actual Git history and transport fixtures, not live GitHub
release evidence or scheduled trigger observation. Current-head remote CI and
rollout qualification remain in PR/Actions records. No host adoption, activation
or Windows Apply was performed. Existing tags are not changed by this
implementation. Windows fixtures establish preservation only; this lane adds
no Windows updating or publishing behavior.
