# Provider release planning and new-session handoff
kind: study
date: 2026-09-27
scope: repository
status: open

## Current handoff: resume here, 2026-09-28

### Latest five-work reconciliation checkpoint

2026-09-28: parent reviewed all five specs/reports after the consumer/capture/PAT
simplifications. No sub-agent was spawned. Added current-reading summaries, repaired
scheduled-refresh's stale App requirement/design deferral and tied its current
05/06/07 schedule to the shared controller. Clarified that the refresh tool can
implement independently while final input wiring follows U1 ownership changes.
Historical proposals remain clearly subordinate to latest amendments.

The repository spec now has "Cross-work pickup and evidence reconciliation" with
the owning-work/dependency table. Candidate template proof, provider PR integration
and delivered template readiness before API release are separate: no circular need
for an unpublished tag, no private-host recurring CI gate. Preserve changed-function
verification and per-domain capture ownership; never reintroduce arbitrary host
extension compatibility or baseline/delta merging. Operational action-needed run
failure is distinct from candidate Required checks.

Remaining work is implementation planning/pickup and evidence, not an unresolved
product direction: concrete trusted master entry retaining old-batch rules, wakeup
after validation, serialized requests/remote writes, timeout/permission/race fixtures,
and actual notification/manual-cycle evidence. Do not mark a lane Ready or provision
anything merely from accepted design. Exact field/CLI names can be chosen during
scoped implementation; any scope/acceptance change returns to planning. No worker
or execution issue is assigned. Source, host state and remote Git settings remain
unchanged; reports all pending. Continue from this checkpoint, not older "next"
paragraphs below.

### Latest controller operating consolidation

2026-09-28: accepted latest spec section "Controller execution and remote-write
simplification" supersedes earlier unresolved/stronger claims. One fine-grained
PAT now includes Actions write for automatic cancellation of only the recorded
owning run/attempt. Timeout begins cancellation, never takeover; confirm termination
and reconcile external effects. No heartbeat or extra scheduler. Known validation/
retry waits are normal, and 07:00 never automatically cancels input refresh.

Master is the observed default branch and controller entry. Restrict secret-bearing
Environment to master and pin controller semantics per batch. Schedule/approval/
resume requests share one record writer; cancellation is read/cancel-only before
write ownership. Operating history/state commit together against the read head,
with non-forced ref update and remote reconciliation after unknown responses.

Master currently has Required checks and strict=false (partial read-only protection
inspection recorded in report). Keep strict=false and head-guard PR merge, recheck
base before it and verify parents/tree afterward. There is no atomic expected-base
guard: an unexpected source merge may occur, but it must not be released. Stop and
notify rather than auto-revert. Single-path manual/automatic promotion is accepted.

Use Actions failed-run notifications only, with distinct failure/action/approval
reason summaries and no Issues-write permission. Suppress deliberate repeats of a
recorded identical blocker; GitHub delivery/duplication and unavailable-record-store
limits remain explicit. Verify real notification receipt at manual rollout. Retry
5/15/30 in PAT-free wait jobs in the same workflow; short controller jobs resume
afterward and reconcile first. Runner wait cost is accepted over new infrastructure.

This completes the discussed controller direction, not its implementation or live
readiness. Next consolidate the remaining implementation lanes/evidence and review
for contradictions introduced by the later simplifications; no automatic new agent
review or source implementation is authorized. Preserve pending report rows. All
work remains local planning plus read-only probes, without Git publication or host
mutation. Earlier sections below are historical when superseded here.

### Latest controller authentication and approval decision

2026-09-28: begin with one dedicated fine-grained PAT, not a GitHub App or per-task
minted tokens. Selected repos are configs/private operations/template, not private
hosts; token permissions are common across the selected repos. Initial Contents/PR
write and Checks/status/Actions read are proposed, subject to actual endpoint needs.
No administration/protection bypass or speculative extra permissions. PAT replacement
is manual. One controller-only Environment holds PAT/locator; routine daily runs do
not require its human approval. Exact allowed-ref/workflow boundary still needs
implementation proof; candidate jobs receive no operational credential/private data.

Exceptional approval uses one manual workflow with exact candidate ID, authorized
actor and frozen candidate/version/impact binding recorded privately; it does not
merge. Controller revalidates before writes. Approval recording must respect the
single-writer protocol. No App/token/environment provisioning or external action
has occurred. Source/remote protections have not been re-audited in this discussion.

Windows save/generation failure semantics are also consolidated: payload before
first connection, inert unconnected leftovers reported, atomic single-file updates,
temporary validated generation and preserved-but-stale prior result. Apply partial
results remain explicit with no automatic rollback. No Windows execution occurred.

Next controller design: concrete trusted-entry ref and remote mutation protocol,
including merge-time candidate protection, serialized approval/record writes,
termination-confirmed takeover (Actions read cannot cancel) and minimal action-only
notification delivery. Avoid reintroducing Apps or unnecessary infrastructure.

### Latest Windows ownership and generation decision

2026-09-28: maintainer explicitly adopted the simplified whole-unit capture model
for Windows too. This supersedes earlier Windows delta-merge and capture baseline
requirements, not Apply outcome/partial-failure records. Keep per-domain formats
and tooling independent. ManagedFiles entries are starting units; provider default
or host payload is chosen, never automatically merged. Preserve unmanaged state
and external profile blocks when applying. Host extensions and future collisions
remain host responsibility, outside provider compatibility/release guarantees.

Windows remains opt-in with core/dependencies. Host declaration carries explicit
settings connections; each unit has enabled and optional document inputs. Versioned
documents carry source/settings. Disabled management does not remove the app/data.
Capture saves host originals and first-use connections after preview, never quietly
enables a feature/setting, commits, publishes or applies. Generation records exact
provider/host inputs and materializes selected active payloads. Changed inputs require
regeneration; target paths/availability are rechecked before explicit Apply. The
latest Windows spec/report owns details and evidence; source inspection only.

Next: settle the small remaining Windows save/generation failure semantics before
W1/W2 pickup, then return to controller credentials/remote-write implementation
design. Native evidence and implementation remain pending. No external repository,
branch, release, app state or host configuration was changed.

### Latest minimal capture boundary

2026-09-28: maintainer explicitly excludes arbitrary host capture-extension
compatibility, including future overlap with provider capture features. Hosts
resolve their own extensions; configs guarantees only its own bounded defaults,
schemas/tools and public extension inputs. Do not add host field registration,
plugin discovery, automatic conflict handling or an application-wide schema.

Each provider capture unit has a behavior switch and optional settings document.
Enabled/no document uses provider defaults; document source chooses provider or
host data; disabled means the host may use entirely separate management. The host
calls the pinned provider tool with explicit unit/destination. Capture never guesses
a provider-source write destination or includes commit/push/apply. Managed optional
key omission removes that key; required omission fails, null is not deletion,
arrays replace, hotkey disable is explicit and unsupported reset semantics refuse.
Provider defaults return is not app factory reset. Details are in the latest
Unix-like spec amendment, with reports pending and no implementation performed.

U2's semantic design can now proceed to implementation planning without introducing
a generic extension framework. Concrete option/CLI/export names are implementation
details. Next discussion may address the remaining independent Windows or release
controller lane; do not carry Darwin's revised model into Windows without an
explicit decision. Source implementation and external mutations have not started.

### Latest Darwin capture ownership decision

2026-09-28: U2 now uses whole-unit ownership transfer. Capture a declared Karabiner
or symbolic-hotkey projection into host JSON and explicitly select source=host;
exclude the provider default for that unit. No automatic delta merging or Darwin
last-applied baseline infrastructure. Return to source=configs explicitly; preserve
dormant data if desired. This change does not supersede Windows capture semantics.

One versioned JSON envelope per unit couples source and settings; host dendritic
modules explicitly import the data. Capture previews, validates and saves data,
never rewrites Nix, provider source, commits/pushes or applies. Prepare all requested
units before writing, replace each file atomically and report any partial multi-file
write honestly. Schema support covers managed structure, not the whole application;
no default Homebrew version pin or implicit host-data migration. See latest Unix-like
spec/report amendment for the full accepted boundary and pending evidence.

Next: settle missing/removed managed keys, array replacement and reset semantics
for host-owned payloads, then concrete U2 module/command wiring. Do not reopen the
accepted ownership model or add a state-diff engine. Current source still applies
provider files and root capture writes provider payloads; nothing implemented yet.

### Latest single-flake consumer decision

2026-09-28: maintainer accepted one root flake/lock for configs-hosts and the
public template, with multiple outputs and dendritic concern modules. Transition
directly to common inputs and resolve actual problems; no proactive host-by-host
old-version exceptions. Keep per-host build/apply/recovery independent. Inspection
confirmed the existing hosts tree still contains seven separate flakes/locks;
none was changed. Template and host adoption remain separately owned work.

Each host declaration selects public constructor, explicit inputs and native
system/home modules. A small consumer-owned connector derives final outputs and
optional comparison data without duplicating provider schema or exporting module
contents. Output identity does not supply hostname. Auto-import discovers modules
but does not enable every concern on every host. Shared accounts/secrets are
extracted only where useful. configs internal module classes stay private; Windows
remains independent of Nix. The latest owning specs record scope and delivery order.

U1 now explicitly includes working composition, defaults/Homebrew integration,
contract generation/minimal reader, standalone readiness and relevant ownership
transfer/checks in one coherent provider PR. Separate host/template and repository
dispatch PRs have coordinated dependencies. Exact candidate-pair proof and one-time
host connection checks do not create a recurring private-host gate. No worker is
assigned, no implementation begun, reports pending. Next planning step: close any
remaining pickup-level decisions or move to later capture/Windows/controller design;
source implementation requires a clear implementation request. Do not reopen the
settled consumer topology or expand verification into a platform matrix.

### Latest reader and bounded evaluation checkpoint

2026-09-28: Unix-like spec/report now record minimal contract fields and migration
entries, optional same-declaration host comparison, host-owned sops+age extension
boundaries, the initial changed-function check map and limited actual evaluations.
No conditional-expression language or sops-specific mandatory provider input is
added. Keep explicit host inputs separate from filled defaults; host module contents
are not serialized. Current trusted-host declaration evaluation is separate from
candidate-data inspection and later candidate evaluation. Generic contract comparison
works without host declaration adoption. No automatic rewriting/pinning/applying.

A temporary external consumer of exact existing source e11bd136 verified the
subdirectory URL, current constructor exports, configs/nixpkgs follows equality and
selected module/identity values. configs.outPath already points at unixlike, whereas
sourceInfo.outPath is the source root. The proposed contract file is still absent;
new constructors are unimplemented. This is limited old-API evaluation, not complete
new-API proof, build or runtime evidence. See the Unix-like report for exact scope.
The pinned stateVersion investigation found the inspected 26.05/26.11 service/ZFS
branches inactive in the affected synthetic fixtures; no private migration or
exhaustive output equivalence was established. Preserve host overrides.

Next: review implementation pickup dependencies and the smallest coherent U1
delivery boundary against this accepted design. Exact new-API consumer checks and
contract generation/reader proof are implementation deliverables, not reasons to
reopen the design or simulate their success. Do not begin source or external-host
implementation merely from this handoff. Later capture/Windows/controller design
remains separate; all reports remain pending. Continue batching documentation.

### Post-audit API and verification refinement

Latest maintainer agreement, 2026-09-28, supersedes conflicting earlier pickup
notes below. Unix-like spec now records concrete constructor inputs, existing
lib exports, dir=unixlike source selection, configs/nixpkgs follows and proposed
checked-in unixlike/api/contract.json formatVersion transport. No hostname argument:
host modules set networking.hostName. Provider stateVersion defaults are 25.11,
25.11 and 6; existing hosts can retain explicit native overrides without automatic
numeric migration. Exact runnable consumer proof and transition analysis remain
pending; this is not a completed implementation.

Verification was deliberately narrowed again: support combinations are examples,
not a mandatory seven-environment suite. Check changed functions/settings and
distinct connections only; common edits alone do not need WSL evidence. Runtime
needs a concrete behavior that cheaper checks cannot establish. Initial selection
uses an explicit small mapping, unions mixed changes, and requires review for
unmapped impact; the old automatic whole-domain fallback is superseded. Unresolved
selection blocks promotion. Full master-to-candidate delta and exact-candidate
evidence remain. See latest amendments in the Unix-like and repository specs.

The source review classified existing checks and found activation/hostname-based
build selection and mixed graphical file/runtime checks to rework. Machine safety
tests move with their code; current prerequisite is test-tool availability, not
standalone system readiness. Host transfer must preserve usable material and remove
provider coupling; actual private-machine adoption remains separate. No source,
host, Git publication or enforced policy was changed. Reports remain pending.

Next: turn the accepted source/constructor/contract connection into a bounded
executable synthetic consumer proof, then resolve concrete transition effects and
the changed-function check map. Keep later capture/Windows/controller lanes separate.

### Final independent review closeout

Latest checkpoint after the full independent audit, 2026-09-28: accepted design
can close this discussion round. No new direction conflict or additional blocking
design defect was found in the five work items under their latest amendments.
Previous five review corrections were confirmed. This is document/source review,
not evaluation, build, native runtime, activation, Apply or live rollout evidence.
Reports remain pending; no implementation lane is assigned or declared Ready.

Next work, without reopening accepted decisions:
1. Make the first runnable public-consumer contract explicit: actual flake entry
   is unixlike/flake.nix (there is no root flake), so source URL, constructor exports,
   public nixpkgs follows edge and contract-data lookup must be tested together.
2. Finish U1 option types/default/override semantics, explicit stateVersion
   transition analysis and bounded required fixture/build coverage. The file-level
   migration map and completion boundary are in the Unix-like spec.
3. Keep later Darwin capture, Windows serialization/projection and controller
   credentials/remote-write protocol as separate lane prerequisites. Do not equate
   U1 delivery with completion of the five-work redesign or live enablement.

The parent synchronized stale acceptance-table times to 05:00/06:00/07:00 and
clarified independent-template AC3 and superseded gitlink navigation. Historical
sections remain for provenance. No new policy or test environment was imposed by
the audit. Continue batching documentation at meaningful boundaries.

This is the compaction handoff requested by the maintainer. Read this summary,
then the latest dated sections and AC1-AC14 in the adjacent spec. Earlier entries
below retain discussion history and are superseded where they conflict. Do not
restart accepted decisions or infer implementation from their acceptance.

### Accepted state at compaction

- configs is one computing environment with independently released Unix-like
  and Windows implementations. NixOS/Darwin/HM/features have no extra series.
  Hosts own machine realization, adoption, actual integration/use and recovery.
- Keep public constructors and host module extension inputs; select environment
  independently of personal machine kind/hypervisor. Transfer machine settings,
  their tools/tests/rules together with explicit ownership. Provider verification
  uses synthetic public consumers and applicable build/native environment checks;
  private-machine availability or adoption is never a recurring release gate.
- configs owns the separate NixOS/HM/Darwin stateVersion compatibility baselines;
  hosts own adoption and persistent-state migration. Initial values are NixOS/HM
  25.11 and Darwin 6. Earlier host-owned stateVersion examples are historical.
- Daily KST sequence: 05:00 input refresh, 06:00 promotion opportunity, 07:00
  cutoff for waiting on ongoing refresh. Failure/no-op/approval-waiting refresh
  does not block ready dev. No automatic cancellation at cutoff. Compatible
  patch refreshes may be integrated by the designated controller after checks.
- Keep dev open; changed candidates require fresh necessary checks and renewed
  exact-candidate approval where required. Caches are allowed, prior-revision
  pass results are not. Automatic patch/minor promotion/publication; major,
  explicit data migration and control-permission/gate/approval/classification
  changes require approval. New control rules apply only to later batches.
- One batch at a time, repeated triggers reconcile/join it. Compare promotion
  against master and cumulative effective domain impact against each last tag;
  one strongest-impact bump per changed domain, explicit reverts, no empty tag.
  Source-only docs/governance promotion is allowed.
- Freeze publication source/versions/payload after promotion. Preserve successful
  tags; retry missing publication only. Exact existing identity means complete;
  conflicting identity stops, never overwrites or chooses another version.
  Publication recovery precedes the next promotion. No local workspace is needed.
- Transient failures: up to three extra attempts after successive 5/15/30-minute
  waits, then one action alert. Validation/configuration/permission/conflict errors
  need action, not blind retry. Alert only failures/action needs; suppress success,
  no-op and routine progress alerts, deduplicate unchanged causes.
- Release transport is immutable annotated domain tags, not GitHub Releases or
  mandatory packages/machine files. Include source, previous release, cumulative
  changes, compatibility/migration, supported/verified scope, evidence references
  and Unix-like baselines. Public evidence suffices for consuming a release.
- Execution remains in public configs. A separate private operating repository
  holds configuration, append-only batch history and a reconstructible current
  index. Public code knows schema/connection contract; CI settings/secrets supply
  locator/authentication. Private settings cannot bypass public control rules.
- Pin operating configuration and control revision for a batch; configuration
  edits affect later batches. Live emergency stop and credential revocation are
  exceptions. No credentials/private-host configuration in operating Git history.
- Trusted privileged control is isolated from candidate execution. Serialize
  writers, check remote revisions and fence superseded/stopped runs; re-read on
  conflicts. Do not assume Actions concurrency alone supplies this protocol.
- Emergency stop prevents new merges/tags, preserves completed operations and
  pending records, and allows read-only work to finish. Clearing stop requires
  explicit resume. Already accepted API writes may complete; reconcile them.
- Missing private storage blocks new writes; unknown remote responses remain
  unknown until reconciled. Old public releases remain consumable. Protect Git
  history; separate backup infrastructure is excluded. Total loss means manual
  recovery, not guaranteed reconstruction of unpublished plans from public tags.
- Automations are opt-in: disabled/unconfigured is quiet normal use; enabled
  with missing/invalid connection/configuration stops and requests action.
  Ordinary CI/development/consumption does not require the private repository.
- Keep private operating context in that repository's short README: purpose,
  layout, access roles/settings locations without secrets, failure diagnosis,
  stop/resume and manual recovery. Link public policy instead of duplicating it.
- Roll out via read-only preview, explicitly authorized manual cycle, then
  separately authorized daily enablement. Fixtures prove failures, not live rollout.

### Later continuation, 2026-09-28

The latest accepted daily times are 05:00 refresh, 06:00 promotion and fixed
07:00 wait cutoff, all Asia/Seoul, superseding earlier times in this document.
The spec's "Later operating agreement" records the accepted minimal records,
termination-confirmed takeover, checked owner/generation, candidate identity
(dev/base/tree), approval binding (including versions/impact), merge-result
verification, delayed/missed-run behavior and positive/negative failure fixtures.
Unknown termination or external outcomes block new writes; generation alone does
not fence remote API calls. Detect missed runs when execution returns; no separate
watchdog or immediate total-outage alert guarantee. These are planning decisions.

Historical next-step note (superseded by the latest consolidation below):
return to minimal Unix-like/Windows support and provider evidence coverage,
initial stateVersions, WSL wiring, administration defaults, Windows ownership and
template gitlink. Then translate accepted control contracts into concrete schema,
API protection, approval mechanism and delivery lanes. Earlier unresolved points
below now concern implementation mechanisms rather than reopening those contracts.

### Latest environment and API consolidation, 2026-09-28

Read the latest consolidation sections in the Unix-like and Windows companion
specs, and "Domain contracts and coordinated template delivery" in the repository
spec. These supersede earlier profiles, standalone limits and template gitlink.

- Unix-like common CLI and coding agents default on. System/home are application
  layers; both provider and host own settings in each. Keep native module override
  inputs, use overridable defaults, and enforce only active-feature prerequisites.
- mkNixos/mkDarwin/mkHome choose application mode. Graphics and WSL are independent
  choices (illustrative environment.graphical/environment.wsl). Standalone is not
  WSL-only or CLI-only. WSL excludes GUI; explicit conflicts and Darwin+WSL refuse.
- Linux graphics is one feature initially; whole opt-out, native value overrides,
  finer switches only when needed. Darwin active system settings are one default
  unit. Commented defaults remain notes: the inferred Dock work is withdrawn.
- Homebrew installation lists start empty and host owns lifecycle policy. Native
  final app selection activates prepared settings, with settings opt-out/overrides;
  all provider settings require synthetic verification even if no private host
  selects them. Provider supplies setting dependencies, not hidden extra user apps.
  Homebrew remains freely updatable; tested versions are evidence, not imposed pins.
- Machine accounts/UID/SSH/network/storage/drivers/hypervisor/Nix trust/GC move
  with relevant tools/rules/safety tests. Host owns NixOS-WSL inputs; provider pins
  a synthetic test integration, with exact follows wiring still unresolved.
- Standalone shares home settings and exposes read-only selected-feature system
  checks/preparation guidance. Host performs actual preparation. Distinguish ready,
  missing and unknown from runtime proof; automatic system mutation is excluded.
- Windows remains opt-in (core plus selected dependencies). Move .wslconfig
  operating policy and personal layouts/workspaces to hosts. Objects merge by key;
  arrays replace; deletion differs from null. Capture against applied source,
  preserving explicit overrides even equal to defaults. Deselection retains data
  and dormant overrides; compatibility checks return on reselection. No implicit Apply.
- Configs owns versioned per-domain API data/tools; template is a thin independent
  consumer, not the API authority or mandatory submodule. Current host tools read
  candidate data before candidate execution, refuse unknown formats, then candidate
  validation follows explicit migration. Contract/API drift fails verification.
- API change work owns required template adaptation and exact candidate-pair proof
  before release. Post-release default-ref updates retry independently, coalesce to
  latest compatible release and never regress refs or alter existing host pins.
- Template follows Unix-like defaults, Windows core opt-in and empty Homebrew;
  requests only necessary host fields. Synthetic examples do not imply ready-to-apply
  machine configurations. Independent provider consumers remain required.

New criteria: Unix-like AC9, Windows AC7, repository AC14; all reports pending.
First standalone cases: general Linux CLI, same OS graphical, WSL CLI. Exact OS
versions/architectures/venues still need verification. Ubuntu26.04 is only an
observed distro name in old records, not verified OS-version evidence. Existing
macOS/Windows/tool baselines remain planning decisions, not fresh live evidence.

### Latest support and delivery refinement, 2026-09-28

The subsequent live homewslu read established Ubuntu 26.04.1 LTS x86_64,
WSL2 kernel 6.18.33.2-microsoft-standard-WSL2. The maintainer selected Ubuntu
26.04 LTS x86_64 as first standalone baseline. Earlier unknown-OS notes are now
historical. Identity is not new composition or runtime acceptance. Accepted target
scope: NixOS x86_64/aarch64 Linux, Darwin aarch64 macOS 26, standalone x86_64 Linux,
and the separate existing Windows LTSC x64 baseline.

