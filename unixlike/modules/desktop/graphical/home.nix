# Provide the XDG and Wayland integration used by the Linux graphical session.
_: {
  modules.homeManager.linuxGraphical = {
    config,
    lib,
    ...
  }: let
    terminals =
      lib.optional config.programs.ghostty.enable "com.mitchellh.ghostty.desktop"
      ++ lib.optional config.programs.wezterm.enable "org.wezfurlong.wezterm.desktop";
  in {
    home.sessionVariables = {
      ELECTRON_OZONE_PLATFORM_HINT = "auto";
      MOZ_ENABLE_WAYLAND = "1";
      NIXOS_OZONE_WL = "1";
      _JAVA_AWT_WM_NONREPARENTING = "1";
    };

    gtk.enable = true;
    xdg = {
      enable = true;
      mimeApps.enable = true;
      terminal-exec = {
        enable = true;
        settings = lib.mkIf (terminals != []) {
          default = lib.mkDefault terminals;
          niri = lib.mkDefault terminals;
        };
      };
      userDirs = {
        enable = true;
        createDirectories = true;
        setSessionVariables = true;
      };
    };
  };
}
