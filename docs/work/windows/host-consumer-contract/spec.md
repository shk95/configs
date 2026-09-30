# Windows host-owned configuration and capture
kind: spec
date: 2026-09-27
scope: windows
status: approved
issue: #427
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

Stop/replan for a provider compatibility promise for arbitrary host extensions,
unrequested uninstall/restore, cross-platform generation, implicit publication
or remote credential changes. Arbitrary host extensions themselves remain
host-owned under the later whole-unit amendment.
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

## W1 pickup preparation and W2 dependency

Amended 2026-09-30: AC1/AC2/AC4/AC5/AC6/AC7 are clarified for W1 pickup;
AC3 remains the dependent W2 capture outcome. This section allocates existing
obligations without changing the acceptance table or accepting a new schema,
support policy or CLI. Read it with the whole-unit and failure amendments above.
Planning delivery, W1 implementation, W2 implementation and Windows release
readiness remain separate results.

W1 produces one Windows-owned host-input/generation contract and its native
implementation. It can be planned and implemented independently of U1, Unix-like
provider delivery, Nix, personal host activation and the repository release
controller. It consumes Windows source at a fixed commit. A later promotion or
release reader may consume its contract; that reader is not a prerequisite for
local generation. Repository CI wiring, release-controller behavior and shared
repository procedures remain separately owned dependencies when actually needed.

Before assigning implementation, the planner resolves or records the following
design boundaries against the latest Windows source. Routine implementation
details inside these accepted boundaries remain the assigned worker's choice.

| Preparation | Required reviewable result before pickup |
| --- | --- |
| Versioned inputs and connections | A concrete declaration/settings-document shape, supported format versions, unit identities and explicit path/connection rules; unknown formats and malformed connections have named refusal behavior. Illustrative filenames above are not an existing public interface. |
| Existing-host migration | An explicit preview/export route for current state-schema selections and host settings, with no automatic declaration write, source update or Apply. First-use opt-in and recorded legacy selections must be distinguished. |
| Settings ownership | A unit inventory identifies provider settings, host-only WSL VM policy and personal layout/workspace data; names what leaves provider management and how preserved host data is connected. Empty provider payloads cannot reset personal data. Ownership transfer is not implicit capture or host adoption. |
| Target support | Identify where the accepted LTSC terminal-delegation exclusion is expressed without waiving unrelated drift or unavailable observations. Any needed change to currently accepted decisions/invariants follows their owning scope; the existing gate is not bypassed. |
| Verification runtime | Identify the Windows-owned version check/fixture for PowerShell 7.6.6 and separate 5.1 entry/bootstrap coverage. If changing hosted CI wiring is necessary, assign that repository change separately and name its dependency. |

The W1 worker receives an explicit lane assignment and approved Git publication
scope, one new dedicated Windows worktree/feature branch from the then-current
origin/dev, and the reviewed plan commit pinned separately. The planning branch
is not the implementation branch. Re-query open issues/PRs and record one
continuation owner in the execution issue before implementation; no issue or
branch is implicitly created by this plan. A plan revision not yet published
must be published before handoff to another worker. Use one Windows PR for the
coherent implementation and its report evidence, with the following boundaries.

| Existing criterion | W1 delivery and required evidence |
| --- | --- |
| AC1 | Native fixtures cover core-only/empty selection, selected dependency closure, unknown names and new optional features staying unselected. Current features and actual interaction cases define bounded coverage. |
| AC2 | Native fixtures and CLI observations cover fixed provider/input/format identity, explicit connections, provider-versus-host whole-unit selection, regeneration, complete temporary output publication, failed first/repeated generation and refusal of changed/stale inputs. Check is read-only; Apply entry refuses incompatible input before any write. |
| AC4 | Native fixtures cover feature deselection and enabled=false without uninstall/reset, document retention and reselection validation, plus external profile blocks. An Apply invocation is not authorized by this work assignment. |
| AC5 | Review and applicable read-only native client checks name the actual LTSC build/revision, application versions, selection and capability states. Hosted Windows Server fixtures do not certify client-only behavior; excluded delegation remains visibly excluded. |
| AC6 | Native management evidence names and checks actual PowerShell 7.6.6, with separate native Windows PowerShell 5.1 entry/bootstrap coverage. A hosted-image default is not the promised version check. |
| AC7 | Review and native fixtures cover source-bound inspection, supported/unknown format versions, explicit template/example connections and consistency between published contract data and generation behavior, without Nix or host mutation. |

