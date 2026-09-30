# Report: additive offline release preview
kind: report
spec: docs/work/repository/release-preview/spec.md
status: pending

Implementation is assigned to B in execution issue #428; pickup pins
9b12302a047f9afe1aae10289074b2378b388ce9 after preparation at
a966f9770fd9f024aa2dc6e5796dfabba8e39458. The additive CLI/parser/rules and seven
narrow synthetic fixture families are
implemented as a Draft. Local POSIX fixtures passed on Git 2.55.0; repository
registry, work-form, hygiene, domain-read and citation checks are kept separate
from native Windows or live release proof. No production bootstrap has been
selected, and final-head CI/native evidence is still pending.
The parent provider-release/controller reports remain pending.

CI wiring and the shared repository-suite registration wait for D's separate
repository wiring execution #431 / PR #433 to enter dev and the integrator to transfer
ownership. The preview command/narrow fixture are independently authored. The
registration patch is preserved locally and will be aligned after that prerequisite.
Document preflight validates form, not acceptance evidence.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Fixtures: local Git 2.55.0 with GNU awk and BSD awk permits complete metadata/Unicode paths and refuses missing/unknown/duplicate/control/NUL/domain/contract/path/invalid-UTF-8 mismatches. Policy checks: registry/work-form/hygiene/domain-read/citation scans pass. Native Windows replay is separately pending in AC7. |
| AC2 | verified | Synthetic separate-history 1.0.0 bootstrap and missing/contradictory baseline, legacy/calendar/lightweight tag refusals; no production record adopted. |
| AC3 | verified | Cumulative patch/minor/major, exact unreleased cancellation including removed effective breaking/migration/approval data, partial/cross-domain/parallel-ancestry/ambiguous refusals and released-target new change fixtures. |
| AC4 | verified | Complete promotion union, add/delete/rename, governance/docs-only and explicit no-op, dependencies/unknown/duplicate rules; partial production mappings refuse. |
| AC5 | verified | Stable replay despite moved tags/replacement refs/legacy grafts; pinned annotation objects and exact source/master/tree/rules/tool/message/runtime binding, required versus advisory and explicit defects; references remain asserted offline data. |
| AC6 | pending | Candidate code/hostile data not executed; source refs/index/status/config unchanged, remote-command guard, CLI/calendar compatibility fixtures. |
| AC7 | pending | Native Git for Windows/Ubuntu current-head runs and minimum Required gate remain pending; missing capability 69 versus REQUIRE_NATIVE failure proved locally. |

## Evidence limits

The narrow command is `tool/version-control/test-release-preview`, and the public
operator command is `tool/configs release-preview`. Its reported engine digest
binds the executing wrapper/awk bytes; expected check tool identities come from
the pinned rules. Offline evidence references are not authenticated transcripts.

These fixtures construct synthetic commits/tags/rules and never designate current
production source as an initial API release. Existing calendar planning, domain
release audits and promotion remain unchanged. The parent controller and provider
release criteria remain pending; this Draft does not implement scheduling, remote
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
Decimal component arithmetic uses string carry, with 2^53-exceeding and long-carry
fixtures plus malformed decimal refusals. File data passed to native Git uses stdin
to preserve MSYS argument guards without depending on POSIX absolute-path conversion.

The current Draft's older published-head CI did not register this narrow suite and
is not the final native preview proof. AC6 remains pending operator documentation and
affected-dispatch alignment; AC7 remains pending current-head Ubuntu/Git-for-Windows
fixture jobs and Required-gate proof after prerequisite ownership transfer. The
report stays pending and the parent release/controller report states are unchanged.
