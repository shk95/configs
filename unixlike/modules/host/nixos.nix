# What a NixOS host is told about itself. `flake/configurations.nix` sets
# `host` from the host's entry in the typed inventory, and a fragment that
# needs a per-host value reads it here, inside the NixOS evaluator, instead
# of naming a host. The name a host answers to and its state version are such
# values: both come from the entry, so the output name, the inventory name
# and `networking.hostName` cannot drift (#191), and
# `wsl.wslConf.network.hostname` defaults to the last, so /etc/wsl.conf
# follows without a second declaration. modules/host/darwin.nix is the Darwin
# half of the same rule.
#
# INV unixlike/nixos-host-inventory
_: {
  modules.nixos.shared = {
    lib,
    config,
    ...
  }: let
    inherit (lib) mkOption types;
    field = type: description:
      mkOption {
        inherit type description;
        readOnly = true;
      };
  in {
    options.host = {
      name = field types.str "Host name, as the inventory names the host.";
      system = field types.str "Platform the host runs.";
      kind = field types.str "What the host is.";
      hypervisor = field (types.nullOr types.str) "Hypervisor of a host of kind vm.";
      user = field types.str "Primary account.";
      stateVersion = field types.str "NixOS release the host was first installed with.";
    };

    config = {
      networking.hostName = config.host.name;
      # The release the host was first installed with, not a number copied
      # from Home Manager's, which tracks a different schedule
      # (modules/state-version.nix).
      system.stateVersion = config.host.stateVersion;
    };
  };
}
