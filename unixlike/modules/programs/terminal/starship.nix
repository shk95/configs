_: {
  programCatalog.starship = {
    profiles = ["shared"];
    nativeEnable = ["programs" "starship" "enable"];
    providers.nix.identifier = "starship";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.starship = {
      enable = lib.mkDefault config.providerTools.programs.starship.enable;
      enableZshIntegration = lib.mkDefault true;

      settings.nix_shell.heuristic = lib.mkDefault true;
    };
  };
}