W1 leaves capture implementation and AC3 pending. W1 coverage of source
selection does not prove capture projection or first-save behavior. For each
criterion, record the actual verified part and the pending dependent work;
verify a whole report row only when every required lane and obligation is met.

Ready requires Required checks and the selected native Windows job at the
final W1 head, after any required base update or repair. Cite the exact head/run,
actual runtime version, counts and unavailable client evidence separately.
The earlier #422 fixture result proves that repair at its own head, not W1.
Foreign-host parsing or fixtures remain supplementary; document preflight is
neither Windows native acceptance nor release evidence. Existing client inventory
is historical planning input and must be refreshed for candidate-specific claims.

W2 waits for W1's implementation/format to enter dev because native stacks are
not supported. Its pickup pins then-current origin/dev and the W1 contract
revision, with a separate owner/worktree/Windows PR. W2 consumes the supported
unit identity, explicit connection, source and validation contract; it owns
observed projection, host-original preview/save, first-document connection,
recoverable per-file failures and removal of implicit provider publication.
It must neither write generated bundles nor silently enable/select a target.
Schema changes needed by W2 return to planning and W1 ownership rather than
being invented as a second incompatible document format.

Stop/replan if preparation leaves substantive schema, support, compatibility
or migration decisions unresolved, if the implementation needs a new cross-scope
dependency, or if native evidence cannot meet the accepted delivery boundary.
Preserve unfinished work and checkpoint before owner or role changes. Separate
release readiness still owes all remaining criteria and the repository evidence
contract; W1 Ready alone does not complete this report.

## W1 implementation pickup, 2026-09-30

Amended 2026-09-30: AC1/AC2/AC4/AC5/AC6/AC7 use the following minimum
Windows implementation design. AC3 remains the separate W2 capture outcome.
This dated pickup resolves serialization, connection and ownership preparation
inside the accepted whole-unit direction; it does not weaken the acceptance
table or accept unverified native behavior. Exact runtime CI wiring belongs
to a separately assigned repository prerequisite. Native LTSC client evidence
remains a separate outstanding observation, never replaced with Server results.
Issue #427 assigns one Windows continuation owner to W1; W2 remains unassigned.
Windows runtime declaration #430 is delivered separately; repository execution
issue #431 owns consuming CI wiring and actual-version evidence.
The execution base and reviewed plan revision are pinned at pickup rather than
frozen by this spec. Actual Apply is permitted only inside isolated fixtures
for this implementation assignment; no real-host Apply is authorized.

### Outcome and ownership

One Windows implementation PR supplies the versioned host declarations, explicit
settings connections, deterministic local generation and its Check/Apply guards.
Use a new then-current-dev Windows worktree; do not implement in the #423 planning
branch. W1 does not depend on U1/Nix, consumer activation or the release controller.
W2 capture/save waits for this format to enter dev. The main orchestrator remains
planner; implementation continuation owner is assigned at actual pickup.

### Initial data formats

`environment.json` is UTF-8 JSON, formatVersion 1, with exactly these root fields:

```json
{
  "formatVersion": 1,
  "provider": { "commit": "<full 40-character configs commit>" },
  "features": ["terminal"],
  "units": {
    "windowsTerminal": {
      "enabled": true,
      "document": "settings/windows-terminal.json"
    }
  }
}
```

