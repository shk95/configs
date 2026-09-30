# Unix-like provider and host customization contract
kind: spec
date: 2026-09-27
scope: unixlike
status: approved
review-by: 2026-10-11
issue: #449

## Current reading order after reconciliation

Reconciled 2026-09-28: latest public-input/reader, single-flake dendritic-consumer
and minimal capture amendments supersede earlier machine/profile, per-host flake,
gitlink, baseline/delta capture and environment-matrix proposals. Provider defaults
are overridable 25.11/25.11/6; host modules own hostname and actual realization.
U1 includes the working consumer API and bounded readiness/contract tools; U2 owns
whole-unit capture and depends on those setting inputs. Native/build lanes in the
acceptance table describe applicable work evidence, not an every-edit suite.
Privately adapted hosts are one-time companion work, not public release CI inputs.
Candidate template proof can precede provider integration; required template code
delivery precedes API release, and default tag-ref follow-up is separate. Old-schema
connection probes below do not certify the unimplemented new API. Reports pending.

## Outcome

Configs implements the Unix-like part of one desired computing environment;
hosts own machine realization, selected capabilities, secrets, customization
and final integration/use validation. Coordinate governance
through `docs/work/repository/provider-release-contract/spec.md` without
introducing a Windows/Nix dependency. This is agreed design, not implemented
behavior or authorization to activate hosts.

## Contract

Keep lib.mkNixos, lib.mkDarwin and lib.mkHome as typed entry points. Promise
documented inputs/defaults, supported compositions, final output paths and
maintained extension recipes. Internal module paths/classes and arbitrary
upstream options are not a blanket stable API. systemModules/homeModules
provide host extensions under normal Nix type, merge and priority rules.
Make intended preferences overridable defaults and expose explicit payload
options; retain required composition and validation constraints.

The original state-version decision below is superseded where the 2026-09-28
amendment differs; do not implement centralization from this historical text.

Centralize NixOS system.stateVersion at 25.11; retain Home Manager 25.11 and
nix-darwin 6. Remove the normal host/template stateVersion input. Do not change
these with scheduled flake refreshes. Future baseline changes are possible but
require separate impact analysis and migration. Initial integration research
found identical toplevel derivations for all five provider NixOS fixtures and
all five private NixOS consumers; rerun after the final implementation.

Darwin capture writes host-owned desired configuration, not provider source.
Configs continues to supply default Karabiner and symbolic-hotkey payloads,
projection, validation and application tools. Expose supported payload/settings
options consumed through homeModules. Preserve one ownership projection for
check/apply/capture; exclude runtime keys. Define deletion, arrays, replacement
and merge behavior before implementation. Prefer deltas where meaningful;
whole owned payload replacement is acceptable where explicitly defined.
Do not attempt generic live-state-to-Nix reverse compilation.

The pinned public template demonstrates this contract and creates independent
hosts with their selected provider revision injected. Old generated consumers
remain compatibility test cases. Do not require template checkout to evaluate
the provider. Provider input overrides create another dependency combination
and require separate evidence.

The following original catalog is migration inventory, not the revised
provider verification matrix:

Initial support planning follows existing fixtures: x86_64 NixOS WSL,
aarch64 UTM, x86_64 VMware, aarch64 OrbStack, reviewed x86_64 AMD APU desktop,
aarch64 Darwin and standalone x86_64 WSL Home. The desktop composition is not
a claim of physical installation. Intel Darwin currently fails in pinned
nixpkgs; recommend excluding it from the initial supported contract, subject
to stage-2 support-matrix acceptance. Minimum tools remain to be selected.

## Stage-2 decision: macOS 26 baseline

Agreed 2026-09-27: begin formal Apple Silicon macOS support with macOS 26.
The initial certified lane is aarch64-darwin on macOS 26; macOS 14 and 15
are not included merely because pinned nixpkgs has a 14.0 deployment baseline.
Later OS versions require explicit validation before extending the supported
matrix. This adds AC5 without changing AC1-AC4. Exact Nix/tool pins, hosted
builder capacity and the remaining platform matrix still need review.
This support choice authorizes no host OS update or activation.

## Stage-2 decision: initial Nix verification version

Agreed 2026-09-27: use upstream Nix 2.34.8 explicitly for the initial CI
verification baseline, with nix-command and flakes enabled in that validation
environment. Record and check the actual implementation/version rather than
relying on an installer action's default. This adds AC6. It is not a minimum
version imposed on consumer hosts, an automatic host update, or a promise that
all other evaluator versions work. Later baseline updates require reviewed
verification; the installation mechanism remains implementation design.

## Environment selection and host realization amendment

Amended 2026-09-28: AC1, AC2, AC4 and AC5 adopt the maintainer-confirmed
environment-selection plus host-module structure. This replaces central NixOS
stateVersion and machine-kind-driven composition in the original plan. AC3
and AC6 retain their criteria; AC7 and AC8 add ownership and evidence boundaries.
This is a planning target, not implemented policy or publication authority.

Keep mkNixos, mkDarwin and mkHome as typed public constructors. mkNixos selects
a documented environment independently of personal machine kind/hypervisor.
Keep systemModules/homeModules for host realization and supported customization;
configs maps public selections to internal classes in one place. Private module
paths are not stable API. Reject unknown, duplicate or incompatible selections,
and document defaults/merge behavior. Exact names and supported platform coverage
remain to be finalized; linux-cli, linux-graphical and wsl-cli are design names.
This does not expand optional-profile support or the existing no-WSLg boundary.

Host modules own account/device/storage/boot/network/access realization. An
environment selection must not silently impose a personal UID, SSH port, disk
layout, hypervisor or privileged-service choice. WSL realization is host-owned;
exact NixOS-WSL dependency pin/follows wiring remains a compatibility decision
before pickup. Preserve shared-kernel protection and effective access/recovery.
Any retained provider security defaults need an explicit independently testable
contract; the precise administrative-policy split remains a design dependency.

The following ownership choice is superseded by the later provider-owned
compatibility-baseline amendment below; it is retained as design history.

Keep NixOS stateVersion explicitly host-owned and preserve existing values.
Preserve current HM/Darwin migration values during this transition; their final
input/ownership API remains a separate decision. Routine provider/input updates
do not change these values. The earlier proposed NixOS 25.11 centralization and
its equality observations do not govern or prove this revised migration.

Replacing kind/hypervisor behavior is an explicit breaking contract transition
with migration guidance and reviewed release classification. Do not silently
reinterpret old calls or promise compatibility across a declared major boundary.
Old pins remain usable as prior source; each consumer chooses adoption. Initial
migration comparisons use each actual prior pin and inputs. Provider publication
does not wait for every consumer's migration or activation.

Provider evidence uses synthetic public-constructor consumers, including valid
defaults/overrides, invalid choices and applicable builds/native behavior. Direct
class tests alone cannot prove the public API. Select builds by target/build
capability, not ability to activate a fixture. Private integration, installation
and actual-use evidence remain host-owned. AC5's consumer evidence means a
synthetic public-API consumer; macOS 26 and Nix 2.34.8 baselines remain unchanged.

Before implementation, assign every moved setting, command, dependency, test
and invariant a new owner and replacement evidence. Consumer execution plans
belong to the consumer repository; provider changes do not establish adoption.
Template updates remain independently owned and never automatically rewrite hosts.

