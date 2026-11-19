_: {
  programCatalog.direnv = {
    profiles = ["shared"];
    nativeEnable = ["programs" "direnv" "enable"];
    providers.nix.identifier = "direnv";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.direnv = {
      enable = lib.mkDefault config.providerTools.programs.direnv.enable;
      enableZshIntegration = true;
      nix-direnv.enable = true;
    };
  };
}
