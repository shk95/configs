_: {
  # terminal file manager
  programCatalog.yazi = {
    profiles = ["shared"];
    nativeEnable = ["programs" "yazi" "enable"];
    providers.nix.identifier = "yazi";
  };
  modules.homeManager.shared = {
    lib,
    config,
    pkgs,
    ...
  }: {
    programs.yazi = {
      enable = lib.mkDefault config.providerTools.programs.yazi.enable;
      enableZshIntegration = lib.mkDefault true;
      shellWrapperName = lib.mkDefault "yy";
      settings.mgr.sort_by = lib.mkDefault "natural";

      settings.plugin.prepend_fetchers = lib.mkIf config.programs.git.enable (lib.mkDefault (map (url: {
        inherit url;
        run = "git";
        group = "git";
      }) ["*" "*/"]));
      plugins.git = lib.mkIf config.programs.git.enable (lib.mkDefault {
        package = pkgs.yaziPlugins.git;
        setup = true;
      });
    };
  };
}