## Provider-owned compatibility baselines

Amended 2026-09-28: AC1 replaces the earlier same-day host-owned stateVersion
choice. The maintainer confirmed that configs owns the compatibility baseline
for NixOS, Home Manager and nix-darwin, while hosts own adoption and migration
of actual persistent state. Machine realization and compatibility-baseline
ownership are separate decisions. This supersedes contrary wording above and
in the earlier constructor examples; host.stateVersion is not a required normal
input in the target API. Exact initial values and any compatibility escape hatch
remain to be reviewed; earlier 25.11/25.11/6 values are candidates, not restored
by this ownership decision alone.

Treat the three evaluator values independently; none is the configs release
version, dependency version or date of the latest host update. Ordinary flake
refreshes must not change them. Provider release records make the selected
baselines discoverable. A baseline change is separate reviewed compatibility
work: identify affected defaults/services, declared support and migration
requirements, and assign release impact from the actual contract change. Do
not assume that a major version or a successful build proves safe data migration.

Provider evidence verifies baseline selection and affected public behavior on
synthetic cases, plus supported transition cases where claimed. Hosts compare
their existing effective values and persistent state with the selected release,
including services introduced through host modules, and perform any necessary
backup, migration, validation and recovery. Initial adoption of a central value
can change defaults in either direction; it must not be described as a harmless
ownership-only move. Old pins remain an explicit option until a host is ready.
Provider publication does not wait for every private host to migrate. No claim
of universal safe migration is made for arbitrary host extensions.

## Common environment and host boundary consolidation

Amended 2026-09-28 (latest discussion): AC1, AC2, AC4, AC7 and AC8 use the
following accepted design, superseding earlier machine-shaped profiles and
WSL-only standalone proposals. This remains planning, not implementation evidence.

Configs provides the common desired Unix-like environment by default. System
and home are application layers, not the configs/host ownership boundary.
Keep mkNixos/mkDarwin/mkHome and systemModules/homeModules. Platform implementations
remain distinct where required; do not add a generic feature graph. Normal host
overrides use existing module options and overridable defaults, not routine
mkForce. Document supported adjustment points without wrapping every native option.
Enforce only genuine active-feature prerequisites, not immutable personal taste.

Application mode, graphics and WSL are separate axes. Accepted illustrative inputs
are environment.graphical and environment.wsl; exact schema still needs evaluation.
Default graphics on supported non-WSL compositions, independent of standalone;
WSL defaults graphics off and an explicit graphics+WSL conflict is rejected.
Darwin+WSL is invalid. Selecting WSL adds provider adaptations, not host realization.
An expressible combination is not automatically a verified supported combination.

Linux graphics starts as one feature (Niri, Noctalia, audio, input method, fonts
and related system/home settings); allow whole-feature opt-out and ordinary value
overrides, defer independent component switches until needed. Darwin active system
environment settings form one default unit with host overrides. Commented-out
Darwin defaults are historical notes, not active settings to migrate or connect:
the proposed Dock-selection work inferred from those comments is withdrawn.

Keep existing common CLI tools by default. Coding agents claude-code/codex become
common default tools across supported Unix-like targets; remove the WSL-only
agents profile, selection branches, fixtures and obsolete restrictions together.
Verify target package availability/builds and opt-out without duplicate ownership.
Darwin Homebrew Claude/ChatGPT GUI apps are separate host choices, not proven
duplicate CLI installations. Use native module disabling where adequate; add
feature switches only for coordinated package/config/integration removal and a
bounded exclusion path for unconfigured common packages. Preserve dependencies
still needed elsewhere and host-added declarations. Opt-out never deletes user
data or silently re-enables an excluded feature through another feature.

Homebrew brews/casks/masApps start empty; host owns app selection, Homebrew setup
and update/upgrade/cleanup policy. Configs supplies shell/PATH integration and
prepared app settings. Read the final native Homebrew selection (normalize entry
names) and conditionally apply corresponding settings; no second app selection
list, no settings-to-install feedback, no forced empty list. Unknown apps install
without provider settings. Host may opt out of settings or override them. Required
fonts/config-generation tools remain provider-owned dependencies; do not silently
add other user apps. Permissions, accounts and licenses remain host preparation.
Keep modules imported and condition their content rather than deriving imports
recursively from final config. Homebrew stays freely updatable; host may pin if
desired. Record tested app versions as evidence, not provider-imposed pins.
Every supplied app configuration needs synthetic selection and applicable behavior
coverage, regardless of private host choices; test empty/known/unknown selections
and settings-only opt-out. Review Ghostty/Karabiner and any installation-coupled
modules individually, without changing Linux ownership accidentally.

Standalone is a general application mode, not synonymous with WSL or CLI-only.
Extract general identity/home-directory/HM-tool/user-Nix setup from wslStandalone;
host supplies home directory rather than a fixed /home derivation. Shared home
retains user shell/editor/tools; integrated system handles system prerequisites.
Standalone uses the same feature choices for home generation and read-only
prerequisite checks/preparation guidance. Initial scope excludes automatic system
mutation. Configs owns required conditions/checks and reference guidance for verified
OSes; host owns actual system preparation/application. Report satisfied, missing
or unknown conditions separately from actual behavior. Check selected features only.
Graphics standalone remains an independent combination requiring its own system
preparation and runtime evidence, not categorically excluded by mode.

Provider default examples include locale preference and system editor integration;
system locale availability must be checked. Consolidate duplicated NixOS shell
registration while host owns login-shell selection/application. Keep platform
startup differences. Provider supplies appropriate flakes configuration; host owns
Nix installation/daemon choice, trusted users and GC policy. nix-ld remains NixOS
only. Machine identity/accounts/UID/sudo/SSH/ports/storage/boot/network/drivers/
hypervisor integration move with their tools, rules and safety/recovery tests.
Host owns NixOS-WSL input/version; provider uses a pinned synthetic integration
dependency for reproducible checks, without imposing that pin on all hosts.
Exact follows/adapter wiring remains open. Preserve shared-kernel protection.

Initial compatibility values are now fixed: NixOS system.stateVersion = "25.11",
Home Manager home.stateVersion = "25.11", Darwin system.stateVersion = 6.
Configs owns these independently of routine refresh; hosts own adoption and actual
persistent-state migration. Earlier statements that values remain undecided are
superseded; existing-state transition assessment remains required.

Retain existing macOS/Nix baseline decisions. Proposed standalone evidence cases
are general Linux without graphics, the same OS with graphics, and WSL adaptation.
Exact Linux OS versions/architectures/venues remain open: an Ubuntu26.04 distro
name is not verified os-release evidence, ubuntu-latest is not a fixed baseline,
and old ubuntu-24.04 venue proposals were not acceptance of OS support. Keep
evaluation/build/system readiness/native behavior distinct and no private host
availability gate. Test defaults, overrides, opt-outs, invalid combinations and
public extension contracts; arbitrary final host composition remains host-owned.

Publish a Unix-like-owned machine-readable API contract and versioned inspection
tooling as specified in the repository contract amendment. Breaking migration keeps
constructor names but does not silently reinterpret removed machine/profile inputs.
Give explicit replacement guidance; old host pins remain usable. API/schema export,
standalone checks and exact public option defaults need concrete implementation
design and scoped lane refinement before pickup.

