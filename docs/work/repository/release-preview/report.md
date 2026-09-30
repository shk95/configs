# Report: additive offline release preview
kind: report
spec: docs/work/repository/release-preview/spec.md
status: done

Implementation is assigned to B in execution issue #428; pickup pins
9b12302a047f9afe1aae10289074b2378b388ce9 after preparation at
a966f9770fd9f024aa2dc6e5796dfabba8e39458. The additive CLI/parser/rules and seven
narrow synthetic fixture families are implemented and verified in this bounded
offline preview lane. Local POSIX fixtures passed on Git 2.55.0; repository
registry, work-form, hygiene, domain-read and citation checks are kept separate
from native Windows or live release proof. No production bootstrap has been
selected. Exact source-head CI and native proof are recorded below; report
publication receives fresh selected checks before Ready.
The parent provider-release/controller reports remain pending.

CI wiring and shared repository-suite registration now consume D's delivered
execution #431 / PR #433 at dev9f72acec541fd987695e5bdbad5fd53c8129e799. The
required companion-document base #436 entered at
60683763b8d201621e3bc92152d64ba66dd81dbf; both were merged without rewriting
published history after explicit file ownership transfer. Ubuntu runs the full
repository suite; Git for Windows runs the narrow preview fixture, with
REQUIRE_NATIVE=1, fail-fast=false and no tolerated failure. The existing Required
gate consumes the matrix aggregate. Positive/negative matrix weakening, aggregate
failure/skip/cancel and preview-file dispatch fixtures pass locally and in the
source-head CI below. Operator usage follows the delivered companion
documentation without changing its adoption or activation meaning.
Document preflight validates form, not acceptance evidence.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Fixtures: local Git 2.55.0 with GNU awk and BSD awk permits complete metadata/Unicode paths and refuses missing/unknown/duplicate/control/NUL/domain/contract/path/invalid-UTF-8 mismatches. Policy checks: registry/work-form/hygiene/domain-read/citation scans pass. Exact Ubuntu and native Windows proof is recorded in AC7. |
| AC2 | verified | Synthetic separate-history 1.0.0 bootstrap and missing/contradictory baseline, legacy/calendar/lightweight tag refusals; no production record adopted. |
| AC3 | verified | Cumulative patch/minor/major, exact unreleased cancellation including removed effective breaking/migration/approval data, partial/cross-domain/parallel-ancestry/ambiguous refusals and released-target new change fixtures. |
| AC4 | verified | Complete promotion union, add/delete/rename, governance/docs-only and explicit no-op, dependencies/unknown/duplicate rules; partial production mappings refuse. |
| AC5 | verified | Stable replay despite moved tags/replacement refs/legacy grafts; pinned annotation objects and exact source/master/tree/rules/tool/message/runtime binding, required versus advisory and explicit defects; references remain asserted offline data. |
| AC6 | verified | Candidate code/hostile data not executed; source refs/index/status/config unchanged, remote-command guard, CLI/calendar compatibility, operator forwarding and preview-file effect fixtures pass in the full local repository suite and Ubuntu CI. README/CONTRIBUTING document bounded inputs, refusal/recovery and separate authorization. Native preview and test-only environment isolation pass as recorded below; supplied evidence remains asserted offline data. |
| AC7 | verified | [Run 36681617644](https://github.com/shk95/configs/actions/runs/36681617644) checks exact source 7a1012910dce222ba4e48fcc7fdd3b3f45518e05: Ubuntu/full repository, native Git for Windows/eight isolation cases plus full narrow preview, all other selected suites and Required checks succeed. Local missing-capability exit 69 and native-required failure remain separate fixture invocations; job REQUIRE_NATIVE=1 remains strict. Report publication receives its own fresh current-head CI before Ready. |

## Evidence limits

The narrow command is `tool/version-control/test-release-preview`, and the public
operator command is `tool/configs release-preview`. Its reported engine digest
binds the executing wrapper/awk bytes; expected check tool identities come from
the pinned rules. Offline evidence references are not authenticated transcripts.

These fixtures construct synthetic commits/tags/rules and never designate current
production source as an initial API release. Existing calendar planning, domain
release audits and promotion remain unchanged. The parent controller and provider
release criteria remain pending; this preview lane does not implement scheduling, remote
reconciliation, release mutation, host activation or Windows Apply.

## 2026-09-30 offline replay refinement

The semantic replay row now includes the full annotated-tag object SHA and validates
its intrinsic name/type/domain/version/source; a changed tag ref never replaces that
object. Source Git and classifier processes ignore replacement refs and legacy graft
files. Normalized true/yes/on/1 promisor configurations and invalid booleans refuse;
lazy-fetch guards plus an empty allowed-protocol list prevent implicit transport.
The protocol guard is documented in the [Git 2.38 implementation](https://github.com/git/git/blob/v2.38.0/Documentation/git.txt); the
newer lazy-fetch guard is additional protection rather than a minimum-version claim.

For a proposed domain version, effective uncanceled contract checks/dependencies are
unioned as domain-release qualification, separate from full master-to-candidate path
selection. Already-promoted source with an older semantic baseline requires its own
exact evidence; missing evidence refuses, sufficient evidence passes. Net-zero/none
adds no release-only qualification. Exact canceled major/breaking/migration histories
remain visible as provenance but do not retain effective metadata or approval reasons.
Uncanceled major history with a net-zero domain tree proposes no new version and
does not retire its previous major. An ambient Git init template cannot install a
merge driver into the isolated scratch repository; a hostile-template conflict
fixture verifies refusal without executing that driver.
Decimal component arithmetic uses string carry, with 2^53-exceeding and long-carry
fixtures plus malformed decimal refusals. File data passed to native Git uses stdin
to preserve MSYS argument guards without depending on POSIX absolute-path conversion.

At the earlier Draft checkpoint, published-head CI did not register this narrow
suite and could not establish native preview proof. AC6 operator documentation
and affected-dispatch alignment had local proof; AC7 and the report stayed pending
current-head Ubuntu/Git-for-Windows and Required-gate proof after prerequisite
ownership transfer. The parent release/controller report states remain unchanged.

## First native matrix diagnostic and original-byte repair

[Run 36666916787](https://github.com/shk95/configs/actions/runs/36666916787)
checks published source 6a94bbf23ca2a76428ebc5c15ecdfcbf70fc6ec0. Ubuntu's full
repository suite, native Windows desired-state, Unix-like and scans pass. The
[Git-for-Windows preview job](https://github.com/shk95/configs/actions/runs/36666916787/job/109733469392)
executes on Git 2.55.0.windows.5, reaches its native fixture banner, then fails the
last missing-capability fixture: the local-mode invocation inherited the job's
REQUIRE_NATIVE=1 instead of testing the local exit-69 mode. Required checks fails
correctly. This diagnostic is not completed native acceptance.

The local-mode fixture now explicitly sets REQUIRE_NATIVE=0 only for that one
invocation; its separate native missing-capability invocation and the CI job retain
1. Local GNU/BSD awk suites pass with the enclosing REQUIRE_NATIVE=1 environment.
Committed bootstrap records validate original UTF-8/NUL/LF/control bytes before
AWK normalization. Raw semantic tag objects validate original UTF-8/NUL bytes
before peeling or field parsing; BSD awk's removal of NUL in a Version field was
reproduced directly. Raw source commit objects validate original UTF-8/NUL bytes
before pretty formatting, which otherwise truncates a message at NUL. Focused
valid and malformed pinned commit/tag/record objects prove these refusals without
choosing a production bootstrap. At that checkpoint, AC7 remained pending the
repaired exact-head native run and publication awaited the actual required
admission base. Earlier CI cannot certify a changed head.

## Independent fixture isolation and second native diagnostic

The publication retry initially passed a command-scoped origin push URL into
fixture child Git through inherited configuration. A synthetic fixture tag was
created in the real repository, while dev/master updates were rejected. The
integrator removed that synthetic tag after explicit maintainer authorization;
subsequent read-only checks confirmed its absence and expected refs unchanged.
Its annotation and source were synthetic fixtures, not domain release evidence.
D's issue #439 / PR #441 separately delivered a test-only Git environment boundary
and eight local positive/negative routing/transport cases. This independent
preview fixture adopts that helper before any Git command and runs the eight-case
proof in its native job; production engines/hooks do not source it.

A subsequent normal SSH push passed its selected local gates but exited 141 when
the transport closed, leaving the feature head unchanged. A normal retry with an
explicit HTTPS destination and no origin push-URL override or hook bypass published
source a1a07e808dcf6b6daf4555e60e179739a01579bf. These transport attempts are separate
from semantic fixture acceptance.

[Run 36677599086](https://github.com/shk95/configs/actions/runs/36677599086) checks
that exact source. Its
[native preview job](https://github.com/shk95/configs/actions/runs/36677599086/job/109765892658)
fails before the eight cases: native Git refuses `/d/a/configs/configs` under the
required MSYS argument guard. This is a diagnostic failure, not completed AC7.
The focused fixture now normalizes repository and scratch absolute paths with
`cygpath -m` when available, while keeping the stub's PATH component in POSIX form.
All eight hostile/local-operation cases, caller HOME/ref/config/source assertions
and MSYS guards remain. The delivered environment helper, main suite, production
preview and CI gates are unchanged. At that diagnostic checkpoint, native proof
remained pending the repaired publication head and its actual required admission
base selected by the integrator.

## Completed source proof and report publication

The integrator's actual required base
09331768863a43d21e15d5e28d10045b7f8f87b2 entered through a normal merge after
#444. Earlier required bases, delivered companion documentation, original-byte
repairs and fixture isolation were preserved without rewriting published history.
Source head 7a1012910dce222ba4e48fcc7fdd3b3f45518e05 was published through a normal
HTTPS push; the selected local gates passed, including the foreign-host Windows
suite with 345 passed, zero failed and three skipped. That foreign-host result is
separate from native Windows evidence.

[CI 36681617644](https://github.com/shk95/configs/actions/runs/36681617644)
completed successfully on that exact source head:

- [Ubuntu/full repository](https://github.com/shk95/configs/actions/runs/36681617644/job/109778138128)
  passed the complete suite, worker checkpoints, isolation and preview fixtures on
  Git 2.55.0.
- [Native Git-for-Windows preview](https://github.com/shk95/configs/actions/runs/36681617644/job/109778138073)
  passed all eight isolation cases, printed Git 2.55.0.windows.5 and completed the
  full narrow preview. Clean, command parameters, counted/orphan configuration,
  ambient/includes/templates and repository-context cases preserve intended local
  operations and refuse external transport. Caller refs/config/source/HOME checks
  pass in these synthetic fixtures.
- Unix-like, native Windows desired-state, scans and classification succeeded;
  [Required checks](https://github.com/shk95/configs/actions/runs/36681617644/job/109780563721)
  succeeded. Promotion policy was intentionally skipped because this PR targets dev.

An optional supplementary native probe observed Git 2.55.0.windows.3 with Git-owned
Bash/cygpath and PowerShell 7.6.6. Its task-TEMP public-source clone failed with
CRYPT_E_REVOCATION_OFFLINE before checkout, fixture-byte overlay or the eight
cases. This probe is unverified; it establishes no overlay or caller-preservation
result. No TLS setting, host configuration or installation changed. Hosted
source-head proof above supplies this lane's authoritative native evidence.

This report-only completion update preserves the verified source and receives
fresh selected CI, including the native preview matrix and Required checks, before
Ready. The PR records that exact publication head and run separately from the
source proof above. The result completes only this offline preview lane: supplied
evidence references remain unauthenticated assertions, no production bootstrap
record or SemVer release policy is adopted, and the controller and scheduler
remain unfinished. No source promotion, release, host activation or Apply is implied.
