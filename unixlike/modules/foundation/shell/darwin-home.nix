_: {
  modules.homeManager.darwin = {
    lib,
    pkgs,
    ...
  }: {
    home = {
      packages = [pkgs.darwin.trash];
      shellAliases.rm = lib.mkDefault "trash";
    };
  };
}