## Refined first delivery and evidence boundary

Amended 2026-09-28 (after support/evidence discussion): this replaces the pickup
interpretation below, including U3's obsolete gitlink dependency. AC8/AC9 and
repository AC5/AC6 use contract-focused evidence; OS names are test baselines,
not certification of every machine or session.

Accepted target architecture scope: NixOS x86_64-linux/aarch64-linux; integrated
Darwin aarch64-darwin on macOS 26; standalone initially x86_64-linux; Windows is
separately governed. Standalone's first OS baseline is Ubuntu 26.04 LTS. A live
read-only homewslu probe returned Ubuntu 26.04.1 LTS, x86_64 and WSL2 kernel
6.18.33.2-microsoft-standard-WSL2. This establishes identity only, not new API,
build, readiness or runtime acceptance. Ubuntu CLI/graphical and WSL are possible
verification venues, not three mandatory per-release session tests.

U1 outcome: a synthetic external host expresses the common environment, graphics
and WSL choice, module overrides and opt-out through the public constructors;
machine realization no longer selects provider composition. Scope: unixlike.
Inputs: reviewed spec revision, fresh origin/dev at pickup, current constructors,
module classes, fixtures and domain policy. Same-scope PR carries implementation,
API metadata/relevant inspection, tests, domain policy/docs and report evidence.
Do not split schema from its working constructors or API examples from their checks
merely to create small PRs. Split only independently reviewable complete outcomes.

U1 includes common home/standalone/platform composition, default coding agents and
profile retirement; compatibility baselines 25.11/25.11/6; graphics/WSL conflict
rules; host extension behavior; and the corresponding setting/tool/test ownership
map. Darwin default-unit and host-selected Homebrew settings must either be part
of this coherent contract or a separately specified dependent complete outcome,
not silently omitted from the eventual domain acceptance.

Required evidence is selected by affected contracts: positive/negative constructor
and override fixtures, generated configuration/dependency checks, relevant target
builds and bounded provider-native behaviors only where static evidence is
insufficient. Include same-input contract/API consistency and synthetic consumers.
Do not require arbitrary host applications, hardware, login, networking or complete
desktop sessions as blanket release gates. Changes to common composition justify
broad affected-target checks; unrelated domains do not. Selected required checks
must pass on the current candidate. Unknown impact broadens within the owning domain.
Advisory observations never become new pass claims, and a discovered public-contract
defect remains blocking even if discovered by an advisory test.

Cross-repository companion T1: configs API change work owns the independent template
candidate adaptation and exact-pair checks under repository AC14. No submodule.
Private host adoption stays a separately owned consumer task and never an activation
permission or recurring provider gate. Root governance/dispatch changes are separate
repository-owned work with explicit dependencies, not smuggled into U1.

Before U1 pickup, finish concrete constructor input shape/default/override semantics,
NixOS-WSL pin/follows bridge, setting/tool/rule migration map and API export/reader
format. These are bounded remaining design tasks; U1 is not marked Ready merely by
this refinement. In particular current fixtures include 26.05/26.11 stateVersion
values: adopting 25.11 requires explicit transition analysis, not a silent claim of
behavior preservation or instructions to downgrade existing host state.

U2 Darwin capture remains separate until Unix-like capture/projection semantics
are specified; Windows merge rules are not silently adopted there. Standalone
read-only readiness tooling belongs with its explicit public contract and fixtures;
no automatic system preparation. Stop/replan for lost safety/recovery ownership,
unexpected effective outputs, broader support, unproven required build capacity,
candidate/contract drift or a proposed private-machine gate. Planner retains
continuation; no worker or execution issue assigned, no source implementation begun.

## Earlier pickup lanes (superseded where refined above)

U1: environment-selection API and machine-realization separation. Inputs:
current origin/dev, this amended spec and reviewed ownership/coverage maps.
One coherent Unix-like provider PR covers AC1/AC2/AC4/AC7/AC8 and applicable
AC5/AC6 evidence, with schema, synthetic consumers, scope-owned policy/docs,
tests and obsolete tool/dependency handling together. Root policy/dispatch
changes require a separate repository lane. Stop/replan for an unassigned safety
obligation, unexplained output change or implicit private-host release gate.

U2: host payload API and Darwin capture. Depends on explicit payload merge
and capture-output contracts. One coherent Unix-like provider PR; any root
capture-command governance change is a separately classified repository
increment. External host adoption is separate. Require projection fixtures,
evaluation/build and native read-only capture evidence. Activation remains
explicitly authorized and separately reported.

U3: public template examples and older-consumer contract checks. Coordinate
with the repository gitlink lane and stage-2 gate design. The template owns its
own PR; private adoption is not a provider release or automatic deployment.
U4: companion private-host migration, planned and owned in the consumer
repository against the reviewed provider interface. Preserve values and compare
old/new outputs; host evaluation/build/runtime and separately authorized activation
remain distinct. Provider publication does not wait for all consumers. This is
a dependency outline, not a consumer execution spec or assigned worker.

No lane is ready until the environment/platform table, ownership map, WSL
dependency wiring and required evidence are reviewed. U2 also needs payload
merge/capture semantics; U3's gitlink remains under repository review. Resolve
the three initial compatibility baselines and explicit transition rules before pickup.
The planner owns continuation; no worker or execution issue is assigned.

Amended 2026-09-28 (latest consolidation): add AC9 for contract discovery
and verification. Earlier criteria are interpreted with the latest dated
consolidation above; historical proposals do not override that amendment.

## Accepted independent-review corrections

Amended 2026-09-28 after accepted independent review: AC4/AC9 distinguish
initial adoption from ordinary updates. Provide explicit pinned-reader bootstrap
for readerless legacy hosts, inspect old declarations and propose migration, then
validate the candidate without implicit activation. Test legacy and reader-aware
updates separately. Required template code must be delivered at an agreed durable
consumer ref before release, not merely validated on an unmerged candidate.

## File-level delivery map and completion boundary

Amended 2026-09-28 (after API and transfer discussion): this makes U1's work map
concrete without claiming pickup or execution. Paths below are current source
locations, not a requirement to preserve their layout or expose internal classes.

