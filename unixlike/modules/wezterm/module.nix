# Unix-like WezTerm configuration. Windows owns an independent copy under
# windows/desired/files/wezterm.
_: {
  # A terminal emulator is a desktop application. WSL sessions use a
  # Windows-owned terminal and should not build a second Linux GUI terminal.
  modules.homeManager.desktop = _: {
    programs.wezterm = {
      enable = true;
      enableZshIntegration = true;
    };

    xdg.configFile = {
      "wezterm/wezterm.lua".source = ./wezterm.lua;
      "wezterm/config".source = ./config;
      "wezterm/platform".source = ./platform;
      "wezterm/fonts.json".source = ./fonts.json;
    };
  };
}
