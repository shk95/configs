# The other half of the pair; see a.nix.
_: {
  modules.homeManager.shared = {
    programs.zsh.initContent = "# import-order probe b";
  };
}
