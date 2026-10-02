# Automate guarded NixOS installation and deployment

kind: spec
date: 2026-09-23
scope: unixlike
status: approved
review-by: 2026-10-23
issue: #341

Agreed with the maintainer on 2026-09-23 as roadmap order 11. The repository
can declare and evaluate disk layouts, prove an installation in a disposable
VM, derive deployment nodes and refuse unsafe invocations. Formatting a real
disk, installing a real host and activating a remote host remain explicit
maintainer actions and supply separate evidence.

## Problem

The supported NixOS machines now have evaluated system configurations and
hand-written installation procedures. Their storage contracts are duplicated
between prose and NixOS file-system declarations, installation has no
disposable end-to-end proof, and updates still require commands inside each
host. Historical issues #24 and #25 describe deploy-rs, disko and
nixos-anywhere, but they are closed context rather than execution authority.

Automation must not weaken the repository's existing boundaries. In
particular, an evaluator must not guess a disk, a deployment must not select a
fleet implicitly, and neither a successful build nor a release tag authorizes
an activation.

## Decisions

### Let each host class own its storage layout

The ordinary booting NixOS hosts compose one of two disko classes at
`unixlike/modules/flake/configurations.nix`, the existing composition
boundary. VMware and UTM use the labelled UEFI, one-disk ext4 layout already
created by their procedures. The AMD desktop uses its accepted UEFI, labelled
LUKS2 and Btrfs subvolume contract. Hypervisor and hardware modules no longer
duplicate file-system declarations once those classes own them.

The tracked layout contains a deliberately unusable installation-target
placeholder. A read-only planning tool accepts only an explicit
`/dev/disk/by-id/...` path and writes a throwaway wrapper flake that overrides
that placeholder for one named host. The device identity therefore remains
reviewable beside the generated plan without becoming a machine-specific
repository value. No tool scans disks or chooses one.

### Pin all three tools and prove installation before physical use

The Unix-like lock pins disko, nixos-anywhere and deploy-rs. The lock-file
refresh is an isolated dependency commit. The flake exposes the two command
line tools needed by an operator while disko's module supplies the layouts.

The x86_64 VMware-shaped guest is the disposable installation proof because
it is native here and has the smaller ext4 layout. nixos-anywhere's VM test
uses a generated plan whose target is the disposable virtual disk, installs
the actual host output and boots it. The test records installation and boot
evidence without touching an installed guest. The aarch64 UTM and physical
desktop layouts still evaluate; neither receives foreign-architecture build
credit from this run.

### Derive a narrow deploy-rs topology from the typed inventory

Deploy nodes are generated for ordinary booting hosts only: `desktop`, `utm`
and `vm` at this order. WSL and OrbStack are excluded. Each node connects as
the inventory's primary user, elevates interactively to root, builds on the
target architecture, and retains deploy-rs automatic and magic rollback.
The node name is also its SSH host alias, so addresses and keys remain local
SSH configuration rather than desired state.

The supported entry point accepts one host and one annotated
`unixlike-v...` tag reachable from `master`. It refuses a branch, the current
checkout, an unknown host and a multi-node invocation. It runs deploy-rs from
that exact release source. The procedure requires a host-specific
`nixos-rebuild test --target-host` and runtime confirmation before the first
deploy-rs switch. Every command that activates a host remains a maintainer
action requiring explicit authorization.

### Keep automatic and installed-host evidence separate

Evaluation covers every layout and node. Native x86_64 build and disposable
VM installation cover only the test host. Review covers the generated plan,
guards and operator procedure. A physical format/install and each remote test,
switch, confirmation and rollback stay pending until the maintainer runs them
on the named host.

## Increments

1. Add this spec and report and open the execution issue.
2. Pin the three inputs, add the two storage classes and explicit plan tool,
   then evaluate every host and run the disposable x86_64 installation proof.
3. Derive deploy-rs nodes, add schema checks and a release-and-single-host
   guard, then prove its positive and negative cases without connecting to a
   host.
4. Add the installation and deployment procedure in repository scope and
   record review separately.
5. On explicit authorization, install or reinstall a real host and exercise
   remote test, switch, confirmation and rollback one host at a time.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Disko, nixos-anywhere and deploy-rs are pinned in one isolated lock refresh, and their required modules or executables evaluate on supported systems. | evaluation, review |
| AC2 | VMware and UTM own the labelled UEFI/ext4 layout and the desktop owns the accepted labelled LUKS2/Btrfs layout through composable NixOS classes, without changing WSL or OrbStack storage. | evaluation, build |
| AC3 | The read-only plan requires one known installable host and an explicit `/dev/disk/by-id/...` target, records both in a generated wrapper flake, and refuses implicit, non-persistent or multi-disk selection. | evaluation, review |
| AC4 | A disposable x86_64 VM runs disko and nixos-anywhere against the actual `vm` output, boots the installed result, and proves its host identity, labelled file systems and SSH recovery contract. | build, native runtime |
| AC5 | The aarch64 UTM and x86_64 desktop installation layouts evaluate, while their native installation and physical runtime remain unclaimed. | evaluation |
| AC6 | Deploy-rs nodes are derived from the typed inventory for ordinary booting hosts only and require primary-user SSH, interactive sudo, native remote builds, automatic rollback and magic rollback; deploy-rs schema checks pass. | evaluation |
| AC7 | The supported deployment entry point requires exactly one known host and an annotated Unix-like release tag reachable from `master`, deploys that exact source and has positive and negative fixtures that make no connection. | evaluation, review |
| AC8 | The procedure separates plan review, destructive formatting, installation, remote test activation, runtime confirmation, switch and rollback and states which commands require explicit authorization. | review |
| AC9 | A real installation and each remote deployment lane record native build, runtime, activation and rollback evidence independently. | build, native runtime, activation |
| AC10 | `Required checks` passes on the head of every pull request of this work before it merges. | evaluation |

## Ownership amendment, 2026-09-25

The verified storage classes, synthetic install-plan checks and disposable VM
installation remain provider evidence. Their original `vm`, `utm` and
`desktop` final-output paths in the criteria above identify the historical
test targets; current provider tests use synthetic fixtures. Private
`configs-hosts` owns final instances, deploy-rs nodes, SSH aliases, guarded
single-host deployment and the real-host procedure. It must choose and verify
its own release source; a `configs` Unix-like provider tag cannot authorize
or certify a private deployment. AC6–AC10 stay pending until the consumer
implements and verifies those lanes and a real host supplies the relevant
native build, runtime, activation and rollback evidence. The report here
will link each consumer increment while retaining the earlier provider proof.
