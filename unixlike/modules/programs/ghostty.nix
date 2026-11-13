# One Ghostty configuration for graphical Unix-like hosts. The Home Manager
# module writes the same XDG config on Linux and macOS; package ownership is the
# platform-specific part.
_: {
  modules.homeManager.desktop = {
    config,
    lib,
    pkgs,
    ...
  }: {
    programs.ghostty =
      lib.mkIf (
        pkgs.stdenv.hostPlatform.isLinux
        || (
          builtins.elem "ghostty" config.providerDarwin.selectedApps
          && config.providerDarwin.appSettings.enable
          && config.providerDarwin.appSettings.ghostty
        )
      ) {
        enable = true;

        # Manual integration survives switching shells inside Ghostty. The
        # feature list keeps Ghostty's precise xterm-ghostty capabilities locally,
        # installs terminfo on SSH destinations when possible, and falls back to
        # xterm-256color when the remote host cannot run tic.
        enableZshIntegration = true;
        themes."Bluegray Light" = {
          background = "#ECEFF3";
          # Let the desktop show through softly while keeping the light page.
          background-opacity = 0.90;
          background-blur = 20;
          foreground = "#303640";
          cursor-color = "#303640";
          cursor-text = "#ECEFF3";
          selection-background = "#D6E1F0";
          selection-foreground = "#303640";
          # Bright accents retain their hue and contrast on the light page.
          # ANSI white is a readable neutral, not a pale foreground.
          palette = [
            "0=#303640"
            "1=#9A3F4A"
            "2=#35604A"
            "3=#76561F"
            "4=#355A87"
            "5=#664C82"
            "6=#2D626D"
            "7=#576474"
            "8=#576474"
            "9=#9A3F4A"
            "10=#35604A"
            "11=#76561F"
            "12=#355A87"
            "13=#664C82"
            "14=#2D626D"
            "15=#303640"
          ];
        };
        settings = {
          shell-integration = "detect";
          shell-integration-features = "sudo,ssh-env,ssh-terminfo,path";

          font-family = "D2KodingLigature Nerd Font Mono";
          font-size = 14;
          # Keep all light colours in the theme so they cannot override the
          # dark member when Ghostty follows the system appearance.
          theme = "light:Bluegray Light,dark:Modus Vivendi";
          minimum-contrast = 1.1;

          cursor-style = "block";
          cursor-style-blink = false;
          mouse-hide-while-typing = true;
          copy-on-select = "clipboard";

          window-padding-x = 10;
          window-padding-y = 8;
          window-padding-balance = true;

          # Useful for long builds without notifying for every short command.
          notify-on-command-finish = "unfocused";
          notify-on-command-finish-action = "no-bell,notify";
          notify-on-command-finish-after = "10s";
        };
      };
  };

  modules.homeManager.darwin = {
    config,
    lib,
    ...
  }: {
    programs.ghostty =
      lib.mkIf (
        builtins.elem "ghostty" config.providerDarwin.selectedApps
        && config.providerDarwin.appSettings.enable
        && config.providerDarwin.appSettings.ghostty
      ) {
        # nixpkgs' Ghostty package is Linux-only. Homebrew owns the macOS app;
        # Home Manager still owns and writes its XDG configuration.
        package = null;
        settings = {
          # Keep right Option available for macOS character input.
          macos-option-as-alt = "left";
          window-save-state = "always";
        };
      };
  };
}