| Source group | Disposition | Completion evidence |
| --- | --- | --- |
| modules/flake/configurations.nix, _host-contract.nix, identity.nix, module-classes.nix, fixtures.nix | Replace machine-kind/hypervisor/profile routing with public environment composition and synthetic hosts; preserve constructor names. | Constructor defaults/overrides/opt-outs, invalid combinations, explicit legacy-input migration and output paths verified through public API. |
| modules/foundation/nixos.nix, home-account.nix, state-version.nix | Separate host identity from provider baselines; generalize standalone identity/home path. | NixOS/HM 25.11 and Darwin 6 asserted; no duplicate home identity or host-name authority; transition impacts recorded. |
| modules/programs/agents.nix, foundation/packages.nix | Default common agents; remove old profile selection and duplicate installation ownership. | Supported-target evaluation/build and exclusion/dependency cases; GUI apps not mistaken for duplicate CLI tools. |
| modules/foundation/shell/*, nix/*, platforms/editor/* | Retain environment shell/Nix/editor configuration; extract common standalone support; transfer login choice, daemon/trust/GC operations to host. | Correct integrated/standalone layering, native override behavior and read-only prerequisite cases; no implicit system mutation. |
| modules/desktop/* | Keep provider graphics as one coordinated feature. | Whole-feature exclusion removes provider contributions, preserves host additions/shared dependencies, and refuses contradictory active-feature settings. |
| modules/platforms/homebrew.nix and related app modules | Empty installation defaults, host lifecycle policy, selected-app settings and provider setting dependencies. | Empty/known/unknown app selections and settings-only opt-out; every supplied configuration has applicable provider checks. |
| modules/platforms/defaults.nix, darwin.nix, foundation/firewall.nix | Retain active Darwin environment defaults; separate host identity and NixOS access policy. | Host override cases; commented defaults remain historical; no inferred Dock feature work. |
| modules/machines/*, foundation/account.nix, sshd.nix and machine parts of firewall.nix | Transfer machine realization/account/access policies with rules and tests; split generic behavior first. | Destination and revision identified; safety/recovery obligations accounted for; provider fixtures no longer certify private machine policy. |
| modules/foundation/installation.nix, flake/install-tools.nix, tool/install-plan, tool/install-vm-test, tool/checks/install-plan-test | Transfer installation implementation and applicable dependencies/tests to host ownership. | Inert/explicit installation target and storage safety preserved; no orphan provider command or input; no installation is performed by migration validation. |
| modules/platforms/wsl.nix, programs/docker.nix | Split provider WSL environment adaptations from host-owned NixOS-WSL realization, UID/mount/access and engine privileges. | Synthetic host explicitly imports host-selected NixOS-WSL; missing/conflicting integration refused; shared-kernel obligations preserved with implementation. |
| foundation/ssh.nix | Keep common SSH client configuration. | Host include/override behavior remains distinct from moved SSH server policy. |
| tool/checks/provider-api-test, flake-test, composition*, eval-coverage*, prerequisite*; flake/*runtime-test.nix | Replace machine-shaped assertions with owning-contract checks; move machine safety tests with their implementation. | Positive/negative public consumers and targeted builds; runtime only for justified provider-owned behavior, never private-machine gates. |
| Justfile and root dispatch/governance | Reconcile callers with moved tools in separately classified work where required. | No dangling commands; scope classification and affected dispatch checked; do not silently widen U1 scope. |

Prepare host-side transferable code/rules first, verify new API integration with
synthetic consumers, and remove old provider responsibility only after destination
and replacement checks are accounted for. Record source/destination revisions,
preserved/changed behavior and transferred safety checks once for this transition.
Do not embed private destination contents in public evidence. This is not permission
to edit a consumer repository or apply machines. Actual consumer adoption is a
separately authorized lane and not a recurring release gate. Ordinary provider CI
must not need private hosts access. Synthetic boot/account/storage settings are
test infrastructure, not a new supported machine-configuration product.

Accepted public-input direction: mkNixos/mkDarwin receive system, user, git,
environment and host modules; mkHome also receives homeDirectory and has no
systemModules. Output names belong to the host flake. Account creation/privileges
and host names belong to host modules. Remove mandatory host stateVersion/profiles.
Host module files receive evaluator arguments and explicit host values via normal
Nix module composition; no required file names. Host imports its NixOS-WSL module
through systemModules; configs' public nixpkgs connection is the default follows
target. Publish only that necessary dependency connection as stable, not all inputs.
Pinning the same nixpkgs does not replace integration checks.

Contract data is generated and checked into the provider source, independently
per domain. CI regenerates and compares against the source declarations plus
authored support/migration information. Readers inspect data without executing
candidate code. Record fetched commit plus contract content rather than embedding
a self-referential commit identity. Separate contract format, domain release version
and source revision. Unknown formats refuse guessing; arbitrary host module effects
require candidate evaluation. Initial tooling reports changes and examples, but
does not rewrite host source automatically or change pins/apply. Template reads the
chosen provider contract instead of copying it.

U1 is complete only when the agreed public composition works, ownership transfer is
accounted for, relevant required checks pass on the delivered candidate, API data
matches implementation, and required template adaptation is delivered/verified.
A passing document preflight or private host activation does not substitute for
these conditions. Exact export paths/format, concrete option types, fixture coverage
and source/target package availability still require implementation design. Standalone
prerequisite tooling and Darwin capture retain their explicit bounded contracts;
do not claim those finished because core composition works.

## Final independent audit and pickup limits

Reviewed 2026-09-28: no new design contradiction was found against the latest
accepted amendments; the previous five review corrections are present. This is
planning review, not implementation acceptance. Before U1 pickup, make a runnable
consumer example using the actual unixlike/flake.nix entry (no root flake): verify
the subdirectory source URL, constructor exports, public nixpkgs follows edge and
contract-data lookup together. Earlier conversational root-URL examples are
illustrative, not executable acceptance evidence. Finish concrete option types,
default/override behavior, stateVersion transition impacts and selected fixture/
build coverage. U2 capture and later Windows/controller lanes retain separate
pickup prerequisites; U1 does not complete all five work items.

## Public inputs and bounded verification consolidation

Amended 2026-09-28 (after the final audit, latest discussion): AC1/AC2/AC4/AC7/AC8/AC9
use the following concrete input direction and change-driven evidence boundary.
This supersedes earlier broader environment-matrix interpretations. These are
accepted design decisions, not runnable-consumer or implementation evidence.

Keep the entry at unixlike/flake.nix and exports lib.mkNixos, lib.mkDarwin and
lib.mkHome. The consumer source explicitly selects dir=unixlike and an immutable
release/revision. The stable dependency connection is configs/nixpkgs (configs
is the consumer's input name); a host-owned NixOS-WSL input may follow it.
Generate and check in API data at unixlike/api/contract.json, with formatVersion.
Inspection reads that file from the exact fetched repository revision without
evaluating candidate code. Actual source fetching, follows and constructor use
still need one executable consumer proof; placeholders are not proof.

| Input | mkNixos | mkDarwin | mkHome |
| --- | --- | --- | --- |
| system | Required, x86_64-linux or aarch64-linux | Required, aarch64-darwin | Required, x86_64-linux |
| user, git.name, git.email | Required strings | Required strings | Required strings |
| homeDirectory | Connect from host system account settings | Connect from host system account settings | Required absolute path |
| environment.wsl | Boolean, false by default | Boolean, true refused | Boolean, false by default |
| environment.graphical | Boolean, defaults to !wsl | Boolean, true by default | Boolean, defaults to !wsl |
| systemModules | Module list, defaults to [] | Module list, defaults to [] | Refused |
| homeModules | Module list, defaults to [] | Module list, defaults to [] | Module list, defaults to [] |

WSL architecture support remains subject to the declared integration boundary,
not every NixOS architecture automatically. Explicit graphical+WSL conflicts,
unknown fields and retired machine/profile inputs refuse with useful guidance.
Environment inputs choose composition; host modules override native defaults.
The user field identifies the recipient, not account creation or privilege policy.
Host modules own account realization, login shell and home placement; integrated
Home Manager identity/path must agree with that realization.

No hostname constructor input is added. Host system modules set networking.hostName;
configs neither supplies a personal name nor infers one from the output name.
Configs provides overridable compatibility defaults NixOS/HM 25.11 and Darwin 6.
Existing hosts may explicitly retain different values through native host modules.
Inspection reports differences without automatically changing them or recommending
numeric upgrades/downgrades. New synthetic fixtures use provider baselines; their
success never proves migration of existing persistent state. Baseline changes
remain separately reviewed from routine input refresh.

Verification units are changed functions and connection contracts, not the list
of supported environments. The seven discussed NixOS/Darwin/standalone/WSL examples
are composition examples, not a mandatory recurring suite or build matrix.
For U1, test the connections actually being changed; do not re-certify unchanged
applications and services. Later changes select only affected checks:

| Change | Necessary evidence boundary |
| --- | --- |
| Shared tool/home setting | Changed declaration or generated result in one representative composition unless platform-specific behavior differs |
| Linux graphics | Changed settings, dependencies or service wiring; no blanket desktop boot/session requirement |
| Darwin defaults | Changed final option values; native execution only when needed to establish the changed behavior |
| Homebrew app settings | Changed app selection/nonselection/override; no installation or launch of every supported app |
| Standalone preparation checks | Satisfied/missing/unknown conditions for the changed check; no blanket live Ubuntu prerequisite |
| WSL | WSL additions, selection/wiring/conflict rules or integration dependencies changed; common-home edits alone do not require separate WSL evidence |
| Constructors, pkgs or shared composition wiring | Each actually affected distinct connection; ordinary settings do not repeat the same fact through every constructor |
| API data/template | Data drift checks and affected consumer examples, not full environment builds |
| Packages/inputs | Affected evaluation and necessary builds; target-specific differences justify extra architecture cases, not full supported-environment runtime |

Reuse provider-api-test for the new public contract. Split flake-test's environment
assertions from machine/installation/recovery assertions. Retain composition,
import-order, formatting, lint and payload checks for their owned inputs. Rework
test/eval-coverage-test so build selection has no host-name/activation-eligibility
dependency and missing selected evidence cannot pass. Separate file/configuration
validation currently embedded in graphical-runtime from justified service runtime.
Existing prerequisite checks tool availability for the test runner; it is not the
new standalone system-readiness contract. Preserve relevant Karabiner setting
fixtures; capture evolution remains its separate lane.

Machine hardware/storage/boot/virtualization, account/SSH/firewall/recovery and
installation tools move with their safeguards/tests. Retire obsolete kind,
hypervisor and agents-profile assertions with their replaced contracts. Classify
each transferred item explicitly: host-owned, retained public provider feature
with bounded checks, or intentionally retired with rationale. Host transfer is the
default for current machine settings; do not retain every item as reusable provider
API. U1 requires preserved, host-connectable transferred material and removal of
provider dependencies, not private fleet adoption/boot. Any retained public feature
still needs its own applicable checks. Host repository writes remain separately
authorized; no private-host gate is introduced.

Start check selection with a small explicit changed-path/function-to-check map,
including additions/deletions and both sides of renames. Each entry explains the
failure it can detect. Mixed changes union checks. Unmapped changes request mapping
review rather than silently passing; broaden uncertain coverage within the relevant
area, not automatically every Unix-like build/runtime. If the area itself cannot
be bounded, resolve classification before promotion. Preserve full master-to-candidate
comparison, current-candidate evidence and positive/negative selection tests.
Evidence lane applicability must be declared before execution with reasons; these
criteria do not require a native run for every edit. Never waive a failed selected
check or call an unselected check passed. Current policy/enforcement must be amended
in implementation; this plan does not disable existing gates.

## Contract reader, host extensions and implementation check map

Amended 2026-09-28 (subsequent reader discussion): AC1/AC2/AC4/AC7/AC8/AC9
use the following minimal reader and host-extension design. This refines, rather
than expands, the preceding change-driven evidence boundary.

Contract data contains formatVersion, domain, entryPoints (constructor paths and
input types/requirements/defaults), constraints (supported combinations),
compatibilityDefaults and changes (host-facing API migration). Do not introduce
a when/then/else expression language: publish constructor-specific defaults and
the finite supported selection cases. Actual constructors enforce validity;
the reader does not duplicate the Nix evaluator or external modules' schemas.
Generate from actual declarations where possible and check authored support and
migration metadata for consistency. No embedded self-referential commit identity,
duplicated release version or CI execution results: the reader reports the exact
fetched commit/selected release and links separate evidence.

The repository-relative contract location is unixlike/api/contract.json. When
using the dir=unixlike flake, configs.outPath already ends in /unixlike, so its
relative location is api/contract.json. Pre-execution inspection uses the fetched
repository tree, not candidate evaluation merely to discover this path.

Migration entries describe changed/removed input names/types/requirements,
default changes with preservation guidance, and removed supported combinations.
They do not duplicate ordinary package-update or internal-refactoring release
notes. Give each transition a stable identifier and before/after contract
conditions. Retain necessary transitions within the maintained major so skipped
releases remain understandable; major boundaries have explicit transition guidance.

Host comparison is optional and needs no arbitrary Nix source parser. A template
can bind one attribute set of explicit constructor inputs, use it for construction,
and expose the same values with constructor identity and module-presence flags
through a host-owned declaration output (name not yet public API). Preserve omitted
fields: do not fill provider defaults before exporting, or explicit selection and
default-following become indistinguishable. Do not serialize modules, their internal
hostname/secrets configuration or runtime values. Any evaluation to obtain that
declaration uses the current trusted pinned host, not a substituted candidate.
Fetching and parsing candidate contract data remains separate from later candidate
evaluation. Without a host declaration, general contract comparison still works.

Report declared-input compatibility, required host edits and candidate-evaluation
needs separately; they may coexist. Omitted fields receive default-change guidance,
explicit still-supported values remain selected, and arbitrary module overrides
remain unknown until evaluation. Declarative compatibility never means safe actual
adoption. Initial tooling does not rewrite files, update pins or Apply/activate.

Sops+age belongs to the host. Existing systemModules/homeModules admit host-owned
external secret modules; add no mandatory sops-nix flake input or dedicated secrets
constructor API. Only add a setting-specific runtime file/reference extension when
existing native options cannot express it. Never read decrypted values during Nix
evaluation into generated store files. Host owns encrypted payloads, key placement,
permissions, decryption/service ordering and actual use verification. Public contract
data contains only provider extension semantics, not host secret inventories/keys.
Provider checks use synthetic references only when that extension changes; private
decryption is never a provider release gate. Reference implementation guidance:
https://github.com/Mic92/sops-nix/blob/master/README.md . No integration was run.

Initial implementation mapping, selected for changes rather than run unconditionally:

| Changed function | Checks |
| --- | --- |
| Constructor inputs/defaults | Accepted/refused inputs, defaults and native overrides |
| System/home connection | Changed constructor's module and user connection |
| Individual program settings | Changed generated settings and necessary dependencies |
| Graphics/WSL selection | Changed inclusion/exclusion/conflict behavior |
| Contract data/reader | Generated-data agreement, comparison results, unknown-format refusal |
| Machine transfer | One-time transfer completeness and remaining provider dependencies |

Use explicit file mappings where sufficient; a file spanning functions selects
their union. No changed-line semantic analyzer is required. Transfer evidence is
one-time redesign evidence, not a recurring private-host migration check. Existing
CI classification policy remains until implementation adopts these changes.

StateVersion transition checks cover supplied defaults, preservation of explicit
host values and migration guidance for retired host.stateVersion constructor input.
The limited pinned-source investigation in report.md found no enabled member of
the inspected 26.05/26.11 service/ZFS branches in the affected synthetic fixtures.
Do not add unrelated database/mail/filesystem runtime gates for that observation;
it is not exhaustive equivalence or permission to lower a real host's value.

## Single-flake dendritic consumers and delivery boundary

Amended 2026-09-28 (latest consumer-structure discussion): AC2/AC4/AC7/AC9
use a single consumer flake/lock producing multiple host outputs, replacing the
earlier per-host flake recommendation. The host companion and public template use
flake-parts/import-tree with concern-oriented top-level modules. They share a
pattern with configs, not its private module classes or composition authority.
Consumer code calls only public constructors and passes native host modules.

One host file keeps its constructor, output identity, explicit inputs, selected
system/home modules and machine-specific settings understandable together. Extract
shared account/secrets concerns only for actual reuse; system.nix/home.nix are no
longer a prescribed layout. Automatic module discovery defines available fragments,
not automatic activation on every host. Each host explicitly selects its fragments.
Keep encrypted payloads/keys outside the auto-imported Nix module source boundary.

A small consumer-owned connection module derives both final configurations and
optional comparison declarations from the same host inputs. A declaration such as
hosts.example = { constructor = "mkNixos"; inputs = { ... }; systemModules = [ ... ];
homeModules = [ ... ]; } is illustrative, not a new provider API. The connector
validates its own structure/constructor choice and prevents ambiguous duplicate
output definitions, but does not duplicate configs' input types/defaults/support
rules. Preserve omitted provider inputs. Pass modules to the constructor without
serializing their contents in the comparison output. Output identifiers do not
set networking.hostName. Standalone still has no systemModules constructor input.

Use one common set of configs/sops-nix/NixOS-WSL inputs where selected by the host
repository. Transition directly to the common lock; do not pre-create old-version
inputs or compatibility paths for each host. Resolve concrete evaluation/build
problems when found; any exception needs actual justification. Input unification
affects future calculations, not simultaneous deployment. Building, applying and
recovering hosts remain individually selected. Actual key delivery is not necessary
to complete the structure transition. Sops remains optional and host-owned.

U1's coherent Unix-like provider PR includes the new constructors/composition,
common tools, graphics/WSL selection, Darwin defaults/Homebrew selection integration,
ownership migration, generated contract/minimal comparison tooling, standalone
read-only readiness, applicable tests and scope-owned documentation. Deliver an
actually consumable result, not a schema awaiting its working implementation.
Darwin capture, Windows changes and live release automation remain separate.

Companion sequence: preserve transferable host code/safeguards; prepare U1 and a
single-flake host/template candidate against its exact revision; evaluate each
host output for this one-time cross-cutting connection change and build only where
the changed behavior requires it; resolve failures; deliver U1 and required template
code, then align references with the delivered/released source. This host exercise
is one-time migration evidence, never a recurring provider CI/private-host gate.
Private source is not copied into public evidence. Root CI/dispatch policy changes
remain a separate repository PR; order compatible prerequisites before U1 and
new-structure dependents after it without an unchecked integration interval.
Actual host adoption/activation remains separately authorized. No external work
has been implemented or assigned by accepting this plan.

## Darwin capture by explicit ownership transfer

Amended 2026-09-28 (latest Darwin capture discussion): AC3 replaces the earlier
delta preference with whole capture-unit ownership transfer. This supersedes the
proposed Darwin last-applied-baseline/diff/automatic-merge design. It does not
change the separate Windows capture contract.

Configs declares capture units and their managed projection. Initially use the
two existing payload concerns: Karabiner (explicit setting keys and profiles)
and macOS input-source symbolic hotkeys (explicit entry numbers). Units may be
captured separately or together. Capture takes the complete supported projection
of the selected unit, even values equal to provider defaults, and assigns its
desired state to the host. The provider's default payload for that unit is then
excluded; it is not merged underneath the captured data. Application installation
and unrelated units remain independent. App-added fields do not silently expand
the projection, and runtime/unmanaged state is excluded and preserved on apply.

Use one JSON document per unit containing formatVersion, source and settings.
The illustrative initial envelope is { "formatVersion": 1, "source": "host",
"settings": { ... } }. Source is explicitly host or configs. Host uses its
validated settings; configs uses provider defaults. Retained settings when source
is configs are dormant recovery data, not applied. File existence or an empty
object/array never selects ownership. A selected host source with absent/invalid
data fails instead of falling back to defaults. A host dendritic module explicitly
connects each data file; capture edits data, not Nix code or provider payloads.
Returning to defaults changes source explicitly and may preserve captured data.

Configs owns the capture/consumer format version and validation rules for only
the structure it reads/writes, with tested app versions and known incompatible
formats. Do not mirror the app's entire schema or pin freely updated Homebrew
apps. An app version change alone does not mean incompatibility. Unsupported
structure or known incompatibility refuses the affected operation. Unknown envelope
formats refuse guessing; explicit format transitions preserve the original and
present a conversion proposal. Host-owned content is never replaced by updated
provider defaults as an implicit schema migration.

Capture has preview and save stages. Preview reads selected units, projects and
validates them, then shows captured content and ownership changes. Save updates
the host documents only, with no app write, commit, push or automatic Apply.
Read/validation failure leaves declarations unchanged. Recheck source and target
changes since preview; changed data requires renewed preview. Prepare/validate all
requested units before saving. Each document is replaced atomically, coupling its
ownership selector and payload; multiple files are not an atomic transaction.
On a partial write report completed and incomplete units explicitly. Do not build
a cross-file transaction/recovery service for this initial capture feature.

No last-applied snapshot is needed to infer manual edits: capture is explicit
adoption of observed projected state, not an automatic merge. Host-owned profiles
arrays are complete values, without automatic rule identity matching. Exact
managed-key deletion/reset semantics and concrete module options/command wiring
remain implementation pickup details to settle before U2 is ready.

Verify projection boundaries, allowed/refused shapes, ownership selection/default
return, valid empty values, invalid-host-data refusal and write-failure reporting
with synthetic file fixtures. Check that regenerated/apply inputs consume the host
document instead of hard-coded provider payloads. Native read evidence is needed
when the actual macOS reader changes; schema-only changes do not require broad
native app testing. Build evidence is limited to changed generated tool/config
artifacts. The existing root capture-to-provider-commit entry needs a separate
repository-owned change; private host wiring is separately owned. No actual app
capture or mutation was performed during this discussion.

## Minimal capture surface and host extension responsibility

Amended 2026-09-28 (latest capture boundary discussion): AC3 requires only the
provider's own capture contract, not compatibility with arbitrary host extensions.
This supersedes any reading of earlier projection/extension discussion that would
require a general host field registry, application-wide schema, plugin discovery,
extension conflict detection or automatic reconciliation in configs.

For each provided unit expose a default-behavior enable/disable control and an
optional settings document. When enabled without a document, use provider defaults;
with a document, honor its explicit source. Disabling the behavior stops the
provider's apply operation for that unit and lets the host use its own modules or
tools. Application selection/settings opt-out still governs default enablement.
Host source using the provided format/tool is distinct from disabling provider
management entirely. No exact public option spelling is fixed by this paragraph.

The provider declares only the fields necessary for its default feature. Hosts
can build their own additional settings, checks and capture/apply tools through
normal module extension or replacement. They need not register those implementations
with configs. Hosts resolve breakage/overlap with future provider features themselves
when adopting updates. Such private extension compatibility is outside provider
validation and release gates; the promised public extension inputs still work.
Do not promise preservation or reconciliation of arbitrary nested host additions
inside a provider-owned whole-replacement unit. Preserve state outside its explicit
managed boundary; unsupported structures within that boundary follow its own
bounded refusal/validation rules, not a universal host-extension contract.

Within a managed unit, required-key absence is invalid; optional-key absence means
that key is absent in the desired result, never filled from provider defaults.
Arrays/objects may be empty only when the supported app format permits it. Null
is an application value, not a generic deletion marker. Managed scope is defined
independently of the keys currently present in the payload, so removed optional
keys do not silently leave previously managed state behind. Array replacement is
whole-value, not a rule-identity merge. For symbolic hotkeys, disabling uses the
explicit enabled=false setting; entry deletion or OS-default reset is supported
only when its meaning and adapter are defined, otherwise refuse it. Returning to
source=configs restores provider defaults, not application factory defaults.

Configs supplies a versioned tool; the host calls its currently pinned version
with an explicit unit and destination host document. No cwd-based repository guess
or default write path into provider source. Missing/ambiguous save destinations
refuse writing. The command's work ends at preview/save; Git publication and actual
application are separate. Replace the root capture-to-provider-commit coupling in
a separately scoped governance change. A host using its own capture need not call
the provider tool. Packaging/export name and exact CLI/options remain ordinary
implementation choices to check against this bounded contract, not reasons to add
another extension framework.

## U1 native override and finite inspection repair pickup

Amended 2026-09-30 after technical review of the delivered U1 source: the
continuation in issue #434 repairs AC2/AC8/AC9 and adds AC1 Darwin explicit
stateVersion coverage. Preserve existing default values, supported combinations
and the public API schema. Ordinary native Darwin preference overrides must
replace provider defaults without routine mkForce. Contract inspection must not
report a forbidden Darwin/WSL declaration as compatible; use the existing finite
constraint/default metadata and preserve module-content privacy and the separate
candidate-evaluation-needed result.

Add bounded fixtures for current constructor metadata versus actual typed inputs,
requirements, defaults and constraints; default preservation and native overrides;
and graphics opt-out preserving host additions/shared dependencies while refusing
active-feature contradictions. No new public module-list default metadata, generic
schema/expression engine, broad constructor refactor or new builder is required.
Run focused regression first, then final-source native Mac evaluation/build and
the selected native Linux CI lanes. Keep prior delivered provider and companion
references as their original evidence; companion repinning is a separately
coordinated adoption. AC3/U2, whole-parent completion, API release and activation
remain separate. Existing AC1/AC4/AC5/AC7 evidence may be recorded as qualified
verified only to the extent its required lanes are actually met.

## U2 implementation pickup

Amended 2026-09-30: AC3's two ownership-transfer units are made concrete below.
The criterion and its review/evaluation/build/native-runtime lanes are unchanged.
This is the U2 pickup plan, not an implemented command or native capture result.
The implementation worker pins its then-current origin/dev independently of the
reviewed revision of this amendment. Issue #449 assigns continuation to C; the
repository entry retirement and private consumer adoption are separate lanes.

### Public inputs and one ownership declaration

Add Home Manager options under `providerDarwin.capture`:

| Unit | Options | Owned settings |
| --- | --- | --- |
| `karabiner` | `karabiner.enable`, `karabiner.settingsDocument` | Required `global` object and required nonempty `profiles` array of objects, each taken whole |
| `symbolic-hotkeys` | `symbolicHotkeys.enable`, `symbolicHotkeys.settingsDocument` | Required `AppleSymbolicHotKeys` object containing exactly entries `60` and `61`, each taken whole |

Both enable options are booleans, default true. Effective management retains the
existing final `karabiner-elements` selection and `providerDarwin.appSettings.enable`
and `.karabiner` gates, then applies the individual unit's enable switch. Turning
either unit off stops its provider apply operation without changing app selection
or the other unit. Disabled units do not load settings documents. The optional
document is a nullable Nix path connected explicitly by a consumer `homeModules`
definition; null uses provider defaults. These are public options, not imports of
provider-internal classes, a new constructor, or discovery of private files.

One versioned unit contract supplies the finite supported scope, required shape
and validators to check, apply, capture and module consumption. Do not add a
parallel ignored-key list or extension registry. Karabiner's unmanaged top-level
siblings and symbolic hotkey entries other than 60/61 remain outside this scope.
App-added top-level members never widen it. A missing required parent/entry is
invalid, not default inheritance. Optional nested members disappear through whole
parent replacement; arrays have no identity merge. Arbitrary extensions remain
host responsibility as in the preceding amendment.

Documents use exactly `formatVersion`, `source`, and `settings`; version 1 has
integer `formatVersion: 1` and `source: "host"` or `"configs"`. Require a JSON
object for settings; validate its unit shape when source is host. Configs source
uses the provider unit and retains dormant settings without applying or merging
them. Unsupported envelope fields/versions, duplicate keys, malformed UTF-8/JSON,
invalid source and invalid active host settings refuse. Never infer ownership from
existence, an empty value or a previous applied snapshot.

The initial supported Karabiner projection refuses absent/empty profiles:
upstream v16.3.0 replaces an empty array with a default profile, so emptiness is
not a stable all-profiles deletion instruction. Empty global/nested collections
are accepted only for shapes the tested app supports, with positive and refusal
fixtures; this plan does not certify them. Null is not a deletion marker. For
symbolic hotkeys require boolean enabled and the supported value object/standard
parameter shape; enabled=false disables an entry. Missing entries, null deletion,
OS-default reset and a factory-reset command refuse. Source=configs returns to
provider defaults rather than application factory defaults.

### Versioned command and explicit destination

Export the pinned Unix-like app/package `darwin-capture`, implemented in
`unixlike/tool/` and using the same unit contract. Proposed operator spelling:

```text
nix run 'github:shk95/configs/<full-commit>?dir=unixlike#darwin-capture' -- preview --unit karabiner --document <host-document> --output <preview-file>
nix run 'github:shk95/configs/<same-full-commit>?dir=unixlike#darwin-capture' -- save --preview <preview-file>
```

Repeat the paired unit/document options to request both units; duplicates,
unknown units, mismatched pairs and ambiguous targets refuse. Read overrides
`--host` and `--hotkeys-host` provide synthetic JSON inputs for fixtures. Native
reads otherwise use the current Karabiner file and read-only defaults export /
plutil conversion. No source-root mutation, Nix-code edit, app write, Git operation
or Apply occurs in either capture command. Save neither selects/enables units nor
creates a consumer connection: the host explicitly supplies that module/path.
First save may create an explicitly chosen absent document with source=host;
connection/evaluation remains the consumer's separate action. Root helpers are
not called. Commands/options here become available only after implementation.

Preview prepares every requested unit before presenting complete projected data
and ownership changes. Its explicitly requested output is a private, versioned
proposal, not last-applied state; use mode 600 and keep it outside provider source,
app files and host originals. Bind tool/unit-contract identity, selected readers,
observed input content and target existence/content/identity. Save validates the
proposal schema and tool binding, rereads current inputs/targets and recomputes
the projection; stale identity or inconsistent proposed data refuses rather than
recapturing silently. This is consistency checking of caller-reviewed input, not
authentication of its author or protection against rewriting an entire coherent
proposal. Self-described hashes provide no signature or external trust. Review
the selected units/destinations when invoking Save; no signing infrastructure is
required. A changed runtime sibling can invalidate input identity even though it
never enters the saved projection.

Reject app targets, provider/store/generated paths, symlink/hardlink destinations,
aliased unit targets and incompatible prospective parents. Recheck path/parent
identity and all prepared inputs before the first write, and the relevant target
again before each replacement. Use a private temporary file beside each document
and atomic same-directory replacement; no cross-file atomicity is claimed. A
later failure reports completed, unchanged, refused and incomplete units honestly;
preserve completed documents and leave remaining originals unchanged. Retrying
requires another explicit preview of the actual current state, not rollback or
an overwrite bypass. Missing readers yield unavailable evidence, not empty data.

### Delivery, proof and stop conditions

One Unix-like implementation PR carries the unit contract, typed module inputs,
packaged command, focused fixtures, affected Unix-like docs and report evidence.
It includes a dated reconciliation of the projection decision/invariant: preserve
their single ownership declaration and historical #177/#178 proof, add proved
host-document-tool enforcement and test finite scope independently of current
settings presence. Retain legacy project enforcement tags/fixture locators until
their actual caller retirement is coordinated; never declare them already moved
or orphan them. Do not silently adopt this plan as durable policy.

The additive command can coexist with separately invoked legacy capture because
it neither calls nor redirects to the commit helper. Preserve the existing tool's
`project` flags and exact `=== karabiner ===` / `=== symbolic-hotkeys ===` section
protocol until the repository caller is retired. Test actual caller compatibility,
not just the new CLI: `tool/version-control/commit` capture and its fixtures still
consume that protocol. Keep enforcement live throughout the transition.

The repository owner separately retires `tool/version-control/commit` capture,
its `tool/version-control/test` cases and root README/CONTRIBUTING instructions
after the versioned CLI is delivered. `Justfile` is Unix-like-owned: the U2
implementation owner owns its legacy karabiner-capture recipe and domain recipes,
not the repository lane. It may retain the compatible legacy recipe until the
caller retirement or refuse the legacy publication route with actual new CLI
guidance; it must not silently redirect a publish command to original Save.
Any newly added transitional adapter owes the provisional registry contract.
If project/caller compatibility cannot be retained, first prepare a separately
reviewed fail-closed repository retirement and integrate that prerequisite before
changing the protocol; new root usage waits for actual CLI delivery. Do not leave
an unverified interval or bypass the root fixtures. Private consumer document
connections/adoption are not made implicitly by either provider PR.

| Evidence | Required U2 result |
| --- | --- |
| review | Inspect final finite scope, deletion/reset refusals, default/disabled behavior, field compatibility and caller separation; preserve prior evidence's original SHA |
| evaluation | An independent synthetic mkDarwin consumer uses homeModules/document paths; check defaults, per-unit disable, both sources, invalid host documents, whole replacements and sibling preservation without a template checkout |
| build | Build the changed packaged command and affected synthetic Darwin configuration natively on aarch64-darwin/macOS 26 with upstream Nix 2.34.8; record actual source and selected outputs |
| native runtime | Final-source native macOS reader/adapter observations and parser/version identity, plus synthetic preview/save/stale/failure/roundtrip fixtures; mock readers and foreign fixtures remain supplementary |

Fixtures cover both units separately/together, valid/default-equivalent capture,
source toggling/dormant recovery, disabled read/write exclusion, finite scope and
runtime preservation, valid/refused empties, whole arrays, invalid format/data,
absent first destination, stale input/target/tool, prepare-all-before-write, atomic
single-file failures and truthful partial saves. Regeneration must consume the
saved host document rather than hard-coded defaults. Actual original writes,
activation, app restarts or installations require separate explicit authorization;
temporary synthetic saves do not supply that permission or deployment evidence.

Installed app version alone is not a support verdict. Source review of v16.3.0
found that the current provider's ask_for_confirmation_before_quitting=false
member is removed by that app; check_for_updates=false already has the current
spelling. The study records exact references. At source pickup, compare shapes and
tested native parser behavior. A behavior-equivalent compatibility correction may
be proposed inside U2, but a changed preference/support guarantee, uncertain
deletion meaning, destructive migration, runtime discovered inside an owned
parent, incompatible app shape or unsafe legacy coexistence returns to planning.
Do not pin Homebrew apps, automatically migrate host documents, normalize away
unsupported originals or claim compatibility merely from JSON parsing. API
release, parent completion and private deployment remain independent outcomes.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC9 | Source-bound Unix-like API metadata and versioned inspection match actual constructors, support current-to-candidate discovery, and provide feature-aware read-only standalone prerequisite checks with explicit unknown results; template and independent consumers verify the contract without implicit system mutation. | review, evaluation, build, native runtime |
| AC1 | Configs defines discoverable NixOS/Home Manager/nix-darwin compatibility baselines, keeps them independent of routine input refresh, and supplies reviewed impact and migration requirements for changes; hosts retain adoption and actual-state migration responsibility, with initial value transitions assessed explicitly and no private migration prerequisite for provider publication. | review, evaluation, build |
| AC2 | Typed public environment selection is independent of personal machine kind/hypervisor; system/home extensions distinguish defaults, supported customization and constraints, with positive/negative public-constructor cases and no stable internal-class API. | review, evaluation |
| AC3 | Darwin capture targets host-owned desired data and regeneration uses it while preserving projection and excluding runtime state. | review, evaluation, build, native runtime |
| AC4 | Synthetic external consumers exercise the public contract without template checkout; older-consumer baselines establish explicit compatibility and migration boundaries without requiring private adoption for publication or promising compatibility across a declared major boundary. | review, evaluation, build |
| AC5 | The initial certified Apple Silicon Darwin lane targets macOS 26 with explicit tools and provider/synthetic-public-consumer evaluation and native build evidence; private-host operation and older or later OS support are not inferred. | review, evaluation, build |
| AC6 | Initial Unix-like CI verification explicitly uses upstream Nix 2.34.8 and records the actual implementation/version, with evaluation and native builds under that baseline rather than installer defaults. | review, evaluation, build |
| AC7 | Personal machine realization is removed from automatic provider selection with an explicit setting/tool/dependency/rule-to-owner migration map that preserves safety and recovery obligations and distinguishes separate host adoption. | review, evaluation, build |
| AC8 | Reviewed provider evidence covers public constructor/default/override/refusal behavior and applicable build/native environment behavior using independent synthetic realization; build selection is separate from activation eligibility and private installation/use is not a recurring release prerequisite. | review, evaluation, build, native runtime |