For an existing unit, omitted entry means enabled with provider defaults when its
feature is selected. `enabled` is a JSON boolean; `document` is optional. Core and
feature dependency closure are added, not inferred from runtime state. Empty
features selects core only. New optional features remain unselected.

Unit identity is the existing case-sensitive `ManagedFiles.Id`; no unit-ID field is
duplicated in the document. Each connected path is explicit, relative to the
host declaration directory and normalized before use. No directory scan, absolute
connection, traversal outside that directory or symlink escape. Reject duplicate
connections to the same resolved document: one settings document owns one unit.
Public examples use synthetic relative paths; real host documents stay external.

A settings document has exactly `formatVersion`, `source` and `settings`:

```json
{ "formatVersion": 1, "source": "configs", "settings": null }
```

or a host source, with a JSON object for Json units and an exact string for
PowerShell/Lua/Kdl/Ini/Text units:

```json
{
  "formatVersion": 1,
  "source": "host",
  "settings": { "theme": "light", "profiles": { "list": [] } }
}
```

The host example is only a format sketch, not valid Windows Terminal content.
A real example must satisfy that unit's complete supported projection, including
profile structure. Source=configs requires settings=null so host content is never
silently ignored. Source=host requires a present correctly typed payload and has
no automatic default merge. Arrays are whole owned values; no deletion language.

Reject unknown format versions, duplicate JSON keys, unknown root/entry fields,
wrong scalar types, non-full provider commits, duplicate selected feature names,
unknown active features/units, missing connected files and unsupported active
payloads. Inactive documents still undergo structural validation; current unit/app
compatibility is checked on reselection. Unknown retired unit identities are allowed
only explicitly disabled, so they cannot accidentally become active. Host extensions
outside this supported catalog stay host responsibility.

### CLI and acquisition

Add Windows-owned `inspect`, `generate` and `export-selection` verbs. Existing
`check`/`apply` accept an explicit generated configuration. Initial transport is an
explicit local configs clone: `-SourceRoot` must resolve the requested full commit,
and its tracked Windows source/tools must agree with that commit. No implicit
clone, fetch, branch update, source bump or credential use. Packaged transport is
later work; do not claim support for arbitrary extracted trees without provenance.

- `inspect -SourceRoot <clone>` emits source-bound formatVersion 1 contract JSON:
  exact provider commit, supported host/document/generation formats, feature
  closure data, unit identities/parsers/comparison/source ownership, supported
  client baseline and excluded capabilities. No host input is required.
- `generate -Environment <file> -SourceRoot <clone> -Output <directory>` validates
  source and originals, prepares selected payloads plus matching native tools in
  a sibling temporary directory, parses the complete result, then publishes it.
- `check -Generation <directory>` performs generation/input integrity validation
  before read-only target observation. Reject selector flags in generated mode:
  environment.json is selection authority.
- `apply -Generation <directory>` uses the same guards before the first host write.
  A worker assignment is not permission to invoke it on an actual host.

The generated directory contains generation.json, a compatible desired manifest,
only active unit payloads and exact matching Windows native scripts/module. Retain
feature catalog metadata as needed by the existing manifest loader, while selection
is explicit in generation.json; copying catalog metadata adopts no extra feature.
No Nix, compiler, generation-history service or rollback engine. Existing source
validation helpers and native reconciliation functions are reused with explicit
generated-root context instead of having Git metadata inferred from a generated tree.
Capture in a generated tree is refused: capture targets host originals, not output.

Generation metadata identifies provider commit, format/tool identity, exact original
input file identities/hashes, selected closure, active units/source choice and the
complete generated payload/tool hash. Preserve original paths solely as local input
bindings. Recompute integrity and input hashes before Check/Apply; changed documents,
declaration, tools or payload require regeneration. Source revision is reported from
metadata, never guessed from a generated tree's parent checkout.

