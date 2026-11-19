_: {
  programCatalog.zoxide = {
    profiles = ["shared"];
    nativeEnable = ["programs" "zoxide" "enable"];
    providers.nix.identifier = "zoxide";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.zoxide = {
      enable = lib.mkDefault config.providerTools.programs.zoxide.enable;
      enableZshIntegration = true;
    };
  };
}
