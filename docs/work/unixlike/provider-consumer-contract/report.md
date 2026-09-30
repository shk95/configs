# Report: Unix-like provider and host customization
kind: report
spec: docs/work/unixlike/provider-consumer-contract/spec.md
status: pending

## U1 external standalone connection checkpoint, 2026-09-28

The implementation branch started from origin/dev
`e11bd1368d2f5138ad0f9b7017040b2b76e055e6`. The reviewed Unix-like plan
is `2b074152fc2278c13fda50367854e921011e49b9`, with the later provisional
planning text copied from its separate worktree (spec SHA-256
`21b1ba22b9b3a41368fd6867a5278175483edb0fe8531fd994f56b284a037b13`).
This local checkpoint is uncommitted and unpublished.

The standalone `mkHome` constructor now requires `homeDirectory`, accepts typed
`environment.wsl` and `environment.graphical`, selects the corresponding home
classes, and rejects graphical WSL and retired or unknown inputs. A plain native
`homeModules` definition retains an explicit `home.stateVersion`; the provider
default is overridable. The initial checked-in contract document describes only
the connected `mkHome` entry point. Its source data supplies the constructor's
supported system and defaults, and a fixture checks generated JSON against it.
It does not claim the unfinished NixOS or Darwin input contract.

Evaluation: `external-consumer-test` locked a separate flake against an isolated
copy of the current Unix-like source using `path:<candidate>?dir=unixlike`
(candidate NAR hash `sha256-zzj6GeR3tEwUv6yu2Bc7wxYJzKqY1nqiC2BXQOOrGX8=`),
followed `configs/nixpkgs`, read
`api/contract.json` from `configs.outPath`, reached final Home Manager identity,
directory, Git setting, selected graphics/WSL classes, native override and
activation derivation, and refused invalid fields/combinations. This is a local
candidate tree, not the old dev revision or a published release.
`provider-api-test` and `bash unixlike/tool/checks/flake-test` passed, along with
composition fixtures, the work-document check and Unix-like Nix formatting.
Import-order verification and its positive/negative fixtures also passed; it
was selected because the standalone class was renamed.

Build: the first `nix build --no-link` attempt on the Mac could not build
`x86_64-linux` derivations on `aarch64-darwin`. The same isolated candidate was
then copied to `homewslu`, a native `x86_64-linux` WSL2 host. With Nix
2.34.8, `external-consumer-test --build` passed, including an actual build of
`homeConfigurations.cli.activationPackage`. The output is
`/nix/store/hhc08i7j10b3fh25da9zykd35n2nh72p-home-manager-generation`, derived
from `/nix/store/hblv1wfg13i228ii87v7p9k5blfzj7ab-home-manager-generation.drv`.
The candidate NAR hash matched the local evaluation above. The remote daemon
could not resolve `cache.nixos.org`; required store paths were copied through the
Mac's cache connection before the build. No host settings were changed. This
proves this selected standalone consumer's native build, not Home Manager
activation or operation of the built configuration. Native runtime and activation
were not exercised. All acceptance rows remain pending; the other U1
constructors, transfer, reader/readiness and template companion remain outstanding.

## Initial versioned contract reader checkpoint, 2026-09-28

`unixlike/tool/contract-inspect` now reads `api/contract.json` from a supplied
Unix-like flake source tree without evaluating that candidate. It compares an
optional current trusted tree or accepts an explicit readerless-legacy mode.
An optional declaration from the current trusted host identifies the constructor,
explicit inputs and module-presence flags; the reader reports candidate input
compatibility, required host edits, omitted-default changes and evaluation needs
separately. The source contract now attaches each migration's guidance to its
entry point, so a readerless host can see the applicable adoption instructions.
It does not print host input values or serialize module contents.
Its source-ref field is explicitly caller-supplied; the JSON digest identifies
the bytes actually read. Pin verification, fetching and later candidate
evaluation remain the caller's separate steps. The reader currently makes
declaration-level compatibility claims only for the published `mkHome` contract;
unfinished constructors return unknown.

`contract-inspect-test` passed for current-to-candidate comparison, omitted
versus explicit defaults, a readerless legacy input requiring migration,
graphical WSL conflict, module-content refusal and unknown format refusal.
After the reader and metadata edits, `external-consumer-test` also passed at
candidate NAR hash `sha256-rwomhchWejGHxWaBAUOrdSxvCEqx1DZ3eeHQcWMHcxA=`.
The native build recorded above belongs to the earlier standalone candidate;
it is not a build claim for this later source identity.
It obtains Python from the locked nixpkgs input on this Mac because the native
`python3` launcher is only an xcrun stub. The test is wired into `flake-test`;
the full fixture suite passed after the initial reader wiring. Following the
later migration-metadata edit, the targeted reader and external-consumer tests
passed; the full fixture suite was not repeated. No host pin, input,
system state, runtime or activation was changed. Reader bootstrap distribution,
other constructors, source-ref binding and standalone readiness remain pending.

## Source-bound reader and standalone readiness checkpoint, 2026-09-28

The reader now optionally checks a consumer lock's `configs` input, requires
`dir=unixlike`, hashes the supplied repository source root as a NAR and refuses
a mismatch with the lock's `narHash`. It reports a lock revision when present;
the source-ref free-text field remains separately marked as caller supplied.
The same check can bind an optional current trusted source/lock pair for
ordinary updates. Synthetic tests passed for both bound sources and a refused
wrong hash.
An actual independent path-flake consumer exercised this lock/source check
before candidate evaluation. The `contract-inspect` and
`standalone-readiness` apps were exported for each
Unix-like flake system, built on `aarch64-darwin`, and launched from the local
candidate. A trusted pinned app can therefore inspect a separate candidate
source without executing the candidate's reader. Readerless legacy hosts still
need a trusted initial app pin chosen by their owner.

