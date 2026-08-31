# One Ghostty configuration for graphical Unix-like hosts. The Home Manager
# module writes the same XDG config on Linux and macOS; package ownership is the
# platform-specific part.
_: {
  modules.homeManager.desktop = {
    programs.ghostty = {
      enable = true;

      # Manual integration survives switching shells inside Ghostty. The
      # feature list keeps Ghostty's precise xterm-ghostty capabilities locally,
      # installs terminfo on SSH destinations when possible, and falls back to
      # xterm-256color when the remote host cannot run tic.
      enableZshIntegration = true;
      settings = {
        shell-integration = "detect";
        shell-integration-features = "sudo,ssh-env,ssh-terminfo,path";

        font-family = "D2KodingLigature Nerd Font Mono";
        font-size = 14;
        # Flexoki Light is the light member of the same family WezTerm
        # selects in assets/wezterm/config/appearance.lua; keeping both
        # terminals in one family is what stops a graphical host from looking
        # like two different machines. Ghostty ships both "Flexoki Light" and
        # "Flexoki Dark" as built-in themes (verified in the pinned nixpkgs
        # ghostty package's share/ghostty/themes/), so the dual form here
        # needs no extra file: Ghostty answers the terminal's own light/dark
        # appearance rather than the colour-scheme query modules/zellij.nix
        # describes, and switches between the two names on its own.
        theme = "light:Flexoki Light,dark:Flexoki Dark";
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
    programs.ghostty = {
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
