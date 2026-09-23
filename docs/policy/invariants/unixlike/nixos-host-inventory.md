id: unixlike/nixos-host-inventory
statement: Every NixOS host is an entry of the typed inventory whose name is its output name and its host name, and only a combination of system, kind and hypervisor that a host lane names evaluates; every host also has one typed profile choice containing only profiles offered by its machine kind.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: schema unixlike/modules/flake/identity.nix
enforced-by: fixture unixlike/tool/checks/flake-test
decision: docs/policy/decisions/unixlike/nixos-hosts-declared-in-typed-inventory.md § Only the combinations the lanes name evaluate
decision: docs/policy/decisions/unixlike/hosts-select-offered-machine-profiles.md § Hosts select profiles offered by their machine kind

The outputs are generated from the inventory, so an output without an entry
cannot exist; the fixture proves the legal combinations are accepted, that
every other one is refused by name, and that each declared host answers to
its entry's name and carries its state version.

Profile choices have a separate typed option. The same fixture proves that
the host names agree, selected profiles are offered by the machine kind and
unknown or repeated choices are refused.