`standalone-readiness` uses the selected `mkHome` environment defaults and
only reads the running system. It separates satisfied, missing and unknown
conditions for target architecture, Ubuntu 26.04 reference OS, declared
account/home, Nix CLI presence, `en_US.UTF-8` locale and the Home Manager
`nix.conf` target. WSL kernel and graphical system conditions appear only when
selected; graphical services and arbitrary host module effects remain unknown
until native verification/final candidate evaluation. Synthetic fixtures
passed for all three statuses, WSL selection, graphical unknown and invalid
graphical WSL selection. On `homewslu`, the actual WSL CLI declaration returned
`satisfied` for target, OS, account/home, Nix CLI, locale and WSL kernel. The
existing `nix.conf` symlink was `unknown`, making the overall read-only
prerequisite summary `unknown`. The probe changed no managed host setting,
service state or activation; it does not certify the linked file's ownership.

At candidate NAR hash `sha256-+3d2ET9t5tLfDbkbRsWzxw2M7WY46yuTx/1QM6oTYiY=`,
the independent external consumer's source/lock check, final evaluation,
refusals and native `x86_64-linux` activationPackage build passed on `homewslu`
with Nix 2.34.8. The realized generation path was again
`/nix/store/hhc08i7j10b3fh25da9zykd35n2nh72p-home-manager-generation`.
After the current-lock comparison and app metadata edits, the same native
external-consumer test with `--build` passed at final Unix-like candidate NAR
hash `sha256-gRynZSr/QcWc5f+PtTVP4OFHwg8zlQ3uIbrN3G8hVvU=` under Nix 2.34.8;
the generation path remained the one above. This is selected build evidence for
that exact source tree, not activation.
`prerequisite-test` and the full `flake-test` suite passed on the Mac after
the readiness tool/test wiring; the later app export passed targeted format,
evaluation, build and launch checks. `nix flake check --no-build` passed after
the app metadata edit; it proves output evaluation, not the unrelated flake
check derivations' builds. No runtime execution of the generated
home, Home Manager activation or private consumer adoption is claimed. U1
and every acceptance row remain pending.

## Machine responsibility inventory before removal, 2026-09-28

Read-only inspection used provider base `e11bd1368d2f5138ad0f9b7017040b2b76e055e6`
plus this worktree, and a clean `configs-hosts` main at
`f7f3010ca4675f705e8a8895dede19786530b6ca`. Its current host flakes still
pass the old constructor fields and do not connect `systemModules` or
`homeModules`. This inventory records responsibility, not private destination
content or evidence that a replacement has been implemented.

| Current provider source | Intended owner and obligation before removal |
| --- | --- |
| `modules/machines/{amd-apu,desktop,orbstack,utm,vmware}.nix` | Host machine modules own hardware, hypervisor integration and boot facts. Preserve the AMD encrypted-storage/graphics contract, OrbStack binfmt refusal, and UTM/VMware integration plus key-only recovery with replacement assertions and refusal fixtures. |
| `modules/foundation/{account,sshd,firewall}.nix`, host login-shell fragments | Host owns account, sudo, SSH and exposure policy. Preserve the headless key-only, no tracked key/password, one-port firewall and recovery checks; no public environment selector may imply an account, port or shell choice. |
| `modules/platforms/wsl.nix`, `modules/programs/docker.nix`, NixOS-WSL input | WSL host owns distro integration, UID/mount mapping, sudo, Docker privilege and the shared-kernel binfmt guard. The provider keeps the WSL Home Manager adaptation and its no-graphics rule. Preserve shared-kernel checks before dropping the old system class. |
| `modules/foundation/installation.nix`, `tool/install-plan`, `tool/install-vm-test` and their fixtures | Host installation owner retains explicit persistent disk selection, inert desired-state target, labelled runtime mounts and disposable VM test. Never infer a target or run installation during migration. Root `Justfile` command reconciliation needs a separately classified repository change. |
| `modules/foundation/nixos.nix`, `modules/flake/{identity,fixtures,configurations}.nix` | Host modules own host name, account/home realization and existing state-version preservation. Provider retains public typed constructor/composition, overridable compatibility defaults and synthetic fixtures; obsolete kind/profile assumptions need replacement checks and policy updates. |
| `modules/foundation/nix/{shared,darwin}.nix`, Darwin account/Homebrew modules | Host owns daemon/trust/GC policy, Darwin account/name and Homebrew app selection/lifecycle. Provider retains flakes support, active Darwin environment defaults and selected-app settings with bounded tests. |

No machine or safety code was removed. Destination code, replacement assertions
and tests are not yet present in the inspected consumer revision. The accepted
plan treats host repository writes as separately owned, so removal of these
provider responsibilities must wait for an authorized destination revision and
evidence that the safety/recovery obligations survived. The remaining public
NixOS/Darwin constructor transition is coupled to that transfer.

## Cross-work reading and dependency reconciliation, 2026-09-28

Latest-reading guidance separates current U1/U2 contracts from retained historical
proposals. Candidate template proof, provider PR integration and required template
delivery before release are distinct; no circular unpublished-tag dependency or
recurring private-host CI gate is intended. Selective evidence remains bounded to
changed functions. This is documentation reconciliation only, with all rows pending.

## Capture scope narrowed, 2026-09-28

