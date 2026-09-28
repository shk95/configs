# Windows host-owned configuration and capture
kind: spec
date: 2026-09-27
scope: windows
status: approved
review-by: 2026-10-11

## Current reading order after reconciliation

Reconciled 2026-09-28: latest capture ownership/local generation and save/failure
amendments supersede earlier desired-state delta merges and last-applied capture
baseline requirements. Apply outcome/partial-failure state is separate and retained.
W1 owns explicit selection/documents/generation; W2 consumes that format for host
capture. Both remain independent of Unix-like/Nix. Settings source selection is
distinct from preserving unmanaged app state and external PowerShell blocks.
Arbitrary host extensions are host responsibility; earlier stop conditions do not
ban such extensions or make their compatibility a provider requirement. The feature
case list is available coverage, not mandatory repetition on every unrelated edit.
Required native Windows evidence applies to changed behavior; document checks are
not native acceptance. Format/CLI names and delivery fixtures remain implementation
work, not evidence already achieved. All report criteria remain pending.

## Outcome

Use win-env.ps1 as the host-facing entry for pinned Windows source, local
composition, Check, Apply and capture. Keep PowerShell-native independence
from Nix and Unix-like execution. Coordinate release governance through
`docs/work/repository/provider-release-contract/spec.md`.

## Contract

The host selects a configs version resolved to a fixed commit and an explicit
feature list. Features are opt in: core is always included, required
dependencies are included, and newly introduced optional features are not
silently adopted. An empty list selects only core. Reject unknown features.
Additional host information is deferred until an actual need establishes its
schema; user directories and Windows capabilities remain detected locally.

Keep provider source, host declarations/captured customization, generated
deployment configuration and runtime state separate. Acquire the fixed
Windows source, combine it locally with host intent, validate/Check, then
Apply only on explicit request. A clone with Windows source extraction is a
valid initial transport; packaged assets can follow. Local generation means
materializing configuration, not requiring a compiler or Nix build.

Generated configuration contains the selected dependency closure, required
payloads and compatible manifest/tools, with provider SHA, host-input identity
and format version. Bind environment-dependent paths/variants on the target
and revalidate that environment before applying. Exact layout and command
verbs remain implementation design; do not advertise nonexistent commands.

Capture writes only host-owned desired customization. Subsequent generation
combines provider defaults with host changes, giving documented host values
precedence. Prefer deltas for owned keys; explicitly define whole-file, list,
deletion and conflict handling before implementation. Reject incompatible
customization before Apply rather than silently discarding it. Keep runtime
cache/session data out of capture and preserve externally managed profile
blocks. Common-default contributions are a separate provider change.

Deselecting a feature stops managing it. It does not uninstall software or
restore prior settings; cleanup/restore is a separate explicit operation.
Changing source revision or capturing settings grants no Apply permission.
Capture no longer implicitly publishes personal changes into configs.

## Stage-2 decision: Windows 10 only

Amended 2026-09-27: AC5 replaces the earlier same-day agreement to retain
Windows 10 and Windows 11 with Windows 10-only support and verification.
The maintainer cannot provide Windows 11 verification and explicitly chose
to remove it from the supported scope. Windows 11 is neither a required
promotion/release evidence lane nor an implicitly supported unverified target.
Reintroducing it requires a later support decision and appropriate evidence.
AC1-AC4 and AC6 are unchanged. Support is conditional on the documented OS
build, application versions and selected capabilities; it is not a promise
that every feature works on every Windows 10 build.
Preserve known support limits and distinguish them from unavailable observations.
The initial client baseline is selected by the later amendment below; minimum
tool versions remain to be verified before release. Hosted native fixtures alone do not
certify client-only behavior. This decision grants no Apply or host-update request.

## Stage-2 decision: LTSC baseline and terminal capability boundary

Amended 2026-09-27: AC5 selects Windows 10 IoT Enterprise LTSC 21H2, x64,
build 19044 as the initial client verification baseline. The observed revision
is 19044.7725; record the actual revision for each candidate rather than
inferring that all revisions, editions or architectures have been verified.
The maintainer accepted this baseline after read-only inventory and explanation
of the default terminal delegation limit. AC1-AC4 and AC6 are unchanged.

Keep Windows Terminal settings, fonts and profiles in the supported contract.
Exclude default terminal delegation from the guaranteed capabilities of this
LTSC baseline: launching a console program outside Terminal is not promised
to open its window in Windows Terminal. This does not remove the terminal
feature or its dependency closure. Registry read-back is not proof of handoff.

The implementation lane must express this capability boundary explicitly in
the consumer contract and promotion/release evidence selection. An excluded
capability must remain visibly outside the guarantee; it must not be reported
as passed or used to waive unrelated unavailable observations or drift. All
included capabilities still require their applicable native evidence.
Current Check/REQUIRE_NATIVE behavior and the accepted support-limit policy
remain unchanged until a reviewed implementation reconciles them with this
planned contract. Do not bypass the existing gate to deliver this plan.

## Stage-2 decision: initial PowerShell verification version

