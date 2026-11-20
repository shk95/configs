_: {
  programCatalog.gh = {
    profiles = ["shared"];
    nativeEnable = ["programs" "gh" "enable"];
    providers.nix.identifier = "gh";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.gh = {
      enable = lib.mkDefault config.providerTools.programs.gh.enable;
    };
  };
}