The maintainer explicitly excluded compatibility/reconciliation for host-owned
capture extensions, including overlap with future configs features. Latest AC3
amendment records the two-input surface, managed-key semantics and host-invoked
pinned tool with explicit destination. No generic extension registry or extra
private-host verification is planned. These remain design decisions; no new source,
capture, native execution or acceptance evidence was produced.

## Darwin capture ownership design, 2026-09-28

The maintainer accepted whole capture-unit ownership transfer, a versioned JSON
envelope with explicit source selection, bounded schema compatibility and separate
preview/save/apply. This supersedes proposed Darwin baseline/delta merging only;
Windows retains its own contract. Existing Karabiner module/tool and root capture
entry were inspected read-only. Current activation still reads provider payloads
directly, and root capture still targets provider source. New host-data consumption,
format checks and save flow are unimplemented. No live app capture, build, native
read verification or activation was performed; AC3 remains pending.

## Single-flake consumer planning, 2026-09-28

The maintainer adopted the latest spec's single-flake dendritic consumer/template
direction and U1 delivery boundary. Read-only inspection found seven current host
flakes/locks and their existing per-directory check loop. No consumer or template
source was modified; new topology, connection helpers, shared-lock transition and
new API remain unimplemented. All criteria remain pending.

## Bounded connection and baseline investigation, 2026-09-28

Nix 2.34.8 was reported ready by tool/configs doctor unixlike. A temporary external
consumer pinned github:shk95/configs/e11bd1368d2f5138ad0f9b7017040b2b76e055e6?dir=unixlike
and followed configs/nixpkgs. Evaluation returned the three current lib constructor
exports, identical followed nixpkgs outPath, injected system/home values, Darwin
hostname and standalone username. These used the existing constructor schema, not
the planned schema. A path probe confirmed configs.outPath is the flake subdirectory
and configs.sourceInfo.outPath is the repository source root. The planned contract
file is absent. No full derivation evaluation, build, runtime or activation evidence
is claimed. A temporary consumer lock was created; provider inputs were not updated.
The initial /tmp symlink path failed and evaluation succeeded using /private/tmp.

The provider pins nixpkgs e94cb152ed51bd6e24eb4a41f1460252beb52cd2. Source inspection
of 26.05/26.11 stateVersion branches followed by selected option evaluation found
postgresql, mysql, grav, netbox, dovecot2, taskchampion-sync-server, hyphanet, lauti,
sabnzbd, tandoor-recipes, olivetin and nextcloud disabled, and boot.zfs.enabled false,
in fixture-wsl (26.05), fixture-vm (26.05) and fixture-desktop (26.11). This bounded
search/evaluation found no active member of those inspected changes. It does not
prove all indirect default effects, whole-output equality or real-host migration.
Home Manager already declares 25.11 and Darwin 6; conversion to overridable defaults
still requires implementation and checks. No acceptance row is completed.

Subsequent accepted design adds minimal contract contents, optional explicit host
declarations, host-owned sops+age extension boundaries and a small changed-function
check map. See the latest spec amendment. Reader and new API are not implemented.

## Post-audit design consolidation, 2026-09-28

The latest spec amendment records accepted concrete inputs, host-owned hostname,
overridable stateVersion baselines, public connection/data paths and narrowed
change-driven verification. Existing check sources were reviewed, not executed.
The environment examples are not required recurring suites. Actual consumer proof,
transition effects, implementation and selected evidence remain pending. This
entry supersedes earlier broader evidence and stateVersion ownership descriptions
where they conflict; it verifies no acceptance row.

Design agreed on 2026-09-27. Adjacent study.md preserves pre-implementation
evaluation evidence. The original centralization plan is superseded by the
2026-09-28 amendment. Constructor migration and host capture are not implemented;
no activation is certified by this report.

On 2026-09-27 the maintainer selected macOS 26 as the first formal Apple
Silicon support baseline. AC5 remains pending until the adopted contract and
complete required native evidence exist. The planning investigation evaluated
all seven current provider fixture derivations on macOS 26.6.2 with Nix 2.34.8;
it did not build or activate them and does not complete AC5.

The maintainer also selected upstream Nix 2.34.8 as the initial exact CI
baseline on 2026-09-27. AC6 remains pending: local evaluation does not establish
the required CI installation or full native build evidence.

On 2026-09-28 the maintainer confirmed environment selection plus host modules.
The dated spec amendment revises AC1/AC2/AC4/AC5 and adds AC7/AC8. It preserves
host-owned NixOS stateVersion and separates public provider evidence from private
machine realization/use. Exact coverage, WSL dependency wiring, administration
boundaries and HM/Darwin migration ownership remain design work. All rows remain
pending; document validation is not implementation or runtime evidence.

Later on 2026-09-28 the maintainer confirmed provider-owned compatibility
baselines with host-owned adoption and persistent-state migration. The latest
AC1 amendment supersedes the earlier same-day host-owned value choice. Exact
initial values, any compatibility escape hatch and concrete transition evidence
remain pending. No effective stateVersion, consumer pin or host data was changed.

## Latest design consolidation, 2026-09-28

The latest dated spec consolidation records environment/host ownership and
domain API/template contracts. All implementation and live evidence remains
pending, including the new API criterion. Document preflight is form validation,
not evaluation, build, native runtime, activation/Apply or live automation proof.
No source implementation, Git publication or host mutation was performed.

## Delivery refinement, 2026-09-28