Agreed 2026-09-27: use PowerShell 7.6.6 explicitly for initial CI management
verification and retain separate Windows PowerShell 5.1 entry/bootstrap checks.
Record and check the actual runtime version rather than inheriting the hosted
image's default silently. This adds AC6. It is a verification baseline, not a
minimum version imposed on consumer hosts or an automatic installation request.
The oldest supported management version and WinGet pin remain open until native
evidence establishes them; contributor Pester/Lua pins remain separate.

## Environment ownership and host customization consolidation

Amended 2026-09-28 (latest discussion): AC1-AC5 retain Windows opt-in, with the
following elaboration; do not import Unix-like default-on behavior. Core remains
required, selected features bring required dependencies, and newly added optional
features are not silently adopted. Windows remains independent of Nix.

Configs owns shell/app settings, fonts and general PowerToys behavior. Move WSL
VM networking/resource policy (.wslconfig) and its application/check obligations
to hosts; this is distinct from Unix-like WSL adaptations. Personal window layouts
and workspaces are host data. Empty provider files must not reset personal data.

Merge provider defaults with host overrides: object keys merge with explicit host
values winning; arrays replace as whole lists, never guessed element merges.
Deletion needs an explicit marker distinct from null. Text uses format-specific
extension points and preserves externally managed blocks. Reject malformed inputs,
removed/unknown active settings/features, incompatible values and violated feature
requirements before Apply. Never silently discard host overrides. Schema and
deletion syntax remain implementation design.

Capture uses the actually applied provider revision, not the newest candidate,
and records newly observed managed differences only. Preserve existing explicit
host overrides even when equal to provider defaults; removing the override explicitly
means following defaults again. Permit explicit equal-value pins. Exclude runtime
cache/session/recent-use data and external blocks. Capture does not publish provider
changes, update source or Apply. Source-aware comparison and merge-conflict fixtures
remain required.

Deselection stops management without uninstall/reset/data removal and retains host
customization. Inactive customization must be structurally valid, but its current
feature compatibility is checked on reselection so obsolete inactive data does not
block unrelated work. Reselection composes current provider defaults and preserved
overrides, validates, and only then permits separately authorized Apply. Migration
guidance never implies host declaration mutation or Apply permission.

Verify core-only, each offered feature with dependencies, maximal compatible
composition, host overrides/capture/deselection/reselection and refusal cases.
Add combinations for actual interactions rather than exhaustive permutations.
Optional features remain provider verification obligations; private installations
are not recurring release prerequisites. Existing LTSC/capability/PowerShell
decisions remain. Publish a Windows-native API/data contract and inspection tooling
under the repository amendment, without a shared Nix evaluator or forced common
schema. No native runtime or Apply evidence is provided by these planning edits.

## Pickup lanes

W1: versioned host declaration, opt-in selection and local generation contract.
Inputs: current dev, current manifest/check/apply implementation, this spec.
One coherent Windows PR. Determine serialization/layout and migration from
existing recorded selections before worker pickup. Native fixtures cover
dependency closure, new features, empty selection, invalid input, regeneration
and source/host/generated separation.

W2: host capture and customization merge, depending on W1's format. One
Windows PR with capture projection, array/deletion/conflict rules and migration
from existing capture/publication behavior. Native fixtures and read-only
capture prove host ownership and source immutability; Apply remains separately
authorized. Governance/publication changes outside Windows have their own
repository increment. Private host/template adoption is separately owned.

Stop/replan for arbitrary host overrides, unrequested uninstall/restore,
cross-platform generation, implicit publication or remote credential changes.
Stage 2 names Windows release evidence; native fixtures alone are not actual
host runtime or Apply proof. The next planner refines lanes before pickup.

Amended 2026-09-28 (latest consolidation): add AC7 for contract discovery
and verification. Earlier criteria are interpreted with the latest dated
consolidation above; historical proposals do not override that amendment.

## Accepted independent-review corrections

Amended 2026-09-28 after accepted independent review: AC2/AC3 require capture
to identify the successfully applied generated configuration, provider revision,
host input and managed-target baseline. Distinguish last applied result, current
host declaration and observed state. Provider SHA alone cannot represent host-only
changes or partial Apply. Initially refuse affected capture on missing baseline,
partial Apply or changed host declarations rather than overwriting pending intent.
Add fixtures; preserve explicit overrides. This is host-local operating state,
not the private release repository. No general recovery engine is required.

## Capture ownership and local generation simplification

Amended 2026-09-28 (latest Windows discussion): AC1/AC2/AC3/AC4/AC7 replace
automatic provider/host delta merging with explicit whole-unit ownership. This
supersedes the earlier object-key merge, capture deletion markers and capture-only
last-applied baseline requirements, including the independent-review correction
above. Ordinary Apply success/partial-failure records remain independently needed.
Keep Windows implementation and format ownership independent of Darwin and Nix.

Use the existing ManagedFiles entries as the starting capture units, not an entire
application/feature by default. A selected unit uses either provider defaults or
host-owned settings; capture adopts the supported observed projection as the host
unit, excludes that unit's provider defaults and never automatically merges later
provider changes into it. Applying the chosen payload while preserving unmanaged
application state is a separate operation from merging desired sources. Preserve
external PowerShell profile blocks and exclude runtime/session/cache state.

