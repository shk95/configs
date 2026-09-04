# Deliberately order-sensitive. The class merge is keyed by file
# (modules/flake/module-classes.nix), so the dependence enters through a
# flake-level list option two files contribute to at the same order and one
# home reads: the walk order decides the list, and so the generated file.
# tool/checks/import-order-test requires this pair to be rejected.
{
  config,
  lib,
  ...
}: {
  options.importOrderProbe = lib.mkOption {
    type = lib.types.listOf lib.types.str;
    default = [];
  };

  config = {
    importOrderProbe = ["a"];
    modules.homeManager.shared.programs.zsh.initContent = "# import-order probe " + lib.concatStringsSep "" config.importOrderProbe;
  };
}
