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
      enableZshIntegration = true;
    };

    xdg.configFile = lib.mkIf config.programs.wezterm.enable {
      "wezterm/wezterm.lua".source = ./wezterm.lua;
      "wezterm/config/appearance.lua".source = ./config/appearance.lua;
      "wezterm/config/behavior.lua".source = ./config/behavior.lua;
      "wezterm/config/bindings.lua".source = ./config/bindings.lua;
      "wezterm/config/fonts.lua".source = ./config/fonts.lua;
      "wezterm/config/startup.lua".source = ./config/startup.lua;
      "wezterm/platform/darwin.lua".source = ./platform/darwin.lua;
      "wezterm/platform/linux.lua".source = ./platform/linux.lua;
      "wezterm/platform/windows.lua".source = ./platform/windows.lua;
      "wezterm/fonts.json".source = ./fonts.json;
    };
    # A finite selection, not a directory rule: future configuration files keep
    # normal store links unless they are explicitly added here.
    configs.editableFiles = lib.mkIf config.programs.wezterm.enable (lib.genAttrs (map
      (name: "${config.xdg.configHome}/wezterm/${name}") [
        "wezterm.lua"
        "fonts.json"
        "config/appearance.lua"
        "config/behavior.lua"
        "config/bindings.lua"
        "config/fonts.lua"
        "config/startup.lua"
        "platform/darwin.lua"
        "platform/linux.lua"
        "platform/windows.lua"
      ]) (_: lib.mkDefault true));
  };
}
