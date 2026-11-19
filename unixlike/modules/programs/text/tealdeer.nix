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
      enableAutoUpdates = false;
      settings = {
        display = {
          compact = false;
          use_pager = true;
        };
        updates.auto_update = false;
      };
    };
  };
}
