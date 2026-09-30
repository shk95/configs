# Additive offline release preview
kind: spec
date: 2026-09-30
scope: repository
status: approved
review-by: 2026-10-14
issue: #428

## Outcome and boundary

Implement the R-preview boundary of
docs/work/repository/provider-release-contract/spec.md as one additive offline
CLI with strict versioned data, deterministic refusal and synthetic fixtures.
Existing calendar plan-release, release audit, hooks and domain contracts remain
effective. This tool neither adopts production SemVer nor implements the controller.
All parent implementation criteria remain pending; this spec verifies this tool only.

No implicit network call, ref/index/worktree change, credential access, candidate
program execution, PR/issue/merge/tag operation or host mutation is permitted.
Temporary scratch files/objects are permitted outside the source repository.
Offline supplied evidence is an asserted replay input, not an authenticated live
approval or proof of the real-world claim behind a reference. R-control owns later
authentication and remote reconciliation. Missing actual bootstrap data refuses.

## Pickup and delivery

Continuation owner: the assigned B worker. One repository-scope branch/PR delivers
the spec/report, operator CLI, parser/mapping, fixtures, narrow native CI wiring and
their evidence. Pin fresh origin/dev separately from the reviewed plan revision.
The preparation base was a966f9770fd9f024aa2dc6e5796dfabba8e39458; execution
pickup pins 9b12302a047f9afe1aae10289074b2378b388ce9 after refreshing dev.
Execution ownership is assigned in issue #428 before implementation.

Owning paths: docs/work/repository/release-preview/, tool/configs,
tool/version-control/release-preview*, tool/version-control/test,
the dedicated repository invariant entry, and applicable operator documentation.
Do not edit the separate U1 documentation alignment owner's README/CONTRIBUTING/
architecture files concurrently; obtain its delivered base before adding the narrow
new-command documentation. Domain source/contract/report files are read-only inputs.

CI dependency: D first delivers the Windows-owned verification declaration wiring.
Do not edit .github/workflows/ci.yml concurrently with D. Implement the narrow
test-release-preview command first. After D enters dev, merge that required base
and add a two-OS matrix to the existing repository job: Ubuntu retains the existing
repository fixture suite; Git for Windows runs only test-release-preview via bash.
Use fail-fast=false and no continue-on-error. Existing needs.repository.result in
Required checks must require the aggregate success; test its pass/fail/skip wiring.
The CI-file change still selects all suites under existing conservative dispatch;
do not weaken that selector to reduce this PR's validation. See GitHub's
[matrix documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations).

## Command and replay grammar

```
tool/configs release-preview --master <commit> --candidate <commit> \
  --rules <commit> --baselines <file> --evidence <file> [--json]
```

Resolve revisions once to full SHA identities. --rules reads data from the pinned
commit's tool/version-control/release-preview.rules; never execute its code.
Use existing POSIX shell/Git/awk without a Nix/model or new runtime dependency.
No caller-supplied rule file overrides pinned rules. Human output and canonical JSON
describe the same decision. A valid candidate/no-op exits 0, missing tool capability
exits 69 (or fails under REQUIRE_NATIVE=1), and malformed/ineligible input exits 1.
JSON has format=1, decision=candidate/no-op/refusal, master/candidate/merge_tree/
rules identities, per-domain baselines/impact/next_version/compatibility/migration,
selected check IDs/reasons/results, unaffected exclusions, approval reasons and
stable refusal codes. Sort domain/check/reason collections; omit ambient timestamps.

Replay files are UTF-8 tab-separated records with LF endings, no blank/comment rows,
exact field counts and no embedded tabs/newlines/control characters. First row is
format<TAB>1. Unknown/duplicate keys/IDs/rows and unsupported formats refuse.
SHA fields are full object IDs; IDs are lowercase alphanumeric words with hyphens.
Comma lists contain unique known IDs, no empty entries or spaces; '-' means empty.
Narrative values are one line, escaped when printed as JSON and never evaluated.

Rules records after the header:

