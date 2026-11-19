# Linux desktop integration shared by Niri applications. Fonts stay in the
# existing homeManager.desktop concern and are deliberately untouched here.
_: {
  modules.homeManager.linuxGraphical = {
    config,
    lib,
    pkgs,
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
    home.pointerCursor = {
      enable = true;
      gtk.enable = true;
      x11.enable = true;
      package = pkgs.bibata-cursors;
      name = "Bibata-Modern-Ice";
      size = 24;
    };

    xdg = {
      enable = true;
      mimeApps = {
        enable = true;
        defaultApplications =
          {"inode/directory" = ["thunar.desktop"];}
          // lib.optionalAttrs config.providerTools.programs.imv.enable {
            "image/gif" = ["imv.desktop"];
            "image/jpeg" = ["imv.desktop"];
            "image/png" = ["imv.desktop"];
            "image/webp" = ["imv.desktop"];
          }
          // lib.optionalAttrs config.programs.firefox.enable {
            "application/pdf" = ["firefox.desktop"];
            "text/html" = ["firefox.desktop"];
            "x-scheme-handler/http" = ["firefox.desktop"];
            "x-scheme-handler/https" = ["firefox.desktop"];
          }
          // lib.optionalAttrs config.programs.mpv.enable {
            "audio/*" = ["mpv.desktop"];
            "video/*" = ["mpv.desktop"];
          };
      };

      terminal-exec = {
        enable = true;
        settings = lib.mkIf (terminals != []) {
          default = terminals;
          niri = terminals;
        };
      };

      userDirs = {
        enable = true;
        createDirectories = true;
        setSessionVariables = true;
        extraConfig.SCREENSHOTS = "${config.xdg.userDirs.pictures}/Screenshots";
      };
    };
  };
}
