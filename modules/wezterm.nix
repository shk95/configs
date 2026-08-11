# Unix-like WezTerm configuration. Windows owns an independent copy under
# windows/desired/files/wezterm.
_: {
  modules.homeManager.shared = {pkgs, ...}: {
    programs.wezterm = {
      enable = true;
      package = pkgs.wezterm;
      enableZshIntegration = true;
    };

    xdg.configFile = {
      "wezterm/wezterm.lua".source = ../assets/wezterm/wezterm.lua;
      "wezterm/config".source = ../assets/wezterm/config;
      "wezterm/platform".source = ../assets/wezterm/platform;
      "wezterm/fonts.json".source = ../assets/wezterm/fonts.json;
    };
  };
}
