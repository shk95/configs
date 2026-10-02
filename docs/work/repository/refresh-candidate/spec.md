# Disposable refresh candidate and shared-control requests
kind: spec
date: 2026-09-30
scope: repository
status: approved
issue: #460
review-by: 2026-10-14

## Outcome and authority

One coherent repository source lane joins actual provider refresh preparation,
local lock-only commit/head identity and existing shared-controller refresh
request/refusal semantics. This is an additive pure child of
`docs/work/repository/scheduled-flake-refresh/spec.md`, not final scheduler
wiring. Completing it cannot verify that parent's AC1-AC5 or any parent
provider-release criterion. Root reviews this plan before implementation.

Only disposable fixtures execute the refresh utility or mutate Git. External
branch/PR calls are supplied fake transcripts and proposed requests. No live
transport, credentials, real provider update, private operating branch, protected
ref, schedule, dispatch/cancel, merge/admission, release or host deployment is
authorized. The existing calendar-tag/promotion policies retain their authority.

## Pickup and dependencies

D owns planning only. Source owner and execution issue are unassigned; root
records both before pickup. Planning base is dev
`54b2b794e5a0aa867f264d1bff548eebe5cc4892`. A worker pins current origin/dev
and the independently reviewed plan revision in a new dedicated source worktree.
Do not reuse the preserved refresh or controller workers' execution spaces.

Prerequisites: merged Unix-like refresh tool; repaired and merged release-controller
preview, including reviewed recovery repairs; reviewed child plan and source
ownership. Source does not start from an unrepaired proposal. Inspect the actual
merged launcher, loader, protocol, manifest, parser/reducer, adapter and fixtures
at pickup. Changed interfaces or required semantics return to planning.

### Execution assignment, 2026-10-01

Root assigned D as sole source continuation owner in issue #460 after the
prerequisites and reviewed plan entered dev. Source pickup pins dev
`21532ddf5b6f98cd7ade1163ffa43a44b16dd339` independently of reviewed plan merge
`4a7e6e2b3c0c231d671cf203cb479c78b8c87b82`. The dedicated source tree is
`../configs-wt/refresh-candidate-source`; prior trees and checkpoints are preserved.
The original planning-only ownership paragraph records the earlier state.
Root reviewed explicit current protocol 2 with exact retained protocol 1 execution,
the unchanged eight-file closure, and actual preparation in fixture code only.
One supplied batch owns a stable automation branch; immutable candidate revision
and operation identities change on a required normal base update. Acceptance
criteria remain unchanged. Root alone integrates; live operations remain excluded.

## Implementation choices and file ownership

Use `tool/configs release-control` and the existing launcher/loader/package.
One assigned source worker owns necessary changes to `tool/configs`,
`tool/version-control/release-control`, its loader and four package Python files,
the package manifest/protocol, `tool/version-control/test-release-control{,.py}`,
new `tool/version-control/test-refresh-candidate-nix{,.py}` integration fixtures,
`.github/workflows/ci.yml`, `tool/version-control/test`, `tool/doctor.sh`,
`tool/dispatch/select`, `README.md`, `CONTRIBUTING.md`,
`docs/policy/decisions/repository/release-controller-preview-boundary.md`,
`docs/policy/invariants/repository/release-control-preview-only.md` and this child
report. Root names any additional file before pickup;
this list does not require unrelated edits. Do not edit
Unix-like utility/source/config/lock, private consumers or another worker's files.
Consume the domain CLI as an explicit dependency; do not duplicate its selection
or exclusion logic. Planner work here owns only this child pair and the parent pair.

Keep executing code in the existing eight-file semantic closure: main.py,
records.py, engine.py, adapter.py, release-preview, release-preview.awk,
release-preview.rules and classify. New bounded schemas/functions can live in
those existing files. Any additional executing dependency needs reviewed closure
and ownership before pickup; do not invent a generic package/plugin framework.
Review a finite semantic protocol evolution if needed, with explicit compatibility
tests. The stable loader must continue to execute supported old packages at their
exact pinned source/protocol and refuse unknown compatibility, without rewriting
old records or substituting new classification/approval meaning.

The existing `pr` promotion meaning remains dev-to-master. Add explicit
refresh-branch and refresh-PR schemas for an automation feature branch targeting
dev; never overload promotion fields to admit a different source/target. Bind
requests to exact fixture repository/branch, source/base commit, lock bytes,
isolated commit/head and operation identity. An asserted status line, mutable PR
body or supplied success flag is not source provenance or check authority.

### Actual preparation and data boundary

Extract the delivered trusted refresh launcher/engine at reviewed exact source
identities for a disposable provider fixture. Local Nix upstreams are explicit
controlled inputs; do not run real provider refreshes. Run in a separate
credential-free process/workspace; no private config, PAT, ambient execution
override or credentials reach it. Actual CLI output has selection JSON plus
text status, not an authenticated result schema. Independently snapshot/compare
all source bytes and permission modes, require only a validated lock to change,
and construct bound lock/source identities. Never execute provider/candidate
code inside a future privileged publisher path; only expected literal lock data
and verified identities cross that boundary. These fixtures do not prove safe
production provenance or a live privilege boundary.
The preview/effect path consumes the bound preparation data; it must not
implicitly invoke the domain CLI. Exercise the unprivileged preparation path
through the actual-Nix fixture boundary without adding a second controller.