```
check<TAB>ID<TAB>DOMAIN<TAB>LANE<TAB>REQUIREDNESS<TAB>DEPENDENCIES<TAB>TOOL_IDENTITY
map<TAB>MATCH<TAB>PATH<TAB>CHECKS
```

DOMAIN is unixlike/windows/repository. LANE is evaluation/build/native-runtime or
fixtures/policy-checks/review. REQUIREDNESS is required/advisory. DEPENDENCIES and
CHECKS are ID lists. MATCH is exact/prefix, never regex or executable text. Match
all applicable rows and union their checks/dependency closure; reject dependency
cycles and missing definitions. Source paths must be relative, nonempty and contain
no traversal/control characters. Ownership comes from the existing classifier,
independently of check-effect selection; unknown ownership refuses.
TOOL_IDENTITY is an exact expected version or digest in the pinned check definition;
evidence must match it, not merely contain an arbitrary nonempty version. Output
also records the executing preview engine's content digest. This verifies replay
binding, not authenticity of an externally asserted execution transcript.

Baseline records:

```
semantic<TAB>DOMAIN<TAB>VERSION<TAB>TAG
bootstrap<TAB>DOMAIN<TAB>SOURCE_SHA<TAB>RECORD_COMMIT<TAB>RECORD_PATH
```

Exactly one record is required for each affected configuration domain. Semantic
version is three nonnegative decimal numbers with no leading zeros; tag must be
the matching immutable annotated DOMAIN-vVERSION, its commit ancestor of candidate.
Its annotation contains unique Release-Format: 1, Domain, Version and Source
fields matching the resolved baseline. Calendar tags are preserved but cannot
masquerade as semantic baselines by a coincidental three-number tag name.
Bootstrap reads a committed version-1 record with exact domain/source, version
1.0.0 and contract IDs from RECORD_COMMIT:RECORD_PATH. That initial source must equal
candidate; the record may be preserved in a separate reviewed history, avoiding a
self-referential source SHA. The tool checks referential consistency, not maintainer
approval or authenticity of that review. Production bootstrap record/source choice
remains unmade; fixtures use synthetic history, never today's dev by default.

Evidence records:

```
evidence<TAB>CHECK_ID<TAB>CANDIDATE<TAB>MASTER<TAB>MERGE_TREE<TAB>RULES<TAB>TOOL_VERSION<TAB>STATE<TAB>REFERENCE
defect<TAB>CONTRACT_ID<TAB>REFERENCE
```

STATE is verified/failed/unverified. Tool version and reference must be nonempty;
all identities match this replay. Required failed/unverified/missing evidence
refuses; advisory failure remains visible without manufacturing a required pass.
An explicit actual-contract defect refuses. References are data, not downloaded
or treated as authenticated live proof. Derive the expected merge tree with Git
in an isolated scratch object store using source objects read-only; conflicts refuse.
No claim of atomic remote merge protection follows from that tree calculation.

## Commit declarations and cumulative decisions

Read case-insensitively named Release-* trailers using git interpret-trailers.
Canonical fields, each exactly once except optional Release-Reverts:

```
Release-Format: 1
Release-Domain: unixlike
Release-Impact: patch
Release-Contracts: unixlike-api
Release-Compatibility: compatible
Release-Rationale: Corrects a provider behavior while preserving its public contract.
Release-Migration: none
```

Domain is unixlike/windows, impact none/patch/minor/major, compatibility
compatible/breaking/unknown. Unknown refuses; breaking requires major and an
existing public migration path in candidate. Migration is none or such a path;
any migration emits an approval-needed reason independent of version magnitude.
Reject unknown/duplicate/missing Release-* data, domain/path or contract-ID
mismatch and patch/minor declarations contradicting explicit breaking data.
Do not claim to infer all semantic compatibility from arbitrary code or prose.

Traverse all incorporated non-merge source commits once. Repository-only changes
need no domain declaration/version. After the previous semantic release, every
relevant domain commit needs a complete declaration, including explicit none.
Initial bootstrap starts at 1.0.0 without rewriting or classifying legacy history;
it cannot certify the new contract from absent evidence. Aggregate strongest
effective impact once per changed domain; none/net-zero produces no new version.
Major starts the next active series and reports the old one retired, not maintained.
This output alone never adopts that maintenance policy or creates a tag.

