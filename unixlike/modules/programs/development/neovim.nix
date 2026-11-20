_: {
  programCatalog.neovim = {
    profiles = ["shared"];
    nativeEnable = ["programs" "neovim" "enable"];
    providers.nix.identifier = "neovim";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.neovim = {
      enable = lib.mkDefault config.providerTools.programs.neovim.enable;
      withRuby = lib.mkDefault false;
      withPython3 = lib.mkDefault false;
    };
  };
}