A host environment declaration identifies fixed configs source, opt-in features
and explicit settings-document connections. One versioned document per unit holds
formatVersion, source (configs or host), and settings. Proposed environment.json
and settings/<unit>.json names are illustrative. No directory auto-discovery. A
host-source document must exist and validate; never fall back silently to defaults.
Source=configs restores provider defaults, not application factory state. Host
data persists across regeneration and remains host-owned across provider updates.

Each unit has enabled and optional document inputs in the host declaration.
Selected feature/enabled unit/no document uses defaults; a document selects its
source; enabled=false stops provider management without deselecting/uninstalling
the application. Feature deselection stops its management and preserves documents
and installed state. Existing inactive-data structural/active compatibility rules
remain. Arbitrary host-owned capture/extensions and future conflicts with provider
features are the host's responsibility, not extra provider compatibility gates.

Capture previews and saves host originals, not generated output or provider source.
It no longer commits/publishes/applies implicitly. For a first document, include
the new explicit connection in the preview and save operation. Capture does not
silently select a feature or re-enable a disabled setting; require the target to
be selected/enabled. Subsequent captures update connected documents. Source/target
identity checks protect pending writes; whole-unit capture does not need to infer
UI deltas from a last-applied snapshot. Schema compatibility and managed projection
validation remain necessary. Do not introduce automatic extension reconciliation.

Generation materializes only the selected dependency closure, active unit payloads
and matching tool/format information, identified by exact provider commit and host
inputs. It is not a compiler/build framework. Each active unit chooses provider or
host payload, never a default-plus-override automatic merge. Validate declaration,
connections and formats separately from target Check (observed state comparison)
and explicitly requested Apply. If host declarations or payloads change after
generation, require regeneration rather than applying stale output as current.
Recheck target-resolved paths and app availability before Apply. Captures always
target the original host documents, never modify a generated bundle.

W1 covers the declaration, explicit settings connections, source selection and
generation/Check/Apply boundary. W2 covers host capture ownership, projection,
first-connection save and removal of provider publication coupling; it depends on
W1's format. Keep tests bounded to changed behavior and affected connections; no
private installation or arbitrary extension becomes a recurring provider gate.
Concrete schema/CLI layout, multi-file initial-save failure handling and stale-input
checks need implementation fixtures. Existing enforced rules remain until their
scoped implementation amendments land. This plan provides no native execution or
Apply evidence.

## Save and generation failure boundary

Amended 2026-09-28 (latest failure discussion): AC2/AC3/AC4 use small recoverable
file operations, not a new transaction or rollback framework. First capture prepares
and validates the payload and declaration, saves the settings document first, then
adds its connection to the host declaration. Preparation or payload-save failure
leaves the declaration unchanged. Connection failure leaves a reported unconnected
document, which is inert because there is no auto-discovery. On retry inspect that
document rather than blindly overwriting it. Existing connected documents use a
single atomic replacement. Prepare all requested units before writes; report
per-unit completion/failure instead of claiming multi-file atomicity.

Generate in a temporary location, validate a complete result, and only then publish
it as the current generation. Failure preserves the previous result but does not
mark it successful/current for changed inputs; stale-input Apply requires regeneration.
First-generation failure leaves no applicable generated result. Add no generation
history/recovery service merely for this. Actual Apply spans multiple settings/apps,
is not atomic, records success/failure separately and does not automatically roll
back. Capture itself never changes actual app configuration.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC7 | Windows-native source-bound contract data and versioned inspection match actual feature/customization/generation behavior and support candidate discovery, unknown-format refusal and template checks without Nix or implicit host mutation. | review, native runtime |
| AC1 | Host-declared opt-in selection includes core and dependencies, rejects invalid input and does not adopt newly added optional features. | review, native runtime |
| AC2 | win-env.ps1 generates a version-identified local deployment configuration from fixed source and host input, and Check/Apply enforce format and target compatibility. | review, native runtime |
| AC3 | Capture transfers a selected managed unit to explicit host-owned settings that survive regeneration and provider updates without default merging; incompatible active documents are refused, and provider source, excluded runtime state and external profile blocks remain untouched. | review, native runtime |
| AC4 | Deselection stops management without implicit removal, external profile blocks survive, and Apply remains a separate authorized action. | review, native runtime |
| AC5 | The initial client verification baseline is Windows 10 IoT Enterprise LTSC 21H2 x64, build 19044, with the actual revision and application versions recorded. Terminal settings, fonts and profiles remain supported; default terminal delegation is explicitly outside this baseline's guarantee and required capability evidence. Windows 11 is outside the supported scope and required evidence matrix. Included capabilities require native evidence, and known support limits, unavailable observations and excluded capabilities are never reported as verified behavior. | review, native runtime |
| AC6 | Initial native Windows CI management checks explicitly use PowerShell 7.6.6 and record its actual version while preserving separate Windows PowerShell 5.1 entry/bootstrap coverage. | review, native runtime |
