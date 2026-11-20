_: {
  modules.homeManager.darwin = {pkgs, ...}: {
    home.packages = [pkgs.darwin.trash];
  };
}