Release guarantees are deliberately bounded to provider contracts. Use affected
evaluation/configuration/dependency/build checks and only justified provider-native
behavior, not mandatory full CLI+graphics+WSL sessions or private machines. Required
and advisory checks are predeclared; actual public-contract defects always matter.
Selection is tested, unioned for mixed changes, and conservatively broadened only
within affected domains for unknown impact. No cross-candidate passes. Record
excluded-as-unaffected distinctly from passed and unavailable. Infrastructure errors
do not waive gates. Same-source promotion still waits for all affected required gates.

The Unix-like spec's "Refined first delivery and evidence boundary" supersedes
old lane descriptions. U1 covers working public composition/overrides/opt-outs,
agents/defaults and ownership migration with API/template candidate proof. Remaining
pickup design: exact constructor schema, WSL follows bridge, owner migration map,
API export/reader format and targeted build/native evidence. Existing fixtures with
26.05/26.11 need explicit stateVersion transition analysis against selected 25.11.
Windows proceeds as independent scoped work; release automation follows contracts.
No implementation or worker assignment has started. Remote heads remain e11bd136
and 2542d77c; no open PRs at this read, no protection re-audit.

### Independent review accepted, 2026-09-28

Five corrections are accepted in the latest owning-spec amendments: 07:00 ends
waiting only; pre-promotion integration updates this candidate; select checks from
the full master-to-candidate delta; capture requires applied generation/host/target
baseline and initially refuses ambiguity/partial Apply; required template code must
be delivered before release (only default tag-ref update is nonblocking); readerless
legacy hosts need explicit pinned-reader bootstrap. Review was read-only.
Next settle constructor input shape, then WSL wiring and API transport.

### Latest file-level delivery preparation, 2026-09-28

Unix-like spec now has "File-level delivery map and completion boundary": current
module/tool/test groups, disposition, evidence and preservation-before-removal order.
Transfer source/destination and safety evidence is one-time migration proof; actual
host adoption is separate and provider CI never depends on private hosts. Synthetic
machine scaffolding is only test infrastructure. Public inputs use system/user/git,
environment and host modules; mkHome adds homeDirectory. Output names/account creation
stay host-owned. NixOS-WSL is host-imported, with the provider nixpkgs connection
explicitly public for follows; actual composition still needs checks.

API data is generated and committed with source, regeneration checked in CI; source
identity comes from fetched revision, separate from format and release versions.
Readers inspect data before candidate execution; first tooling provides comparisons
and migration examples, no automatic source rewriting/pin update/apply. Remaining
work is concrete option/schema/transport and evidence mechanics, not reopening this
accepted shape. No worker, Git publication, migration or source implementation began.

### Remaining work (mechanisms and evidence, not reopening accepted direction)

1. Specify concrete operating-record schema and remote writer/fencing protocol,
   including crash windows before/after merge, partial tags and index updates.
2. Resolve exact dev/master/tested-merge evidence binding, approval identity and
   conditional gate implementation; do not infer that a job approval proves a SHA.
3. Select private repository identity and actual GitHub App/key/environment/ref
   restrictions with a live account/protection audit before provisioning. No such
   repository is named or created yet; its README is a requirement, not delivered.
4. Verify exact supported OS/architecture combinations and available build/runtime
   venues, including standalone graphics. Finalize public schema/default semantics,
   WSL dependency wiring and setting/tool/test migration map. Initial stateVersions
   and independent template direction are settled above, not open questions.
5. Specify API data transport/export and old-tool format transition, host override
   encoding, template integration mechanics and delayed-run/failure fixtures.
   Refine coherent scope-owned delivery lanes; old R2 gitlink lane is superseded.
   No worker or execution issue is assigned. Continue planning before implementation.

### Workspace and evidence limits

Continue in configs-flake-refresh-plan, detached at
e11bd1368d2f5138ad0f9b7017040b2b76e055e6. Preserve its five untracked planning
directories: repository/provider-release-contract, repository/scheduled-flake-refresh,
unixlike/provider-consumer-contract, unixlike/automatic-flake-refresh and
windows/host-consumer-contract under docs/work/. Nothing is committed or pushed.
The private operating repository does not yet exist as a selected task target.
No branch creation/change, commit, push, merge, tag, credential setup, notification,
schedule enablement, input refresh or host mutation was performed for this plan.
Read current primary-checkout policy before later implementation; these work
documents do not replace it. Document checks validate form only, not runtime.

The maintainer prefers sustained discussion with documentation batched at
meaningful boundaries or handoff, rather than editing after every confirmation.
No memory update was requested. Do not inspect notes/ or treat an absent process
or branch as permission to remove this worktree.

## Earlier 2026-09-28 consolidation (historical navigation)

Latest consolidation: the repository spec's "Accepted execution, notification
and recovery contract" and AC12 record subsequent accepted decisions on trusted
roles, candidate-bound review, no cross-revision pass reuse, action-only alerts,
three delayed retries, idempotent tags and preview/manual/scheduled introduction.
Release authority remains annotated tags; initial tag metadata is agreed.
Next resolve durable batch storage using the comparison below. No operational
branch, issue, comment, App, credential or workflow has been created. Continue
discussion in batches; do not write documents after each confirmation.

Latest batched decisions: the maintainer accepted the daily cycle recorded in
the repository spec's "Accepted daily cycle and automation boundary" and AC11.
08:00 KST input refresh; 09:00 promotion; wait for ongoing refresh only until
10:00. Failed/no-op/approval-waiting refreshes do not block integrated dev.
Compatible patch refreshes may be admitted by a designated integrator; dev's
patch/minor promotion/publication is unattended after gates. Major or explicit
data-migration batches require exact-candidate approval. Candidate changes renew
evidence/approval. Dev remains open. Serialize cycles, join repeated triggers,
and finish failed publication with the same source/versions before another
promotion. Compute one cumulative effective bump per changed Unix-like/Windows
domain; no separate NixOS/Darwin/HM series. No new delta means no domain tag.
Manual urgent runs use the same rules. All host adoption/deployment stays separate.

This replaces earlier twelve-hour/open-cadence/dev-freeze recommendations below.
The daily refresh and Unix-like tool companion plans have been reconciled;
reports remain pending and no live automation is authorized by these documents.
Next discuss execution actors, minimum credentials, approval/notification
channels and exact source/merge-result evidence binding. Initial compatibility
values, supported coverage and remaining domain ownership questions still need
resolution before implementation. The maintainer prefers uninterrupted discussion
with batched documentation at meaningful boundaries, not edits after each assent.

Latest continuation: the maintainer confirmed environment selection plus
host-owned system/home modules. The Unix-like companion spec now carries a
dated AC1/AC2/AC4/AC5 amendment and new AC7/AC8; its report remains pending.
Latest correction confirmed by the maintainer: configs owns all three evaluator
compatibility baselines; hosts own adoption and actual persistent-state migration.
This supersedes the earlier same-day host-owned stateVersion proposal and the
host.stateVersion fields in the schematic examples below. The companion spec's
latest AC1 amendment governs. Exact initial values, environment names/coverage,
WSL dependency wiring and administration boundaries remain unresolved. Next settle the
minimal supported environment/platform table and provider evidence, then resume
stage-2 promotion/batch design. No implementation lane is assigned or ready.

The maintainer agreed to realign all three stages around one definition:
configs is one desired computing environment. Windows and Unix-like are its
platform-specific implementations. Within Unix-like, NixOS, nix-darwin and
Home Manager are configuration mechanisms, while desktop/graphics and other
features express capabilities; these are not necessarily sibling products.
Hosts map a selected version of this environment onto real computers and own
their final compositions and actual-use validation.

Configs supplies supported configuration elements, defaults, constraints,
composition interfaces and their implementation. Its release verifies that
public contract with explicit coverage. It does not certify the final state
of a private machine. Hosts own hardware facts, instance identity, selections,
customization, final build/integration, deployment, actual use and recovery.
Provider defects remain configs obligations even when discovered by a host.
This is an agreed planning direction, not an implemented policy change.

### Agreed clarification: environment and machine desired state

Agreed 2026-09-28: both configs and hosts declare desired state. The boundary
is environment desired state versus machine desired state, not optional versus
mandatory settings, nor desired state versus non-declarative host facts.
Configs implements the desired default desktop/work environment, its supported
customization points, dependencies and requirements; it is more than a catalog
of possible settings. Hosts declare how that environment is realized on their
actual hardware, including device/driver selection, monitor identity/layout,
storage, boot and network configuration, and validate the final composition.

Reusable machine-configuration recipes may remain in configs as explicitly
selected implementations. Hosts own their applicability and selection. Review
the current desktop's mandatory storage, swap and network choices against this
boundary before changing them; this agreement does not choose a replacement
schema or authorize a migration. The stateVersion ownership and template
submodule recommendations below remain proposals requiring separate resolution.

### Machine ownership and release independence clarification

Agreed 2026-09-28: potential reuse is not a reason by itself to retain machine
configuration in configs. The earlier option was motivated by existing machine
modules and the installExt4/installLuksBtrfs imports in configurations.nix; it
was not a requirement to preserve those modules as provider products.
Plan to move personal machine realization to the private hosts repository,
preserving behavior and identifying each setting's owner before migration.
No private-host edit or migration is performed by this planning clarification.

Retain a reusable implementation only when it serves an explicit environment
contract and has bounded provider verification independent of private machines.
Optional selection alone does not remove release obligations. If the provider
ships a supported implementation, its required contract checks still gate the
release; private-machine availability, installation success and actual-use
acceptance must not become provider release prerequisites. If the proposed
guarantee cannot be verified independently, narrow the public guarantee honestly
or move that responsibility and implementation to hosts before adoption.
Never retain a supported broken implementation and waive its required tests.

### Reassess the three stages

| Stage | Retain | Reassess before execution |
| --- | --- | --- |
| 1: environment and host contract | Host-owned facts/customization; independent consumers; explicit adoption; platform implementation boundaries. | Define the supported configuration surface and extension rules. Revisit machine-kind restrictions, central stateVersion ownership and mandatory template submodule integration against the new boundary. |
| 2: promotion and release | Separate promotion, domain release and adoption; immutable source binding; deterministic classification; independent domain versions as the existing planning baseline. | Replace the private-machine-shaped mandatory matrix with contract-derived synthetic cases and justified platform/native checks. Reassess final-output comparison as a release prerequisite. Then settle triggers, batch/candidate binding, publication and recovery. |
| 3: recurring input refresh | Twelve-hour provider-only refresh; default on with explicit exclusions; isolated lock changes; no implicit host updates. | Classify dependency changes against the stage-1 contract and stage-2 gates; reconcile scheduling, PR lifecycle, opt-out semantics and failure recovery. Lock-only changes are not automatically compatible. |

A single environment identity does not by itself adopt a single version,
cross-domain evaluator, common payload, or synchronized domain release train.
Existing independent-domain planning remains the baseline; any change needs an
explicit decision. Nor does the new direction select arbitrary feature mixes
as supported: stage 1 must specify supported composition and extension limits.

The companion Unix-like and Windows specs retain their historical decisions
and pending reports. Reconcile their acceptance criteria through dated,
scope-owned amendments before pickup, especially Unix-like AC1 (stateVersion),
AC2/AC4 (extensions/consumer cases), AC5/AC6 (support/tool baselines), and Windows
AC1-AC6 (selection, generation, customization and native evidence). Central
stateVersion is reopened for review because it may encode host migration
history; no replacement ownership or new baseline is selected here. Template
examples remain useful, but a pinned submodule must justify its role separately
from the environment definition. No companion criterion is silently waived.

Existing OS/tool baselines are retained as planning inputs, not automatically
broadened or removed. For every claimed capability, distinguish provider
evaluation/build/native evidence from host integration/use evidence. A native
provider behavior may still require native testing; handing deployment to a
host does not make syntax validation sufficient. Do not drop a failing required
test to make a candidate pass. Define the revised matrix before a release run.

### Next discussion and pickup boundary

First finish stage 1's public contract and ownership table, then select the
minimal justified stage-2 evidence and recurring batch rules. Stage 3 follows
those outputs. Avoid expanding machine manifests, hashes or packaging first.
The earlier assistant suggestion of daily opportunities plus manual triggers,
and temporarily pausing dev integration during promotion, is an unaccepted
option. No promotion cadence, integration pause or unattended authority has
been selected by this realignment.

Continue in this dedicated detached worktree. All five planning directories
remain local and untracked; preserve them. No lane is ready for execution and
no worker is assigned. Current repository policy remains authoritative.
The repository spec's 2026-09-28 amendment governs the revised planning target;
the previous handoff and research below remain historical where they conflict.

Read-only refresh on 2026-09-28 found remote dev at
e11bd1368d2f5138ad0f9b7017040b2b76e055e6 and master at
2542d77c09823417c62c179f4c69d9f7f5ba51ae, with no open provider PRs.
Protection/settings and native hosts were not re-audited. These observations
are not candidate release evidence. This continuation only edits local
repository-scope planning documents; no branch change, commit, push, merge,
tag, publication, input refresh, activation or Apply is authorized or performed.

## Stage-1 contract proposal, 2026-09-28

Status: concrete proposal for maintainer discussion, following the agreed
environment/host realignment. The boundaries below are not yet adopted domain
API changes. No companion acceptance criterion or current invariant is waived.
Read this section next when resuming, before selecting stage-2 batch rules.

### Three kinds of configuration

| Kind | Provider responsibility | Host responsibility | Proposed override contract |
| --- | --- | --- | --- |
| Environment preference | Supply opinionated, usable defaults for shell/editor/terminal, appearance and input behavior. | Select documented capabilities and override exposed preferences. | Valid explicit host values override provider defaults; defaults may evolve through reviewed releases. |
| Composition constraint | Declare types, dependencies, incompatible selections, supported platforms and ownership of managed data. | Supply valid inputs and satisfy the selected capability's prerequisites. | Invalid combinations fail clearly. An override cannot turn a violated public constraint into supported use. |
| Instance and migration fact | Provide typed inputs, validation and reusable implementation where useful. | Own identity, hardware/disk/network facts, secrets, provider pin and persistent-state migration choices. | Provider updates do not invent, replace or silently migrate these facts. |

One computing environment should retain useful opinionated defaults. This work
does not turn configs into a generic framework, expose every internal option,
or require a new abstraction for every program. Start with existing constructors,
selection APIs and a small documented set of extension points. Public means
explicitly documented and tested; internal module paths are not a stable API.

Host precedence is an API property, not a blanket last-writer-wins rule. Specify
scalar replacement, list merge/replacement, key deletion and whole-payload
replacement for each exposed setting category. Provider validation still runs
after composition. Existing Nix systemModules/homeModules and planned Windows
host customization are mechanisms to implement this contract, not proof that
all current settings already support overriding. Do not promise arbitrary Nix
upstream options or arbitrary Windows file edits as supported provider inputs.

If a host replaces an entire implementation through a documented replacement
point, its custom implementation is host-tested; other provider guarantees
remain scoped to the retained provider behavior. Using an internal path does
not make that path a stable API. A defect reproducible through supported inputs
remains a provider defect, even if first found on a private host.

### Concrete findings and recommended dispositions

Read-only inspection of local dev e11bd1368d2f5138ad0f9b7017040b2b76e055e6:

- `unixlike/modules/flake/configurations.nix` exports mkNixos, mkDarwin and
  mkHome with module extension inputs. mkNixos chooses required imports from
  machine kind/hypervisor; only the WSL composition offers the agents profile.
  `_host-contract.nix` admits a finite kind/architecture/hypervisor catalog.
  Preserve convenient reviewed compositions while separating actual technical
  restrictions from choices inherited from the old personal-machine inventory.
  Do not immediately replace these APIs with an unrestricted feature graph.
- The desktop composition requires installLuksBtrfs; the UTM/VMware
  compositions require installExt4. `unixlike/modules/machines/desktop.nix`
  asserts storage labels/layout, swap and networking along with its portable
  machine contract. Recommend separating desktop/graphics behavior from
  host-selected storage/network recipes. Recipes may remain provider-owned
  and tested when selected; their applicability is not a universal desktop
  requirement. This needs an explicit Unix-like policy/invariant migration.
  Existing WSL graphical exclusions are not changed by this proposal.
- NixOS stateVersion is currently a host input; Home Manager 25.11 and Darwin
  6 are provider assignments. Recommend preserving persisted compatibility
  choices with the host and supplying reviewed initial suggestions for new
  consumers, rather than replacing every host value with one provider baseline.
  Each evaluator needs its own migration analysis; moving declarations must
  preserve existing values and output behavior. A new template default must
  never rewrite an existing host's value. The earlier centralized-stateVersion
  plan requires a dated Unix-like amendment if this recommendation is adopted.
- Windows already exposes feature selection through win-env.ps1. Retain
  provider-declared dependencies and planned host-owned selection/customization;
  do not infer that local generation/capture redesign is already implemented.
  The public contract should describe managed settings and merge semantics,
  not promise an entire Windows installation's operational state.

