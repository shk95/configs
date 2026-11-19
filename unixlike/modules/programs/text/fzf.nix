_: {
  modules.homeManager.shared = {
    programs.fzf = {
      enable = true;
      enableZshIntegration = true;
      enableBashIntegration = false;
      enableFishIntegration = false;
      enableNushellIntegration = false;
      # Keep upstream walkers, matching and widget actions. Base16 uses
      # terminal backgrounds; its current row uses bright white. Use the
      # default foreground for that row (upstream already makes it bold),
      # and ANSI 8 instead of dim default text for the border. The separator
      # inherits the border colour, so it needs no independent override.
      defaultOptions = [
        "--height=40%"
        "--layout=reverse"
        "--border"
        "--color=16,fg+:-1,border:8"
      ];
    };
  };
}