Release-Reverts contains a full target commit SHA. Cancel only exact inverse
touched-path/blob changes inside the same unreleased cumulative domain range.
Reject wrong/cross-domain/missing targets, partial/intervening changes or ambiguous
pairing. A revert of already released source is a new declared change. Parse all
necessary declarations before declaring net-zero; unresolved metadata refuses.

## Initial changed-function table

Always select from the complete current-master-to-candidate promotion delta,
including additions/deletions and both sides of renames. Version aggregation uses
the separate previous-domain-tag-to-candidate range. Record why each check runs;
unaffected exclusions are not newly verified evidence. Candidate movement requires
new exact-bound evidence; no cross-candidate pass reuse.

Seed only bounded known rows: docs/ to repository-policy; Unix-like API data and
constructor wiring to unixlike-api and its declared evaluation/build dependencies;
contract-inspect/readiness tool paths to their existing domain fixture IDs. Record
the actual paths/check definitions in the pinned rules file. Unmapped paths refuse
with mapping-review-needed, never empty success or automatic whole-domain fallback.
No Windows W1 production mapping is invented before its contract is delivered;
synthetic Windows rows prove generic union/version behavior. Incomplete production
coverage is an explicit limit of this additive preview, not a weakened release gate.
An explicit common/ input refuses as an unsupported release product even if no
current classifier arm admits it. Repository/docs-only no-op still preserves the
distinct full promotion-selection and per-domain-version comparison identities.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Strict version-1 trailers and replay grammars accept valid declarations and refuse malformed/missing/duplicate/unknown or ownership/contract/compatibility contradictions without an adapter. | fixtures, policy checks |
| AC2 | Explicit source-bound bootstrap proposes independent initial 1.0.0, semantic baselines preserve legacy/retired tags and absent or contradictory initial records refuse without rewriting history. | fixtures, policy checks |
| AC3 | Cumulative strongest-impact versioning, source-only/no-op, migration reasons and exact inverse same-range revert handling are deterministic; ambiguous or wrong/partial/already-released cancellation is refused. | fixtures, policy checks |
| AC4 | Full master-to-candidate mapping covers declared rows/dependencies and mixed/add/delete/rename cases, records unaffected exclusions and refuses unmapped/unknown scope without previous-candidate pass reuse. | fixtures, policy checks |
| AC5 | Required exact-bound evidence passes only when verified, missing/failed/wrong identities refuse, advisory and explicit defects remain distinct, and identical complete replay inputs yield stable machine output despite ambient time/ref changes. | fixtures, policy checks |
| AC6 | Public CLI preserves source refs/index/worktree and remote state, executes no candidate code, propagates stable output/refusal and preserves existing calendar planning; tests cover permitted and refused progress plus hostile data. | fixtures, policy checks, affected dispatch |
| AC7 | Narrow fixtures run on final-head hosted Git for Windows and Ubuntu, MSYS/prerequisite behavior and matrix/gate success/failure/skip wiring are verified, and current-head Required checks passes without claiming native domain or controller/live rollout proof. | fixtures, policy checks, affected dispatch, review |

## Verification and stop conditions

Each AC is one of the seven positive/negative proof families. Fixture units name
the narrowly adopted read-only-preview tool-contract invariant; existing evidence,
MSYS, operator-entry and gate invariants are tagged only where actually proved.
Add the new invariant with rationale in AGENTS.md Governance design and Rules that
are expensive to break; it constrains the offered preview, not production release
policy. Run narrow preview fixtures before the broader repository suite/scans and
native CI. Synthetic declarations/evidence are fixture proof only.

Return to planning for new release meaning/support promises, weakened gates,
production bootstrap selection or live-authority requirements, loss of ownership,
domain-source changes, or scope/acceptance changes. Concrete first-release source
and actual bootstrap adoption need maintainer judgment; their absence does not
block generic offline implementation. Never mark the parent controller/release
criteria complete from this additive lane. No activation, Apply or cleanup.
