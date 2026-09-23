# Hosts select profiles offered by their machine kind

date: 2026-09-23
scope: unixlike
status: accepted
reopen-when: A second optional profile needs different selection semantics or a machine cannot state its required classes without a host-specific exception.
source: docs/work/unixlike/host-selected-machine-profiles/spec.md § Decisions

Feature files contribute to deferred NixOS and Home Manager module classes.
The machine-kind table in `unixlike/modules/flake/configurations.nix` groups
those classes into required layers and named optional profiles. The host
chooses among profiles offered by its machine kind through the typed
`hostSelections.nixos` option, separately from `identity.nixosHosts`.
The same composition file checks the choice and imports the resulting classes.
Feature files never name a host, and the host never imports a class directly.

Each inventory host has exactly one selection entry. An empty list is an
explicit choice. An unknown profile, a profile the machine does not offer,
a repeated profile, or an extra or missing host entry fails evaluation.
This keeps host choice reviewable without turning every package into a switch.

The first optional profile is `agents`, offered by NixOS-WSL and selected by
the existing `nixos` host. The graphical classes remain required for the
UTM and VMware guests and physical desktop; their existing recovery and
graphical contracts are not weakened. Existing outputs are preserved.