U1 now names a coherent public environment/host contract outcome, dependencies,
evidence and stop conditions. Ubuntu 26.04 LTS x86_64 is the first standalone
baseline; the live 26.04.1 WSL OS read is identity evidence only. Earlier claims
that initial stateVersion values remain open are superseded by 25.11/25.11/6;
transition analysis remains pending. Required/advisory contract checks replace
blanket machine/session certification. Input schema, WSL wiring, ownership map
and contract export still need resolution before pickup. All rows remain pending.

## Independent review follow-up, 2026-09-28

Accepted independent-review corrections are now recorded in the owning specs.
They clarify cutoff/candidate timing, complete-delta check selection, template
delivery, initial reader bootstrap and host-local applied-state capture. All
implementation evidence remains pending; this update is design acceptance only.

## File-level delivery preparation, 2026-09-28

The spec now maps current source groups to retained provider behavior, host
transfer or split ownership, with corresponding evidence and completion conditions.
It records the accepted public-input and generated-contract approach and one-time
transfer evidence, without private-host CI dependency. No migration, build, native
test, activation or implementation completion is claimed. All rows remain pending.

## Final independent planning audit, 2026-09-28

An independent agent reviewed all five work items against latest accepted
amendments and confirmed the previous five corrections without identifying a
new direction conflict. This is planning review only. Concrete consumer paths,
U1 types/transitions/evidence and later lane prerequisites remain; all acceptance
rows stay pending and no implementation or live rollout is certified.

## U1 connected candidate checkpoint, 2026-09-29

The provider source is still an uncommitted linked-worktree candidate from
`e11bd1368d2f5138ad0f9b7017040b2b76e055e6`. It now exports public
NixOS, Darwin and Home constructors, rejects retired machine/profile inputs,
and routes WSL and graphics through typed environment selections. Synthetic
NixOS CLI, graphical, ARM CLI and WSL, Darwin and standalone outputs evaluate.
Common coding agents and bounded package exclusions, compatibility defaults
25.11/25.11/6, Homebrew final-selection settings and read-only contract and
standalone tools are connected. The provider no longer declares machine,
account, access, storage, installation or Homebrew app-selection state.

At private consumer base `f7f3010ca4675f705e8a8895dede19786530b6ca`,
an uncommitted dedicated worktree contains a one-flake/seven-output transfer
candidate. Its root lock has a published bootstrap provider pin; checks used an
explicit override to this exact local provider tree. All seven final output
derivations evaluated. The transfer evidence checked positive and negative
access, WSL UID/interop, guest integration, OrbStack binfmt, AMD graphics,
storage and compatibility values. The private install-plan refusal fixture
passed with a temporarily overridden lock; the original bootstrap lock was
restored. These are evaluation checks, not selected host builds, runtime or
activation. No private module contents are a recurring provider gate.

The public template base `dcb8c6d81ebd72ca4b19e8364269494ffcbdc5c2`
has an uncommitted detached-worktree single-flake candidate. Its synthetic
NixOS output and structure check passed with the same provider source override.
Its published bootstrap lock remains on the earlier constructor API and needs
alignment only after the provider source has a durable ref. Neither companion
is published or activated.

Provider `provider-api-test`, `external-consumer-test`, the versioned reader
and readiness fixtures, `flake-test`, composition and import-order fixtures,
and local-system `nix flake check --no-build` passed on the relevant candidate
revisions. The invariant registry is currently blocked on the separate
repository-owned AGENTS.md change that removes its last reference to a retired
OrbStack invariant; the other registry failures were resolved. A separate
repository worktree holds that change. The root `Justfile` installation entry
retirement is Unix-like-owned and stays in this U1 worktree.

On an Apple Silicon Mac running macOS 26.6.2 and Nix 2.34.8, the synthetic
Darwin `system.build.toplevel` built without activation as
`/nix/store/zali9xigbysq0c5cksbs72mb5vpsv357-darwin-system-26.11.4cff07d`.
The current contract-inspect and standalone-readiness app packages also
built. This is a native selected provider build, not a private Mac build or
runtime confirmation.

The selected current-source native `x86_64-linux` build attempt used
`homewslu` and its retained Nix 2.34.8 binary. It failed before realization
because the host could not resolve `cache.nixos.org`; its default Nix is now
2.35.1. The earlier successful native Home Manager build belongs to an older
U1 source hash and does not prove this candidate. The generated home was not
run or activated. On 2026-09-29 the maintainer said that this host's network
cannot be repaired immediately and requested an orderly pause with a handoff.

A separate repository-scope worktree now holds two U1 prerequisites: removal
of the obsolete OrbStack invariant reference in `AGENTS.md`, and a CI Unix
job that requests the official upstream Nix 2.34.8 installer URL through
`cachix/install-nix-action@v31.10.6`, enables `nix-command flakes`, prints
the resulting implementation/version and refuses any value other than
`nix (Nix) 2.34.8`. The URL responded HTTP 200 and its script names the
2.34.8 x86_64 Linux archive. YAML parsing passed locally. This is source
review only: no GitHub CI run has exercised the change.

New negative public-constructor tests found that WSL selection without the
host integration module raised a raw missing-attribute error. The provider
assertion now guards that access so the intended integration message is
reported. The refusal cases for absent integration and enabled WSL graphics
driver passed locally. This is evaluation evidence, not WSL runtime.

After these changes, provider formatting, lint, `flake-test`,
`nix flake check --no-build`, and the selected native macOS fixture build
passed; the build path remains
`/nix/store/zali9xigbysq0c5cksbs72mb5vpsv357-darwin-system-26.11.4cff07d`.
The private seven-output candidate and public template candidate also passed
their root `tool/check-hosts` checks against the current local provider
override, with no lock file write. The repository version-control fixture
suite passed. The provider's standalone invariant check still identifies the
old `AGENTS.md` reference; a temporary index combining the two separate
worktree changes passed with 71 registered invariants, none pending and no
untagged fixture units. The combined check is evidence of the proposed
dependency only, not integrated source.

