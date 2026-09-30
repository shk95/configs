# Report: Windows host-owned configuration
kind: report
spec: docs/work/windows/host-consumer-contract/spec.md
status: pending

## W1 source implementation, 2026-09-30

Issue #427's W1 lane now implements `inspect`, `generate` and read-only
`export-selection` with version 1 environment/settings/generation formats.
Generation binds exact provider source and execution tools, explicit original
documents and selected payloads. It refuses unsupported formats, ambiguous keys,
invalid UTF-8/UTF-16 input, unsafe connections, hidden Git index flags and stale
input/tool/file identities. Atomic publication preserves an earlier result on
failure. Generated Check/Apply require the generation's own tools and selection.

The selected complete document supplies the owned JsonSubset projection; app keys
outside it, externally generated Terminal profiles and foreign profile blocks are
preserved. Disabled profile units stop hook management. The catalog retires provider
WSL configuration and personal FancyZones layouts/hotkeys without deleting host
files. Generic default layouts remain provider defaults or complete host content.
Generated terminal delegation is explicitly excluded, with no registry observation
or mutation. Schema 3 records generation success and partial fixture Apply failure
separately; source-only capture refuses generated runtime state pending W2.

Foreign-host PowerShell 7.6.6 generation fixtures passed 56/56, including two actual
PATH Application candidates with selected child execution and exit forwarding,
strict encoding, hidden-index edits and a different imported module at an otherwise
identical generation-module revision. The full foreign-host suite passed
384 tests, failed 0 and skipped 16; native-only/e2e skips retain their separate
proof obligations. Staged Windows classification, 73 invariant registrations,
document preflight, design-citation, record and hygiene checks passed.
This is fixture evidence on a foreign host,
not native Windows acceptance. Hosted exact-runtime checks and candidate-specific
LTSC generation/Check evidence remain pending. Apply occurs only under isolated
fixture mocks. Whole AC rows below remain pending; W2 capture, domain API release,
deployment and host activation are not supplied by this W1 lane.

## W1 implementation pickup, 2026-09-30

The main orchestrator assigned W1 declaration/connections/local generation to
one Windows worker after the planning PR entered dev. The reviewed spec revision
was 83b05dcdf9d387587280e32c7c676389020a399f; the execution pickup base was
a966f9770fd9f024aa2dc6e5796dfabba8e39458. Before source implementation, the
worker resumed issue #427 at origin/dev
6629e8a002e615054708bb27c6540727e04bc832 after the Windows runtime declaration
prerequisite #430 entered dev. The original reviewed spec pin is retained
separately from this required base update. The dated pickup amendment concretizes
versioned JSON inputs, explicit unit connections, source selection and integrity,
legacy-selection preview, unit ownership, unmanaged target-state preservation,
LTSC capability exclusion and required native proof. No implementation evidence
is supplied by this amendment.

W1 records proof below by obligation and evidence lane. Keep every whole AC row
pending until all its required obligations and lanes have been verified. In
particular, W1 source selection is not W2 capture/save proof (AC3 and capture
parts of AC7), hosted native fixtures are not LTSC client acceptance (AC5), and
Windows-owned runtime data is not exact-version CI wiring proof (AC6). Exact
PowerShell 7.6.6 CI wiring has the separately owned repository execution issue
#431. An authorized read-only LTSC client route is available: preparatory
inventory observed Windows 10 IoT Enterprise LTSC x64 build 19044.7725,
PowerShell 7.6.6 and inbox 5.1.19041.7725. This is environment availability,
not final-head generation/Check acceptance. Actual
Apply is tested only in isolated fixtures, not on a real host. No release,
activation, integration or cleanup is implied by partial delivery.

## W1 pickup preparation, 2026-09-30

The planner reconciled the pickup boundary with the latest whole-unit and
save/generation-failure amendments. W1 owns Windows declaration, explicit
connections, source selection and local generation/Check/Apply guards; W2 owns
capture/save and waits for W1's format to enter dev. U1/Nix and private host
activation are not W1 prerequisites. Repository release-controller implementation
and any needed hosted CI wiring remain separately assigned scope work.

