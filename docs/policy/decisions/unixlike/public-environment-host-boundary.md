# Public environment selection and host realization boundary

date: 2026-09-28
scope: unixlike
status: accepted
reopen-when: A supported consumer cannot express a necessary environment choice or safe host realization through the public constructors and native modules.
source: docs/work/unixlike/provider-consumer-contract/spec.md § Common environment and host boundary consolidation

`configs` supplies the common Unix-like environment through typed
`lib.mkNixos`, `lib.mkDarwin` and `lib.mkHome` constructors. Public inputs
select target system, user, Git identity and the independent WSL and graphical
environment choices. NixOS and Darwin accept native `systemModules` and
`homeModules`; standalone Home Manager accepts `homeModules` and requires an
actual `homeDirectory`. The consumer owns output names and its input lock.
Internal deferred module classes and file paths are not public API.

The provider owns shared tools, coding agents by default, its coordinated
graphical environment, WSL adaptations, platform defaults and the NixOS,
Home Manager and Darwin compatibility baselines 25.11, 25.11 and 6. Those
values are overridable when an existing host needs to preserve its effective
state. Changing a baseline requires separate compatibility and persistent
state review; updating flake inputs does not advance it.

The consumer's native modules own hostname, account creation and privileges,
access, network, storage, boot, hypervisor and Nix daemon policy. A WSL NixOS
consumer supplies its own NixOS-WSL integration; the provider checks that it
matches the selected environment and keeps graphics integration disabled.
Homebrew app selection and install/update/cleanup policy belong to the host;
provider app settings respond to the final native selection and can be
disabled without removing host-owned apps.

The provider's outputs are synthetic public-constructor examples. They verify
its own contract, not private machine safety, installation or deployment.
Host safety assertions, installation tools and their tests move with the
machine modules to the consumer. This transfer is one-time comparison work;
ordinary provider CI does not read a private consumer. A provider release is
not a host activation or proof of that host's persistent-state migration.

The former machine-kind inventory and optional profile routing were rejected
for this boundary because a personal machine kind made provider composition
and host realization inseparable. Constructor names remain, but removed
machine/profile fields are a declared breaking transition with migration
guidance; old pinned source remains usable until a consumer adopts the new
contract.