At resumption, refresh all four worktree diffs and remote heads; finish the
provider, repository, private consumer and template checks on their current
sources; review the repository prerequisite integration order; then align
the consumer locks to a durable provider ref and run the selected native
`x86_64-linux` build when a working native builder is available. Keep the
macOS 26 build and x86 result in separate evidence lanes. Native build
capacity, final contract pin alignment, repository prerequisite integration,
current-head CI and host runtime remain open. No host activation was requested.
All acceptance rows below remain pending.

## U1 native build and verification-selection resumption, 2026-09-29

The maintainer restored `homewslu` networking and asked to resume U1. After a
transient closed SSH connection, a new connection succeeded and
`cache.nixos.org` resolved on the native `x86_64-linux` WSL host. The retained
upstream Nix executable reported `nix (Nix) 2.34.8`; the host's default shell
path does not expose that executable, so the checks selected it explicitly.
No host configuration or activation was changed.

The current provider `unixlike/` source was copied to a temporary host path.
At consumer-locked candidate NAR hash
`sha256-zFqdfwn1HCn/5aE+0tYDjSQEJhhbbmPJOxhkHuYRuHc=`, the independent
`external-consumer-test --build` passed its source/lock binding, contract,
constructor/refusal evaluations and actual standalone Home Manager
`activationPackage` build. The same source built
`nixosConfigurations.fixture-cli.config.system.build.toplevel` as
`/nix/store/jliyiybpmaxdrgf3wwlsd6d37596b2z7-nixos-system-fixture-cli-26.11.20260925.e94cb15`.
The `unixlike/` subdirectory itself hashed to
`sha256-kSopIsh5ad5NFSlvbYvU4Vc9BKy33H5pGWqkKJt4Z8U=` on both the Mac
and `homewslu`; the first hash above belongs to the separate consumer's
repository-root source containing that subdirectory.
These are native builds of synthetic public consumers, not a private host
build, Home Manager run, NixOS boot or activation.

Review found that `unixlike/tool/checks/test` still chose NixOS builds by the
running host name, despite the new outputs being synthetic. It now evaluates
every exported configuration, selects representative native builds by system
or exact `CHECKS_BUILD_TARGETS`, and refuses a selected output without a
passing native build. The positive selection fixture and missing/foreign
negative fixtures passed on macOS. The Unix-like definition of done and
invariant were updated for this evidence boundary. Repository-owned
`AGENTS.md`, CI and the dated evidence decision are held in a prerequisite
repository-scope candidate. A second repository-scope candidate holds the
user-facing README, CONTRIBUTING and architecture updates for after provider
and private-consumer integration. Each staged worktree classifies as its
intended single scope.

On macOS 26.6.2 with Nix 2.34.8, the current provider
`unixlike/tool/checks/test` passed all local flake checks, evaluated every
synthetic output and selected/built the native Darwin `fixture-mac` output.
Format, lint, work-document validation and the selection fixture passed.
The repository version-control fixture suite passed. A temporary index that
combined the proposed repository `AGENTS.md` with the provider candidate
passed invariant registration: 71 registered, none pending, no untagged
fixture units. This is combined-candidate evidence, not an integrated commit.

The same exact provider source ran `standalone-readiness` on `homewslu` with
the declared WSL CLI environment. Target, Ubuntu 26.04, account/home, Nix CLI,
locale and WSL kernel conditions were `satisfied`; the existing `nix.conf`
symlink remained `unknown`, so the read-only summary was `unknown`. This is
native execution of the prerequisite reader, not operation of the generated
Home Manager configuration. The private single-flake candidate evaluated all
seven outputs and the public template evaluated its example against the
current local provider override without writing their bootstrap locks.

The full `x86_64-linux` `unixlike/tool/checks/test` then passed under Nix
2.34.8: all exported synthetic configurations evaluated, the selected
`homeConfigurations.example` and `nixosConfigurations.fixture-cli` built,
and the local-system flake checks passed, including the graphical runtime VM
fixture. This VM test is provider fixture runtime evidence, not a private
host's graphical session. The exact-source `flake-test` and both companion
`tool/check-hosts` checks passed with the current provider source. GitHub CI,
durable provider ref, companion lock alignment and actual host runtime remain
pending. No commit, push, PR, tag, release, activation or Apply occurred.
AC3 Darwin capture remains the separate U2 lane.

