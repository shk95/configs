_: {
  programCatalog.tealdeer = {
    profiles = ["shared"];
    nativeEnable = ["programs" "tealdeer" "enable"];
    providers.nix.identifier = "tealdeer";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.tealdeer = {
      enable = lib.mkDefault config.providerTools.programs.tealdeer.enable;
      settings.display.use_pager = lib.mkDefault true;
    };
  };
}
