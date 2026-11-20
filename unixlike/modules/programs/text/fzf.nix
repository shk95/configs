_: {
  programCatalog.fzf = {
    profiles = ["shared"];
    nativeEnable = ["programs" "fzf" "enable"];
    providers.nix.identifier = "fzf";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.fzf = {
      enable = lib.mkDefault config.providerTools.programs.fzf.enable;
      enableZshIntegration = lib.mkDefault true;
      enableBashIntegration = lib.mkDefault false;
      enableFishIntegration = lib.mkDefault false;
      enableNushellIntegration = lib.mkDefault false;
      # Keep upstream walkers, matching and widget actions. Base16 uses
      # terminal backgrounds; its current row uses bright white. Use the
      # default foreground for that row (upstream already makes it bold),
      # and ANSI 8 instead of dim default text for the border. The separator
      # inherits the border colour, so it needs no independent override.
      defaultOptions = lib.mkDefault ["--height=40%" "--color=16,fg+:-1,border:8"];
    };
  };
}