After explicit approval to publish the repository prerequisite and provider
as Draft PRs, the repository-scope prerequisite was committed and pushed as
`9b5c41caa5eb0444e97417304d8e26c6635b405f` in
[PR #420](https://github.com/shk95/configs/pull/420), still Draft. Its
current-head CI run `36569886968` passed `Required checks`, repository scans,
version-control fixtures, native Windows and the Unix-like job, including the
upstream Nix 2.34.8 version assertion. The PR head remains the exact commit
above, its base remains `e11bd1368d2f5138ad0f9b7017040b2b76e055e6`,
and GitHub reports it cleanly mergeable with no review threads or auto-merge.
This is CI for the repository prerequisite's current source, not the U1
provider candidate. Provider publication remains
dependent on that prerequisite entering `dev`: the provider removes the old
OrbStack invariant, while the unmodified `dev` AGENTS.md still cites it.
The combined candidate index passed, but a provider-only commit would fail
the required invariant hook. The provider worktree remains uncommitted and
unpublished; no hook bypass, merge or activation was authorized. Explicit
authorization to make PR #420 Ready and merge it was requested separately.

## U1 repository prerequisite integration, 2026-09-29

The maintainer separately authorized Ready conversion and integration of
[PR #420](https://github.com/shk95/configs/pull/420). Immediately before the
merge, GitHub reported exact head
`9b5c41caa5eb0444e97417304d8e26c6635b405f`, base
`e11bd1368d2f5138ad0f9b7017040b2b76e055e6`, passing Required checks,
clean mergeability, no reviews or review threads, and no auto-merge request.
The PR entered `dev` through merge commit
`d2c2aebf9e2141dbfbdf332afd7677cf08c8ddb1`. The provider branch then
fast-forwarded to that commit and restored its staged source without conflict;
the restored patch checksum matched its pre-update backup. The provider-only
staged diff classifies as `unixlike`, and its invariant check passed with 71
registered, none pending or untagged. On the updated base, macOS/Nix 2.34.8
format, lint and the full `unixlike/tool/checks/test` passed, including every
synthetic configuration evaluation and the native Darwin `fixture-mac` build.
Post-merge CI for the prerequisite and current-head provider CI remain separate
pending evidence. No real host activation or Apply occurred.

## U1 delivery verification resumed, 2026-09-30

The maintainer requested resumption. Live GitHub and local inspection found
the delivery worktree clean at the published Draft PR #421 head
`a69dd589c98b698b5d381cc7d4f904f28be18403`. Source commit `50444ef`
and isolated lock commit `a69dd58` preserve the same final tree as the original
unpushed candidate; the original worktree, stash and saved patch remain backups.

[Exact-head CI run 36574608460](https://github.com/shk95/configs/actions/runs/36574608460)
passed Required checks, repository scans and native x86_64 Linux evaluation,
selected builds and the graphical VM fixture under upstream Nix 2.34.8.
The published PR records the native macOS pre-push evaluation and Darwin build.
These are provider fixture and build results, not private host runtime or activation.

The repository prerequisite's post-merge
[CI run 36572924610](https://github.com/shk95/configs/actions/runs/36572924610)
failed on attempt 2 in its separate Windows job; the Unix-like and
repository jobs passed. PR #422 subsequently repaired that fixture. The
post-merge [CI run 36648870125](https://github.com/shk95/configs/actions/runs/36648870125)
at `1758fe98aff677b815fd28d14d53228e29bf5371` passed the native Windows
suite (320 passed, zero failed, one skipped), repository scans and Required
checks. This is prerequisite evidence, separate from U1's final-head evidence.
PR #421 remains Draft with no auto-merge request. Companion bootstrap pins,
publication, provider integration and U2 Darwin capture remain pending.

On resumption, both companion `tool/check-hosts` checks passed with an explicit
override to the exact delivery worktree's unchanged `unixlike/` source. The
private consumer evaluated all seven final output derivations and its flake
checks; the public template evaluated its synthetic example and structure
check. Their existing bootstrap locks were not rewritten. This repeats
connection evaluation only; it adds no companion build, runtime or activation
evidence. Work-document validation and `git diff --check` passed for the
source-state and evidence-record corrections in this resumption.

## U1 continuation and delivery boundary, 2026-09-30

The assigned U1 continuation owner inspected the existing provider worktree and
both single-flake companion candidates without replacing their uncommitted
work. At this continuation's initial inspection, the provider source head was
`a69dd589c98b698b5d381cc7d4f904f28be18403`, with only the source-state
and report corrections uncommitted. The
required integration base is `1758fe98aff677b815fd28d14d53228e29bf5371`,
which includes the repaired Windows fixture. The maintainer then authorized the
required base merge, the prepared documentation commit/push and PR body/Ready
handoff. Checks must run on the revised head; the prior provider green run does
not certify it. PR #421 records the final published head and its own checks.
Companion pin changes and publication remain separately unauthorized.

Ready handoff for the provider means its coherent U1 source result is published,
its current-head required checks pass and outstanding review/blockers are
accounted for. It is separate from dev integration, the full contract report's
completion (including U2), companion publication and API release readiness.
Required template code delivery and durable reference alignment remain visible
companion obligations before API release; private host activation is not a
provider delivery or release prerequisite. Both companion bootstrap pins remain
`e11bd1368d2f5138ad0f9b7017040b2b76e055e6`. Candidate checks can use one
explicit immutable published provider revision; final pins must be selected
from the delivered source and rechecked together after authorized alignment.

Both companion `tool/check-hosts` checks also passed against the same immutable
GitHub provider revision `a69dd589c98b698b5d381cc7d4f904f28be18403`, using
`CONFIGS_PROVIDER_OVERRIDE` with `?dir=unixlike`. The private candidate evaluated
all seven declared output derivations and its no-build flake checks; the public
template evaluated its synthetic example and no-build flake checks. Neither
lock was written: both still name the bootstrap revision. This verifies the
published candidate connection, not final pin alignment, publication, native
companion builds, runtime or activation. The work-document working-tree
preflight and `git diff --check` passed for these corrections.

## Provider integration and delivered companion pair, 2026-09-30

The maintainer authorized source publication and separately integrated
[provider PR #421](https://github.com/shk95/configs/pull/421) at
`3d6d945f1a7c32428ae506586eb5b644129e5614`. Delivered head
`c8b6e818e2dc13043ad37010616684d09f4b24e3` passed its own
[CI run 36651282314](https://github.com/shk95/configs/actions/runs/36651282314)
and Required checks. That head's macOS 26.6.2/Nix 2.34.8 check evaluated all
seven synthetic provider outputs and built `fixture-mac` natively. The merge
passed its separate [post-merge CI run 36653252448](https://github.com/shk95/configs/actions/runs/36653252448)
and Work closure run 36653252520. The native x86_64 CI checks cover public
constructor/default/override/refusal behavior, all-output evaluation, selected
native Home/NixOS builds, the graphical VM fixture and import-order independence.
Earlier Draft, bootstrap-pin and authorization-pending notes above describe
their original checkpoints; they are superseded by this delivered evidence.

Both companions explicitly adopted the same immutable delivered provider
`3d6d945f1a7c32428ae506586eb5b644129e5614?dir=unixlike`, with source
adaptation and lock changes in separate commits. Neither follows `dev`
implicitly or claims a provider release tag.

| Source | Published candidate | Integrated source | Exact merged-source CI |
| --- | --- | --- | --- |
| Public template [PR #1](https://github.com/shk95/configs-host-template/pull/1) | `64cc43e80607d9e14780849af0e3b2357e2b57a6` | `bd72568b4fd7fd740dc21d0a8fe8927cc9934e4b` | [36655493199](https://github.com/shk95/configs-host-template/actions/runs/36655493199), evaluate passed |
| Private consumer [PR #21](https://github.com/shk95/configs-hosts/pull/21) | `18e7a1e0e4301a376f75da524cc16ec35e959f59` | `9b04a7635b8eb3e1c6e179827b87efcea9aa5672` | [36655638053](https://github.com/shk95/configs-hosts/actions/runs/36655638053), evaluate passed |

Source-bound metadata fetched from both immutable integrated consumer refs
confirmed that their original/locked provider selection names the delivered
SHA, `dir=unixlike` and the same
`sha256-Kz6FVMMnLTslQInuc3x1Kw7TTSpJ2Prc0eflALzouVo=` source narHash.
Read-only flake checks and toplevel evaluation against those refs, without
overrides, passed for the public synthetic example and all seven private
outputs. This is a locked delivered-pair result, replacing the earlier local
override-only connection evidence. No private source or host values are copied
into this public report.

The private consumer's `lib.transferEvidence` passed its actual host-module
assertions and negative overrides, including access, WSL, hypervisor, storage
and AMD safeguards. Its standalone synthetic access/WSL check and explicit
install-plan acceptance/refusal fixture also passed. The safety checker now
reads the WSL evaluator from the consumer-owned input rather than the removed
provider input. The checks touched no host disk or application.

The private candidate built its Darwin system natively on macOS 26.6.2 with
Nix 2.34.8. Candidate `18e7a1e0` is an ancestor of integrated `9b04a763`;
their complete Git trees are equal. Re-evaluating the Darwin derivation from
the immutable merged source produced the same derivation as that built
candidate, and its output is present in the local store. This binds the build
to unchanged integrated source; it does not claim another build invocation or
host activation at the merge commit. The other six private outputs were
evaluated only in this continuation.

Build selection follows the changed behavior. The available native Mac build
checks the changed private connector/realization's final Darwin result. The
template changes the connector, pin and synthetic declaration without a new
template-owned executable or package source; its source-bound example
evaluation is the selected connection check, with no native template Linux
build claimed. Provider-native fixture builds remain provider evidence.

Provider integration, required template source delivery and the one-time
host-connectable ownership transfer are now evidenced. This does not close
the full parent acceptance table, implement U2 capture, certify API release
readiness or authorize host rollout. Future release-tag alignment is separate;
private host activation is neither a provider completion condition nor a
recurring public CI gate. The report remains pending.

The remaining U1 rows distinguish delivered implementation evidence from the
technical coverage review still to be recorded by the orchestrator or its
assigned follow-up inspector. That reviewer can verify a row or name a specific
gap; pending status creates neither a new implementation lane nor a routine
user-approval gate. Ask the maintainer only if that review discovers an actual
new baseline, support or compatibility-policy decision. The maintainer's final
report acceptance belongs at full parent completion. AC3 still requires U2
implementation and its applicable checks. No missing private activation or
blanket host-runtime suite is implied by these rows.

## U1 technical review and bounded repair, 2026-09-30

Issue #434 continues from `origin/dev` at
`cfd6d2718dc048cc1803e95267113d66f54e603d`, reviewing spec revision
`50444ef94897402979a2ed4b402997f78675c833`. The narrowly approved pickup
amendment was published in `6082cf9a61c3b01f03eff7cef602b84f62bcd5c7`
before source implementation, in [PR #435](https://github.com/shk95/configs/pull/435).

Technical review found two actual delivered-source defects: ordinary native
Darwin `KeyRepeat = 4` conflicted with the provider's value 3, and inspection
reported a forbidden Darwin/WSL declaration as compatible when graphical was
omitted. The repair lowers each active native default leaf's priority, retaining
deferred class composition priority. A root-level priority wrapper was rejected
by the nested regression because a partial CustomUserPreferences override lost
unrelated provider domains. The leaf implementation preserves those siblings.
All 106 active leaves supplied by the delivered Darwin default unit compare
equal in the unchanged synthetic realization. Varied ordinary numeric, boolean,
custom-domain and time-zone overrides plus explicit Darwin/HM state versions
pass; these checks do not claim every arbitrary host-module override is valid.

Inspection now computes effective WSL/graphics choices from the existing finite
metadata and honors constructor-specific constraints. Tests cover forbidden
Darwin WSL with graphical omitted and false, allowed Darwin selections, effective
candidate defaults, and constructor-specific omitted-default reporting. Unknown
constructors and arbitrary module effects retain their unknown/evaluation-needed
boundaries; module contents remain excluded. Public API data, default values and
supported combinations are unchanged.

The finite public-contract fixture checks 71 cases against actual constructors:
published export/output identities, required omissions, declared/wrong types,
supported/unsupported systems, environment defaults and WSL constraints, unknown
inputs and neutral empty home extensions. Existing tests continue to compare
generated JSON with contract.nix, bind fetched source to its consumer lock, and
exercise module extensions, retired-input migration and read-only readiness.
The graphical opt-out fixture preserves a host-added package/setting and a host
reference to the still-shared jq dependency while removing the provider's
graphical contribution. Its negative Niri case exercises the existing native
merge refusal between an active Niri definition and a contradictory ordinary
false value; it introduces no new fixed-component policy.

Focused provider API, contract inspection, lint and format checks passed. On
macOS 26.6.2/aarch64-darwin with Nix 2.34.8, flake-test and test passed,
evaluating all seven outputs and building the native synthetic fixture-mac.
The final-source native Mac and current-head CI evidence is supplied with the PR;
selected builds and runtime applicability remain separate from activation.
No companion pin or host state was changed in this repair. Earlier provider,
template and private refs retain their original delivered-source evidence;
adopting the repair in consumers remains coordinated follow-up.

Technical review accepts AC1's bounded initial transition investigation: the
latest amendment explicitly limits it to the inspected service/ZFS branches,
default selection, preserved explicit host values and retired-input guidance.
It proves neither exhaustive output equivalence nor safe persistent-state
migration. AC4's older `e11bd136` external connection and preserved consumer
history, together with new retired-input refusal and migration guidance, establish
the declared breaking boundary, not cross-major compatibility. AC5's native Mac
proof belongs to the synthetic public-constructor fixture; the separately locked
Darwin API example has evaluation evidence, not another native build invocation.

The AC7 inventory accounts for host-owned machine/account/access/storage/WSL,
installation and Nix daemon/app-lifecycle material at the durable consumer refs
above. Disko/nixos-anywhere and installation tools moved to the host; unused
deploy-rs was retired. Provider nixos-wsl remains solely a reproducible synthetic
integration dependency; hosts own their selected integration pin. Safety/refusal
and install-plan proof do not imply disk installation, headless boot/recovery or
the unselected Linux install-VM branch passed. Provider Linux Home/NixOS builds,
graphical VM, native Darwin fixture, all-output evaluation and companion
evaluations keep their original source and lane limits. AC3/U2 and full parent
report acceptance remain pending; release and host rollout are separate.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Source-defined 25.11/25.11/6 defaults, explicit native preservation and retired-input migration guidance pass. Technical review accepts the latest amendment's bounded initial service/ZFS transition investigation; this is neither exhaustive equivalence nor private persistent-state migration. The repair adds explicit Darwin/HM override and unchanged-default coverage. |
| AC9 | verified | Generated-data agreement, finite actual-constructor metadata coverage, source/lock binding, legacy/current comparison, format/module-data refusal and readiness three-state evidence pass. The repair refuses forbidden Darwin/WSL selections using effective finite metadata and confines omitted-default guidance to the selected constructor/layers; unknown constructors/module effects retain evaluation needs. The observed readiness unknown is not a host-preparation gate. |
| AC2 | verified | Public typed inputs, defaults, module extensions, invalid/retired-field refusals, WSL wiring and finite metadata agreement pass. The ordinary native Darwin preference defect is repaired with leaf default priority and varied nested override/sibling-preservation checks. These tests cover the stated input/extension boundary, not all arbitrary host-module effects. |
| AC3 | pending | U2 must implement the host-owned Darwin capture format, projection/ownership selection and preview/save path, then supply its selected evaluation/build/native-reader evidence. No capture result is certified here. |
| AC4 | verified | Older `e11bd136` external connection and preserved consumer history establish the old pin; new independent locked consumers, native x86 synthetic realization, retired-input refusals and stable migration guidance establish the declared breaking adoption boundary. Older pins remain explicit choices; compatibility across that boundary is not promised. |
| AC5 | verified | Delivered `c8b6e818` macOS 26.6.2/Nix 2.34.8 all-output evaluation and native aarch64-darwin synthetic public-constructor build establish the selected macOS 26 lane. Separate external Darwin API evaluation is qualified as evaluation. Older/later OS support and private runtime are not inferred. |
| AC6 | verified | Delivered provider head `c8b6e818` and merge `3d6d945f` passed their own CI with the explicit upstream Nix 2.34.8 assertion, evaluation and selected native builds; matching macOS evidence is recorded above. |
| AC7 | verified | Technical review maps provider removals to durable host-owned machine/account/access/storage/WSL, installation, daemon/app lifecycle and actual safeguard fixtures. Disko/nixos-anywhere moved; unused deploy-rs retired; provider WSL input remains synthetic test infrastructure. Delivered pair evaluation and qualified Darwin build are recorded; installation, headless boot/recovery and host rollout are not claimed. |
| AC8 | verified | Changed native Darwin defaults/reader/composition coverage includes finite API probes, varied ordinary overrides with unchanged defaults/siblings, graphics opt-out host/shared-dependency preservation and existing Niri merge refusal. Native Mac evaluation/build and prior qualified Linux/graphical/companion evidence retain source boundaries; current repair-head selected Linux CI is supplied with the PR before Ready. ARM/WSL/other graphical builds, private runtime and activation are not inferred. |
