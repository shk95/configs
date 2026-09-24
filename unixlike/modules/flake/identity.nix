# Typed schemas only. Concrete, non-secret host identity and profile choices
# live in `inventory.nix`; the two option namespaces remain separate.
#
# INV unixlike/typed-identity — this file is the schema; tool/checks/flake-test
# proves it accepts the inventory and refuses a wrong shape.
{
  lib,
  config,
  ...
}: let
  inherit (lib) mkOption types;

  contract = import ./_host-contract.nix {inherit lib;};
  checkedHost = name: host:
    contract.checkHost {
      inherit name host;
      wslUser = config.identity.wsl.user;
    };
in {
  options.hostSelections.nixos = mkOption {
    type = types.attrsOf (types.submodule {
      options.profiles = mkOption {
        type = types.listOf (types.enum ["agents"]);
        default = [];
        description = "Optional machine profiles selected by this NixOS host.";
      };
    });
    default = {};
    description = "NixOS host profile choices, keyed by inventory host name.";
  };

  options.identity = {
    gitName = mkOption {
      type = types.str;
      description = "Author name shared by the managed Unix-like Git configurations.";
    };

    gitEmail = mkOption {
      type = types.str;
      description = "Author address shared by the managed Unix-like Git configurations.";
    };

    wsl = {
      user = mkOption {
        type = types.str;
        description = "Account managed in the WSL configurations.";
      };
    };

    # INV unixlike/nixos-host-inventory — the attribute name is the host name
    # and the name of its nixosConfigurations output, so the two cannot
    # differ; `apply` refuses a combination no lane names.
    nixosHosts = mkOption {
      default = {};
      apply = lib.mapAttrs checkedHost;
      description = "Every NixOS host, by host name.";
      type = types.attrsOf contract.hostType;
    };

    darwin = {
      user = mkOption {
        type = types.str;
        description = "Account managed by nix-darwin and Home Manager.";
      };
      hostName = mkOption {
        type = types.str;
        description = "Darwin host and computer name.";
      };
      system = mkOption {
        type = types.enum ["aarch64-darwin" "x86_64-darwin"];
        description = "Darwin target platform.";
      };
    };
  };
}
