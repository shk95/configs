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

## Dated adoption evidence: accepted patch incorporated into dev (2026-10-07)

Accepted input patch [PR #534](https://github.com/shk95/configs/pull/534)
used source head `5a14c5895cda24ff843e172d693582f063c8c580`, parent
`81229c16a05dde8b0ba9cc0d7412976b48d948fb`, and master merge
`60bcd46a9afb7ec5e5583825856f6af0e812e745`. Its exact changed paths were
`unixlike/flake.lock` and `unixlike/release.json`. Required checks passed in
[run 37546859748](https://github.com/shk95/configs/actions/runs/37546859748).

Protected adoption [PR #539](https://github.com/shk95/configs/pull/539)
retained the accepted patch head as an ancestor: its topic head was
`76e40f48c95d196ecabd3ff4cbf81c0a32cdac9d`, with parents
`e38f29d886d22b07807211f36eb61799413c2f69` and the exact #534 source head.
The protected dev merge was
`07c4ff8325e38568afa4c0d8845117ff3164909a`, with parents
`e38f29d886d22b07807211f36eb61799413c2f69` and the #539 topic head. Required
checks and the Unix-like evaluation/build job
passed in [run 37556326715](https://github.com/shk95/configs/actions/runs/37556326715).

The `unixlike/` subtree object is identical at the #534 source head, #539
topic head, and actual dev merge: `c6bc7b384e43bbbae4c85335c04b4a94a0919596`.
The adoption brought the accepted patch source into dev without reverse-
merging the master promotion commit. This records GitHub history and CI
evidence for the already-completed adoption; it does not claim a Darwin build,
host activation, or a new release tag.

## Limits

Local proof uses actual Git history and transport fixtures, not live GitHub
release evidence or scheduled trigger observation. Current-head remote CI and
rollout qualification remain in PR/Actions records. No host adoption, activation
or Windows Apply was performed. Existing tags are not changed by this
implementation. Windows fixtures establish preservation only; this lane adds
no Windows updating or publishing behavior.