Failed first generation yields no applicable result. Failure during regeneration
leaves the previous directory intact but refuses it as current for changed inputs.
Prepare/validate before publish; use an individual atomic current-manifest replacement
or equivalent small recoverable directory operation, with exact failure fixtures.
There is no automatic selection write, app change or Apply during generation.

### Desired source versus unmanaged application state

Current `Set-WinEnvManagedFile` copies the complete payload even for JsonSubset;
that implementation cannot be reused unchanged to promise unmanaged-key preservation.
W1's writer updates only the chosen unit's owned projection on the app target,
retaining unowned object keys. Arrays owned by that projection replace as whole lists.
This is target-state preservation, not merging configs defaults into host settings.
Fixtures distinguish these two operations explicitly. Whole-file modes retain their
whole-unit semantics, while supported generated/runtime profile entries are preserved
where the unit's comparison contract already excludes them. Refuse malformed input
that prevents safe projection rather than overwriting it by guesswork.

If powershellProfile.enabled=false, skip its related hook check/write as well as the
payload; core still installs/selects the required management package. Do not delete
an existing hook or profile. Enabled hooks preserve foreign blocks and refuse unpaired
markers. Deselection/disabled units leave installed apps and host documents untouched.

Apply outcome records identify the generated result and successful/partial-failed
attempt independently of capture. Extend the runtime state contract deliberately,
with unknown-version refusal and supported old-state readers; do not reinterpret an
old success record as success for the current generation. A partial operation reports
what completed and keeps no false current-success record. Mocked failure fixtures
exercise this without authorizing real Apply. W2 whole-unit capture does not depend
on reconstructing UI deltas from an applied snapshot.

### Legacy selection preview/export

`export-selection -State <file> -SourceRoot <clone>` writes a proposal to stdout only:
exact observed old selection, its provenance, proposed declaration and unresolved
migration actions. It does not overwrite source, runtime state or host originals.

Schema 2 uses the exact recorded features; do not substitute all current features.
Schema 1 requires the manifest at recorded state.gitCommit to reconstruct its former
full selection. If that exact source is unavailable, refuse the inference and report
that input requirement. With no state, propose []/core only. Malformed state is a
failure rather than a first-use default. Removed/unknown selections are explicit
blockers: export may describe them, but a blocked proposal cannot be generated or
silently lose the host's previous intent. No mandatory account/hostname fields.

### Specific unit ownership and LTSC handling

- Retire wslConfig and its only owning feature wsl from provider-managed offerings.
  The .wslconfig file, networking/resource policy, application/check obligations and
  old host tuning stay untouched and become host responsibilities. Migration reports
  old wsl selection as requiring explicit declaration correction and a host-owned
  management arrangement; no automatic uninstall, WSL restart or firewall write.
- Remove provider management/default payloads for fancyZonesCustomLayouts and
  fancyZonesLayoutHotkeys: both currently ship empty lists that can reset personal
  data. Retain the machine-independent generic fancyZonesDefaultLayouts provider
  default; a connected whole-unit host document can replace it. General FancyZones
  settings and Workspaces/settings.json hotkey/sort preferences remain provider units.
- workspaces.json and applied-layouts.json remain excluded runtime/session data.
  They are not the general Workspaces/settings.json unit and are not capture inputs.
- Keep Windows Terminal feature/packages/fonts/profiles. In the new generated
  contract, default terminal delegation is explicitly excluded from the LTSC build
  19044 guarantee. Do not query/write its registry as an included managed setting,
  count it as verified or turn unrelated drift/unavailability into success. Show an
  `excluded` capability record distinct from supported, drifted and unavailable.
  Existing legacy observations remain historical; reconcile affected Windows decision,
  invariant, status and fixture declarations in the implementation's own scope.
- Source-only legacy capture remains distinct until W2; refuse legacy provider capture
  against a new host-generation runtime context instead of silently publishing personal
  settings. This guard does not certify W2 capture, save or publication removal.