Supporting upstream guidance, checked 2026-09-28: the
[Home Manager upgrade guide](https://nix-community.github.io/home-manager/usage/upgrading.html)
says to retain home.stateVersion through updates and change it only after
reviewing release notes and migrating affected configuration. The
[NixOS stateVersion guidance](https://wiki.nixos.org/wiki/FAQ/When_do_I_update_stateVersion)
distinguishes persistent-state compatibility from the current software version.
These support reviewing ownership; they do not establish identical semantics
for nix-darwin or decide this project's policy by themselves.

### Minimal assurance and effect on the remaining stages

Stage 1 should produce a short supported-input/default/constraint/extension
contract and a provider-versus-host responsibility table, followed by scoped
API migrations. Retain old consumer compatibility cases during migration.
The template is a convenient example/bootstrap consumer, never a requirement
for ordinary evaluation. Recommend deferring mandatory submodule adoption until
contract testing or distribution demonstrates a concrete need; AC3 remains
unchanged until that choice is explicitly amended.

For stage 2, begin with three evidence questions, not a machine count:

1. Do valid inputs/defaults/overrides compose, and do invalid inputs fail?
2. Do representative public outputs build or generate on the claimed platforms?
3. Do provider-owned behaviors that cannot be established statically pass their
   necessary native tests, with exclusions and unverified scope stated?

Host-specific disks, accounts, custom modules, target integration and actual
deployment/use are host verification. Contract-derived provider build/native
checks remain necessary where the provider makes the corresponding claim.
Exact cases and supported-platform coverage must be reviewed before automation.

Then define scheduled promotion opportunities, exact candidate binding and
serialization, unchanged-batch behavior, domain version aggregation and retry
after partial publication. Daily opportunities/manual triggers remain an option,
not a selected interval. All domains share source promotion under current policy;
independent domain tags do not permit cherry-picking a passing domain to master.

Stage 3 updates provider dependencies under this contract. It preserves host
pins and migration facts. A compatible refresh is a patch candidate; a lock
diff alone does not demonstrate compatibility. Twelve-hour refresh opportunities
remain separate from promotion, release and host-adoption clocks.

### Decisions for the next discussion

Recommend agreeing the three-way preference/constraint/instance boundary first.
Then resolve host-owned migration values and opt-in machine recipes in the
Unix-like contract, and the need for a template submodule in the repository
contract. Domain implementation plans remain blocked on these design choices;
this proposal is not a worker handoff. No code, host state or release was changed.

## Machine migration inventory and sequence proposal, 2026-09-28

Status: source-backed planning proposal, not execution authorization. This is
the next concrete step after the agreed ownership/release boundary. Source
inspection used provider e11bd1368d2f5138ad0f9b7017040b2b76e055e6 and the local
private consumer checkout f7f3010ca4675f705e8a8895dede19786530b6ca, whose working
tree was clean. Consumer pins differ from the inspected provider: NixOS
consumer declarations select 3f7371abec637a4ddce380a2969195f8c5353f21; Darwin
and standalone Home Manager select b8a8770164edd9b713253c63980bb59962c8a27f.
These are declared source pins, not a new lock/evaluation/build verification.
Do not infer consumer adoption from the provider checkout or historical README
runtime tables. No private identities or payloads are copied into this plan.

### Proposed ownership by behavior, not directory

All paths in this table are relative to unixlike/modules/.

| Current source | Proposed disposition | Release consequence |
| --- | --- | --- |
| machines/amd-apu.nix | Move AMD initrd, microcode, firmware and device-specific graphics selections/assertions to hosts. | No physical AMD desktop is needed to release the general graphical environment. |
| machines/desktop.nix | Move storage-layout, swap and network selections and their combined machine assertion to hosts. | Desktop environment verification no longer asserts that every consumer uses this disk/network recipe. |
| foundation/installation.nix | Move personal ext4 and LUKS/Btrfs layouts, boot choices, installer wiring and layout-specific checks to hosts; assess associated tools/dependencies as one migration. | Personal installation tests stop defining provider release acceptance; retain a minimal synthetic boot substrate only where needed to test provider behavior. |
| machines/utm.nix | Move QEMU/serial/DHCP integration, UTM software-rendering workaround and instance tuning to hosts. Review shared graphical recovery hooks separately. | UTM availability and its graphics runtime are host evidence, not provider release prerequisites. |
| machines/vmware.nix | Move hypervisor integration and DHCP selection to hosts. Review shared graphical recovery hooks separately. | VMware availability and guest integration are host evidence. |
| machines/orbstack.nix and its coupled account/shell/service choices | Move the concrete guest realization to hosts; preserve shared-kernel safety constraints and recovery knowledge with their owner. | A live OrbStack machine is not a provider gate. Removing provider code does not authorize unsafe kernel-global operations. |
| desktop/graphical/, desktop/niri/, desktop/noctalia.nix, fonts/input/audio/media | Keep environment behavior and generic service prerequisites in configs; inspect individual settings for device or instance assumptions. | Provider tests cover the selected environment contract on synthetic configurations and applicable platforms. |
| UTM/VMware dconf-service reload and stale-DISPLAY recovery hooks | Unresolved: retain as generic environment lifecycle behavior only with a reproducible synthetic regression; otherwise move with host recovery. | Do not require both private hypervisors merely because the same recovery code was first observed there. |
| flake/configurations.nix and flake/_host-contract.nix | Separate public environment composition from the closed personal-machine catalog. Keep typed identity/extension validation; design the migration interface before removal. | Public inputs and composition tests replace inventory membership as the contract. |

This is an initial inventory focused on desktop/guest machine realization, not
a completed audit of every platform module. WSL shared-kernel boundaries,
headless recovery/account/firewall settings and installation CLI/test callers
need a caller-and-policy pass before any implementation lane is assigned.
Do not delete directory contents mechanically. Environment needs such as
hardware.graphics enablement or a display-session service may remain provider
requirements even while vendor selection and machine boot wiring move out.

### Transition without tying future releases to private adoption

1. Define a supported environment composition API and explicit host realization
   inputs. Prefer evolving existing constructors/extensions over inventing a
   feature graph. Specify which old machine-kind behaviors cease to be public
   guarantees and the compatibility/version impact. Complete scope-owned specs
   and policy/invariant amendments before implementation.
2. Prepare provider environment separation plus synthetic contract fixtures in
   a Unix-like lane. Prepare hosts-owned machine modules against that reviewed
   interface in the consumer repository. Compare each consumer using its actual
   prior pin and inputs; the current provider checkout is not its baseline.
   Avoid importing the same machine implementation from both sides.
3. Publish the provider change under its declared compatibility classification
   once provider evidence passes. If removing the old public contract is
   breaking, use the planned major-transition contract rather than pretending
   that it is a compatible refactor. Existing consumers may retain old pins;
   a provider release does not wait for every consumer to upgrade or activate.
4. Adopt the reviewed provider revision in hosts explicitly and verify final
   evaluation/build, output differences and required host behavior there.
   Activation remains separately authorized. An ownership-only move should
   preserve behavior; explain derivation differences instead of assuming path
   relocation is byte-identical. Host migration acceptance is a one-time work
   outcome, not a permanent provider promotion gate.
5. Retire obsolete provider machine modules, tests, installation commands,
   fixtures, dependencies, docs and invariants as part of the reviewed API
   transition, not ad hoc cleanup after a release. If removal is staged, give
   compatibility support an explicit end; do not silently maintain two owners.

Provider public-API compatibility, synthetic environment tests and applicable
native provider behavior remain required. Host realization/installation tests
move with the corresponding implementation. A synthetic provider test may
need an arbitrary test disk or virtual GPU to execute; that fixture does not
make its layout/hypervisor a supported deployment product. Preserve tests that
actually prove environment guarantees, changing their setup rather than simply
removing coverage alongside machine modules.

### Next design decision

Recommended next step: define the minimal change to mkNixos that separates
environment selection from machine realization while retaining mkDarwin/mkHome
as configuration-system entry points. Specify a synthetic desktop consumer
with host-supplied boot/storage/device modules; do not choose a concrete new
argument name or promise compatibility until the API alternatives are reviewed.
Keep this work in stage 1. Stage-2 scheduling resumes once this public boundary
and its minimal evidence are concrete; no daily cadence or dev freeze is adopted.

## Second-pass omission review and interface direction, 2026-09-28

The first inventory was incomplete outside machines/. This pass traced source
references through foundation/platform modules, constructor schemas, fixtures,
test entry points, CI, installation tools, flake inputs, invariants and the
connected consumer/template interfaces. It is a static source review, not
evaluation, build, native runtime, deployment or a guarantee that arbitrary
dynamic consumers have been found. The following additions are required in the
implementation plan before claiming the migration inventory complete.

| Additional area and evidence | Required treatment |
| --- | --- |
| platforms/wsl.nix fixes UID 2000, automount ownership and WSL integration; foundation/sshd.nix fixes port 2223. | Move installation/coexistence choices to the host. Separate generic WSL adapter behavior and shared-kernel protection from this particular Windows machine's UID/port allocation. Preserve protection through migration; no kernel-global experiment is authorized. |
| foundation/account.nix fixes OrbStack UID 501, immutable-user and sudo behavior; shell/orbstack.nix and sshd.nix add coupled choices. | Move the complete guest realization together, not just machines/orbstack.nix. Preserve effective identity, groups, access and recovery. |
| foundation/account.nix, sshd.nix, firewall.nix and shell/headless.nix enforce account, key-only SSH, exact firewall exposure and login-shell wiring. | Decide which reusable security defaults are public environment behavior and which access/exposure decisions are host policy. Do not assume all foundation code remains provider-owned or relax security while transferring ownership. Keep plaintext secrets excluded; separately review the old blanket ban on declarative authorized public keys for private consumers. |
| foundation/nix/shared.nix and nix/darwin.nix set trusted users, daemon management and automatic GC/retention; home-account.nix and platforms/darwin.nix derive account/home identity. | Distinguish environment prerequisites from host administrative authority, account realization and rollback retention. Parameterize or transfer host choices while preserving current values. Routine provider updates must not silently choose a new retention policy. |
| programs/docker.nix enables Docker and group membership only through the WSL class. | Separate the offered development capability from its machine-catalog restriction and host privilege/service choice. Do not remove Docker simply because WSL machine realization moves. |
| platforms/homebrew.nix supplies app inventory plus activation auto-update/upgrade; defaults.nix mixes preferences and stateVersion. | Keep environment app/preferences decisions distinct from host installation prerequisites, account entitlement, update timing and migration choices. A provider source release cannot certify mutable external app bytes or App Store entitlement. |
| flake.nix inputs disko, nixos-anywhere and deploy-rs; flake/install-tools.nix exports nixos-anywhere; tool/install-plan, install-vm-test and their tests/callers. | Trace dependency and command ownership before removal. deploy-rs has a direct input declaration but no implementation reference found by this pass outside the lock; investigate as an unused-input candidate rather than silently deleting it. Stage-3 refresh must follow the resulting provider input set, never a host installer lock. |
| Justfile still contains refusal wrappers and WSL archive staging/login-shell operations; CONTRIBUTING documents installation tools. | Audit public commands, stale help and remaining host mutations alongside the module move. Preserve intentional refusal behavior or document its removal; transferring modules alone does not transfer commands. |
| flake/identity.nix, fixtures.nix, _host-contract.nix, module-classes.nix, configurations.nix; provider-api-test, flake-test, composition/import-order/eval-coverage checks. | Rewrite machine-catalog assumptions, path declarations and positive/negative cases together. Preserve typed inputs, public-output coverage and composition ownership; do not just remove tests that reject newly supported compositions. |
| flake/headless-runtime-test.nix and graphical-runtime-test.nix read fixture-vm identity; graphical runtime directly imports classes. | Make the test substrate synthetic and independent of the old inventory. Retain behavior tests where that behavior stays public, and add public-constructor integration proof so direct-class tests cannot hide a broken API. |
| tool/checks/test selects NixOS builds using activatable_here and host-name equality unless CHECKS_BUILD_ALL is set; eval-coverage-test exercises that policy. | Provider build selection must follow supported target/build capability and the reviewed evidence map, not ability to activate a synthetic host. Preserve accurate skipped/foreign reporting while changing the selector and its fixtures. |
| .github/workflows/ci.yml runs the Unix-like suite; nix flake check in tool/checks/test reaches exported checks. | Trace the complete dispatch chain before changing evidence requirements. A moved host-only check must not remain an indirect provider gate, and a retained provider check must not disappear accidentally. Root workflow changes are repository scope. |
| Template hosts/example calls mkNixos with kind=orbstack; both consumer/template tool/check-hosts evaluate outputs only. | Update the public example independently of private adoption. These tools supply evaluation evidence, not build/runtime acceptance. Use each actual consumer pin and lock at migration pickup. |
| Windows manifest manages .wslconfig and selects an OS-build-dependent source. | Record a Windows follow-up for host-wide networking/resource policy versus environment defaults. Do not move Windows behavior into the Unix-like consumer or mutate it as part of a Unix-like migration. The Unix-like hosts repository alone is not a Windows migration destination. |

### Policy and evidence closure

Revise the accepted meaning and enforcement together for the affected
Unix-like invariants: nixos-host-inventory, typed-identity,
composition-in-one-place, eval-covers-every-host, headless-key-only,
install-target-explicit, graphical-guests-keep-recovery,
amd-apu-desktop-portable-base and orbstack-shared-kernel. Review the connected
desktop-not-wsl and nixos-no-channel obligations rather than changing them by
accident. Keep historical decision evidence; adopt amended ownership/rationale
through new or amended decisions and update current status/usage/procedures.
Provider source relocation does not repeal the session's shared-kernel safety
rules. Enumerate old rule -> new owner -> enforcement -> evidence for each
transferred obligation before implementation. A test disappears only when its
obligation has moved, been explicitly retired or is proved by its replacement.

The first pass's recommended host moves remain valid proposals, but the exact
security/administration split, WSL adapter boundary, graphical recovery hooks,
stateVersion and Windows host contract remain open design decisions. These do
not justify further machine-matrix expansion. Resolve them as ownership choices
before worker pickup. No runtime checks, consumer edits or settings changes
were performed in this review.

### Next step: minimal public-interface proposal

Prefer retaining mkNixos/mkDarwin/mkHome as entry points and changing the
selection boundary inside them. The proposed inputs are conceptually:

- Typed identity, target platform and host-owned migration values.
- A documented environment selection with supported defaults/dependencies.
- Existing systemModules/homeModules extension mechanisms for host realization
  and supported customization, with explicit merge/ownership behavior.

Machine kind/hypervisor must not silently select personal storage, networking,
UIDs or exposure. The host supplies those through its own modules. Configs
still owns the mapping from its public environment selection to its internal
classes; host modules do not become direct imports of private class paths.
The alternative of exposing raw internal classes is not recommended: it would
couple consumers to source layout and obscure the stable contract. A new general
feature/dependency framework is also unnecessary for this migration.

This is an interface direction, not a selected argument schema. Next compare
one concrete NixOS desktop example before/after and one WSL case to test the
ownership distinction; preserve Darwin/Home Manager entry points without
claiming their administrative-policy questions are resolved. Use synthetic
host facts and no activation. Then amend the owning Unix-like spec/report and
associated repository acceptance where decisions actually change. Do not begin
implementation from this study alone.

## Concrete constructor proposal: desktop and WSL, 2026-09-28

Status: structure confirmed by the maintainer and reflected in the amended
Unix-like spec; example spellings and dependency wiring remain design proposals,
not implemented syntax. Retain the three constructors and their
existing systemModules/homeModules extension inputs. Add one explicit
environment selector to mkNixos; remove kind/hypervisor as composition inputs
in the breaking contract transition. Keep name, typed host identity/target and
git inputs initially to avoid unrelated API reshaping. The examples below are
schematic: named local module files do not exist yet and have not been evaluated.

### Public input meanings

| Input | Proposed meaning |
| --- | --- |
| name, host.system, host.user | Typed output/host identity, target architecture and environment account; supplied by the consumer. Provider must not invent UID, hardware or network facts. |
| host.stateVersion | Preserve the existing NixOS consumer value. This example does not decide the separate HM/Darwin migration-value API. |
| environment | The supported environment implementation to compose, not a physical-machine inventory entry. Proposed initial NixOS names are linux-cli, linux-graphical and wsl-cli; names/coverage require review. |
| profiles | Existing explicit optional capabilities. Keep agents available in its currently supported WSL CLI case initially; broadening support is separate from moving machine wiring. Reject unknown, duplicate or unsupported selections. |
| systemModules | Host-owned account, storage, boot, device, network, administration and platform-realization modules, plus documented environment customization. |
| homeModules | Host user customization through supported options; does not expose private provider class paths. |
| git | Existing explicit identity input; not inferred from the provider checkout or a template. |

The provider maps environment/profile choices to its internal classes in one
place. Host modules cannot silently redefine the environment selector or bypass
public constraints. Preferences use documented merge rules; invalid inputs and
contradictions fail. Merely importing a module list does not prove that required
machine facts exist: ordinary NixOS checks plus the documented constructor
preconditions validate the resulting configuration. Avoid filesystem-name or
module-count heuristics for detecting a complete host.

### Desktop before and after

Today mkNixos derives a desktop composition from host.kind = "desktop";
that selects AMD configuration, LUKS/Btrfs, headless access and graphics together.
The proposed consumer shape is:

```nix
configs.lib.mkNixos {
  name = "example-desktop";
  host = {
    system = "x86_64-linux";
    user = "example";
    stateVersion = "25.11"; # Synthetic value; preserve each real host's value.
  };
  environment = "linux-graphical"; # Proposed API, not available today.
  profiles = [];
  git = { name = "Example"; email = "example@example.invalid"; };
  systemModules = [ ./machine.nix ];
  homeModules = [ ./preferences.nix ];
}
```

The consumer's machine.nix owns account realization, AMD/device support,
storage/boot, swap/network and selected remote access; its preferences.nix owns
instance-specific user settings such as display layout. Configs supplies the
graphical environment, generic graphics/session requirements and shared user
tools. The same environment could be used by a VM whose host module supplies
guest realization instead. This is a composability example, not a newly
certified hardware/hypervisor support matrix. Moving existing desktops must
retain their access, kernel protection and recovery behavior.

### WSL before and after

Today host.kind = "wsl" selects the upstream NixOS-WSL module plus provider
fragments containing UID, SSH, Docker and other system choices. Proposed shape:

```nix
configs.lib.mkNixos {
  name = "example-wsl";
  host = {
    system = "x86_64-linux";
    user = "example";
    stateVersion = "25.11"; # Synthetic, not a migration instruction.
  };
  environment = "wsl-cli"; # Proposed API, not available today.
  profiles = [ "agents" ];
  git = { name = "Example"; email = "example@example.invalid"; };
  systemModules = [ ./wsl-machine.nix ];
  homeModules = [ ./preferences.nix ];
}
```

Recommend that wsl-machine.nix import a host-pinned NixOS-WSL module and own
default-user/UID, automount ownership, shared-kernel protection, access ports,
Docker/service selection and administration. The provider supplies WSL CLI
environment settings and constraints, including the existing no-WSLg boundary.
The host's adapter must preserve kernel-safety behavior before any old provider
implementation is removed. This selection does not automatically introduce
WSL system options into standalone mkHome, which cannot manage that system.

Moving the upstream NixOS-WSL dependency is a recommendation, not an adopted
lock edit. Its tested compatibility with the provider's nixpkgs must be explicit:
choose reviewed follows/override wiring during domain design and record both
pins in host evidence. Do not introduce a second hidden package-set authority,
assume every adapter revision is compatible, or make provider CI fetch private
host locks. A public synthetic pinned adapter case may test the claimed public
interface without certifying private WSL installation or kernel behavior.

### Public contract proof and transition

For each selected environment, test the public constructor with synthetic host
modules, not merely the internal class graph. Verify valid defaults and a
documented override, rejection of invalid/contradictory choices, and the absence
of provider-injected personal storage/UID/port/administration choices. Evaluate
and build the declared reference outputs; retain justified native environment
tests. Host tests separately preserve the migrated realization, with build and
runtime evidence distinct. The exact supported environments/platforms and test
set must be reviewed; these examples do not certify them.

Replacing kind/hypervisor with environment and shifting required host wiring
is a breaking constructor-contract change. Do not silently reinterpret old
calls: publish migration guidance with explicit compatibility classification.
Old pinned consumers continue on their old provider; new consumers provide
their machine modules. Provider publication waits for its contract checks,
not for every real consumer's migration. Initial consumer regression evidence
supports the migration project without becoming a recurring private-host gate.

This proposal deliberately leaves the security-default split, HM/Darwin
stateVersion API and template submodule decision open. No approved companion
criterion has been rewritten on the assumption that these recommendations were
accepted. The next discussion is whether this single environment selector and
host-owned WSL realization express the intended boundary; then update the
Unix-like spec/report with a dated contract amendment before implementation.

## Baseline change procedure proposal, 2026-09-28

Ownership is now agreed: configs defines NixOS/HM/Darwin baselines separately,
and hosts own adoption/data migration. Earlier same-day host-owned-value advice
and sample fields are historical. The following procedure develops that decision;
exact version values and compatibility exceptions are not yet selected.

1. For initial migration, inventory current effective values per evaluator and
   compare proposed provider baselines under the actual prior consumer inputs.
   Preserve the distinction between a source move and a changed effective value.
2. Pin the chosen provider baselines explicitly. Routine twelve-hour input
   refresh changes dependencies, never these values. Test that separation.
3. For a later baseline change, review affected defaults and public behavior,
   required data transitions and the supported starting baselines. Classify the
   resulting contract impact; do not mechanically infer patch or major solely
   from a changed number. Exercise claimed transitions with synthetic data where
   relevant; build success alone cannot prove persistent-state compatibility.
4. Publish the baseline/impact/migration information with the verified provider
   release. Hosts with extra services assess those separately and choose adoption.
   Private adoption or migration completion does not block the provider release.
5. Keep an old provider pin when adoption is deferred. Do not assume reverting
   source restores migrated data; document data recovery separately where needed.

The earlier 25.11/25.11/6 choices remain initial-baseline candidates for review,
not an automatic consequence of confirming ownership. A host override could
create a different tested contract; do not silently add one as a workaround.
The normal proposed constructor no longer needs host.stateVersion. The next
design pass should settle initial values and minimal supported environment
coverage, then resume promotion cadence/batching. No code or host migration
occurred in this planning update.

## Operational record storage comparison, 2026-09-28

Superseded selection: the later accepted public-execution/private-records contract
uses a separate private repository with ordinary Git history. The public orphan
operating branch below was an alternative, not the selected implementation. Moving
the controller into the private repository was also discussed and not selected.
The durability findings remain useful; proposed public operational-ref exceptions
are no longer required by the chosen storage location.

This is a proposal, not an adopted storage mechanism. Read-only remote queries
still found dev e11bd1368d2f5138ad0f9b7017040b2b76e055e6 and master
2542d77c09823417c62c179f4c69d9f7f5ba51ae, with no open provider PRs. Protection,
token settings and actual retention were not audited. Current plan-release is
read-only, proposes calendar tags from existing names and checks master ancestry;
it is not an implemented semantic-version allocator or durable batch controller.

| Option | Benefit | Limitation | Assessment |
| --- | --- | --- | --- |
| Actions artifacts/logs | Natural per-run evidence and no source commits. | Retention and run deletion can remove recovery inputs; reruns are separate executions. | Useful detailed evidence/cache, not the sole durable publication plan. |
| Structured PR body/comments | Beside human review, no new Git branch. | Mutable/deletable records need integrity/provenance handling; comments can notify on normal progress; PR text is not accepted classification authority. | Keep as a review projection, not the sole publication plan. |
| Dedicated append-only operational Git branch | Versioned small JSON records, remote recovery and source/version history independent of artifact retention. | Requires an explicit governance exception, restricted writers/protection and concurrency design; more operational machinery than PR text. | Recommended for durability if the maintainer accepts the policy cost. |

The proposed branch (illustrative name ops/release-state) would contain only
batch plans/events, never environment source or executable workflows. It would
never merge into dev/master or receive a domain version. Store only public-safe
identities, digests, summaries and references; no credentials or private-host
data. Keep verbose logs in Actions, but retain the minimal verification manifest
and frozen publication payload needed for long-term interpretation/recovery.
Final tag metadata stays authoritative for completed releases; the operational
record cannot redefine or replace an existing tag.

Minimal data: batch ID, controller revision, dev/master candidate pair and tested
tree/result identity, evidence/tool/check identities, approval binding, previous
domain tags, selected versions, frozen tag payloads, actual merge commit, per-domain
publication outcome, retry count/timing and notification deduplication key.
Keep candidate-plan revisions before promotion distinct from the fixed publication
plan afterward. The real merge commit is observed only after merge; pre-merge
intent and the post-merge result must both be recoverable. A crash after merge
but before recording it recovers from the promotion PR's observed merge, verifies
the expected candidate/result, then records it; it must not promote again blindly.

Use one trusted writer and serialized commits with non-forced ref updates against
the read tip; conflicts reload/reconcile instead of overwriting. Exact concurrent
write/ref protocol needs positive/negative fixtures. Actions concurrency can
serialize execution but is not the durable record or a guarantee that every
queued trigger runs. Every start first loads/reconciles the outstanding batch.
No fixed publication payload may be edited after the first external write;
corrections require an explicit reviewed recovery path, not a tag replacement.

Policy cost is real: current CONTRIBUTING models source topic branches, the
GitHub-agent workflow rejects extra central databases/locks, and tracked-runtime
hygiene would need a precise operational-ref boundary. Before implementation,
adopt this narrow exception through repository governance with tests, branch
protection and an explicit retention/recovery contract. Do not silently exempt
dev/master source, bypass their PR rules or create an ops branch now. The write
token needs repository contents permissions; branch/ref restriction must be
enforced and tested, not assumed from an App permission label. No API call here
provisioned that permission.

Sources checked 2026-09-28:
- [Artifact removal and retention](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts): default retention and deletion with the owning run.
- [Concurrency](https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency): default pending-run replacement and optional queuing; neither persists application state.
- [Git references API](https://docs.github.com/en/rest/git/refs): ref creation/update and contents permission requirements.
- [Contents API](https://docs.github.com/en/rest/repos/contents): file updates require the prior blob SHA; this is not a substitute for a complete tested writer protocol.

Pending decision: accept the operational-branch exception or choose a different
durable store. Do not treat the storage recommendation as accepted merely because
the maintainer already accepted workspace-independent recovery. Exact approval
and evidence-to-merge binding still require design whichever store is chosen.

## Previous handoff, 2026-09-27

The maintainer requested a session handoff after clarifying the central goal:
give external hosts useful release points they can deliberately pin, and design
a recurring dev -> master promotion/release process. Machine-based distribution
is only one option. Start with the release cycle, not more machine schemas,
hash algorithms or feature-combination matrices. Prefer a simple initial design
and add precision when an actual need justifies it.

### Workspace and authority

- Role: planner, scope: repository. Stage 2 is unfinished; no implementation
  worker or execution issue is assigned. Continue this plan in the next session.
- Worktree: `configs-flake-refresh-plan/`, relative to the workspace root.
  Detached at e11bd1368d2f5138ad0f9b7017040b2b76e055e6. All five planning
  directories below remain untracked, uncommitted and unpushed. Preserve them;
  neither an absent branch nor pending reports authorize cleanup.
- Primary checkout: `configs/`, relative to the workspace root.
  Read current AGENTS.md, CONTRIBUTING.md and applicable policy/skills there
  as needed; write planning changes in the dedicated worktree. Use plan-work
  and run-version-control-workflow. Some newer skill/Context Bridge files exist
  in the primary checkout but not the detached planning tree.
- Current policy remains authoritative. No commit, push, branch change, merge,
  tag, release publication, runner enrollment, activation or Windows Apply is
  authorized by this planning/handoff request. Do not create a scheduler or
  perform remote host checks simply to resume design. Do not update memories
  or create remote issues/messages as an inferred part of this local handoff.

### Read in this order

1. This handoff, then the adjacent spec.md, especially the dated AC1/AC7
   "release checkpoints first; distribution boundary open" amendment and
   AC5/AC6 representative-configuration amendment. report.md tracks pending
   implementation, not whether the user agreed to the design.
2. docs/work/unixlike/provider-consumer-contract/spec.md and report.md.
3. docs/work/windows/host-consumer-contract/spec.md and report.md.
4. Only when stage 2 is ready to feed stage 3: the existing
   docs/work/repository/scheduled-flake-refresh/ and
   docs/work/unixlike/automatic-flake-refresh/ plans. Reconcile their earlier
   assumptions with the final stage-2 contract before execution.

These are the five local planning directories to retain. The long research
history below is reference material; the next session need not reread it all.
Its dated decisions are superseded where the current spec says so.

### Agreed direction versus open choices

- Independent domain semantic versions; repository governance has no host
  output or domain release. Initial implemented/verified Unix-like and Windows
  stable contracts start at 1.0.0 independently. Maintain one active major per
  domain; retain old tags without an implied backport service.
- Source promotion, domain release and host adoption are separate. Docs and
  repository changes may reach master without a domain release. A new release
  does not automatically update a host pin or authorize deployment.
- Changed domains require representative build/native generation evidence
  across all declared supported platforms before master promotion. Exhaustive
  feature combinations and private-host behavior are not guaranteed. Required
  failures/missing evidence cannot be waived. Prefer hosted native builders;
  keep Windows client-specific evidence distinct. Actual capacity remains open.
- Windows: Windows 10 IoT Enterprise LTSC 21H2 x64/build 19044 (earlier observed
  revision 19044.7725). Windows 11 excluded. Terminal settings/fonts/profiles
  included; default terminal delegation excluded. PowerShell 7.6.6 CI baseline
  with a separate Windows PowerShell 5.1 bootstrap path.
- Unix-like: initial Apple Silicon macOS 26 support and upstream Nix 2.34.8 CI.
  The planned catalog covers existing Linux/WSL/guest/desktop compositions;
  Intel Darwin is not in that initial catalog. Tool baselines are reproducible
  CI inputs, not automatic upgrades or consumer-host minimums.
- Classification runs deterministically in ordinary CLI/CI without an agent
  adapter. Structured reviewed declarations and actual evidence determine
  none/patch/minor/major; commit prose alone is insufficient. Exact file/trailer
  encoding, traversal and legacy migration remain open.
- Comparison includes provider-supplied dependencies and consumer tools, and
  distinguishes contract changes from external environment/provenance. Hosts
  own customizations, adoption and operational recovery. Provider public-contract
  defects remain provider obligations.
- Machine-specific distribution/files/subset identities are optional proposals.
  Domain snapshots, platform/profile bundles and optional indexes remain
  alternatives. Domain versioning need not match packaging granularity.
- The eight-plus-eight matrix was rejected as too complex. One maximal
  compatible reference per machine (seven Unix-like plus one Windows) is a
  simpler candidate, not an adopted delivery architecture or implemented gate.
  Verification cases do not dictate distribution units.
- GitHub immutable assets are a researched option; current annotated-tag-only
  policy remains effective. Publication transport is deferred.
- Stage 1's provider/host ownership, independent generated consumers, pinned
  template direction and planned NixOS/Home Manager 25.11 / Darwin 6 state
  baselines remain. Stage 3's proposed twelve-hour input refresh is NOT an
  accepted master-promotion or release interval.

### Next session: design the recurring cycle

Use this sequence as a discussion outline, not a newly adopted operational
workflow or permission to execute it:

1. Define a release opportunity: event-driven after coherent dev changes,
   scheduled batching, or a hybrid. Decide docs-only promotion and no-change
   behavior. Do not invent a cadence from stage 3.
2. Fix a candidate source revision and the relevant baselines: current master
   for source promotion, each domain's last release for version/change analysis.
   Classify affected domains and validate structured declarations.
3. Obtain required representative evidence and bind it to the exact candidate
   or tested merge result. Resolve dev moving during validation and the final
   promotion merge's identity; do not relabel old evidence for a new revision.
4. Promote via same-repository dev -> master PR merge commit under adopted
   policy. This accepts source history, not domain cherry-picks. A combined
   candidate waits if any required lane fails, even when another domain passes.
5. For actual domain artifact/contract deltas, compute the next domain version
   and publish an immutable record bound to verified source on master. Handle
   promotion success followed by publication failure without mixing records or
   inventing an extra source change just to retry publication.
6. Expose a discoverable fixed release point. Hosts choose when to adopt it.
   A simple source snapshot may suffice initially; compare distribution options
   against concrete consumer needs.
7. Define concurrency, idempotent retries, failed-candidate repair and the
   authorization model for future unattended actions. Then refine necessary
   record fields, domain implementation lanes and stage-3 refresh.

The immediate next question is the opportunity/batching rule in step 1.
Present a small set of concrete alternatives with a recommendation, rather
than expanding another detailed architecture before the operating flow is set.

### Fresh handoff snapshot and evidence limits

Read-only queries repeated at this handoff on 2026-09-27 found origin dev at
e11bd1368d2f5138ad0f9b7017040b2b76e055e6 and master at
2542d77c09823417c62c179f4c69d9f7f5ba51ae, with no open provider PRs. The queried
Unix-like/Windows tag sets contain unixlike-v2026.08.31 and windows-v2026.08.31;
both peel to 9586eb97114162fa96eadf1da8c90a492fcbc6f9. Re-query before relying
on these values in a future session; settings/protection were not audited in
this handoff. Other worktrees exist and are unrelated to this handoff.

This session produced planning edits, source/documentation research and small
read-only probes; reports remain pending. No current release-gate implementation,
full platform build matrix, native client certification or deployment was
completed. Earlier dated partial evaluation/Windows observations in the study
do not become evidence for a later candidate. No new remote host operation was
performed for the handoff. Work-document/whitespace checks validate document
form only; this local handoff is not a remote backup.

Suggested new-session prompt:

```text
configs-flake-refresh-plan worktree의
docs/work/repository/provider-release-contract/study.md에서
"Current handoff: resume here"를 읽고 2단계 설계를 이어가자.
머신별 배포는 선택지일 뿐이며, 호스트가 고정할 릴리즈 시점과
주기적인 dev → master 승격·릴리즈 흐름이 핵심이다.
우선 승격·릴리즈 기회를 여는 시점과 배치 규칙부터 검토하자.
아직 구현하거나 커밋·푸시·병합·태그·배포하지 않는다.
```

## Earlier continuation notes (historical navigation)

Latest priority clarification, 2026-09-27: machine-based distribution is one
option, not a fixed requirement. The maintainer's central goals are release
checkpoints hosts can deliberately pin and a recurring dev -> master promotion
and release process. The spec's dated AC1/AC7 amendment reopens the earlier
machine-subscription choice. Read the final "Release checkpoints before unit
granularity" entry first; all machine schemas, hashing detail and proposed
matrices below remain design options. Verification cases do not dictate units
of distribution. Exact cadence and publication transport remain open.

Latest research, 2026-09-27: see "Machine release manifests: research and
critical review" below. The maintainer requested investigation of per-machine
release files for external-host pinning. The findings propose identities,
publication choices and verification cases; they do not adopt an exact schema,
transport, new acceptance criterion or automatic publication authority.
The subsequent "Provider-bounded assurance and host responsibility" discussion
records the maintainer's response: investigate narrower guarantees and prompt
fixes, leave private-host integration/recovery with hosts, and keep publication
location open. The subsequent accepted amendment selects mandatory machine
reference configurations across all supported platforms; exhaustive feature
combinations and private-host behavior are outside the guarantee. Current
AC5/AC6 in the spec and the final dated entry below record that selection.
The subsequent "Proposed minimal machine release record" section develops the
next design step. Its field names and comparison protocol are a reviewable
proposal, not a newly accepted schema or implemented host interface.
"Proposed change-identity calculation" follows with domain-specific inputs and
comparison limits; it likewise remains proposed detailed design.
The eight-plus-eight "Proposed mandatory reference matrix" below is historical:
the maintainer judged it too complex. The final "Simpler starting point" section
replaces that recommendation with one maximal compatible reference per machine,
seven Unix-like cases and one Windows case, with separate required client evidence.

Latest stage-2 scope amendment, 2026-09-27: Windows support and verification
are Windows 10 only. This replaces the earlier same-day Windows 10/11 choice.
The dated scope amendment at the end and the current spec/report criteria
govern this planned work; earlier research retains its historical context.
The latest client baseline is Windows 10 IoT Enterprise LTSC 21H2 x64,
build 19044 (observed 19044.7725). Terminal settings, fonts and profiles stay
supported; default terminal delegation is outside this baseline's guarantee.
The final dated amendment and Windows AC5 record that accepted distinction.

The maintainer approved stage-1 direction and requested written continuity.
The next operation is planning stage 2, not implementation or promotion.
Read this document, the adjacent spec/report, and both companion domain specs.
Use plan-work and run-version-control-workflow; use context-bridge-workspace
when examining the external template or private host consumers.

The local delivery is in the existing linked worktree named
`configs-flake-refresh-plan`, a sibling of the main configs checkout. It is
detached at e11bd1368d2f5138ad0f9b7017040b2b76e055e6. These documents are local,
uncommitted and unpushed at handoff; they are not present on dev/master or in a
remote PR. Preserve this worktree. Do not clean it up or infer completion from
the absence of a branch. Read there even if the new session starts in the main
checkout. Explicit Git publication authorization is still needed; before
delivery, follow the linked-worktree/topic-branch procedure and preserve
single-scope commits/PRs. No remote message or issue has been created.

## Three stages

1. Release meaning and consumer contract: design agreed; the three specs
   capture it, implementation pending.
2. Master promotion and domain release gates: next planning session.
3. Scheduled refresh: after stage 2 defines its integration/release boundary.

Stage 1 keeps configs as the declared-infrastructure provider. Hosts supply
instance information and own customizations. Unix-like uses Nix constructors;
Windows uses its own PowerShell entry and local generated configuration.
Shared ownership language does not introduce a shared evaluator or release.

Agreed directions:

- Host-consumable master with frequent domain releases; compatible routine
  dependency updates should normally produce patch releases.
- Pinned template submodule as contract/example/generation source; independent
  generated hosts; no automatic template synchronization.
- Central NixOS/Home Manager stateVersion 25.11, Darwin stateVersion 6.
  Future changes are separate reviewed compatibility work, not input refreshes.
- Host-owned capture on Darwin and Windows; preserve host customization on
  future regeneration/adoption; exclude runtime state.
- Windows win-env.ps1 is the entry. Features are opt in, core is required,
  dependencies are included, future new features stay unselected.
- Provider flake updates, unlike Windows features, are default-on with opt out
  and run every twelve hours. Private host flakes do not update implicitly.

## Refreshed repository observations

Read-only GitHub/remote inspection on 2026-09-27 found:

- dev: e11bd1368d2f5138ad0f9b7017040b2b76e055e6.
- master: 2542d77c09823417c62c179f4c69d9f7f5ba51ae.
- No open provider PRs at that observation.

These are a snapshot, not a pickup base. Re-query remote branches, PRs,
required checks, protection, default branch, workflow permissions and existing
plans at the beginning of stage 2. Do not repeat old divergence counts as live
facts. Earlier template/host research revisions were respectively dcb8c6d and
f7f3010; refresh both through the Context Bridge before adoption work.

## Stage 2: questions to resolve

Design the minimum evidence for master to compose supported hosts and for each
domain release to certify its own contract. Distinguish evaluation, build,
native runtime and activation/Apply. Private deployment is not a universal
provider release gate. Preserve native Windows evidence for Windows behavior.

Decide supported platform/tool baselines, old-consumer/template checks,
candidate-SHA evidence, dispatch rules for unrelated domains, expensive-build
coverage, and handling of external mutable dependencies. Define promotion
batching, one-open-promotion behavior, failures/retries, revert/recovery and
initial dev-to-master transition. Decide release triggers, initial semantic
version, bump aggregation, legacy tag recognition and annotation contents.
Do not silently turn fast releases into permission for unattended merging,
tagging or deployment.

Current policy gaps to resolve through ordinary governance:

- Calendar-tag tooling and evidence conventions versus semantic releases.
- Windows per-host release evidence versus the planned reusable consumer model.
- Existing capture publication into configs versus host-owned capture.
- NixOS host-owned stateVersion schema/docs versus central ownership.
- Current Intel Darwin enum versus the supported platform matrix.

Existing policy still governs execution until adopted replacements land.
At this original handoff, initial 1.0.0, one active major, exact cron minute
and a GitHub App were recommendations. The later dated maintenance decision
accepts the first two; it does not accept the cron minute or a GitHub App.
Do not promise universal app/runtime compatibility: Homebrew auto
update/upgrade and external version managers are outside the flake lock.

Suggested new-session prompt:

> configs-flake-refresh-plan worktree의
> docs/work/repository/provider-release-contract/study.md부터 읽어줘.
> 1단계 합의와 세 범위의 spec/report를 유지하면서 2단계인 master 승격 및
> 도메인 릴리즈 조건을 조사하고 설계해줘. 원격 상태를 재확인하고 선택지를
> 좁혀 제안해줘. 아직 구현·커밋·푸시·승격·태깅·호스트 적용은 하지 마.

## Stage 3: questions to resolve

Refresh every independently locked provider input by default, with explicit
exclusions. Document follows semantics; preserve excluded sources and reject
unknown exclusions. Empty selection/no changes are no-ops, failure leaves no
partial lock. Generate isolated unixlike-deps changes through dev PRs.

Revisit scheduling on the actual default branch, twelve-hour cadence and
queue delays, token permissions/PR CI triggering, concurrency, reuse of the
update PR, contamination refusal, retry/failure notification and credentials.
Connect integration and release only through the stage-2 approved boundaries.
No host activation, Windows Apply or automatic consumer lock update is implied.

The two earlier plans are retained as inputs, not ready worker instructions:
`docs/work/unixlike/automatic-flake-refresh/spec.md` and
`docs/work/repository/scheduled-flake-refresh/spec.md`.
Their implementation details must be reconciled with stage 2 and amended
explicitly rather than blindly executed.

Suggested later-session prompt:

> provider-release-contract/study.md와 완료된 2단계 설계를 읽어줘.
> 기존 automatic-flake-refresh 및 scheduled-flake-refresh 초안을 검토해
> 12시간 주기, 기본 포함·opt out 방식의 3단계 계획을 구체화해줘.
> 2단계가 미완성이면 의존사항부터 확인해줘. Windows 기능은 별도의 opt in
> 정책이며, host lock이나 activation은 자동 갱신 범위에 넣지 마.

## Carry-forward research

The Unix-like companion study records the ten equal-derivation stateVersion
comparisons, reproduction expression, override probes and capture limitations.
The Windows companion study records current selection, auto-detected host
information and the gap between current capture and the proposed host model.
No raw private identity or machine state needs to be copied into public plans.

## Stage-2 continuation: proposal, 2026-09-27

This section began as research and a proposed design. On 2026-09-27 the
maintainer accepted full supported-platform builds before master promotion;
that decision is now recorded as AC5 in the adjacent spec/report. Other
recommendations remain proposals. Stage-1 criteria and the companion domain
spec/report pairs remain unchanged, and implementation remains pending.
Neither the proposal nor that design choice grants execution authorization.
Scope here is repository governance. Platform test implementation and support
contracts belong to the companion domain plans. No worker is assigned.

### Live observations and the gap

Read-only GitHub API inspection during this continuation found:

| Item | Observation |
| --- | --- |
| dev | e11bd1368d2f5138ad0f9b7017040b2b76e055e6 |
| master | 2542d77c09823417c62c179f4c69d9f7f5ba51ae |
| Open PRs | None |
| Comparison master...dev | Diverged; 539 ahead, 7 behind; a history count, not a count of unreviewed changes |
| Default branch | master |
| Protection | Both require Required checks and resolved conversations; administrators enforced; force pushes and deletion disabled |
| Strict base | dev true; master false, intentionally avoiding reverse promotion merges |
| Merge methods | Merge commits enabled; squash and rebase disabled; auto-merge enabled but not authorized by this design |
| Workflow defaults | Read permission; workflow PR-review approval disabled |
| Domain tags | unixlike-v2026.08.31 and windows-v2026.08.31 |

The dev CI run [36231842628](https://github.com/shk95/configs/actions/runs/36231842628)
succeeded at that exact dev SHA. Unix-like and global scans ran; Windows and
repository fixtures were skipped by selection. This is not all-domain release
evidence. Re-query these observations at pickup and before any mutation.

At the inspected source revision, `.github/workflows/ci.yml` uses one Ubuntu
Unix-like job and one native Windows suite. `unixlike/tool/checks/test` evaluates
all exported fixtures, skips foreign builds, and normally skips synthetic NixOS
toplevel builds. `CHECKS_BUILD_ALL=1` removes the latter skip, not the foreign
system restriction. The current suite therefore does not establish full
x86_64-linux, aarch64-linux and aarch64-darwin build coverage in CI.

The existing release planner uses calendar versions and local master
reachability. Windows annotations remain per host; native read-only host checks
are distinct from hosted Pester evidence. The stage-1 provider model needs
explicit amendments to those contracts. Keep the current rules until adoption.

### Proposed admission boundary

Accepted 2026-09-27: require full supported-fixture builds for a changed domain
before promotion. Windows uses its native generation/validation equivalent.
This makes "host-consumable master" mean the documented constructors or Windows
generation contract work and the supported outputs can be produced. It does not
promise every private customization, upstream application, or physical device.
The maintainer chose this over evaluation and representative builds before
promotion with full builds deferred until tagging. The rest of the detailed
admission mechanism below still requires review; the choice does not approve
every recommendation in this study.

| Boundary | Proposed required evidence | Meaning |
| --- | --- | --- |
| Topic PR to dev | Existing effect-selected suites and global policy scans; new contract fixtures as their owning implementations land | Reviewed integration candidate |
| dev to master | Global scans, promotion source/queue checks, changed-domain current and retained-consumer contract checks, full supported native builds, required synthetic runtime checks | Accepted source satisfying the declared consumption contract |
| Domain tag | Successful validation of the actual target commit, domain compatibility review, supported-environment coverage, version and annotation validation | Immutable release of that domain's contract |
| Private adoption | The consumer's pinned inputs, evaluation/build and target-specific checks | Evidence for that consumer only |
| Activation or Apply | Explicit request and target-specific deployment procedure | Host mutation, never granted by a merge or tag |

Select promotion coverage from the previous master tree to the proposed merged
tree, not merely the latest dev commit. Release classification covers all domain
changes since that domain's previous release, even across several promotions.
Unchanged unrelated domains do not run or block a promotion. A batch containing
both changed domains must satisfy both; failure cannot be excused as unrelated.
Common has no release lane until a real component and its checks are adopted.

Documentation-only edits keep the ordinary policy-scan path. Changes to declared
support, compatibility cases, test selection, or gate implementation require the
affected contract suites even if some inputs are documents. Shared dispatch
changes select every affected suite. Unknown inputs fail closed. Do not silently
weaken the existing effect-selection invariant to implement the new gate.

### Supported consumers and cost

Proposed initial Unix-like matrix follows the stage-1 fixtures: x86_64 NixOS-WSL,
x86_64 VMware, x86_64 AMD APU desktop, aarch64 UTM, aarch64 OrbStack,
aarch64 Darwin and standalone x86_64 WSL Home Manager. Evaluate every supported
composition and retained extension recipe; build all declared final fixture
outputs on the matching system at promotion and release validation. Keep the
generic booted headless test as narrowly scoped runtime evidence. The desktop
row does not certify installation or graphics hardware; a generic VM does not
certify UTM, VMware, WSL or OrbStack runtime integration.

Recommend excluding Intel Darwin from the initial supported promise as identified
in stage-1 research. That needs an explicit support-matrix decision, owning-domain
schema/document changes and tests; it is not enacted here. New architectures and
platforms are deliberate additions, not inferred from an upstream enum.

Retain immutable synthetic consumers from the first stable release and each
later public contract addition, deduplicating only demonstrably identical cases.
Run them against the candidate provider without rewriting their old usage to
fit the candidate. Also generate a new consumer from the pinned current template
and inject the candidate SHA. Test ordinary provider consumption without recursive
submodule checkout. Fetch template material only for generation/contract checks.
Record template and retained-case revisions independently of the provider revision.
Compatibility cases cover the active major's supported contracts. Older-major
cases remain historical migration evidence; an accepted major transition names
which old contracts end and tests the migration/new contract explicitly. For the
first stable release, preserve pre-release examples as migration cases without
claiming that the planned stateVersion/schema change is backward compatible.
External repositories were not re-inspected in this continuation; use Context
Bridge and refresh them before selecting actual fixture revisions.

For Windows, native validation and the complete Pester/E2E suite are necessary
but not proof of a Windows client host. Add synthetic old host-declaration and
generated-format cases, core-only selection, feature dependency closure, opt-in
behavior and customization preservation. Keep read-only client checks for changes
to Appx detection, registry, paths, fonts, capture or application lifecycle, with
OS build, application versions and selected features recorded. Hosted Server
fixtures cannot stand in for client-only APIs. Expected drift is a classified
observation, not convergence; unavailable required capabilities block admission.
Known unsupported selections must be rejected or reported by their declared
contract, never relabelled as a successful supported configuration.

The matrix must distinguish supported, unsupported and unverified combinations.
Do not promise every Windows 10 feature or infer current OS support from the old
status table. Before approval, the Windows owner must choose client build and
feature boundaries using current upstream sources and native evidence. PowerShell
5.1 bootstrap and PowerShell 7 management remain separate paths. Pester 5.7.1 and
Lua 5.4.6 are current contributor pins, not consumer minimum versions.

Exact minimum Nix, macOS, Windows, PowerShell 7 and WinGet versions remain open.
Set them from upstream requirements and a passing oldest-supported test lane,
then exercise that baseline and the chosen current version. An installer action
version or a moving `*-latest` runner label is not a minimum-tool specification.
This evidence gap prevents calling these lanes pickup-ready today.

Budget full builds at promotion rather than at every feature PR. Native builders
may use caches, but a cache hit must still realize and verify the candidate's
outputs; it is not reuse of an old green check. A missing builder blocks the
promised lane instead of reducing support silently. The existing no-extra-runner
decision needs explicit reconsideration for this stronger guarantee. Measure
runner availability and cold/warm cost before choosing hosted or dedicated
builders. No provisioning, credential or host-global change is authorized here.

### Candidate identity, batching and failure

Keep one same-repository dev -> master PR and merge commits. One authorized
integration session records base master B, dev head H, the tested PR merge commit
P and its tree, selected domains, support-contract revision, tools and evidence
run IDs. Do not use a green check from another SHA. GitHub's `pull_request`
GITHUB_SHA denotes the PR merge commit, not necessarily H
([GitHub event documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)).

Immediately before an explicitly authorized merge, re-query B, H, checks,
conversations and competing promotions. Match the expected head in the merge
request. A changed base or head requires refreshed candidate validation. Keep
master strict-base false; the one-controller rule and base recheck matter because
the merge API's expected SHA guards the head, not an independently supplied base
([GitHub merge API](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request)).

After merge, inspect actual master commit M and its tree. Run required validation
on M before tagging, retaining post-merge verification under current policy.
Release validation explicitly selects the releasing domain's complete required
matrix, even if the latest master push skipped that domain. This also applies
when releasing an older commit reachable from master. A successful unrelated
or documentation-only push cannot fill the missing domain evidence.
Even identical trees are not yet an adopted cross-run evidence-reuse rule: source
metadata, locks, tool/environment versions and remote dependencies can matter.
Record P and M separately. If they unexpectedly differ in content or validation
fails, block tags and further promotion pending diagnosis; fix or revert through
dev and promote again. Do not rewrite master or move a published tag.

Use demand-driven promotion batches after one or more coherent dev outcomes have
passed. During the final expensive checks, agree a short integration pause to
avoid continuously moving H; this is an operating procedure, not a frozen branch
or extra release branch. If dev advances anyway, invalidate the old candidate
and validate the new one. Time-based promotion and unattended merge remain out
of scope; twelve-hour dependency refresh belongs to stage 3.

For infrastructure failures, rerun the same candidate and retain failure and
retry references. For source failures, repair on a domain-owned topic branch
through dev; never patch the promotion. Do not repeatedly rerun a deterministic
failure until it happens to pass. A blocked changed domain blocks that combined
promotion; to proceed without it, review a revert in dev rather than cherry-pick
a subset into master. Historical consumer pins remain available for recovery;
using them to roll back a host still requires deployment authorization.

The first transition is a full bootstrap of both present domains' contracts,
not a routine patch inferred from the last lock commit. Review the actual merge
tree and all included outcomes, resolve current provisional/migration conditions
through dev, and collect complete candidate evidence. The 539/7 snapshot is not
permission to reverse-merge, rewrite history or ignore old-only master changes.
If the approved provider contracts have not landed, do not describe the initial
promotion or tags as satisfying them.

### Semantic release proposal

Recommend `unixlike-v1.0.0` and `windows-v1.0.0` independently when each stable
contract is implemented and verified. Recommend maintaining one active major
line per domain initially; old tags remain usable but receive no implied backport
service. These choices were later accepted under AC9; see the dated stable-series
decision below. They were not inherited stage-1 decisions.
Windows ProjectVersion, manifest/state schema versions and a domain release tag
are separate concepts; define their mapping before implementation rather than
silently treating the current ProjectVersion 0.6.0 as a release-series decision.

Classify the cumulative unreleased domain result: major for a documented contract
break or removed support, minor for compatible public additions or deprecation,
patch for compatible corrections and routine dependency updates after review.
Aggregate to the strongest required bump, resetting lower components normally.
Conventional Commit types help locate changes but do not prove compatibility.
Reverted changes are reviewed against the final result, with the rationale kept.
This applies SemVer to the explicitly documented API
([SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)), not all upstream behavior.

A successful promotion with a releasable domain delta makes that domain eligible
for a tag; it does not create one. Repository-only changes need no domain tag.
Pure descriptive documentation changes normally need none; changes to promised
support or compatibility are contract changes even when expressed in prose.
Never publish the same version again, create a tag with no required evidence,
or use a major bump to excuse an accidental failing supported case. Intentional
breaks require a reviewed new contract, migration information and passing cases
for it. No new prerelease or moving major-alias scheme is proposed initially.

Keep old calendar tags immutable and recognize their original annotations by
explicit legacy identity. Do not numerically sort calendar tags together with
the new semantic series or allow a newly backdated tag to claim legacy status.
The planner, audit, annotation parser, fixtures and documented consumption examples
must migrate together. Re-check remote tag existence and target reachability
before creation and push. A failed push resumes only for the identical tag
object; any conflicting remote tag is an error, never a force push.

Retain annotated-tag-only publication. Proposed annotation fields are domain,
semantic version, target SHA, previous domain tag, contract/support revision,
template revision where relevant, compatibility summary/migration references,
and per-platform evidence rows with commands, exact tested SHA, run references,
tool/OS versions, feature selection and limits. Record evaluation, build, native
runtime and deployment separately. Required lanes must pass; optional unavailable
observations are named and cannot satisfy a gate. Windows evidence rows identify
synthetic/client environment classes, never private machine identities. The new
provider annotation form must explicitly replace the current Windows per-host
contract through governance. Deployment remains "not performed by release".

Homebrew updates, WinGet repositories, application stores and external version
managers remain mutable dependencies outside the flake lock. Record tested
versions and retrieval time where relevant; validate failure handling and
prerequisites. Do not claim reproducible installation or universal app runtime
compatibility. A detected supported-contract failure blocks the affected
candidate; fixing or pinning it belongs to its domain, not an evidence exception.

### Adoption map and next decisions

The prevented failures are admitting an unbuildable supported consumer to master,
tagging stale evidence, disguising a contract break as a patch, and coupling
unrelated domain releases. The repository maintainer owns acceptance.

| Concern | Proposed authoritative owner and implementation |
| --- | --- |
| Meaning of master and domain releases | Architecture/decision records; scoped invariants and Definition of Done |
| Candidate, retry, recovery and authorization procedure | CONTRIBUTING.md |
| Agent orchestration | Existing promotion/release workflow skill; no duplicate model adapter policy |
| Selection, candidate binding, version and annotation refusal | Repository tools, CI and fixtures; stable Required checks gate |
| Platform baselines and contract checks | Owning domain declarations, documentation and native tools |
| Adoption gaps | Scope status documents |
| Per-run evidence | PR/CI artifacts and immutable tag annotations |

Repository implementation must include positive and negative fixtures for wrong
source/duplicate promotion, moved B/H, stale evidence, missing platform rows,
unavailable required checks, unrelated-domain dispatch, malformed versions,
legacy spoofing, reused tags and unreachable targets. Domain fixtures prove
consumer behavior. Manual review covers compatibility classification, migration
clarity, support choices and annotation privacy; name the maintainer and the
reviewed revision as its evidence. A parser alone cannot prove semantic compatibility.

The full-build master choice is accepted and captured in repository AC5.
At this point initial 1.0.0 and one active major per domain were still choices;
they were subsequently accepted under AC9. Continue resolving the
precise support/tool matrix and native builder/client-check availability, and
the detailed candidate/release mechanism. Resolve those before adding further
stage-2 acceptance criteria to the existing scope-owned specs and matching
pending report rows. Refine R1/R2 and the dependent Unix-like/Windows lanes then;
do not create an approved stage-2 spec from unaccepted recommendations.
Stage 3 waits for those boundaries and grants no unattended integration,
tag creation/push or private-host update permission.

## Stage-2 support and builder investigation, 2026-09-27

The full-build admission decision above is accepted. During this investigation
the maintainer also chose to retain both Windows 10 and Windows 11 and begin
Apple Silicon macOS support at 26; the respective domain AC5 rows record these
scope decisions. Other matrix details and tool pins below remain
proposals for the next review, not additional accepted support promises.

### Source and environment observations

Context Bridge inspection refreshed provider dev e11bd136, public template
dcb8c6d and private consumer main f7f3010; GitHub agreed with these local heads.
Both connected checkouts were clean. The template still consumes provider
66fed098 and demonstrates an aarch64 OrbStack constructor. It is not already
testing current dev. Only source/pins and relevant ownership/evidence text were
read; no consumer lock, host declaration or external repository was changed.

The provider exports five synthetic NixOS instances, one Darwin instance and
one Home Manager instance. The source declares three build systems. Pinned
nixpkgs e94cb152ed51bd6e24eb4a41f1460252beb52cd2 identifies itself as
26.11.20260925.e94cb15; its `lib/minfeatures.nix` requires Nix >=2.18,
`lib/systems/default.nix` sets the Darwin deployment baseline to 14.0, and
`doc/release-notes/rl-2611.section.md` records removal of x86_64-darwin support.
These are upstream input properties, not proof of configs' oldest working tools
or of every application's oldest OS. Do not revive Intel Darwin merely because
the current provider constructor enum still admits it.

Read-only local probes found aarch64 macOS 26.6.2 and Nix 2.34.8. The already
running OrbStack Linux machine reported aarch64, Nix 2.34.8 and about 33.6 GiB
free in its Nix-store filesystem. UTM guests were stopped; none was started.
OrbStack 2.2.3 and UTM 4.7.5 are observed local application versions, not minimum
runtime guarantees. No native Windows PowerShell was available in this session.
Machine identifiers, addresses and private output names are intentionally absent
from this public research record. No host build or activation followed these probes.

A fresh evaluation on the local Mac with Nix 2.34.8 resolved all seven final
fixture derivations at provider e11bd136: five NixOS toplevels, the Darwin system
and the Home Manager activation package. This was an impure local-path evaluation
of the clean provider source with its existing lock, not a build or activation.
The five NixOS derivation hash prefixes match the earlier companion study.
No older Nix or macOS baseline was exercised.

### Proposed matrix and execution venue

| Build/generation system | Supported composition candidates | Preferred promotion venue |
| --- | --- | --- |
| x86_64-linux | NixOS WSL, VMware, AMD APU desktop; standalone WSL Home Manager | Explicit Ubuntu x64 hosted image, initially ubuntu-24.04 |
| aarch64-linux | NixOS UTM and OrbStack | Explicit native ARM hosted image, initially ubuntu-24.04-arm |
| aarch64-darwin | Apple Silicon Darwin | Explicit macOS ARM hosted image, initially macos-26 |
| Windows x64 (architecture proposal) | Core and supported opt-in combinations on Windows 10 only after the scope amendment; exact builds pending | windows-2025 for native suite/generation; separate Windows 10 client read-only evidence for client-dependent behavior |

All seven Unix-like fixture outputs must build, even though only three execution
platforms are necessary. Building a VMware fixture on native x64 Ubuntu is native
build evidence, not VMware runtime evidence. Hosted build environments need no
private consumer identity, secret or installed private host. The current two
Linux architectural lanes and Darwin lane need full-output coverage assertions
so an empty or accidentally reduced selection fails.

[GitHub's runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
lists these architectures and labels for public repositories. It also lists a
Windows 11 ARM runner; that does not prove x64 client behavior or authorize a
new Windows ARM support promise. Explicit labels still receive image updates:
record the actual image, OS, tool versions and candidate SHA in every result.

Prefer hosted full builds initially, with local native machines available for
diagnosis or separately collected evidence. This avoids making promotion depend
on a private VM being awake. It remains subject to a measured cold/warm build
spike: published standard-runner storage is 14 GB, while a complete graphical
closure can be large. Split fixtures into native jobs if needed without dropping
coverage. If hosted capacity is inadequate, return to builder design; do not
silently skip a fixture, expand emulation or configure a personal runner.
The existing no-extra-runner decision must be explicitly revised on adoption.

Accepted 2026-09-27: macOS 26 is the initial certified Apple Silicon OS baseline.
It matches the observed host family and has a hosted ARM lane. This is narrower
than nixpkgs' 14.0 deployment baseline. Supporting macOS 14 or 15 would require
a later support decision with their own checks and application constraints.
Later OS versions also need explicit validation. The later exact-tool review
below records the separate acceptance of hosted-first verification and tool
pins; none of these decisions provisions a runner.

### Tool versions: tested baseline rather than an invented minimum

| Tool | Observed/upstream fact | Proposed initial contract |
| --- | --- | --- |
| Nix | Pinned nixpkgs requires >=2.18; local Mac and ARM Linux have 2.34.8 | Pin 2.34.8 for initial validation; establish a lower supported version only with a complete passing lane, not from nixpkgs' guard alone |
| Nix features | Provider/consumer tooling uses flakes and nix-command | Require both explicitly; no host-global enablement is implied |
| Windows PowerShell | Current entry/bootstrap is 5.1-compatible | Preserve the 5.1 entry/bootstrap path and test it independently |
| PowerShell management | Current setup checks major >=7; upstream current LTS is 7.6.6 | Use a pinned 7.6 LTS patch as initial validation candidate; do not claim all 7.x from that source guard |
| WinGet | Required by current bootstrap/check; current upstream release is 1.29.380 | Probe the existing client version and all used CLI flags before choosing the oldest tested pin; upstream latest is a candidate, not an installed-host fact |
| Pester/Lua | windows/toolchain.json pins 5.7.1 / 5.4.6 | Keep as contributor validation dependencies, not consumer minimum requirements |

The upstream release observations came from the official
[PowerShell v7.6.6 release](https://github.com/PowerShell/PowerShell/releases/tag/v7.6.6)
and [WinGet v1.29.380 release](https://github.com/microsoft/winget-cli/releases/tag/v1.29.380).
[PowerShell's lifecycle](https://learn.microsoft.com/en-us/powershell/scripting/install/powershell-support-lifecycle?view=powershell-7.6)
identifies 7.6 as LTS. A tool update is reviewed and tested at an exact patch;
"latest" must not silently replace the recorded evidence identity. A baseline
pin is not a promise that every greater version works. Installed tools were not
updated during this investigation.

Earlier decision, superseded by the Windows 10-only amendment below:
preserve Windows 10 and 11 with explicit capability boundaries.
Actual x64 Windows client OS edition/build, PowerShell, WinGet, WSL and selected
application versions still need a read-only inventory before certifying a floor.
A stopped VM's name does not establish its architecture or installed versions.

Do not compress Windows support into one minimum OS number. For example, the
existing terminal-delegation contract requires Windows 11 22H2 or Windows 10
19045.3031 and Terminal 1.17+, whereas WinGet's own documented OS floor is
Windows 10 1809. The former does not follow from satisfying the latter
([Terminal policy](https://learn.microsoft.com/en-us/windows/terminal/group-policy),
[WinGet installation](https://learn.microsoft.com/en-us/windows/package-manager/winget/)).
Lower-build terminal delegation remains a known support limit, not success;
the selection/feature contract must describe it before a release can claim it.

For WSL, distinguish guest consumption from Windows-owned .wslconfig features.
Pinned NixOS-WSL recommends Store WSL2 and associates >=2.4.4 with the .wsl
installation transport; it documents an older import route too. Thus 2.4.4 is
not established as the minimum guest runtime. Current Windows-owned payloads
have their own WSL/application/build checks, including mirrored-networking and
DNS conditions. Preserve those independently rather than impose a cross-domain
release dependency ([WSL configuration reference](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)).

Next review should settle the remaining architecture/composition matrix and
tool pins, then assign the missing native client inventory and hosted capacity
measurements as evidence tasks. Windows 10-only support (as subsequently amended)
and the macOS 26 starting baseline are accepted; no support row becomes verified
merely by being selected.

## Stage-2 exact-tool and CI evidence review, 2026-09-27

Accepted during this review: explicitly use upstream Nix 2.34.8 and PowerShell
7.6.6 for the initial CI verification baseline; retain Windows PowerShell 5.1
entry/bootstrap coverage. The respective domain AC6 rows record the decision.
These are reproducible verification inputs, not newly imposed minimum host
versions and not authorization to install or update software on private hosts.

### What current CI actually proves

Read-only inspection of [Windows run 36226424647](https://github.com/shk95/configs/actions/runs/36226424647)
at cf76ddeeba7e8bc827efb96e3d74bcb4164d80df found 320 tests passed, zero failed
and one skipped. Its Windows job ran from 07:19:39 to 07:22:28 UTC on 2026-09-26.
The logged runner was windows-2025-vs2026 image 20260922.246.2; that exact
[image manifest](https://github.com/actions/runner-images/blob/win25-vs2026/20260922.246/images/windows/Windows2025-VS2026-Readme.md)
lists PowerShell 7.6.6. The logs show Pester 5.7.1 installation. The suite's
non-Windows capture-refusal case intentionally skips on native Windows; skipped
is not passed. No Windows-source diff was present from this commit to inspected
dev e11bd136, but this remains historical evidence, not a run on a new candidate.
The runtime version was not independently emitted by the job; the image manifest
is the source of the PowerShell version observation.

Neither the inspected job log nor its image manifest established the actual
WinGet version. Successful Lua/Zellij installation proves those operations on
that runner, not an oldest-supported WinGet or Windows client check. Source
inspection found package presence uses `winget list` exit statuses, not parsed
table text; validate success, known absence and other-error outcomes on the
chosen client version. WinGet remains an explicit open evidence item.

[Unix-like run 36231842628](https://github.com/shk95/configs/actions/runs/36231842628)
at e11bd136 explicitly logged installation of Determinate Nix. The checked-out
installer action v22 resolved to ef8a148080ab6020fd15196c2084a2eea5ff2d25 and its
default is `determinate: true`. Thus this historical CI cannot be described as
upstream Nix 2.34.8 merely because local Nix or a package in the build has that
version. Installer version, client implementation/version and daemon version
must be separate evidence fields where they differ.

The action's pinned README says upstream-install support ends on 2026-01-01.
Do not assume changing only `determinate: false` is a supported migration now.
The official Nix 2.34.8 Git tag exists and its
[versioned installation script](https://releases.nixos.org/nix/nix-2.34.8/install)
returned HTTP 200 during a read-only request; nothing was executed.
An upstream-capable installer such as
[install-nix-action](https://github.com/cachix/install-nix-action) exposes an
explicit `install_url`. Select an immutable installer revision, verify the
versioned artifacts and actual installed Nix on all three native systems before
claiming AC6. Choosing this mechanism is implementation work, not a host change
authorized by the version decision.

### Evidence tasks before admission is implemented

1. Validate installation and reported versions on the proposed native hosted
   images. Preserve all existing suite results while changing the installer;
   neither a missing prerequisite nor a different implementation is a pass.
2. Measure complete fixture builds on the exact provider candidate: elapsed
   time, initial/minimum free disk, memory pressure and realized outputs. Compare
   cold and warm cache runs. Split by fixture if needed; coverage stays complete.
3. Collect read-only Windows 10 client inventory: OS edition/build and
   architecture, PowerShell executable/version, WinGet version, WSL version and
   selected feature/application versions. Record known limits and unavailable
   observations separately; omit private identity. Do not install, restart or
   Apply merely to fill this inventory.
4. Test the actual Windows generation/Check path and WinGet exit behavior on
   the selected client versions. Then select a supported WinGet baseline with
   evidence; the latest upstream release alone is insufficient.

The repository is public and GitHub reported zero registered repository
self-hosted runners during this review. This describes configuration, not
hosted capacity or permission to provision a runner. The maintainer accepted
hosted-first full builds with separate Windows client evidence; repository AC6
records this venue decision. No new workflow, runner, CI run, release or host
operation was created.

### Windows 10-only local availability: superseded scope analysis

The consequences below were assessed while both Windows 10 and 11 remained
support targets. The subsequent explicit scope amendment removes the Windows
11 gate described here; this section is historical analysis, not current pickup
instructions.

The maintainer raised the current constraint of having a Windows 10 validation
environment but no Windows 11 one. This is user-provided availability, not a
fresh native inventory. Do not infer availability from a stopped VM name or
start/provision a guest to fill the gap without a separate task.

Windows 10 and hosted Windows Server can still supply their own native suite,
generation and read-only evidence. Synthetic build/version cases prove branch
selection and refusal behavior; they do not prove the Windows 11 operating
system implements the selected behavior. Client-only Appx routes, terminal
delegation and Windows 11 WSL/networking behavior need their named native
environment. Neither Windows 10 success nor a mocked build number fills it.

Keep Windows 11 in the agreed support target and mark absent native evidence
unavailable. Before admission implementation, enumerate which generation and
runtime criteria require that client environment, using changed behavior and
the support contract rather than runner availability to decide. A required
Windows 11 row without evidence blocks its affected candidate under AC5; do not
quietly defer it to tagging or label the release fully verified. Unchanged
unrelated Unix-like work does not acquire a Windows prerequisite, while a batch
that also changes affected Windows behavior must satisfy the Windows gate.

The hosted Windows 11 ARM lane is an investigation option for ARM client
semantics, not a substitute for x64 acceptance or a decision to add ARM support.
If x64 Windows 11 behavior remains required, obtain an appropriate client
environment/evidence or explicitly revise the promised coverage through planning.
An explicit review of coverage would be a new decision; the availability
question alone does not narrow the already accepted Windows 10/11 scope.

### Accepted amendment: Windows 10-only support and verification

Amended 2026-09-27: after reviewing the absence of a Windows 11 verification
environment, the maintainer explicitly chose Windows 10 only. Windows AC5 and
repository AC6 now reflect this reduced support and evidence matrix. This
replaces the earlier support choice; it is not a waiver that calls missing
Windows 11 evidence passed.

Windows 11 is outside the initial supported contract. It is not an outstanding
required lane, a promotion blocker, or a promised later runtime check. No
Windows 11 client/ARM runner investigation is required for this plan. A future
addition needs a separate support decision and its evidence. Hosted Windows
Server remains a suite/generation venue, not another supported consumer OS.
Required Windows 10 client evidence remains separate, and all required rows in
the reduced matrix must pass before the applicable promotion/release boundary.

Retain the initial PowerShell 7.6.6 CI baseline and Windows PowerShell 5.1
bootstrap checks. Determine the exact Windows 10 edition/build, architecture,
WinGet version and feature/application limits from native evidence. Windows 10
support does not turn unsupported terminal delegation or Windows 11-only WSL
capabilities into available Windows 10 features.

This amendment changes plans only. Existing implementation branches, build-based
payload variants and historical evidence have not been deleted or reclassified
as failures. Their future documentation/validation treatment belongs to the
Windows implementation lane. No host update, Apply, commit or publication was
performed by this scope decision.

### Accepted amendment: LTSC client baseline and delegation exclusion

Amended 2026-09-27: after read-only native inventory and an explanation of
default terminal delegation, the maintainer accepted the Windows AC5 amendment:
Windows 10 IoT Enterprise LTSC 21H2 x64, build 19044 is the initial client
baseline. The observed revision is 19044.7725. Retain Windows Terminal settings,
fonts and profiles; default terminal delegation is outside this baseline's
guarantee. Windows 11 remains outside the supported matrix.

The native inventory, exact installed versions, probe boundaries and source
implications are recorded in docs/work/windows/host-consumer-contract/study.md.
PowerShell 7.6.6 is installed; WinGet 1.29.380 is observed but its verification
pin/minimum compatibility contract is not yet accepted. No provider native
suite, generation, host Check or Apply was run during inventory.

Repository AC5/AC6 still require complete applicable evidence before promotion.
The capability exclusion defines the promised Windows matrix, not an exception
that passes missing evidence. Windows implementation must reconcile the explicit
capability contract with existing Check/REQUIRE_NATIVE behavior and repository
gate selection before this matrix is operational. Current support-limit policy
and gates remain authoritative in the meantime. Candidate evidence must identify
the baseline, included capabilities and excluded delegation guarantee, and must
not suppress unrelated drift or unavailable observations.

### Next decision: bind release evidence to its target, 2026-09-27

This is a proposal awaiting the maintainer's choice, not an added acceptance
criterion. Read-only remote recheck still found dev at e11bd136 and master at
2542d77, with no open PRs. No candidate was created or merged.

GitHub documents that a pull_request run's default GITHUB_SHA is the temporary
PR merge-branch commit. Record that tested candidate P separately from the
actual master merge commit M. The merge API's expected sha guards the PR head,
not an independently supplied master base. These details support the candidate
identity and final base/head recheck proposed above; they do not themselves
require one particular evidence-reuse policy.

| Choice | Required work and tradeoff |
| --- | --- |
| Recommended initial rule: validate the actual release target | Full affected-domain validation on P before promotion; run the releasing domain's complete required matrix against M (or the explicitly selected reachable release target) before tagging. More runs, with direct tested-SHA evidence and no cross-SHA evidence equivalence mechanism. |
| Design evidence reuse first | Prove equivalence of source tree, revision-dependent inputs, locks, tools, support/consumer fixtures and relevant environment observations before reusing any P evidence for M. Saves repeated work only for cases the rule can actually prove; missing equivalence requires rerunning. Tree equality alone is insufficient. |

For the recommended initial rule, applicable Windows client checks are also
target-bound: fresh read-only inventory alone cannot stand in for testing the
provider at that target. Excluded LTSC terminal delegation remains outside the
guarantee. Required supported-capability observations must pass; neither hosted
Server success nor a previous client Check can fill a missing required row.
Apply remains separately authorized and is not part of this release action.

Rerunning a build may consume valid cached outputs; it does not require a cold
rebuild. Report actual cache use and elapsed cost rather than promising a cache
hit or a fixed duration. A later tag on an already validated exact target can
refer to its complete target-bound release-validation record; this choice is
about crossing commit identities, not mandating a third run just to create a
tag. Changed support/tool/consumer inputs or relevant new failures require
revalidation, and mutable external observations must retain versions and times.

Sources checked again during this decision:
[GitHub PR workflow event](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request)
and [merge API](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request).
Do not change AC1-AC6 or mark report rows verified until a choice is accepted
and its eventual implementation is separately evidenced.

### Maintainer direction: promotion and host change discovery, 2026-09-27

The maintainer clarified that repository and documentation changes may also
enter master. This replaces the preceding discussion's suggestion to wait for
a host-output change before initiating every promotion. Source promotion and
consumer release discovery are separate decisions: a promotion need not create
a domain release. Required policy and affected-contract checks still apply.

The desired consumer behavior is programmatic discovery of releases and of
changes to the host's selected machine configuration. Configs should provide
machine abstractions. Whether ownership scopes need subdivision is a design
question, not an accepted classifier or directory change. Automatic promotion
and release are under design, not authorized or implemented by this discussion.

Recommended design, awaiting review:

- Retain unixlike/windows/common ownership and repository governance. Introduce
  stable consumer configuration IDs within each active domain rather than using
  new Git scopes to represent every build output. Common is presently reserved:
  the inspected classifier has no active common/ arm; adoption must establish
  its contract and checks before there is a common consumer release.
- Keep domain versions independent. Publish a machine-readable release inventory
  mapping supported configuration IDs and variants to their verified artifact
  identities, contract compatibility and evidence. A newer domain version need
  not change every configuration. Additions, removals and incompatible formats
  must be explicit; missing/unknown records must not mean unchanged.
- Separate artifact identity from source revision, release version and evidence
  metadata. Record all of them, but a change in provenance alone must not be
  mistaken for a changed machine payload. If provenance is actually embedded in
  consumed payloads, report that real change rather than silently erasing it.
- Include the complete consumption boundary: Unix-like final outputs and their
  required runtime closure; Windows generated payloads and the required
  generation/check/application tools, schema and dependency selection. A payload
  hash alone cannot describe a changed Windows management engine. Public API or
  support changes need a separate contract signal even when a default artifact
  stays identical. Digest equality is not proof of runtime equivalence.
- Standard provider configurations permit remote inventory comparison. Arbitrary
  host customizations require a second local comparison: hold host declarations,
  customizations and non-provider inputs fixed, select the old/new provider, and
  evaluate/generate both. Treat changed, unchanged, incompatible and unable to
  determine as distinct outcomes. Input comparison is not completed build proof;
  exact artifact comparison requires available realized artifacts. Neither
  discovery nor comparison authorizes activation, Apply or an automatic pin edit.
- Compare discovery against the host's recorded consumed release/configuration
  identity, not merely the immediately preceding global release. Track detected,
  selected and deployed versions separately so a declined or failed update is
  not lost. Upstream mutable package versions remain an independent observation;
  a provider inventory cannot certify future external installation results.

An initial publication option consistent with annotated-tag-only releases is
a versioned machine-readable inventory in the tag annotation. It binds an
already verified target commit and artifact identities without committing a
self-referential target SHA or generated post-build record back to master.
An external downloadable index would be a separate publication decision with
its immutability and integrity rules; no GitHub Release or new artifact service
is adopted here. Define schema, stable IDs, digest boundaries, compatibility,
verification evidence and host-side selection before implementation.

This clarification does not accept either pending cross-commit evidence choice
above, or silently relax repository AC5's full supported-platform build bar.
Selective rebuilding and evidence reuse still need an explicit, testable
identity and coverage rule before amending that criterion.

### Configuration subscription design, accepted 2026-09-27

Source inspection at e11bd136 confirms seven existing Unix-like fixture
compositions in unixlike/modules/flake/configurations.nix and fixtures.nix.
Only the NixOS WSL composition currently offers the optional agents profile.
Windows desired/manifest.json declares core, font, zellij, terminal, wezterm,
powertoys and wsl; core is required, terminal requires font and zellij, and
wezterm requires font. This inventory is source evidence, not a new support
approval, build result or consumer-facing ID implementation.

Accepted subscription shape: stable machine-kind ID plus architecture,
with explicit selected profiles/features and support-baseline metadata.
Maintain one independent version per domain. The unselected alternative was
a separately named ID for each fixed feature combination; it increases
catalog size and makes ordinary feature selection a catalog change.

| Planned machine ID | Initial architecture | Consumption boundary |
| --- | --- | --- |
| unixlike/nixos-wsl | x86_64 | NixOS toplevel including managed Home Manager; agents optional |
| unixlike/nixos-vmware | x86_64 | NixOS toplevel including managed Home Manager |
| unixlike/nixos-utm | aarch64 | NixOS toplevel including managed Home Manager |
| unixlike/nixos-orbstack | aarch64 | NixOS toplevel including managed Home Manager |
| unixlike/nixos-desktop-amd-apu | x86_64 | Current AMD APU desktop composition's NixOS toplevel; physical runtime remains separate |
| unixlike/darwin | aarch64 | nix-darwin toplevel including managed Home Manager; initial macOS 26 baseline |
| unixlike/home-wsl | x86_64 | Standalone Home Manager activation package |
| windows/client | x86_64 | Selected generated configuration plus required management tools and format; initial IoT Enterprise LTSC 21H2 build 19044 baseline |

These are planned public IDs, not personal host names or current flake output
attribute names. Publishing them must include a reviewed mapping to supported
constructors and synthetic cases. The table does not extend desktop hardware,
Windows editions or macOS versions beyond separately approved support. IDs
should not contain routine application versions, OS patch revisions or release
numbers; record those in compatibility/evidence metadata. A semantically
different machine family needs a distinct ID or explicit migration.

Keep requested selection and resolved dependency closure distinguishable. For
example, Windows terminal selection resolves to core,font,zellij,terminal, and
a font change may affect that consumer without a direct terminal-file edit.
The generated selection identity must include generator/management-engine and
contract dependencies, not merely a set of payload hashes. Define deterministic
encoding and preserve any ordering that has semantics before hashing it.

Shared Home Manager content is already inside NixOS/nix-darwin results and
must not become a second independently selected update for the same managed
user. Standalone home-wsl remains a distinct consumption path. Windows wsl
means Windows-side WSL settings; it is not the Unix-like NixOS WSL guest and
does not imply that one domain deploys or versions the other.

Do not enumerate all arbitrary feature/customization combinations as certified
public artifacts. Publish precisely which standard variants were tested, and
use selected-dependency impact plus local generation/evaluation for others.
Unlisted selections cannot inherit a false unchanged/verified result. Exact
selection, local customization and non-provider inputs belong to host-side
comparison; private values must not be copied into public release records.

The maintainer accepted this shape after reviewing the catalog and the example
of separate Windows terminal/wezterm selection. The adjacent spec now records
the planned IDs and adds AC7; its report remains pending. Complete variant
evidence coverage, detailed support validation and artifact digest format are
subsequent decisions. AC5 and the pending cross-commit evidence-reuse choice
are unchanged. No classifier, constructor, generator or release tool changed.

### Artifact comparison boundary, accepted 2026-09-27

The maintainer confirmed the recommended boundary and asked to continue.
The adjacent spec records it as AC8 with pending implementation evidence.
Compare what configs supplies to
the selected consumer, including its necessary dependencies and management
tools, and report public-contract changes separately. External unpinned
application versions are a separate environment observation; making all of
them pinned reproducible artifacts would require an additional domain design.

Source observations at e11bd136:

- unixlike/tool/checks/test selects config.system.build.toplevel for NixOS
  and Darwin, and activationPackage for standalone Home Manager. The proposed
  release artifact comparison covers these realized results and their runtime
  dependency closures, plus any separately consumed provider tools.
- unixlike/modules/platforms/homebrew.nix declares applications and activation
  behavior, with autoUpdate and upgrade enabled; installed external app bytes
  are not all supplied by the Nix store closure. The declaration and generated
  activation logic belong to the provider artifact; future external versions
  cannot be certified by equality of that artifact.
- Windows win-env.ps1 forwards to tool/bootstrap.ps1 and other consumer tools;
  tool/setup.ps1 imports src/WinEnv.psm1. Comparing settings alone would miss
  changes to the code interpreting or applying them.
- Get-WinEnvDesiredStateHash currently hashes all of manifest.json and selected
  payloads, including every declared OS variant for those selected items. It
  does not hash the management engine. Its existing drift/state purpose is not
  the proposed precise per-configuration release-discovery contract; neither
  reuse it unchanged nor modify it as a side effect of this planning discussion.

Proposed externally distinguishable signals:

| Signal | Meaning |
| --- | --- |
| Artifact change | Supplied configuration, realized runtime dependencies or required consumer tools differ for the selection |
| Contract change | Supported inputs, formats, capabilities or support conditions differ, even if a default artifact stays the same |
| Environment change | Observed host prerequisites, mutable external app versions or live drift differ; not a provider artifact release by themselves |
| Provenance-only change | Release/source/evidence metadata differs while the separately compared supplied artifacts and contract remain equal |

Use independently identifiable payload and tooling components where useful so
a tooling update need not be presented as changed deployed settings. Shared
management-engine changes conservatively affect its consumers unless narrower
dependencies are proven. Do not claim semantic equivalence of arbitrary scripts
from tests or attempt to strip executable differences from the artifact digest.

For Nix, derivation/input changes identify work to investigate or build; they
are not a completed content comparison. The realized closure comparison must
retain dependency references, not hash only a top-level display file. Use a
versioned deterministic inventory of actual artifact identities/content;
timestamps, registration details and CI run IDs are evidence metadata rather
than payload identity. If source/version information is actually embedded in a
consumed artifact, report it honestly instead of deleting it from comparison
without an explicit, validated separation. Byte identity is not runtime proof.

For Windows, include selected and required-feature payloads, their effective
declarations, consumer tooling and interpreted format. Validate target baseline
and selected source variants explicitly. Preserve comparisons of public
provider artifacts separately from private host-bound generated results.
Pin/download directives and declared hashes belong to provider inputs; bytes
later supplied by mutable WinGet or application-store sources are environment
observations unless an explicit immutable artifact contract captures them.

All signals must distinguish known equality/difference from missing data or
incompatible inputs. Hold the same host input and non-provider dependency
choices during old/new provider comparison; report host changes separately.
No comparison invokes activation/Apply or persists a new host pin. Initial
build coverage, exact digest encoding, publication and evidence reuse remain
open; this decision does not weaken AC5 or mark any report row verified.

Reference: [Nix path-info](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-path-info)
supports recursive store information and JSON output but does not itself build
or substitute the queried results. Tool output must be converted to an explicit
versioned inventory, not assumed to be an immutable public schema.

### Initial stable series and maintenance, accepted 2026-09-27

The maintainer accepted both recommendations. The adjacent spec records AC9;
implementation evidence remains pending. Start
each domain's first implemented and verified stable consumer contract at its
own 1.0.0, preserving immutable calendar tags outside the new numeric series.
Unix-like and Windows may reach that point on different dates; no release is
being created by this planning choice. Windows ProjectVersion 0.6.0 and schema
versions are not proof that the provider domain has already begun its stable
semantic series. Their implementation mapping still needs explicit treatment.

Maintain one major per domain initially. After an intentional
2.0.0 transition, old 1.x tags remain available, but receive no promised fixes
or backports. A host may stay pinned; discovery can report a newer major and
the maintenance status separately without automatically changing the pin.
Publishing an immutable pin does not guarantee indefinite external download
availability or support for the old environment.

The alternative initial 0.x series allows unstable public contracts before
1.0.0 and needs an explicit preview-selection policy. Maintaining two majors
would require a backport, verification and source-promotion design in addition
to the existing dev -> master line. Neither alternative is silently adopted.
SemVer defines version compatibility, not a maintenance duration; the latter
is a maintainer policy choice. These choices do not create a release or
authorize automatic publication. A fresh read-only remote query still found
only unixlike-v2026.08.31 and windows-v2026.08.31 for these two domains;
recheck tag existence and target evidence at actual publication time.

Reference: [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html).

### Version classification for automation, accepted 2026-09-27

The maintainer accepted structured, mechanically evaluated classification and
explicitly required operation without an agent/adapter layer. AC10 in the
adjacent spec records this requirement with pending implementation evidence.
Declare release impact with each domain-owned change before dev
admission, then having release automation aggregate accepted declarations and
candidate evidence from that domain's last release to the target. Use none,
patch, minor and major with affected configuration/profile/feature identities
and a short compatibility rationale. Declare migration for an intentional
break. Commit types are hints, not the compatibility authority.

Keep the durable declaration with its owning domain and reviewed change;
do not make every domain PR cross-scope by putting its declaration in a
repository-owned directory. Exact format/path is implementation design.
Bind classification to the reviewed revision; mutable labels alone cannot
silently change the accepted release impact after source integration.

For each domain, aggregate cumulative effective changes to the strongest
required bump. Several patches yield one next patch release, not one version
increment per commit. A minor plus patches yields one next minor; an accepted
major plus lower changes yields one next major. No consumer artifact or public
contract delta means no domain tag, even though docs/repository source may be
promoted. Reverts/cancellations require explicit net-change reconciliation;
do not blindly count a reverted feature or silently erase a promised migration.

Tests and artifact/contract comparison corroborate the declaration but cannot
prove all semantic compatibility. Missing classification, detected contract
breaks declared as patches, or mismatched coverage stop publication rather
than defaulting to a patch or guessing a major. A new major cannot excuse a
failed supported case. Any authorized automatic dependency-refresh classifier
must have its own reviewed rules and stop conditions in stage 3; this decision
does not impose or approve a new unattended dev integration procedure.

Alternative: infer versions primarily from Conventional Commit messages.
It needs less explicit metadata but cannot distinguish a compatible change
from a breaking provider/input/support change solely by feat/fix/chore labels.
This alternative was not selected. The accepted method uses structured data
preserved in commits, not semantic inference from free-form commit messages.
It is about version intent, not permission to merge or publish a candidate.

Ordinary CLI/CI tools must reproduce the result from the complete input set:
history, release baseline and candidate, structured declarations, versioned
rules and explicit evidence records. Same inputs yield the same version or
refusal. Agent adapters may write inputs or call these tools, but cannot be a
required classifier, missing-data repair step or unrecorded decision source.
PR labels/descriptions alone are insufficient because they can change outside
the source history. Test all of this without an agent runtime.

The conversation's Release-Domain, Release-Impact and Release-Configurations
trailers were format examples, not an adopted exact schema. Choose encoding,
merge/revert traversal and initial legacy-history migration during detailed
design; do not rewrite immutable history to add new declarations. No parser,
workflow, classifier or runtime source was changed by this acceptance.

### Next decision: declaration storage and history traversal, 2026-09-27

Recommend storing release declarations as structured trailers on the change
commit. Alternative: a committed structured record inside the owning domain.
Both can satisfy AC10; trailers bind directly to the Git commit without adding
metadata files to consumer source trees. File records allow ordinary content
edits but need explicit record identity, revision and duplicate handling.
The storage choice is awaiting the maintainer; the sample below is not an
adopted schema or an implemented command contract.

```text
fix(unixlike): correct WSL configuration

Release-Schema: 1
Release-Scope: unixlike
Release-Impact: patch
Release-Target: unixlike/nixos-wsl@x86_64
Release-Reason: Correct existing supported behavior.
```

Use ownership scope here, not a false repository configuration domain. Check
it against actual classified paths; do not trust the Conventional Commit
subject's scope, which can describe a different domain than path ownership.
The full machine/architecture example conservatively covers all supported
selections of that configuration; narrower profile/feature selectors need an
explicit grammar and dependency checks, not an interpretation of prose.

Source e11bd136's commit-msg hook currently checks subject grammar and closing
keywords, and exempts Git-written merge/revert subjects from subject grammar.
It does not implement release trailers. The future release validator must
not inherit that exemption as permission to skip release-impact checking.
Native Windows authoring and ordinary Git/CLI operation must remain viable.

Read-only local parser probe on Git 2.55.0 passed the sample through
git interpret-trailers --parse --no-divider on stdin and returned the five
fields intact. No commit, Git configuration or source file was written.
This demonstrates syntax extraction only, not schema validation, graph
traversal, cross-platform support or release classification. Exact parser
options/version support and strict rejection of duplicate singleton fields,
unknown schema, invalid values and disguised/missing fields require fixtures.

Proposed traversal constraints to complete after the storage choice:

- Inspect the unique commits reachable from the release candidate but not
  from the preceding domain release; include topic history, not only merge
  subjects or first-parent titles. Refuse an invalid baseline or incomplete
  history instead of calculating from an arbitrary shallow range.
- A pure integration/promotion merge does not repeat its parents' declarations.
  Do not ignore every merge: conflict-resolution changes or other merge-only
  content need coverage and verification of the actual result. The exact
  reproducible detection and declaration rule needs implementation fixtures.
- Reverts reference exact objects and are evaluated against the cumulative
  effective result. Never subtract a version number or cancel impact merely
  because the title starts with Revert. A revert of already released behavior
  is itself a new change; a revert-of-revert needs explicit deterministic handling.
- Correct published declarations through reviewed follow-up records referring
  to exact commits, without amending/rebasing published history. Define conflict,
  ordering and supersession rules; ambiguous corrections stop publication.
  Correction record encoding remains open, not a blanket override capability.
- Define a reviewed initial-release boundary for legacy commits without the
  new metadata. Do not label all old commits none or rewrite their history.
  Continue requiring the complete first-release contract evidence.

Sources: [Git trailer parsing](https://git-scm.com/docs/git-interpret-trailers)
and [Git revision traversal](https://git-scm.com/docs/git-rev-list).
No acceptance criterion is added for the unselected storage format yet.

## Machine release manifests: research and critical review, 2026-09-27

### Question and recommendation

The maintainer proposed separate release files for each machine, then requested
research including criticisms. Recommend this as a machine-oriented discovery
and consumption interface while retaining independent domain SemVer. Treat
machine files as generated release results and change declarations as reviewed
source inputs. They serve different purposes and must not become competing
hand-maintained descriptions of the same release.

The preceding trailer recommendation remains a historical proposal. The later
discussion explored in-domain structured files and per-machine output files;
neither exact encoding nor final storage location has been adopted. Keep AC10's
agent-independent deterministic requirement whichever representation is chosen.
This research changes only the study, not accepted policy or AC1-AC10.

The principal qualification is that configs currently provides constructors
and desired-state material. It does not produce one universal prebuilt image
for every private host. A machine release record can bind the provider recipe,
supported selections and verified reference outputs. An arbitrary customized
host still needs its own input lock and verification.

### Evidence inspected and its limits

Read-only inspection on 2026-09-27 found provider dev at
e11bd1368d2f5138ad0f9b7017040b2b76e055e6 and master at
2542d77c09823417c62c179f4c69d9f7f5ba51ae. GitHub returned no open PRs and an
empty release list. This does not inspect or enable immutable-release settings.
The repository doctor passed. No implementation, build, activation, Apply,
publication or private-host adoption was performed for this investigation.

The public configs-host-template checkout and remote HEAD both resolved to
dcb8c6d81ebd72ca4b19e8364269494ffcbdc5c2. Its synthetic example already pins
provider revision 66fed0985e6cf6f8a8e5eab1cce4f1b7ab21d39d and a source narHash
in an independent host lock. Machine manifests therefore add relevant-change
discovery, compatibility information and evidence association; exact source
pinning is already possible. No private host implementation was inspected.

Provider constructors accept identity and host-owned systemModules/homeModules.
These can change outputs beyond a public reference fixture. Current reference
configurations also do not cover every supported selection: the WSL reference
selects agents, which alone does not verify the unselected variant.

Windows manifest inspection found required core and six optional features.
A jq enumeration of dependency closure produced 64 requested subsets and 32
distinct resolved selections. For example terminal includes font and zellij;
terminal plus wezterm shares font. This is manifest arithmetic, not native
Windows execution or verification of 32 working configurations.

Get-WinEnvDesiredStateHash currently hashes the whole manifest plus selected
payload files, including their OS variants, but not the management engine.
That drift hash is not a complete or sufficiently precise release identity:
unselected metadata may change it, while engine behavior can change without it.
The setup path also warns that project-version downgrade is disabled. An old
release pin must not be advertised as a tested Windows deployment rollback.

### Distinct identities and what a host pins

Use three linked records with separate responsibilities:

| Record | Responsibility | Must not imply |
| --- | --- | --- |
| Domain release root | Domain version, exact provider source revision, schema and digests of machine records | Every private host has identical output |
| Machine record | Stable machine ID, architecture, supported selection rules, contract/artifact identities and bounded evidence | A new version whenever its containing domain releases |
| Host-local lock | Chosen release/root digest, source revision, resolved machine selection and host-owned inputs | The host has applied the configuration |

Deployment state and local verification are separate from the desired pin.
A domain release can update one machine's artifact while carrying forward
another's artifact identity. Record lastArtifactChange as explanatory history;
do not use it alone to choose the provider revision. A later release can retain
the same artifact while changing compatibility, support status or evidence.
Silently pinning the older source would also discard those changes.

Retain AC7's machine-kind plus architecture identity and separate selections.
An illustrative bundle layout is:

```text
release.json
machines/nixos-wsl/x86_64.json
machines/nixos-orbstack/aarch64.json
machines/darwin/aarch64.json
```

This is a Unix-like release bundle example, not an approved tracked-file path.
Windows has its own root and client record. A host resolves one machine from
one complete release snapshot; it must not combine individually fetched latest
files from different snapshots. Machine IDs should remain stable across path
reorganization. Renames/removal need explicit migration information.

The root binds machine records using algorithm, digest and byte size. Records
bind artifact descriptors and evidence to exact inputs. A digest verifies
content identity; trusted signatures/attestation or an independently trusted
expected digest establish provenance. A moving latest pointer only assists
discovery and is never the reproducible pin.

Nix locked rev/narHash identify fetched source, not the realized machine output.
Compare provider source, selected contract and output identities separately.
The Nix flake interface exposes source revision metadata to evaluation, so
release-metadata-only commits cannot universally be assumed output-neutral.
See [Nix flake references and locks](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake.html).

### Main criticisms and mitigations

1. **Precision can be overstated.** A filename naming a machine says nothing
   about whether dependency analysis is sound. A shared module or Windows
   engine change can affect many machines/features. Use conservative dependency
   coverage and explicit unknown/refusal states. A claim of unchanged needs
   evidence, not merely an unchanged machine-specific source directory.
2. **Variant count grows quickly.** Even today's Windows choices resolve to 32
   combinations before adding OS baselines or host extensions. Distinguish
   supported selections from cases actually checked. Dependency closure,
   exclusions and coverage must be machine-readable. Sampling cannot silently
   replace the accepted complete supported-platform gate; any evidence-reuse
   or reduced-combination rule needs a separately accepted justification.
3. **Reference outputs are not customized host outputs.** Provider fixtures
   establish bounded contracts. For arbitrary host extensions, compare old and
   new provider selections with the other host inputs fixed locally. Evaluation
   can expose planned changes; realized-byte equivalence requires appropriate
   builds. Do not upload private host identities/configuration into public
   release records to make this comparison possible.
4. **A pin does not freeze the external world.** Homebrew/WinGet repositories,
   downloads and machine state can vary. Current Darwin activation requests
   Homebrew update/upgrade. Record provider-controlled configuration and the
   separately bounded external-dependency policy; do not claim pinned future
   package bytes where the provider does not control them.
5. **Rollback has several meanings.** Restoring a manifest, recovering a store
   closure and safely reversing applied configuration are different operations.
   Old tags do not guarantee cache retention, downloadable packages or reversible
   application data. Preserve release records; define artifact retention and
   test domain-specific recovery before advertising rollback support.
6. **Hand-maintained machine files drift.** A common fix could require many
   repetitive edits, with omissions or contradictory versions. Authors should
   declare change intent once and tools derive affected records from inputs and
   evidence. Intent can be checked mechanically, but arbitrary semantic
   compatibility cannot be inferred perfectly from a diff or hash alone.
7. **A current pin and safe update discovery need different guarantees.** A
   historical pin deliberately remains old. Discovery must separately detect
   stale metadata, withdrawal and replay if automatic updates are later enabled.
   Publish an advisory for a bad immutable release instead of rewriting its
   bytes. TUF's rollback/freeze/mix-and-match analysis is useful guidance; this
   does not propose implementing all of TUF in the first version.

References: [TUF specification](https://theupdateframework.github.io/specification/latest/)
and [OCI content descriptor](https://github.com/opencontainers/image-spec/blob/main/descriptor.md).
The descriptor model is useful without adopting an OCI registry.

### Generated results should not alter the source they certify

Building revision M and then committing its generated manifest creates M-prime.
Evidence for M is not automatically evidence for M-prime. Embedding the final
commit's own identifier in a file inside that commit also creates a circular
definition. Putting the manifest outside the evaluated subdirectory may reduce
some churn, but does not justify universal source/output equivalence.

Prefer reviewed declarations and schema in the source tree, with final machine
records generated after fixing and verifying the release source revision.
Publish results outside that source tree and explicitly bind them to it. This
preserves useful source diffs for release intent and provides immutable output
files without an extra result-generating master commit. It also respects the
existing prohibition on direct commits to master.

The promotion candidate versus final merge revision needs the same care. AC5
still requires the accepted evidence before promotion. A future controller must
define how evidence binds to the tested merge result, and revalidate or refuse
when inputs change. This study does not authorize reusing parent-commit evidence
for a different final master revision merely because the visible diff is small.

### Publication alternatives

| Option | Advantages | Costs and limits | Assessment |
| --- | --- | --- | --- |
| Final manifests committed with source | Visible Git diff; Git-only retrieval | Evidence/source circularity, extra commits, possible evaluation churn | Do not use as the initial final-result authority |
| Structured annotated tag | Fits current release-record policy; portable with Git | Per-machine files need extraction; large evidence bundles are awkward; tag immutability needs enforcement | Viable compact baseline |
| Immutable GitHub Release assets | Direct machine files/bundle; platform binds tag, source and assets | Requires policy revision and platform availability; notes/latest are still mutable | Strong candidate for a file-oriented pilot |
| Separate metadata Git branch/repository | Independent source/result history | Additional synchronization, trust and recovery rules | Possible but unnecessary initial complexity |
| OCI content-addressed artifacts | Natural immutable descriptors and artifact graphs | Registry lifecycle, authentication and tooling burden | Revisit if scale or distribution needs justify it |

GitHub now documents immutable releases: associated assets and tags are locked,
and release attestation binds the tag, commit and assets. Draft the release,
upload the complete set, then publish. Titles, notes and latest/prerelease
marking remain editable and should not be machine authority. Enabling this is
prospective; this repository's setting has not been verified or changed.
See [immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)
and [enabling immutability](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes).

The accepted annotated-tag-only decision remains authoritative. Immutable
assets change a premise worth reassessing, and consumers needing standalone
machine records supply a concrete reason to review its reopening condition.
Use one authoritative digest-bound record graph if policy changes; do not
maintain independently authoritative release notes, tag prose and JSON.
Keep the schema transport-independent and the complete bundle exportable.

GitHub offers release/asset integrity verification. Automatically generated
source zip/tar archives are not covered by the asset-verification command;
an explicitly uploaded release bundle has a clearer verification contract.
See [release integrity verification](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/verify-release-integrity).

Evidence must outlive an ordinary CI URL. Store durable evidence summaries and
their input identities with the release; optionally retain full logs separately.
Deleting a workflow run deletes its artifacts. GitHub also announced that,
starting 2026-10-01, checks, workflow runs and statuses join retention enforcement;
that date is still future at this study's 2026-09-27 observation. Do not base
indefinite release verifiability on run pages or their default retention.
See [workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)
and [retention announcement](https://github.blog/changelog/2026-08-27-actions-retention-will-cover-checks-workflow-runs-and-statuses/).

### Deterministic host and publisher behavior

Proposed publisher sequence: fix the candidate and declaration baseline;
resolve support/selection coverage; obtain required evidence; compute net
artifact and contract changes and domain version; generate the complete bundle;
validate references and download verification; publish the immutable release;
only then expose an advisory discovery pointer. Existing promotion authorization
and source-history constraints apply throughout. Docs/repository-only promotion
does not produce a domain version when artifact/contract identities are unchanged.

Serialize publication within each domain. Retrying the same version must either
recover exactly the same content or refuse a conflict. Partial upload, tag
creation or a CI success badge must not look like a complete release to a host.
Define crash recovery for tag creation, draft publication and pointer updates;
do not assume several API calls are one atomic operation. The domain lanes can
release independently, while one source-promotion candidate still requires
all affected domains to satisfy its gate.

Host algorithm: read a trusted release root; verify selected record bytes;
resolve its machine ID, architecture and selection closure; check contract and
support compatibility; compare relevant identities against the local lock;
report artifact, contract, external-policy and provenance changes separately.
Unknown selection, missing record or unsupported schema returns an explicit
refusal/unknown result, never "unchanged". Fetching or reporting an update does
not rewrite the host lock or authorize applying it.

Version the schema. Reject duplicate keys, invalid required fields and unknown
incompatible schema versions. Hash exact published bytes with a named algorithm;
clients should verify before parsing, rather than reserializing JSON differently.
If semantic canonicalization is required, specify it fully. RFC 8785 is one
candidate, with constraints on numbers and Unicode as well as property order.
Sort feature sets where order is immaterial, but preserve semantically ordered
module lists. Bound sizes and paths; data records must not implicitly authorize
shell execution. See [JSON Canonicalization Scheme](https://www.rfc-editor.org/info/rfc8785/).

### Required future verification cases

| Scenario | Expected behavior |
| --- | --- |
| Only repository/docs content changes | Source promotion eligible under its own gate; no domain bump |
| One machine changes in a domain | Domain bumps; other records retain artifact identity while source/provenance remain accurate |
| Shared module/engine changes | All potentially affected selections covered; no path-only unchanged claim |
| Reference bytes identical but extension contract breaks | Contract change detected and incompatible release classified |
| Windows font or terminal dependency changes | Resolved dependent selections included; unsupported combinations refused |
| Host owns arbitrary modules | Provider relevance reported with limits; exact host impact verified locally |
| Record absent, corrupt, incompatible or mixed across releases | Refuse; never silently fall back to latest or call unchanged |
| Source changes between verification and publication | Reject stale evidence or obtain evidence under the accepted binding rule |
| Concurrent publisher or upload interruption | No mixed public snapshot; idempotent recovery or explicit conflict |
| Old release cache/payload disappears | Pin remains identifiable; unavailable realization reported honestly |
| Release later withdrawn | Historical bytes preserved; separate advisory prevents presenting it as recommended |
| Repeat with no agent installed | Same input bundle yields identical classification, manifest or refusal |

These are proposed acceptance/test cases, not passed tests. Current evidence
consists of source and public documentation inspection, remote snapshots and
the Windows dependency-closure enumeration. Build capacity, precise artifact
identity algorithms, evidence reuse, retention budget, publication recovery and
host-local comparison remain implementation/research work.

Recommended next design order: define machine/selection/contract identity and
the host-local pin; choose the authoritative release-record transport with any
necessary policy amendment; then specify declaration encoding, comparison and
coverage rules. Retain domain versions and begin with a small, explicit verified
catalog. Avoid adding per-machine SemVer or claiming universal host output
equivalence simply because the delivery files are split by machine.

## Provider-bounded assurance and host responsibility, 2026-09-27

The maintainer responded to the research by proposing either sufficiently
reliable release-file-only discovery or a narrower assurance contract with
active corrective releases. They also proposed relaxing exhaustive combination
coverage, excluding arbitrary host customization from provider guarantees,
leaving operational recovery to hosts, and retaining publication location as
an open consideration. They agreed that source/result circularity must be
resolved and challenged the earlier caution about Nix pinning.

Recommend separating reliable metadata from universal behavioral correctness.
A host should not need to inspect provider commits to discover a published
change: its selected machine record is the public discovery interface. Ordinary
tools must deterministically bind that record to the source, selected inputs
and evidence. The provider promises its stated verification and repair process,
not absence of every defect in every allowed composition or private host.

Keep structural checks strict: malformed records, wrong source/hash binding,
missing mandatory evidence and contradictory classification still refuse
publication. Relaxation concerns the explicitly declared verification coverage,
not permission to describe an unverified or failed case as passing. Newly
discovered defects are fixed through new immutable releases with appropriate
version impact. Record a regression case where practical and preserve prior
records; no repair-time SLA or old-major backport commitment is implied.

For change detection, distinguish a record's envelope digest from the selected
consumer-content and contract identities. A domain version, publication time
or evidence link can change without changing a machine's configuration. Raw
JSON file inequality may trigger inspection; it must not automatically mean
the host's output changed. The machine record must contain enough information
to make that distinction without reading Git history. Absent/unknown identity
is not unchanged. Conservative "possibly affected" classification is preferable
to a false unchanged result when exact impact is not available.

The proposed assurance boundary is every declared supported platform with
explicit mandatory reference cases, plus bounded feature/dependency regression
checks. All optional-feature combinations and arbitrary host customizations
would not be certified exhaustively. This proposal revises the earlier rejection
of representative builds and must be accepted as a dated AC5/AC6 amendment
before implementation. A clarification was requested between this option and
also allowing missing supported-platform verification. No answer is assumed;
AC5/AC6 remain unchanged while that selection is pending. Existing Windows 10
client-specific evidence and hosted/native distinctions also remain in force.

Private-host composition, local inputs, mutable machine state, backups,
deployment decisions and operational rollback belong to the host. The provider
still owns the correctness of its declared public interface, dependencies,
reference checks and machine release records. A host-owned recovery obligation
does not excuse a known provider contract regression. Retaining old release
records identifies pins without promising indefinite binary-cache service.

The Nix objection narrows the earlier recommendation: a host with its full
source/input graph and configuration pinned can keep using that chosen release
while unrelated machines and newer support metadata advance. It need not adopt
the latest provider merely to receive updated release metadata. Staying on an
explicitly chosen old pin is different from automatically redirecting a new
release selection to an older revision using lastArtifactChange alone.

Nix provides precise locked inputs and derivation/store identities within its
model. An input-addressed output path is not a measurement proving that every
rebuild has identical bytes; the manual explicitly treats equal-derivation
output equality as a purity assumption, not a universal guarantee. Published
realized closure content can be identified with content hashes where needed.
Neither kind of identity proves mutable host runtime or activation behavior.
This is compatible with the proposed bounded provider contract and need not
expand the first release into a universal reproducible-build audit.

References: [Nix flake locks](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake.html)
and [Nix purity, store objects and closures](https://nix.dev/manual/nix/2.34/glossary.html).
These moving 2.34 manual URLs currently identify 2.34.9; the previously selected
initial CI baseline remains 2.34.8. No version selection changed in this review.

Continue with two concrete design items: accept the mandatory coverage boundary,
then define the minimal machine-record contract for machine/architecture,
requested/resolved selection, source pin, consumer/contract identities and
verified coverage. Keep the final publication transport open as requested.
The generated-record placement must resolve the circularity described above.
No source implementation, Git publication, host evaluation/build or deployment
was performed in this follow-up.

### Accepted assurance boundary: all platforms, representative configurations

Accepted 2026-09-27: the maintainer selected mandatory representative machine
configurations on all supported platforms. This resolves the preceding pending
question. The adjacent spec now contains a dated AC5/AC6 amendment and updated
acceptance rows; the report retains pending implementation status.

All required machine/platform reference cases of a changed domain must pass
build/native generation before promotion. Exhaustive optional-feature
combinations and arbitrary private-host behavior are not guaranteed. Required
platform evidence cannot be skipped. Keep bounded feature/dependency checks,
accurate coverage reporting and corrective immutable releases when defects
are found. Hosted-first verification, separate required Windows 10 client
evidence, OS/tool baselines and the one-active-major maintenance scope remain.

The earlier research's exhaustive-combination concerns now describe a consciously
excluded assurance claim, not a requirement to test every combination before
release. Metadata/source integrity and deterministic refusal of failed mandatory
conditions remain strict. Missing behavioral coverage must not be mislabeled
as a passing test or used as proof that two artifacts are equal.

Next design work is the machine release-record contract and a finite named
reference matrix. A minimal record should let ordinary tooling identify the
machine/architecture, requested and resolved selections, exact provider source,
consumer-content identity, compatibility identity and verified coverage. Domain
version and publication/evidence metadata must be distinguishable from a change
to the selected consumer content. Exact fields, digest rules, optional-selection
impact precision and publication location remain design choices, not accepted
schema. This amendment does not select a transport or authorize implementation.

## Proposed minimal machine release record, 2026-09-27

The maintainer requested continuation after accepting the bounded assurance
matrix. This section makes the discovery/pinning contract concrete without
choosing publication transport or adding a new acceptance criterion. Scope is
repository release discovery; domain evaluators still own composition and
artifact calculation. No domain source or consumer implementation is changed.

### File boundary and fields

One record file represents one stable machine kind and architecture within a
domain release. It may contain several exact resolved selection entries; it
does not create an independent version series for each selection. The domain
release root authenticates the complete snapshot and binds the machine record's
exact bytes by digest. A consumer normally reads that root and its one selected
machine record, without interpreting source history or human release notes.

Proposed field groups:

| Group | Meaning |
| --- | --- |
| schemaVersion | Supported record grammar, independently versioned from the domain release |
| release | Domain, domain version, immutable release reference and exact provider source revision |
| machine | Stable configuration ID and architecture; no private hostname or user identity |
| selection | Allowed choices, defaults, required choices and dependency/exclusion rules needed to resolve the request |
| cases | Exact resolved selections and comparison identities available for each case |
| compatibility | Machine-readable platform/tool/interface requirements and migration references |
| verification | Named reference cases, exact inputs, evidence lanes, outcomes and limitations |

Release identity fields repeated from the root must match it; they are not a
second independently editable authority. A source location includes the domain
entry/subdirectory as needed. A tag alone is not the source pin. Registry keys,
normalization and hash algorithms must be schema-defined before implementation.

Each case carries separate identities for supplied configuration/runtime
closure, separately consumed management tools, and the public contract.
This separation implements AC8 without interpreting a management-tool fix as
proof that deployed settings changed. Identities include a scheme version;
different schemes require an explicit supported conversion or return unknown.
Synthetic reference inputs and their identity are part of the comparison basis.
Changing the reference definition makes comparison unknown unless the tool has
an explicit validated mapping; do not conceal it by reusing the reference name.

The artifact identity describes provider-supplied reference content. It does
not describe the private host's final output. Include runtime dependencies in
the domain-defined artifact calculation, and external-package declarations as
provider inputs where applicable. Do not silently fold mutable external package
bytes into that identity. A source/input fingerprint or planned derivation
identity may be useful supplementary information, but cannot masquerade as a
measurement of realized artifact bytes.

Contract identity is a digest of the consumer-facing contract, not a new SemVer
counter. Equality identifies unchanged declared contract content. Inequality
alone does not prove incompatibility: compare requirements and explicit
compatibility/migration information. Hashes cannot prove semantic compatibility.
If a host skips releases, checking the target's last patch alone is insufficient;
discovery must resolve the relevant intervening compatibility/migration records
or return that compatibility is unknown. Domain major changes remain an explicit
review boundary under the accepted maintenance/version contract.

### Illustrative machine record

The following abbreviated JSON shows shape only. Angle-bracket values are
placeholders, not valid production revisions/digests or evidence of a release.
It deliberately leaves exact support predicates and evidence encoding open.

```json
{
  "schemaVersion": 1,
  "release": {
    "domain": "unixlike",
    "version": "1.1.0",
    "ref": "unixlike-v1.1.0",
    "sourceRevision": "<exact-provider-commit>"
  },
  "machine": {
    "id": "unixlike/nixos-wsl",
    "architecture": "x86_64"
  },
  "selection": {
    "profiles": ["agents"],
    "default": [],
    "required": [],
    "dependencies": {},
    "exclusions": []
  },
  "cases": [
    {
      "resolvedProfiles": ["agents"],
      "referenceInputsId": "<reference-input-identity>",
      "comparison": {
        "scheme": "<versioned-domain-comparison-scheme>",
        "artifactId": "<measured-reference-content-identity>",
        "toolsId": "<consumed-tools-identity>",
        "contractId": "<public-contract-identity>"
      },
      "verificationRefs": ["<reference-evidence-id>"]
    }
  ],
  "compatibility": {
    "requirementsRef": "<digest-bound-requirements-record>",
    "migrationsRef": "<digest-bound-migration-record>"
  },
  "verification": {
    "recordsRef": "<digest-bound-evidence-record>",
    "assurance": "required-reference-cases"
  }
}
```

This example does not select the WSL default or its mandatory reference matrix.
The default and case above illustrate grammar only. With these sample cases,
an agents consumer can find a reference comparison; a base-only consumer cannot
infer equality from that agents case. The actual release must contain all
mandatory cases selected by the approved matrix. Optional case records can be
added as comparison information becomes available without requiring exhaustive
native runtime testing of every combination.

Requirements and evidence may be inline or digest-bound companion records;
that packaging decision remains open. The plain comparison path should not
require network requests per field. Bundle retrieval can satisfy all references
locally. Missing referenced data cannot silently default to compatibility.

### Host comparison and pinning

1. Verify the release root and machine record, supported schema and exact
   release/source binding. Unknown schema, bad digest, missing machine or invalid
   record is a protocol error, not a configuration change notification.
2. Resolve the host's requested selection using the published deterministic
   rules. Preserve both requested and resolved choices in the local pin. Recheck
   resolution against the candidate; a dependency/default change may alter the
   effective selection even when the request is unchanged.
3. Find comparable case information in the old and new records. Identity scheme,
   reference basis and coverage must be suitable for the comparison. If an exact
   selection has no valid comparison, report unknown and let the host perform
   local comparison; never borrow another selection's success as proof.
4. Compare artifact, tools and contract identities independently. Report fields
   such as artifactChange, toolsChange and contractChange, each with unchanged,
   changed or unknown. Report compatibility and verification coverage separately.
   Changed source SHA, domain version or evidence metadata alone is not proof
   that selected configuration content changed.
5. Let the host decide whether to retain its existing pin, inspect a candidate
   or adopt it. Do not describe a discovered candidate as a necessary deployment.
   A local lock pins release-root/record digests, exact provider source and
   requested/resolved selection alongside host-owned inputs. It is desired
   configuration, not proof of activation or Apply.

For a target with identical artifact/tools/contract identities, discovery can
report no provider-content change for the comparable selection even though the
domain version advanced. Updated support or advisory information remains visible
separately. A host can retain its old source pin; the discovery tool must not
silently substitute an older source for a newly selected release.

Raw file-digest comparison is an integrity/change-notification shortcut only.
It cannot distinguish new publication metadata from changed consumer content.
lastArtifactChange may be an optional human convenience and is not required in
the minimum record or used as an automatic pin selector.

### Worked outcomes and unresolved implementation choices

| Old versus candidate | Machine-readable conclusion | Host decision boundary |
| --- | --- | --- |
| Another machine changed; selected identities equal | Artifact/tools/contract unchanged; domain release newer | Can keep current pin |
| Selected configuration bytes or runtime closure changed | Artifact changed | Inspect/adopt according to host policy |
| Management tool changed; settings identical | Tools changed, artifact unchanged | Assess management behavior separately |
| Requirements changed; artifact identical | Contract changed; compatibility assessed separately | May retain old pin or review migration |
| Same request resolves to different dependencies | Selection changed; compare exact resulting cases if available | No silent feature adoption |
| Only unrelated evidence/publication metadata changed | Metadata changed, selected content unchanged if comparable | No inferred rebuild/apply requirement |
| Optional combination has no comparison record | Artifact/contract comparison unknown where unproven | Local verification remains available |
| Host has additional private modules | Provider-reference result with explicit boundary | Host owns final combined-output comparison |
| Malformed/mixed-snapshot record or failed required evidence | Invalid candidate/refusal | Do not accept as a valid release |

This design separates metadata completeness from exhaustive behavioral testing.
The accepted representative-build boundary is unchanged. Exact artifact hashing,
dependency-sensitive optional-selection coverage and semantic compatibility
checks must be designed and tested; the shape above does not prove those
algorithms correct. The first implementation should make incomplete precision
visible rather than inventing a successful unchanged result.

Next review can accept or amend these field responsibilities and comparison
outcomes, then choose the named mandatory reference cases and the exact
identity calculation for each domain. Publication transport stays deferred.
No AC11, executable schema, publisher, host updater or Git publication has
been introduced by this proposal.

## Proposed change-identity calculation, 2026-09-27

The maintainer requested the next design step: what the proposed machine-record
identities are calculated from. Recommend a versioned SHA-256 digest of explicit
content inventories, independently for artifactId, toolsId and contractId.
Avoid hashing the whole repository, release JSON or commit history as a proxy
for machine output. Keep the exact provider revision and locks in provenance
so every result remains traceable without forcing every machine's content
identity to change whenever its domain publishes.

### Common calculation and comparison rules

Use a deterministic domain-owned inventory, then serialize it under an exact
versioned format. A candidate formula is SHA256 over a prefix naming the
domain, identity kind and scheme version, followed by canonical inventory bytes.
Specify framing unambiguously; do not concatenate arbitrary values without
lengths/separators. Record scheme plus digest in the release record.

RFC 8785 is a candidate for canonical structured inventories, not permission
to normalize the bytes of supplied payloads. Sort true sets with a defined
ordering; preserve ordered operation/module lists. Hash actual delivered file
bytes, modes and link targets where meaningful to their packaging format.
Reject duplicate keys and inventory collisions. A canonicalizer needs its own
cross-platform vectors; jq property sorting alone does not establish JCS
conformance. See [RFC 8785](https://www.rfc-editor.org/info/rfc8785/).

Compare only equal schemes and comparable reference definitions. The reference
basis contains fixed synthetic identity, target platform class and host-owned
inputs. It must not include changing provider-controlled inputs as a reason to
declare every dependency refresh incomparable: those changes are precisely
what the artifact calculation measures. Record the full source/input graph
separately for provenance. New reference cases or a changed synthetic baseline
need old/new computation on a common basis or an explicit unknown result.

Exclude publication version, timestamp, CI URL and signature from content
inventories when they are only release-envelope metadata. If the same data is
embedded in a consumed output or influences consumer behavior, include it in
the appropriate identity. Do not strip real bytes merely to suppress releases.
File equality is content identity, not universal semantic equivalence.

For absent separately consumed tools, use an explicit empty tools inventory.
For unavailable measurement, use an explicit unknown status and reason, not the
empty inventory's digest or the previous release's digest. Different hashes
mean the stated inventory differs; same hashes mean equality only within that
inventory's declared completeness, reference basis and cryptographic assumption.

### Unix-like artifact inventory

Build/realize the required reference output, then enumerate the realized runtime
closure. The roots are NixOS system toplevel, nix-darwin system result including
managed Home Manager, or standalone Home Manager activation package as appropriate.
Identify root roles explicitly; a bag of reachable objects alone is insufficient.

For each reachable store object, record its store path, NAR content hash, NAR
size and references. Sort entries and reference sets deterministically, then
hash the root-role mapping and inventory. Obtain content information from the
verified/trusted realized store; query output is not itself a fresh integrity
scan. The collector must define its store-integrity/trust preconditions.

Do not include build-only dependencies, the full derivation graph, registration
time, deriver metadata, cache signatures or builder identity solely because
they appear in query output. Include any object that is actually reachable in
the output's runtime closure, even if normally described as build tooling.
Separately consumed provider tools have their own root-role/closure inventory
for toolsId. A tool already embedded in the system naturally also contributes
to that system's artifactId; separation does not remove real dependencies.

Nix documents recursive path queries and JSON metadata. path-info does not
build/substitute absent paths, so evaluation-only or missing closure information
cannot produce a measured artifactId. The current 2.34 manual also describes
JSON format variants: explicitly pin the collector's supported output shape
against the accepted CI baseline rather than consuming an unspecified default.
See [nix path-info](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-path-info.html)
and [nix-store query](https://nix.dev/manual/nix/2.34/command-ref/nix-store/query.html).

Store paths remain part of deployed identity: equal file bytes at different
store addresses are not silently collapsed. A changed source revision, store
path or timestamp embedded in generated files can therefore cause a real
artifact delta. If source-only promotion is intended to leave artifacts equal,
verify this property; do not assume that comments/docs can never influence
paths or embedded provenance. A derivation ID is useful supplementary planned
input information, not a replacement for measured closure content.

### Windows artifact and tool inventories

Use the domain loader/resolver to compute required-feature closure and select
the OS-specific payload for the declared target class. Export a stable provider
desired-state bundle under fixed synthetic inputs, without querying or changing
a private host. The inventory covers effective selected declarations, supplied
payload bytes, logical destinations, parser/comparison modes, dependency order
where meaningful, and applicable package/font/configuration instructions.

This bundle represents the supplied desired configuration, not a snapshot of
an installed machine. Preserve symbolic host paths or explicitly fixed synthetic
paths as the format requires. Private files merged with JsonSubset, discovered
terminal profiles and mutable application state stay outside this public
identity; their generation/merge behavior belongs to tools and contract checks.
Future external WinGet bytes are not measured by hashing their declarations.

The source at e11bd136 confirms Get-WinEnvDesiredStateHash includes the entire
manifest and all variants of selected payloads. It intentionally serves drift
tracking and cannot directly supply the narrower release identity. A release
collector must project the effective target/selection rather than changing that
existing hash incidentally. On the selected build-19044 baseline, a higher-build
WSL source variant alone should not alter the effective payload identity.
However, a file named for another platform that is actually shipped as part of
the selected bundle remains included; directory names do not prove exclusion.

For toolsId, inventory the actual consumer management bundle: entry/bootstrap,
generation, Check/Apply/capture code and required helper files according to the
published tooling contract. Do not hash only WinEnv.psm1 and miss a helper it
executes. Exclude developer tests/docs unless they are consumed runtime inputs.
Initially treat the shared management engine as affecting every selection that
receives it. A change in its unused branch or comment still changes delivered
tool bytes; precise function-level semantic independence is not promised.

The repository's .gitattributes requests CRLF for Windows PowerShell scripts.
Hash deterministic packaged bytes from the native release producer, with the
packaging encoding/newline rules fixed, rather than whatever checkout bytes an
arbitrary observer happens to have. Do not normalize strings or script payloads
after hashing and then distribute different bytes. Native producer validation
and cross-platform record parsing remain separate evidence lanes.

ProjectVersion is currently read to influence setup's comparison/Apply decision.
It cannot be discarded as harmless release metadata without a reviewed behavior
change. Record this behavioral input in tools/contract identity even if deployed
settings remain equal. Domain SemVer in an external release envelope need not
affect it automatically; their mapping is still a separate migration design.

Source-reading clarification: setup emits a "downgrade is disabled" warning,
but shouldApply also depends on force/state/desired-state/feature changes.
The warning alone does not prove all downgrade paths are blocked. Earlier
research established no tested rollback contract; that remains the conclusion,
not a claim that every lower-version invocation is prevented.

### Contract identity and release consequence

Hash the structured public contract: accepted constructor/selection inputs,
defaults and dependency rules, platform/tool requirements, exposed entry points,
relevant state/format compatibility and supported capability boundaries. Keep
display-only prose and evidence timestamps out. A new public behavior cannot
be fully inferred from a hash; reviewed declarations and schema/export checks
must keep this contract record aligned with the implementation.

Given comparable records, artifact/tools/contract inventories can independently
change or remain equal. A changed supplied management bundle is a release delta
even when the deployed settings remain unchanged, under AC8. A public contract
change can require a release with identical artifact bytes. Required checks must
pass and the cumulative reviewed impact determines SemVer; hashing does not
choose patch/minor/major. No delta means no domain tag, although source promotion
can proceed under its own gate. If missing comparison evidence prevents that
decision, do not assert no delta: obtain evidence or return an explicit refusal
under a defined release-coverage rule.

The representative-build amendment does not supply hashes for all optional
combinations. Generation-only Windows bundle identities may be measurable for
more selections without applying them; Unix-like unbuilt selections may have
only planned identities. Do not promote planned/source identity to measured
artifact equality. Optional-selection coverage and its release-classification
rules must be explicitly settled before implementation; they are not resolved
by requiring every private host to build or by silently reinstating exhaustive
combination builds.

### Proposed verification vectors and standing

| Input change | Expected identity effect |
| --- | --- |
| Publication time, CI URL or signature only | Envelope changes; content identities equal |
| Provider source changes but measured closure and contract stay equal | Provenance changes; no inferred artifact change |
| One Nix runtime dependency changes | Artifact identity changes even if a root-only comparison would miss it |
| Only build metadata changes; realized closure stays equal | Artifact identity equal |
| Source revision is embedded in an output | Artifact identity changes; no provenance stripping |
| Unselected Windows desired payload changes with tools/contract held fixed | Selected bundle identity equal |
| Selected font or a required feature changes | Dependent selection's inventory changes |
| Inapplicable Windows OS variant changes | Effective target bundle equal if no consumed tool/contract delta |
| Shared management helper changes | toolsId changes for every selection receiving it |
| Runtime-significant ProjectVersion changes | Behavioral tools/contract identity changes; settings may remain equal |
| Host cache timestamps or discovered app versions change | No provider-content identity change |
| Comparison scheme/reference basis changes without a mapping | Unknown, never unchanged |
| Missing required output or failed mandatory verification | No valid measured record/publication |

These are design vectors, not executed fixture results. This turn inspected
source, repository attributes and official documentation and ran repository
planning preflight only; no Nix evaluation/build, Windows native generation,
Apply or publisher implementation ran. Exact inventory schemas, producer
commands, content trust checks and optional-case policy remain unaccepted design
details. The next planning decision is the finite mandatory reference matrix
and how additional supported selections receive comparison records.

## Proposed mandatory reference matrix, 2026-09-27

Superseded recommendation: the maintainer subsequently requested a much simpler
starting point. See "Simpler starting point" below; do not implement this
eight-plus-eight list as though it had been accepted.

The maintainer requested continuation to the concrete reference list. Recommend
eight Unix-like build cases and eight Windows native generation cases initially.
These are reference-case counts, not counts of CI jobs, fresh compilations or
deployed hosts. Shared dependencies/caches can reduce work; measured runner
capacity and valid evidence reuse still require separate design. This list is
a proposal implementing the accepted all-platforms/representative-cases
boundary, not an additional accepted criterion or proof that it currently runs.

### Unix-like: eight required build cases

| Proposed case ID | Machine | Target | Selection | Required result |
| --- | --- | --- | --- | --- |
| U-W0 | nixos-wsl | x86_64-linux | profiles=[] | NixOS toplevel including managed Home Manager |
| U-W1 | nixos-wsl | x86_64-linux | profiles=[agents] | NixOS toplevel including managed Home Manager |
| U-V | nixos-vmware | x86_64-linux | no optional profile | NixOS toplevel including managed Home Manager |
| U-D | nixos-desktop-amd-apu | x86_64-linux | no optional profile | NixOS toplevel including managed Home Manager |
| U-H | home-wsl | x86_64-linux | standalone home | Home Manager activation package |
| U-U | nixos-utm | aarch64-linux | no optional profile | NixOS toplevel including managed Home Manager |
| U-O | nixos-orbstack | aarch64-linux | no optional profile | NixOS toplevel including managed Home Manager |
| U-M | darwin | aarch64-darwin, macOS 26 | base provider composition | Darwin system result including managed Home Manager |

Each case requires public-constructor evaluation, realization/build of its
required result and the measured release inventory. Use upstream Nix 2.34.8
as previously selected. The architecture/OS families require matching native
build capacity: five x86_64-linux cases, two aarch64-linux cases and one
aarch64-darwin/macOS-26 case. Exact hosted images, Linux builder distribution,
disk/time budgets and scheduling remain to be measured; no current hosted
capacity claim is made here. A hosted Linux build of a UTM/VMware/WSL-targeted
configuration is build evidence, not execution under that hypervisor or WSL.

The two WSL cases are justified because agents is the only optional Unix-like
profile currently exposed and its presence must not hide a broken base case.
This happens to cover today's permitted public profile combinations; it does
not impose exhaustive combination builds when more profiles are introduced.
Future features must be assigned explicit reference or bounded feature-test
coverage when introduced, without silently changing a host's selection.

Use fixed synthetic host/user/Git inputs. The same WSL identity must be used
in both cases so their distinction is the selected profile, not a renamed host.
Do not copy private-host hardware facts or modules into these records. Implement
the already accepted centralized NixOS/Home Manager 25.11 and Darwin 6 contract
before claiming first stable-release evidence. Current fixtures still contain
legacy per-host stateVersion values; they are not the final planned baseline.

A desktop/guest system build does not prove disk installation, boot, graphics,
networking or activation. Those remain explicitly separate runtime/adoption
evidence, not hidden prerequisites to run every release on personal hardware.
Existing required domain checks and any separately accepted native evidence
remain applicable; this matrix does not erase them.

### Windows: eight required native generation cases

All rows target windows/client, x86_64, Windows 10 IoT Enterprise LTSC 21H2
build 19044. The actual client revision and relevant application versions are
evidence attributes, not an assertion that every Windows 10 edition/build works.
Generation and management fixtures use the selected PowerShell 7.6.6 baseline.

| Proposed case ID | Explicit optional request | Resolved selection |
| --- | --- | --- |
| W-C | [] | core |
| W-F | [font] | core, font |
| W-Z | [zellij] | core, zellij |
| W-T | [terminal] | core, font, zellij, terminal |
| W-E | [wezterm] | core, font, wezterm |
| W-P | [powertoys] | core, powertoys |
| W-W | [wsl] | core, wsl |
| W-A | [font,zellij,terminal,wezterm,powertoys,wsl] | all seven current features |

Use an explicit list for W-A, not an unbounded all flag that silently adopts
future features. Feature order follows the domain's defined execution semantics;
set comparison alone must not reorder execution. W-T and W-E test dependency
inclusion, W-C protects the accepted opt-in minimum, and W-A detects broad
interaction/duplicate-dependency problems. These eight cases cover every
feature individually or with its dependencies and one aggregate interaction;
they do not prove all 32 resolved selections behave correctly.

Each row requires native desired-state generation/export, validation and
inventory collection in an isolated fixture. Generation is not installation or
Apply. The future producer must accept an explicit target/reference context or
run on the target client, so a hosted Server's detected build cannot silently
select the payload for a different OS. Hosted fixtures with injected build
19044 prove resolver/generator behavior, not a real Windows 10 client's behavior.
Such a release producer is planned, not a currently implemented public command.

Keep Windows PowerShell 5.1 entry/bootstrap compatibility as a separate required
check. Do not multiply the eight management-generation cases by two runtimes or
claim the management engine runs under 5.1. Preserve required native parsers and
existing schema/feature/source validation; limited full-combination coverage
does not authorize skipping a malformed source or missing mandatory parser.

### Windows client evidence and bounded checks

Keep a separate build-19044 client evidence record for actual included native
capabilities: relevant Appx/package discovery, profile/path handling, font and
Terminal/profile behavior, and selected Windows-side WSL observations as defined
by the reviewed capability contract. Do not count a Server fixture or mocked
registry response as proof of those client capabilities. Default terminal
delegation stays explicitly excluded as already accepted; Windows 11 is not a
required or implicitly supported client lane.

Use read-only native observations where they can establish the claim. If an
included claim requires state changes to verify, it needs a separately authorized
test environment or a reviewed narrower claim; Check alone does not prove Apply.
No eight-way feature activation cycle on the maintainer's home machine is
proposed. Discovery of unavailable client evidence blocks its required gate or
returns the claim to planning. Evidence freshness/reuse for unchanged capability
inputs remains to be specified; this proposal does not silently reuse an old
client observation for every future candidate.

Bounded fixtures supplement the reference cases: unknown/duplicate selections,
dependency/exclusion rules, newly added features remaining opt-in, source-variant
boundaries, host customization preservation and invalid input refusal. Existing
domain invariants and older-consumer compatibility checks continue independently
of the number of reference artifacts. The matrix is not the complete test suite.

### Current implementation gaps and comparison coverage

Read-only source inspection at e11bd136 found seven Unix-like output fixtures
(five NixOS kinds, one Darwin, one standalone home), with agents selected on
the WSL fixture. flake-test evaluates the profile-selection branches, but this
does not build a second WSL output. The proposed U-W0 needs explicit build and
inventory coverage. No build or evaluation was run in this investigation.

The current Unix-like CI job uses one ubuntu-latest runner, and its test script
distinguishes evaluation from skipped/non-native builds. Its default NixOS build
selection depends on the local matching host; a green current job is not the
proposed eight-case build gate. The current Windows job runs desired-state and
Pester checks, not the proposed release-bundle producer and eight inventories.
No workflow or source was edited to close these gaps during planning.

Release records must provide measured identities for every required row of
the released changed domain. The eight Unix-like rows cover the current planned
public machine/profile catalog; Windows rows leave other legal combinations
without mandatory measured records. A host choosing one of those combinations
must receive an honest comparison-coverage result rather than another case's
identity. Additional deterministic Windows bundle generation can supply further
records without promising additional native runtime coverage; feasibility and
the requirement to cover all legal selections remain a separate decision.

Recommended initial dispatch is the entire mandatory matrix of each changed
domain. Do not prematurely infer a smaller machine subset from paths alone.
If only Windows changes, Unix-like cases are not prerequisites, and conversely.
Source-only repository/docs promotion does not automatically create a domain
release, while repository dispatch changes still need their affected checks.

Before implementation, choose the named matrix, finalize optional-selection
comparison policy, measure builder capacity and specify exact candidate/evidence
binding and publication recovery. All results in this section are proposed
requirements or source observations, not passed platform evidence. No SSH client
operation, installation, build, activation, Apply or Git publication was run.

## Simpler starting point, 2026-09-27

The maintainer judged the preceding proposal too complex and suggested one
maximally configured case, or otherwise a substantially simpler starting point.
Replace the eight-plus-eight recommendation with one maximal compatible public
reference configuration per machine. The earlier exact matrix was not adopted;
this correction therefore does not weaken an accepted sixteen-case gate.
Keep the accepted AC5/AC6 all-supported-platform representative-build boundary.

| Domain | Initial recommended reference cases |
| --- | --- |
| Unix-like | Seven: NixOS WSL with agents, VMware, AMD APU desktop, UTM, OrbStack, Darwin, and standalone WSL Home Manager |
| Windows | One: client x86_64/build 19044 with all seven current compatible features selected |

For Unix-like, agents is offered only on NixOS WSL; do not force it into other
machines or invent new options to make every machine look alike. The other
machines use their existing complete provider compositions. Keep the already
selected architecture/OS boundaries and synthetic identities. One maximal
case cannot replace builds for a different machine kind or supported platform.

For Windows, explicitly select core, font, zellij, terminal, wezterm, powertoys
and wsl. This is a generation/validation fixture, not permission to install or
Apply all features on the maintainer's host. Keep the required Windows 10
client evidence and PowerShell 5.1 bootstrap check separate, without multiplying
the release-artifact matrix. Excluded terminal delegation stays excluded.

Drop the proposed mandatory base-only WSL build and seven extra Windows
generation cases. Use existing lightweight selection/schema/dependency fixtures
to check opt-in defaults, empty selection, required dependencies and invalid
inputs. Add a distinct expensive reference case only when a concrete defect,
incompatible feature combination or support boundary makes it necessary.
Maximum-feature success is deliberately not proof of every subset's behavior.

Keep the initial release interface correspondingly small: one reference-content
record per machine. Do not require a table of all feature-subset identities to
start. A host can discover that its machine's reference content changed and
decide whether to inspect/adopt it. For a subset, report that reference-level
change without claiming its customized/subset output definitely changed or
stayed equal. Exact subset comparison remains unknown where no evidence exists,
consistent with AC7/AC8. Per-feature precision can be developed later; this
proposal does not silently amend those criteria or certify absent measurements.

The accepted host feature opt-in contract is unchanged: maximal CI selection
does not become a host default or automatically add newly introduced features
to existing pins. Update the explicit reference selection through the reviewed
feature change; if features become mutually exclusive, select a documented
compatible maximum and add a case only for the otherwise uncovered behavior.

This simplified recommendation takes priority over the earlier detailed matrix
and exhaustive selection-record exploration. Exact schema/hash/publication
mechanics remain proposed design. Only this planning study was changed; no
workflow, evaluator, host setting, Git publication or build was performed.

## Release checkpoints before unit granularity, 2026-09-27

The maintainer clarified that machine boundaries are one possible distribution
unit and other choices must remain open. The primary objectives are suitable
release points for external hosts to select/pin and a structure supporting
recurring promotion and releases through master. The detailed machine-centric
design had become more prescriptive than those objectives require.

The adjacent spec now contains a dated AC1/AC7 amendment. It preserves independent
domain versions, ownership, bounded platform verification, deterministic tooling
and host-controlled adoption, while reopening mandatory machine subscriptions.
The report remains pending. No implementation or publication is authorized.

Separate the decisions:

| Decision | Current standing |
| --- | --- |
| A stable release point a host can pin | Required outcome |
| Recurring dev -> master promotion with evidence and failure handling | Required outcome; cadence/controller still to design |
| Domain ownership and independent version series | Retained |
| Distribution as domain snapshot, platform/profile bundle or machine record | Open alternatives |
| Machine-specific build fixtures | Useful verification candidates; do not determine packaging |
| Exact subset/output change discovery | Optional precision beyond the initial useful checkpoint; do not claim unavailable precision |

A simple domain snapshot tied to an exact source revision is a legitimate
baseline alternative. Machine-specific metadata can be added later if it earns
its complexity. A single domain release may also contain multiple optional
indexes without becoming multiple version trains. No alternative is selected
by this clarification, and common/repository boundaries remain unchanged.

The next planning step should focus on the promotion/release cycle: what opens
a release opportunity, what candidate revision is fixed, which evidence admits
it, what records a successful source promotion and applicable domain release,
and how failure/concurrency is recovered. Do not continue expanding machine
record schema or combination coverage before this central flow is settled.

Periodic opportunities need not force empty domain versions: docs/repository
source can enter master without a domain artifact/contract delta, and a failed
candidate waits for a corrected verified candidate rather than being published
because a timer fired. The twelve-hour input-refresh proposal is not an accepted
master promotion or release cadence. Current policy still requires same-repo
dev -> master PR merge commits, and unattended action authority remains to be
designed/adopted separately. Hosts select their pins independently of that cadence.
