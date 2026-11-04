# Local consumer development
kind: spec
date: 2026-11-04
scope: unixlike
status: approved
review-by: 2026-12-04

Implement the maintainer-approved local provider-to-consumer development loop:
edit, apply and test without a provider release, then promote the tested pair
through the repositories' existing publication and adoption procedures. Real
host information and execution state stay local. The selected current provider
and adjacent consumer checkouts are the implementation workspace; no commit,
branch switch, publication or real host activation is part of this source task.

The public provider owns generic orchestration and synthetic fixtures. The
consumer owns target resolution, native activation, runtime generation checks
and exact release adoption. Local explicit argv recipes implement existing
repository publication procedures; they add no version-control authority.
The consumer's experimental lane remains distinct from ordinary pinned master.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Connections and receipts stay in checkout-local Git metadata; source snapshots include new source while excluding ignored data and notes; changed source invalidates evidence. | evaluation, review |
| AC2 | A synthetic consumer evaluates current provider changes through an override without modifying its source pin or lock. | evaluation |
| AC3 | Consumer-owned application and verification check the selected native target, exact package and runtime receipt; failure does not retain successful evidence. | evaluation, review |
| AC4 | A reviewed local promotion plan delegates publication, requires exact released provider content and matching pinned closure, journals progress, and refuses stale or changed plans. | evaluation, review |
| AC5 | Documented Just commands and consumer adapter support the complete loop; provider checks do not depend on private hosts. | evaluation, review |

Real host closure builds, native runtime, actual activation and remote
publication are intentionally not acceptance lanes for adding this tooling.
They remain separate explicitly requested operations after implementation. Tiny
synthetic fixture builds may exercise the tooling without certifying a host.

## Acceptance amendment — 2026-11-04

The maintainer extended the source task to add automatic tests for both
provider-to-consumer development and consumer-to-provider extraction, each
covering unreleased development and subsequent exact adoption. Disposable
candidate changes must not enter original source. A native switch is authorized
for the selected test target, followed by restoration; the maintainer can
perform terminal-only authentication and execution. Commit the implementation
in both selected checkouts after the requested tests pass. Publication and
actual releases remain outside this follow-up authorization.

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC6 | Both directions complete development and exact promotion in temporary repositories using real Git/Nix/local remotes; original repositories receive no test configuration or history. | evaluation, build |
| AC7 | The consumer native runner isolates candidate source, checks local pin equivalence and extraction closure equality, and preserves original source/index/HEAD/status. | evaluation, build |
| AC8 | On the selected NixOS host, each native test checks its active marker and generation, then restores and verifies the original system/profile; failed or interrupted cases attempt recovery without claiming success on recovery failure. | native runtime, activation, review |

The local-source pin lane does not certify a real remote release. Synthetic
protocol activation/audit in provider integration cases does not certify native
activation or the production release audit. Native runner evidence remains
private and host-owned; public work prose records only aggregate lane results.
