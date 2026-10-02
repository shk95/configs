# Report: disabled release controller and pure recovery fixtures
kind: report
spec: docs/work/repository/release-controller/spec.md
status: done

## Pickup and proof boundary

Root assigned B through parent issue #451 on 2026-09-30. Execution base is
5204457ee9d16ff934b2b2260471202784c6c6c9; reviewed pickup delivery is
c35feccf35e4824ee92383c20025a2a2e6fc7582. The dedicated linked workspace and
branch are recorded in the spec and local checkpoint. Root reviewed and approved
child plan commit 5e1c8901fda9c0d38f6c27acbc0edaf7851bdaae and content identity
309dcda29fbaea7b22d36a6d5e9c3650daef4a9b before source implementation.
Document preflight proves form only.

The disabled controller source and seven pure proof-family fixtures are implemented.
Local narrow fixtures and the full repository suite passed on 2026-09-30 with
existing Python 3.13.15 and Git 2.55.0 on macOS. Working-tree/staged work, invariant
registry (77 entries), hygiene, domain-read, design-citation, records, provisional,
whitespace, shell syntax and Python syntax checks passed. Source review corrected
one workflow-fixture `choices`/`options` assertion failure, then reran the narrow
suite successfully. Historical observation lists preserve unknown-to-applied
replay; stop-race observation and two-domain partial recovery cases also pass.
The local suite includes supplied fake API transcripts and disposable file-only
repositories, without live transport. The full suite exercised inherited routing
isolation and the retained R-preview/classifier. A normal temporary source update
between independent fixture families does not provide an immutable-head CI claim.
The first normal source commit hook reported controller fixtures unverified
because its default Python shim was unavailable; the separate local suite used
the discovered functional runtime and passed. Subsequent delivery commands bind
that existing runtime explicitly. No failed/unverified check is recorded as pass.
Self-review then strengthened observed remote ID grammar, actual merge-commit SHA
binding and canonical synthetic annotated-tag object bytes, with narrow reruns.
Draft source head 95d4f836dc946944547c72837a537f8867ac11dd's
[CI 36705255125](https://github.com/shk95/configs/actions/runs/36705255125)
passed Linux repository, Unix-like and policy scans but failed native Windows
controller launch: guarded MSYS script paths reached native Python as an incorrect
drive path. Explicit native script conversion and normalized Python-to-sh paths
repair that owning-source failure. Windows desired-state also failed independently
while winget obtained Lua (`0x8a15000f`, source data missing); no Windows source
repair is claimed. A new published-head successful native/dispatch run is required.
Final hardening drops ambient credentials/execution overrides from child runtime
environments and rejects contradictory duplicate/parent/head record histories;
separate old-package fixtures refuse both missing evidence and missing approval.
Final state review preserves publication freeze across stop/resume, reloads
observed operating parents before later record intent and blocks stale parents,
binds publication versions to the candidate, and suppresses ambient Python site
packages. Narrow positive/refusal cases passed after those owning-source repairs.

Source head df79ecec508467f71e49b8f2ee50628f64a756cb's
[CI 36712555106](https://github.com/shk95/configs/actions/runs/36712555106)
passed Linux repository, policy scans and Windows desired-state. Native Windows
ran all seven controller families, but AC1's synthetic weakened-package marker
used platform text output and differed only by CRLF. Its marker now writes exact
LF bytes; this repairs the fixture contract without weakening TSV byte refusal.
Review also binds the ordinary Python diagnostic's exact newline to the host;
this does not normalize supplied records or permit additional diagnostic content.
This failed run does not verify the pending rows; a new source-head run is required.

All seven child rows are verified by repaired source-bound checks and targeted
peer review below. Historical proof covers its tested cases only; the newly
reviewed transitions are verified by the fresh repaired-head run. Parent
`provider-release-contract/report.md` remains pending with zero
of fourteen criteria verified; its domain/live obligations and R-manual and
R-scheduled lanes are not replaced by this child. Delivered R-preview evidence
is independent. No live transport, credentials, Environment, schedule, dispatch,
cancel, promotion, tag/release or host operation occurred.

## Targeted source review, 2026-09-30

Root and D reviewed exact head 13d75eff51b464edc74fbc045c814c79f053f218 and
reproduced parsed-record gaps: unknown old merge effects allowed candidate
replacement, completed effects could downgrade to absence or replay with new IDs,
tag refs lacked an observed-object gate, cancellation targets were not bound to
the recorded owner, and unknown classifications or migration flags could bypass
approval. PR #456 returned to Draft before source edits, with no admission or
auto-merge. These violate existing AC3–AC6; their repair changes no acceptance bar.
Historical green runs are retained as partial tested evidence, not completion of
these untested transitions. The repaired-head proof and independent peer review below close these child gaps.

Root also clarified that this child reads one supplied synthetic outstanding-batch
envelope only. A second batch after completion refuses. Actual global history
slicing, retained-config/package transitions, authenticated interfaces and repeated
live controller operation remain parent obligations. No synthetic fixture completes
that source or live wiring. Parent remains 0/14 pending; scheduler remains separate.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | `test_ac1_retained_full_bundle_and_old_gate`: exact checked-in manifest/source bytes, old approved synthetic merge extraction and retained preview/classifier execution pass. A newer weakened package cannot waive old evidence or approval; provenance/protocol/ancestor/tampered/incomplete closure refuse. Full operator path refuses old outstanding gates and permits safe no-op without changing caller HEAD. Review, policy and dispatch proof is recorded below. |
| AC2 | verified | `test_ac2_original_bytes_and_projection`: literal Unicode/narrative escaping, strict original UTF-8/control/CRLF/NUL, fields/IDs/tuple arity, format/decimals, contiguous filenames/digest chain, unsafe paths, impossible transitions and index disagreement are covered by positive/refusal cases. Parsing never normalizes original record bytes. Repaired source/native/review proof below. |
| AC3 | verified | `test_ac3_requests_evidence_and_invalidation`: exact synthetic approval/check bindings pass; forged actor/run/attempt/ref/workflow/event, moved candidates, missing requests/checks, canceled pending approval and major classification or migration with a waived approval flag and unknown classification refuse; exact approved migration passes. Sources remain supplied fake observations. Repaired source/native/review proof below. |
| AC4 | verified | `test_ac4_writer_wait_termination_stop`: exact terminal writer/attempt/jobs permits takeover; acknowledgement alone, incomplete pages, changed attempt or timeout alone does not. Stop prevents claims/intents while allowing observation of an accepted merge. Operating parent reload and stale-parent refusal are also proved in AC5; frozen stop/resume is proved in AC6. Repaired source/native/review proof below. |
| AC5 | verified | `test_ac5_endpoint_reconciliation_gaps`: intent/payload identity, lost record response with advanced observed head, PR uniqueness, actual merge commit/parents/tree, tag/cancel identities and unknown-to-applied history pass. Exact owner cancellation passes; changed run/attempt/workflow/job refuses. Contradictory/duplicate/incomplete histories, changed duplicate operations and stale later parents refuse; unknown candidate effects fence replacement; confirmed-absent replaced effects become superseded with zero proposed intents. Stale old intent/observation refuses. Applied success is absorbing, and stale/forked complete history cannot lower the current operating head or erase success; exact known-chain advancement passes. Repaired source/native/review proof below. |
| AC6 | verified | `test_ac6_immutable_publication_and_conflicts`: canonical synthetic tag object/annotation bytes, fixed source/version/time/run and two-domain partial publication retain completed refs and propose only missing operations. Refs require the exact observed object and canonical fixed operation ID; completed same/new-ID replay, including a later owner generation, refuses. Completion is terminal and a second batch refuses. Occupied conflicting tags, changed fixed payloads, unexpected parents/tree, missing completion, reopened candidate or duplicate promotion after stop/resume refuse. Repaired source/native/review proof below. |
| AC7 | verified | `test_ac7_inert_runtime_isolation_and_timing`: disabled quiet/no-op, enabled misconfiguration, bounded retry/opportunity simulation, duplicate signals, private summary/argument suppression, ambient credential/runtime-context removal, missing runtime 69/local versus failure/native, file-only Git isolation and no HTTP/candidate execution pass. Source workflow has inert preview only, master/event guard, independent inspector, fixed writer concurrency/timeouts and no secrets/Environment/schedule. Actual Linux and native Windows proof below. |

## Repaired source-bound checks and review

[CI 36728254716](https://github.com/shk95/configs/actions/runs/36728254716)
completed successfully for repaired source head
1ef074975fb44a883243870562f110597593a753 on 2026-09-30. This head preserves
repair commit 503605eb63fe98b1277a375ff54b8a41607a12ca and the integrator-required
normal merge of dev 54b2b794e5a0aa867f264d1bff548eebe5cc4892, without rewriting.

- [Linux full repository fixtures](https://github.com/shk95/configs/actions/runs/36728254716/job/109930735536)
  pass all seven controller families and the inherited repository fixtures.
- [Native Git-for-Windows fixtures](https://github.com/shk95/configs/actions/runs/36728254716/job/109930735569)
  pass the retained preview and seven controller families with Git 2.55.0.windows.5,
  explicitly acquired CPython 3.13.15 and REQUIRE_NATIVE=1. The native log records
  seven tests and OK. Local macOS proof remains separate.
- [Policy scans](https://github.com/shk95/configs/actions/runs/36728254716/job/109930735363),
  [Unix-like checks](https://github.com/shk95/configs/actions/runs/36728254716/job/109930735476),
  [Windows desired-state](https://github.com/shk95/configs/actions/runs/36728254716/job/109930735790),
  classification and [Required checks](https://github.com/shk95/configs/actions/runs/36728254716/job/109934097885)
  pass. Promotion policy is correctly skipped for this dev-target source PR.

B reviewed the complete repair diff and production-grammar positive/refusal cases
for the existing AC3–AC6 gaps, stale operating-head advancement and terminal
single-envelope completion. D independently reviewed the stable engine SHA-256
b6252602760e7452454c32c050391b8b2883a1d03046a4c4a9b01edb89ea023d:
AC3–AC6 families passed 4/4 and seven independent parsed repro probes refused
pending replacement, unobserved-object ref, observed-ref demotion, arbitrary ref
ID, unrelated cancellation, unknown classification and a second envelope.
D found no further blocker in the stale-head guard and fixture diff. Root reviewed
the same source/guard and ran the official shell fixture entry at the merged
source head with functional locked Python PATH: 7/7 passed. These peer probes are
local synthetic review, distinct from the fresh native hosted evidence above.

Normal explicit-runtime commit and push hooks passed, including repository
fixtures, inherited Unix-like fixtures/evaluation/native Darwin build and audit
with zero warnings/failures. No host activation or foreign build is claimed.
The repaired package manifest SHA-256 is
341e7175733f659b09fa21cba6a1d272fff3db6a7c37560d8c1be8a0d71aaa2f
(Git blob 2e9f3e3eb8b8716fd2dbaf6a8ca00904f5cefcd4). The dated scope clarification
content is 10eb00d93fa0c9aae2891964e65ed4dc80375dd7, separate from original pickup
plan pins; AC1–AC7 text is unchanged. This certifies supplied pure preview source
and fixtures only, not authenticated provenance or global/live wiring.

## Earlier source-bound checks and review

[CI 36715576059](https://github.com/shk95/configs/actions/runs/36715576059)
completed successfully for source head
3863d33f0377f67c034ac4beb5ea8bf43a15bcce on 2026-09-30:

- [Linux full repository fixtures](https://github.com/shk95/configs/actions/runs/36715576059/job/109887608735)
  pass, including the seven controller families and inherited release-preview,
  operator routing, worker checkpoints and Git isolation.
- [Native Git-for-Windows fixtures](https://github.com/shk95/configs/actions/runs/36715576059/job/109887608660)
  pass the retained release-preview and all seven controller families. The log
  declares Git 2.55.0.windows.5 and explicitly acquired CPython 3.13.15, with
  REQUIRE_NATIVE=1. This is native hosted proof, separate from local macOS proof.
- [Policy scans](https://github.com/shk95/configs/actions/runs/36715576059/job/109887608666),
  [Unix-like checks](https://github.com/shk95/configs/actions/runs/36715576059/job/109887608700),
  [Windows desired-state](https://github.com/shk95/configs/actions/runs/36715576059/job/109887608738)
  and classification pass. The conservative affected dispatch remains intact.
- [Required checks](https://github.com/shk95/configs/actions/runs/36715576059/job/109890584515)
  pass. Promotion policy is intentionally skipped for this dev-target PR.

B read the final source diff and all seven tagged positive/refusal fixture units.
The loader verifies the full eight-file semantic dependency closure before retained
execution; the adapter builds data and consumes supplied observations without a
transport. Commands use `tool/configs`; hooks/CI call implementation tools, without
domain deployment. Public summaries have only outcome/stage/count. Prose has no
undeclared bare account or host name, and no temporary measure was introduced.
The assigned child decision records only this preview boundary, without adopting
production trust or changing parent acceptance. Registry/work-form/hygiene/domain-read,
design-citation/records/provisional/secret/syntax/whitespace checks passed; the
registry has 77 entries and no untagged fixture unit. Normal explicit-runtime
commit/push hooks and final source audit passed with zero warnings/failures.

The source package manifest SHA-256 is
6b86e2d68d0245f00de0a00170d458cd9c8f44de26f2c65fe3d17ee5c5ba283a
(Git blob 1a66dd18e605183ff6a18fc28589d5bacb39eb97). This identifies source
bytes, not production approval. Historical failed runs remain failed: 95d4f83's
36705255125 launch/winget failures, df79ece's 36712555106 marker newline failure
and 7746291's [36714443920](https://github.com/shk95/configs/actions/runs/36714443920)
ordinary diagnostic newline failure do not supply acceptance evidence.

The earlier report-only publication preserved its executing and fixture source
bytes, and PR #456 recorded publication head 13d75eff51b464edc74fbc045c814c79f053f218
and successful run 36716968971 separately. Targeted review reopened that
completion; the fresh repaired proof above supplies its child completion. Child completion
can certify only pure preview
source/fixtures; parent remains zero of fourteen verified and issue #451 stays
open. Synthetic trust assertions are not production provenance authentication.
Actual credentials, operating repository bootstrap, Environment/protection/actor
permissions, notification receipt, live/manual coverage and authorized schedule
enablement remain separate obligations. No live operation or host activation/Apply
follows from this report.