For changed locks, create a local disposable automation branch and one isolated
`chore(unixlike-deps)` commit. Verify parent/base/head and that its diff changes
only `unixlike/flake.lock`; source edits cannot share that commit. No-op/failure
creates neither a commit nor a PR request. Preserve prior fixture branch history
with normal merges only for a required update; refuse unrelated human changes,
wrong ownership/parent/head or an occupied conflicting branch. No force push,
rebase, squash, protected-ref commit or remote transport is implemented.

The shared pure reducer models one supplied outstanding-batch envelope. Its
append-only/index proof is not long-lived global storage or automatic old-config/
package selection. Record exact intent before a proposed effect, reconcile unknown
responses against complete exact observations, preserve completed effects and
permit only unchanged confirmed-missing operations. Stop prevents next intent;
resume and takeover retain the repaired shared controller's requirements.

## Evidence and runtime boundaries

Actual local Nix fixtures prove the preparation/lock/Git portion, using the delivered
CLI rather than a fake refresh function. Require functional Python >=3.9, Git,
POSIX shell and the Nix CLI update/reference/output-lock capabilities; refuse
missing prerequisites without installation. Select native Linux/Darwin actual-Nix
proof explicitly and report its exact host/runtime/source. At least one selected
native Nix lane must pass; an unselected or unavailable other host is not a pass.
Wire the actual-Nix fixture into an existing Nix-enabled CI lane. Do not impose
Nix as a native Windows prerequisite. Fake schema/reducer/request fixtures still
require Linux and native Git-for-Windows proof for new governance shell behavior.

Fake transcripts cover open/merged/stale PRs, contamination, head/check movement,
lost responses, stop/resume and finite transient/timeout outcomes. Actual CLI
failure and controlled fault injections remain distinct. A timed-out process must
be confirmed terminated before its disposable candidate is consumed; a timeout
or cancellation acknowledgement alone supplies no success/ownership. Cleanup
of fixture-owned scratch is allowed; existing workspaces/backups are preserved.

Simulate once-per-day 05:00 Asia/Seoul refresh, 06:00 promotion opportunity and
fixed 07:00 refresh-wait cutoff, manual duplicate joins and delayed/missed arrivals.
The cutoff never cancels refresh or extends the wait; before-promotion integration
invalidates bound candidate evidence/approval, after-promotion integration waits
for the next opportunity. Use existing bounded transient/retry and action-summary
semantics; do not create another scheduler, watchdog or notification service.
No simulation establishes actual Required checks, compatible-patch admission,
live schedule, actor/PAT/protection/Environment identity or notification receipt.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The delivered trusted refresh CLI runs against disposable local upstreams and produces an independently verified lock-only candidate with exact source/base/lock identities; new inputs/exclusions/follows use the domain tool, and no-op/failure/confirmed-timeout outcomes produce no consumable candidate. | review, fixtures, policy checks, affected dispatch |
| AC2 | Changed fixture locks form isolated local dependency commits with exact parent/branch/head identities; source changes, unrelated human content and wrong ownership/base/head refuse, while existing history is preserved without protected-ref commits, forced updates or rebase. | review, fixtures, policy checks, affected dispatch |
| AC3 | Existing shared control constructs separate bounded refresh-branch/refresh-PR requests targeting dev, retains unchanged promotion semantics and exact executing closure, and executes supported old semantic packages unchanged while unknown protocol/compatibility or missing closure refuses. | review, fixtures, policy checks, affected dispatch |
| AC4 | Single-envelope fake lifecycle joins duplicate requests, reconciles open/merged/stale PR and unknown response identities, retains completed operations, and requires exact current-head/check/owner/stop conditions before any next proposed operation; mismatched observations or unsupported recovery refuse without blind replay. | review, fixtures, policy checks, affected dispatch |
| AC5 | Actual CLI/Git integration and Linux/native-Windows fake-control fixtures preserve credential-free preparation and data-only publisher boundaries, prove quiet disabled/no-op and bounded failure/transient/late/missed-opportunity behavior, and expose no real provider update, external transport, live credential/schedule/admission or unsafe public summary. | review, fixtures, policy checks, affected dispatch |

## Stop and return to planning

Stop for changed scope/acceptance/protocol compatibility, unrepaired/unmerged
dependencies, competing source ownership, additional manifest files, domain edits,
actual provider/host locks, production provenance or credentials, live transport,
long-lived multi-batch/history/config migration, schedule enablement, protected-ref
mutation, unattended admission, candidate-code execution in privileged control,
unsupported coverage or protection bypass. Checkpoint useful work; root owns the
continuation decision. Native runtime absence remains unverified, not success.
