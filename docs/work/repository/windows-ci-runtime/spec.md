# Bind native Windows CI to its declared runtime
kind: spec
date: 2026-09-30
scope: repository
status: approved
review-by: 2026-10-07
issue: #431

## Problem and decision

Windows CI currently inherits the hosted-image PowerShell version. The
Windows-owned declaration and reader delivered in PR #430 select the exact
management ZIP and distinguish inbox bootstrap coverage. Repository wiring
must consume that interface without becoming a second version selector.

Read the trusted Windows declaration using the hosted PowerShell only for
acquisition. Verify the official ZIP against its declared SHA256, extract it
into runner temporary space, and assert version, architecture and executable
identity in a fresh child. Management preparation, validation and tests use
that executable explicitly. Restore its PATH precedence after contributor
setup and prove that nested pwsh resolves the same runtime. Preserve failure
status immediately and retain REQUIRE_NATIVE and the existing stable gate.

Record inbox Windows PowerShell 5.1 separately. Execute the declared entry
and bootstrap sources in native children with controlled dependencies for
success, refusal and forwarded child failure; never Apply real desired state.
The hosted image is not the Windows client support baseline.

## CI-runtime lane

Owner and execution dependency are recorded in issue #431. Pickup waits for
the declaration/reader to enter dev, then pins current origin/dev independently
from the reviewed Windows decision and the dedicated plan revision. One new
repository branch/PR owns workflow orchestration, internal helpers, repository
fixtures, a durable binding invariant/decision and scope-owned documentation.

Inputs: windows/tool/ci-runtime.json and windows/tool/read-ci-runtime.ps1 from
the reviewed #430 delivery; the Windows CI-runtime decision; the current
workflow, setup-dev behavior, Windows entry/bootstrap sources and gate/fixture
contracts. C retains Windows schema/runtime semantics; B holds workflow edits
and retains its separate preview test registration. This lane modifies neither.

Evidence: meaningful positive/negative native fixtures, repository policy and
dispatch checks, and final-head native CI naming actual downloaded management
version/architecture/executable and inbox bootstrap execution. Local foreign
checks cannot replace native Windows evidence. Existing full selected suites
and Required checks remain required. ZIP extraction is runner-local preparation,
not installation on the maintainer's host or consumer activation.

Stop/replan for a declaration/schema change, a Windows-source fix, a new
version-selection rule, a conflicting owner or a substantive permission/trust
choice. Native CI failures within the assigned orchestration are worker repairs.
Preserve existing worktrees, patches, stashes and checkpoints; notes/ is not
context. No stack, auto-merge, dev merge, release, activation, Apply or cleanup.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Repository CI consumes the Windows-owned declaration, verifies the downloaded ZIP hash before extraction, and refuses missing or mismatched runtime identity in fresh native children. | fixtures, policy checks, review |
| AC2 | Management setup, validation and full Windows tests execute the declared runtime explicitly; nested pwsh resolution remains bound after PATH refresh; failed or unavailable child results fail the gate. | fixtures, policy checks, review |
| AC3 | Native execution records declared management version/architecture and separate inbox 5.1 entry/bootstrap positive and negative evidence without host desired-state mutation. | review |
| AC4 | The final repository-only delivery preserves Windows source/selector ownership, existing check selection and fail-closed Required checks, with current-head native Windows CI and required selected suites passing. | fixtures, policy checks, affected dispatch, review |
