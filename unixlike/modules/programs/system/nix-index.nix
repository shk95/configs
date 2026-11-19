_: {
  programCatalog.nix-index = {
    profiles = ["shared"];
    nativeEnable = ["programs" "nix-index" "enable"];
    providers.nix.identifier = "nix-index";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.nix-index = {
      enable = lib.mkDefault config.providerTools.programs.nix-index.enable;
      enableZshIntegration = true;
    };
  };
}