Read-only source inspection at dev 1758fe98aff677b815fd28d14d53228e29bf5371
confirmed the existing manifest features/ManagedFiles, runtime-recorded selection,
provider-targeted capture and absence of a host generation verb. The Windows
job currently invokes the Windows validation/test implementations with
REQUIRE_NATIVE and WIN_ENV_E2E; it does not explicitly select PowerShell 7.6.6.
That is a preparation dependency to resolve, not evidence that AC6 is met.

The added pickup matrix identifies unresolved concrete format, migration,
unit-ownership and LTSC capability/gate choices before implementation assignment.
It maps the existing criteria to W1 proof obligations without certifying a new
schema or a host migration. A new dedicated latest-dev implementation worktree,
reviewed plan revision, one continuation owner and explicit publication scope
remain pickup requirements. No W1 implementation, generation, native suite,
client Check, capture or Apply ran. All acceptance rows remain pending.

## Cross-work reading reconciliation, 2026-09-28

Latest-reading guidance marks delta/baseline capture as superseded, preserves Apply
records and external state, and distinguishes changed-behavior native evidence from
an unconditional feature matrix. Host-owned extensions are not prohibited or
certified by provider checks. No Windows execution or implementation was performed.

## Save/generation failure planning, 2026-09-28

The latest amendment records document-before-connection first capture, inert
unconnected-file recovery, atomic individual replacements and validated temporary
generation with stale-input refusal. Apply reports partial results without automatic
rollback. No implementation or Windows execution was performed; all rows pending.

## Capture and generation simplification, 2026-09-28

The maintainer accepted whole-unit ownership transfer, separate feature/settings
selection, explicit host document connections and source-identified generation.
The latest spec amendment supersedes earlier capture delta merging and baseline
requirements; Apply outcome/partial-failure records remain. Read-only inspection
of capture.ps1 and desired/manifest.json confirmed current provider-targeted
capture/publication and ManagedFiles structure; none was changed. New host formats,
capture destinations and generation behavior remain unimplemented. No Windows
suite, Check, capture or Apply ran, and all acceptance rows remain pending.

Stage-1 design agreed on 2026-09-27. Current implementation observations are
in study.md. No new host schema, generation command, capture destination or
selection semantics have been implemented. No provider native suite, generation,
host Check or Apply was performed in this planning session. Read-only inventory
and version/help probes are recorded separately in study.md.

On 2026-09-27 the maintainer initially chose Windows 10 and Windows 11, then
explicitly narrowed support and verification to Windows 10 because Windows 11
verification is unavailable. The dated AC5 amendment records the replacement
decision. A later same-day AC5 amendment selects Windows 10 IoT Enterprise
LTSC 21H2 x64, build 19044 (observed revision 7725), and excludes default
terminal delegation from its guarantee while retaining Terminal settings,
fonts and profiles. Native inventory establishes this environment's identity,
not provider acceptance. Capability-aware contract and gate implementation,
and candidate-specific native acceptance evidence, remain pending.

The maintainer selected PowerShell 7.6.6 as the initial exact CI baseline on
2026-09-27, preserving Windows PowerShell 5.1 bootstrap coverage. AC6 remains
pending until the explicit version contract is implemented and verified.

## Latest design consolidation, 2026-09-28

The latest dated spec consolidation records environment/host ownership and
domain API/template contracts. All implementation and live evidence remains
pending, including the new API criterion. Document preflight is form validation,
not evaluation, build, native runtime, activation/Apply or live automation proof.
No source implementation, Git publication or host mutation was performed.

## Independent review follow-up, 2026-09-28

Accepted independent-review corrections are now recorded in the owning specs.
They clarify cutoff/candidate timing, complete-delta check selection, template
delivery, initial reader bootstrap and host-local applied-state capture. All
implementation evidence remains pending; this update is design acceptance only.

## Final independent planning audit, 2026-09-28

An independent agent reviewed all five work items against latest accepted
amendments and confirmed the previous five corrections without identifying a
new direction conflict. This is planning review only. Concrete consumer paths,
U1 types/transitions/evidence and later lane prerequisites remain; all acceptance
rows stay pending and no implementation or live rollout is certified.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
| AC7 | pending | |
| AC2 | pending | |
| AC3 | pending | |
| AC4 | pending | |
| AC5 | pending | |
| AC6 | pending | |
