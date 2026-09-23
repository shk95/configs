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

  # The combinations the host lanes name. A host is one of these or it does
  # not evaluate: a guest module written for one platform or hypervisor would
  # otherwise fail late, in whatever option it assumed.
  legalHosts = [
    {
      system = "x86_64-linux";
      kind = "wsl";
      hypervisor = null;
    }
    {
      system = "x86_64-linux";
      kind = "vm";
      hypervisor = "vmware";
    }
    {
      system = "aarch64-linux";
      kind = "vm";
      hypervisor = "utm";
    }
    {
      system = "aarch64-linux";
      kind = "orbstack";
      hypervisor = null;
    }
    {
      system = "x86_64-linux";
      kind = "desktop";
      hypervisor = null;
    }
  ];

  describe = host:
    "${host.system} ${host.kind}"
    + lib.optionalString (host.hypervisor != null) " on ${host.hypervisor}";

  checkedHost = name: host:
    if !(lib.elem {inherit (host) system kind hypervisor;} legalHosts)
    then
      throw ''
        identity.nixosHosts.${name}: ${describe host} is not a host this repository configures. The legal combinations are: ${lib.concatMapStringsSep "; " describe legalHosts}.''
    else if host.kind == "wsl" && host.user != config.identity.wsl.user
    then
      throw ''
        identity.nixosHosts.${name}: a host of kind wsl receives the WSL home classes, which are written for identity.wsl.user (${config.identity.wsl.user}), and declares ${host.user}.''
    else host;
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
      type = types.attrsOf (types.submodule {
        options = {
          system = mkOption {
            type = types.enum ["x86_64-linux" "aarch64-linux"];
            description = "Platform the host runs.";
          };
          kind = mkOption {
            type = types.enum ["wsl" "orbstack" "vm" "desktop"];
            description = "What the host is; selects its composition.";
          };
          hypervisor = mkOption {
            type = types.nullOr (types.enum ["vmware" "utm"]);
            default = null;
            description = "Hypervisor of a host of kind vm; null for every other kind.";
          };
          user = mkOption {
            type = types.str;
            description = "Primary account.";
          };
          stateVersion = mkOption {
            type = types.str;
            description = "NixOS release the host was first installed with.";
          };
        };
      });
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
