# One-call manual domain release: report
kind: report
spec: docs/work/repository/manual-domain-release/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Fixtures: a complete cycle uses actual objects/refs in a disposable bare Git origin, production inspection/check binding/advance/publication, and simulated GitHub transport/CI artifacts. It fetches an API-created refresh head into the fresh runner, waits through both PR checks, verifies both actual merge parents/trees, publishes the immutable Unix-like patch tag, preserves the Windows tag and adds no PR/tag on unchanged rerun. Real local Nix refresh CLI fixtures also pass. Affected dispatch: both workflows pass actionlint and workflow-boundary fixtures; changed-path CI selection requires repository, Unix-like and Windows suites. These prove source/dispatch behavior locally; required hosted CI remains the PR gate, and live release/schedule evidence is separate in Actions and annotations. |
| AC2 | verified | Fixtures/review: manual clock/day bypass still requires matching checks and source declarations, human-change review, stale-candidate refusal and immutable tag content. Refresh has no writer secret; approval has neither writer credential nor writer concurrency. Both writer jobs use accepted master tooling, release-control and the existing shared writer concurrency. Non-master dispatch refuses before checkout. Active manual runs make ordinary release inspection wait. |
| AC3 | verified | Fixtures: failed checks, bounded timeout, changed wait candidate, newer CI rerun, no-op completion and final CLI wait refusal are covered. Existing actual Git/API fixtures cover refresh graph synchronization, missing-tag-only recovery, source identity loss and remote confirmation after ambiguous writes. The controller keeps only a deadline and current wait identity in process; PRs/checks/tags and job outputs are the state. |
| AC4 | verified | Review: README documents the web and CLI one-call entry after master rollout. CONTRIBUTING covers the same REST dispatch, enablement and credentials, 60-minute CI budget, approval, cancellation and recovery. Status and usage distinguish manual operation from actual scheduler delivery and host adoption. |

## Handoff

Local validation on 2026-10-06: all 20 bounded release fixtures pass,
the complete repository fixture suite passes, both release workflows pass
actionlint, and classification, work, invariant, hygiene, domain-read,
design-citation, provisional and record checks pass. The repository suite's
expected unavailable-origin refusal fixture is not a failed remote fetch
against this repository. These are local source/fixture results, not hosted
CI, live manual publication or scheduler evidence.

The end-to-end fixture initially reproduced a fresh-runner failure: API-created
refresh objects were absent because the writer guard fetches only dev/master.
Inspection now validates and fetches the exact missing managed head before
merge-base evaluation. The regression fixture passes without mocking writer
acceptance, inspection, check-artifact binding, advance or publication. Its
network API, check outcomes and Environment infrastructure are simulated;
actual GitHub protections/runner operation still require live qualification.

Source was authored and locally verified in a dedicated linked worktree at
base 421a40408793fc21093c2608cb6cd00ef0b92ff7 before publication. The maintainer
authorized branch/commit/push, protected integration/promotion and a live manual
release trial on 2026-10-06. Remote qualification remains in Actions/PRs and
release annotations rather than a CI-result-copy commit. This source report
does not certify live operation, host adoption, activation or Apply;
#515's actual scheduled observation remains independent.
