# Unix-like WezTerm configuration. Windows owns an independent copy under
# windows/desired/files/wezterm.
_: {
  # A terminal emulator is a desktop application. WSL sessions use a
  # Windows-owned terminal and carry no Linux GUI applications.
  programCatalog.wezterm = {
    profiles = ["desktop"];
    requiredClasses = ["desktop"];
    nativeEnable = ["programs" "wezterm" "enable"];
    providers.nix.identifier = "wezterm";
  };
  modules.homeManager.desktop = {
    config,
    lib,
    ...
  }: {
    programs.wezterm = {
      enable = lib.mkDefault config.providerTools.programs.wezterm.enable;
      enableZshIntegration = lib.mkDefault true;
    };

    xdg.configFile."wezterm/wezterm.lua".source = lib.mkIf config.programs.wezterm.enable (lib.mkDefault ./wezterm.lua);
    configs.editableFiles = lib.mkIf config.programs.wezterm.enable {
      "${config.xdg.configHome}/wezterm/wezterm.lua" = lib.mkDefault true;
    };
  };
}
