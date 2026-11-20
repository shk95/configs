_: {
  # a modern replacement for `ls`
  programCatalog.eza = {
    profiles = ["shared"];
    nativeEnable = ["programs" "eza" "enable"];
    providers.nix.identifier = "eza";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.eza = {
      enable = lib.mkDefault config.providerTools.programs.eza.enable;
      enableZshIntegration = lib.mkDefault true;
      git = lib.mkDefault true;
    };
  };
}
