_: {
  programCatalog.firefox = {
    profiles = ["linuxGraphical"];
    platforms = ["x86_64-linux" "aarch64-linux"];
    requiredClasses = ["linuxGraphical"];
    nativeEnable = ["programs" "firefox" "enable"];
    providers.nix.identifier = "firefox";
  };
  modules.homeManager.linuxGraphical = {
    config,
    lib,
    ...
  }: {
    programs.firefox = {
      enable = lib.mkDefault config.providerTools.programs.firefox.enable;
      configPath = "${config.xdg.configHome}/mozilla/firefox";
    };
  };
}
