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

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | Baselines, override tests and transition guidance checked locally; delivered revision pending. |
| AC9 | pending | Source-bound reader, independent consumer and live read-only WSL readiness passed; template pin and delivery pending. |
| AC2 | pending | Public constructor/refusal and selected fixture checks passed; delivery pending. |
| AC3 | pending | Darwin capture is the separate U2 lane. |
| AC4 | pending | Independent locked consumer evaluated and built on native x86; durable provider and companion pins pending. |
| AC5 | pending | macOS 26.6.2/Nix 2.34.8 full local check and native Darwin build passed; delivered evidence pending. |
| AC6 | pending | Local native x86 and macOS checks used Nix 2.34.8; pinned CI candidate has not run on GitHub. |
| AC7 | pending | Host-owned transfer and seven final outputs checked against local provider source; publication/order pending. |
| AC8 | pending | Mac and x86 selected native builds and provider graphical VM fixture passed; current-head CI and delivery pending. |
