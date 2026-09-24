# Linux desktop integration shared by Niri applications. Fonts stay in the
# existing homeManager.desktop concern and are deliberately untouched here.
_: {
  modules.homeManager.linuxGraphical = {
    config,
    pkgs,
    ...
  }: {
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

    programs.firefox = {
      enable = true;
      # Firefox is new to the managed Linux graphical home, so it can adopt
      # Home Manager's current XDG location without migrating host state.
      configPath = "${config.xdg.configHome}/mozilla/firefox";
    };

    xdg = {
      enable = true;
      mimeApps = {
        enable = true;
        defaultApplications = {
          "application/pdf" = ["firefox.desktop"];
          "audio/*" = ["mpv.desktop"];
          "image/gif" = ["imv.desktop"];
          "image/jpeg" = ["imv.desktop"];
          "image/png" = ["imv.desktop"];
          "image/webp" = ["imv.desktop"];
          "inode/directory" = ["thunar.desktop"];
          "text/html" = ["firefox.desktop"];
          "video/*" = ["mpv.desktop"];
          "x-scheme-handler/http" = ["firefox.desktop"];
          "x-scheme-handler/https" = ["firefox.desktop"];
        };
      };

      terminal-exec = {
        enable = true;
        settings = {
          default = [
            "com.mitchellh.ghostty.desktop"
            "org.wezfurlong.wezterm.desktop"
          ];
          niri = [
            "com.mitchellh.ghostty.desktop"
            "org.wezfurlong.wezterm.desktop"
          ];
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
