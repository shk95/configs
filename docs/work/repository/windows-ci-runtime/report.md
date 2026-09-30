# Report: native Windows CI runtime binding
kind: report
spec: docs/work/repository/windows-ci-runtime/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Run 36659933239 at implementation 6b39f625: native verified archive acquisition and fresh 7.6.6/x64 identity, matching/tampered archive and missing/incorrect identity fixtures pass; registry and repository fixtures pass. |
| AC2 | verified | Same native job proves explicit runtime controller and management children, identical nested resolution after PATH refresh, conflicting resolution refusal and child 0/23/69/terminating-error behavior. Existing stable gate and immediate status checks are preserved. |
| AC3 | verified | Same native job records management 7.6.6/x64 separately from actual Desktop/5.1/x64 inbox entry/bootstrap execution: help 0, unknown 64, missing prerequisite 1, successful check 0 and forwarded child failure 37. |
| AC4 | pending | Complete run 36659933239 passes all selected suites plus Required checks at implementation 6b39f625. Final review found helper-only changes lacked Windows dispatch; targeted effect mapping and positive/negative fixtures are now prepared and require new exact-head CI before final verification. |

## Local preparation

Pickup base: cfd6d2718dc048cc1803e95267113d66f54e603d, current origin/dev after
the Windows declaration/reader and companion evidence prerequisites entered.
The approved dedicated spec/report was created and preflighted in this
task-dedicated linked worktree; the runtime selector remains Windows-owned.

Foreign-host PowerShell 7.6.6 parses all five CI source/fixture files and reads
the trusted Windows declaration. Harmless synthetic ZIP hash acceptance/refusal
and native child exit 0/23/69 checks pass on macOS; these are limited helper
checks, not native Windows identity or bootstrap evidence. Repository fixtures,
staged registry (73 registered, zero pending/untagged units), work preflights and
whitespace checks pass. Actual dispatch selects repository, Unix-like and
Windows suites because shared workflow input changed. No configuration source,
Windows selector/reader, public operator interface or B preview registration
was changed. At this initial preparation checkpoint native evidence and every
acceptance row were pending.

The first native run (36659135714, head bc66c84634ba37fac77c72d0734def074e69bdcb)
verified the archive and actually executed management 7.6.6/x64, then refused
the identity probe because its comparison included every PATH candidate. The
probe now selects the first application candidate, matching native invocation
resolution. This failed run is diagnostic evidence, not completed acceptance;
the repaired head requires new native and selected-suite evidence.

Run 36659343728 at 2f86e9b1cedcd51a593098a0036886d845984a20 then passed
actual runtime selection and version/architecture refusal. Its empty-PATH
negative fixture was invalid: PowerShell still discovers its own executable.
The fixture now places a conflicting harmless application candidate first,
testing refusal of a real resolution mismatch. This run also remains diagnostic.

Run 36659665308 at 5c833ccb6a8e2b8ffea5a34aa55d318686feff4a showed
that fresh selected PowerShell restores its own runtime directory ahead of
the parent's conflicting PATH. The refusal fixture therefore introduces the
conflict inside a fresh native child before executing the real identity probe.
The bootstrap copy also retains the provider's windows/tool layout and a
synthetic clone marker, with only downstream setup replaced. No source guard
or Windows selection semantics are changed; new-head evidence remained required.

## Native implementation evidence

[CI run 36659933239](https://github.com/shk95/configs/actions/runs/36659933239)
checks implementation 6b39f625a1d71b9669cf78d68d1be7a5dc015472.
[Native Windows job](https://github.com/shk95/configs/actions/runs/36659933239/job/109712355361)
passed the selected `.github/tests/test-windows-ci-runtime.ps1` directly before
contributor preparation and the full Windows suite. Acquisition, controller,
fixture and post-PATH-refresh records all name management 7.6.6/x64, with actual
and nested executable equal to the temporary verified ZIP's pwsh.exe. Refusal
records include wrong version/architecture and a conflicting nested executable;
fixtures also prove tampered hash refusal before extraction, missing executable,
reader refusal and child failure/unavailable propagation.

Inbox records independently name Desktop/5.1/x64 at
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe. Exact entry/bootstrap
source copies run in a provider-shaped synthetic clone with a harmless downstream
setup dependency, preserving `-Check -Minimal`, actual selected management child,
success 0 and child failure 37. Actual entry help 0/unknown 64 and actual bootstrap
missing prerequisite 1 also pass. These prove native bootstrap execution, not
client support baseline, real host convergence, Apply or activation.

The full management Windows suite reports 343 passed, zero failed, one skipped,
zero inconclusive/not-run. Classification is repository only; actual dispatch
selects repository:fixtures, unixlike:suite and windows:suite. Repository fixture
job 109712355356 and policy scan job 109712355381 pass, including registry 73
registered/zero pending/zero untagged and history audit zero warnings/failures.
The Unix-like suite, including import-order verification, and Required checks
also pass in this complete implementation run. After recording this evidence,
the published report head must receive its own
complete selected checks before Ready; implementation-run green is not reused
as new-head evidence.

## Delivery and limits

All changed files belong to repository governance. Windows declaration/reader
and configuration source are unchanged, as are the existing job keys, selected
suite interface, REQUIRE_NATIVE handling and Required gate semantics. The new
native fixture is selected directly by the Windows controller; repository
wiring assertions separately prove that selection. Positive/negative native
fixtures and interpreted runtime loaders/probes are registered under
repository/windows-ci-runtime-bound; no public operator CLI or preview-work
registration is introduced.

The final report publishing revision and its exact-head check results are
delivered through [PR #433](https://github.com/shk95/configs/pull/433). Ready
requires that revision's own completed native and selected checks. This report
does not claim client support baseline, maintainer-host installation, private
host behavior, desired-state Apply, activation, promotion or release. Root owns
any separately approved integration; the worker does not arm auto-merge.

Final dispatch review found that shared workflow edits selected all suites,
but a later runtime helper/fixture-only edit would select only repository
fixtures. Known runtime inputs now explicitly select the complete Windows
suite; additions, modifications, deletions and a rename into the fixture are
positive dispatch cases. CODEOWNERS and an unrelated script remain negative
Windows-effect cases. Local gates select the runtime module/controller that
their wiring assertions actually read. Shared workflow machinery retains
conservative all-suite selection. Native proof for this repaired delivery is
pending; prior implementation green is not new-head proof.
