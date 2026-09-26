# Synthetic toplevels exercise all three projections without a host module tree.
{
  config,
  lib,
  ...
}: let
  probe = builtins.derivation {
    name = "import-order-probe";
    system = "x86_64-linux";
    builder = "/not-built";
    content = lib.concatStringsSep "" config.importOrderProbe;
  };
in {
  options.importOrderProbe = lib.mkOption {
    type = lib.types.listOf lib.types.str;
    default = ["stable"];
  };
  config.flake = {
    homeConfigurations.probe.activationPackage = probe;
    nixosConfigurations.probe.config.system.build.toplevel = probe;
    darwinConfigurations.probe.config.system.build.toplevel = probe;
  };
}
