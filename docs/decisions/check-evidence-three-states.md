# A check reports verified, failed or unverified

date: 2026-08-16
scope: repository
status: accepted
source: 9f1e8ce:docs/status.md § Check evidence states
source: 9f1e8ce:docs/status.md § Invariant registry

A check has three possible outcomes — verified, failed, and unverified — and
only the first two could be expressed. A shell exit status carries a binary
answer, so every place that needed the third state invented one, and eight call
sites disagreed. `pre-push` reported an unverified Windows check and passed;
`check-desired-state.ps1` and `test.ps1` threw before validating anything;
`Test-WinEnvSourceFile` skipped a missing Zellij silently and so reported
unverified as valid; the Unix-like branch of both hooks had no detection at
all; `doctor.sh` accepted a shell that `pre-push` rejects. This document's own
requirement is unverified rather than valid, and none of those answers were
unverified except the first.

The failure being prevented is a native Windows clone that cannot push its own
domain's work, and its mirror, a clone reporting a payload as verified when
nothing parsed it. The owning scope is `repository`. The architecture already
reserved the position: root tooling may dispatch domain checks without owning
their semantics, and must not turn one domain's success into a prerequisite for
a change in another.

The contract itself is `docs/architecture.md § Repository governance plane`.
Hooks leave that unset because the local gate is advisory. CI sets it because
the merge gate is the one place where "nobody could check this" must not
pass. Deterministic enforcement lives in `.githooks/evidence`, which both
hooks source, and in each domain's own checks, which decide what their
prerequisites are. The hooks select which checks run and never decide whether
a missing tool is a failure. Domains do not share an implementation of the
probe; each detects its own tooling in its own language, which is the
ordinary duplication this repository prefers over a cross-domain abstraction.

Evidence is the fixtures in `tool/version-control/test`, which run the real
pre-push hook against a stand-in check and require that 0 passes, that any
other status blocks, that 69 passes while reporting, and that 69 blocks under
`REQUIRE_NATIVE`.

2026-09-03: `tool/checks/prerequisite` carries the shared contract; every
domain check reports through it.

2026-09-03: The review of the verification suite led to four rulings, landed
as the governance-hygiene change: `tool/version-control/audit` runs on every
push and in CI and delegates commit subjects to the commit-message hook; the
`common` job, dispatch unit and classifier arm are removed until a common
component exists (restored by the change that creates it).