### Exact runtime and repository dependency

Windows-owned verification data declares the initial management verification version
7.6.6 and separate 5.1 entry/bootstrap coverage, without imposing a minimum consumer
management version or installing software on a maintainer host. A narrow repository
CI increment consumes that declaration and runs the Windows job under an exact
verified 7.6.6 runtime; default hosted pwsh is not enough. Keep the version selector's
semantics in Windows and workflow dispatch/setup in repository. Assign/land this
prerequisite or establish an equivalent native CI run at the final W1 candidate.
The existing #422 320/0/1 result and any foreign-host run are not W1 native proof.

### Acceptance/evidence and stop boundary

| Existing criterion | W1 proof and pending boundary |
| --- | --- |
| AC1 | Native tests: core-only, terminal closure(core/font/zellij), wezterm/font closure, each offered feature, new optional feature not adopted, unknown/duplicate selection refusal. |
| AC2 | Native generation/CLI tests: exact source/tool/format, explicit connection, configs versus host payload, stale originals/output/tools, parser failures, first/repeated generation failure, target-dependent recheck and pre-write Apply refusal. Runtime success/partial-failure records have mocked engine tests. |
| AC4 | Native tests: unit disable/feature deselection retains documents/apps, inactive structure/reselection compatibility, no uninstall/reset, no disabled profile-hook write, foreign-block preservation and unmanaged target-state projection. |
| AC5 | Reviewed contract exposes LTSC x64 build19044 and excluded delegation. Read-only native client checks record actual build/revision/application versions/selection and applicable unchanged versus changed capabilities. Hosted Server fixture success never substitutes for client-only behavior. |
| AC6 | Exact final-head native CI records actual PowerShell7.6.6 and separate inbox5.1 parser/entry/bootstrap tests. Requires the separately owned runtime selector/wiring evidence. |
| AC7 | Native source-bound inspect/template tests match actual features/units/versions; unknown formats/refused active documents and older consumer fixture cases remain visible. No Nix, host mutation or directory discovery. |
| AC3 | Remains pending for W2. W1 source-selection tests do not prove observed capture projection, first-connection save or recoverable multi-file capture. |

Final W1 Ready requires its exact head's Required checks and native Windows job after
all repairs/base updates. Record partial criterion evidence without prematurely
verifying an entire report row. Separate native client gaps and remaining W2/release
controller obligations. No actual Apply, activation, release, merge or cleanup.

Stop/replan only for a real new support/compatibility promise, destructive migration,
unsafely unpreservable host values, cross-scope dependency lacking an assigned owner,
or required evidence that cannot be supplied. Routine serialization/CLI/internal
implementation choices above stay within accepted direction. No new maintainer
tradeoff is presently unresolved; inspect actual legacy values during authorized
migration preview before claiming that an existing host has a safe proposal.

### Read-only upstream/runtime availability check, 2026-09-30

Official release and tag APIs plus the release page confirm PowerShell v7.6.6 is
published, non-draft and non-prerelease, published_at 2026-09-08T20:28:01Z:
https://github.com/PowerShell/PowerShell/releases/tag/v7.6.6
Windows x64 ZIP and MSI are available. Official ZIP SHA256:
02FE458BE20493FBDF43F61EA20610B811EE6C738AB1676C61B9CFCD1A33C860.
The repository CI lane can use the hash-verified portable ZIP and assert the actual
version in a fresh child process, without installation on a maintainer host.

No live LTSC client connection was checked during this source-read/design task.
The study's prior SSH inventory(build19044.7725/PowerShell7.6.6) remains historical
input. Before candidate-specific AC5 claims, the orchestrator must identify the
available client observation route and authorize its read-only final-head generation,
Check and capability inventory. Lack of that route is an external-evidence requirement,
not permission to substitute hosted Server fixtures or actual Apply. No minimum host
runtime or support-guarantee change is inferred from release artifact availability.

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
