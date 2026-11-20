_: {
  programCatalog.mpv = {
    profiles = ["linuxGraphical"];
    platforms = ["x86_64-linux" "aarch64-linux"];
    requiredClasses = ["linuxGraphical"];
    nativeEnable = ["programs" "mpv" "enable"];
    providers.nix.identifier = "mpv";
  };
  modules.homeManager.linuxGraphical = {
    config,
    lib,
    pkgs,
    ...
  }: {
    programs.mpv = {
      enable = lib.mkDefault config.providerTools.programs.mpv.enable;
      scripts = lib.mkDefault [pkgs.mpvScripts.mpris];
    };
  };
}
