# Typed schema only. Concrete, non-secret host inventory lives in
# `inventory.nix`; keeping the two separate makes it clear which values are
# machine declarations and which are reusable option contracts.
#
# INV unixlike/typed-identity — this file is the schema; tool/checks/flake-test
# proves it accepts the inventory and refuses a wrong shape.
{lib, ...}: let
  inherit (lib) mkOption types;
in {
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
