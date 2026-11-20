# One Ghostty configuration for graphical Unix-like hosts. The Home Manager
# module writes the same XDG config on Linux and macOS; package ownership is the
# platform-specific part.
_: {
  programCatalog.ghostty = {
    profiles = ["desktop"];
    requiredClasses = ["desktop"];
    nativeEnable = ["programs" "ghostty" "enable"];
    defaults = {
      linux = "nix";
      darwin = "homebrew";
    };
    providers = {
      nix = {
        identifier = "ghostty";
        platforms = ["x86_64-linux" "aarch64-linux"];
      };
      homebrew = {
        identifier = "ghostty";
        kind = "cask";
      };
    };
  };
  modules.homeManager.desktop = {
    config,
    lib,
    pkgs,
    ...
  }: {
    configs.editableFiles = lib.mkIf config.programs.ghostty.enable {
      "${config.xdg.configHome}/ghostty/config" = lib.mkDefault true;
    };
    programs.ghostty =
      lib.mkIf (
        (pkgs.stdenv.hostPlatform.isLinux && config.providerTools.programs.ghostty.enable)
        || (
          config.providerTools.programs.ghostty.enable
          && builtins.elem "ghostty" config.providerDarwin.homebrew.casks
          && config.providerDarwin.appSettings.enable
          && config.providerDarwin.appSettings.ghostty
        )
      ) {
        enable = lib.mkDefault true;

        # Manual integration survives switching shells inside Ghostty. The
        # feature list keeps Ghostty's precise xterm-ghostty capabilities locally,
        # installs terminfo on SSH destinations when possible, and falls back to
        # xterm-256color when the remote host cannot run tic.
        enableZshIntegration = lib.mkDefault true;
        settings = {
          shell-integration = lib.mkDefault "detect";
          shell-integration-features = lib.mkDefault "sudo,ssh-env,ssh-terminfo,path";
          window-padding-balance = lib.mkDefault true;
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
        config.providerTools.programs.ghostty.enable
        && builtins.elem "ghostty" config.providerDarwin.homebrew.casks
        && config.providerDarwin.appSettings.enable
        && config.providerDarwin.appSettings.ghostty
      ) {
        # nixpkgs' Ghostty package is Linux-only. Homebrew owns the macOS app;
        # Home Manager still owns and writes its XDG configuration.
        package = null;
      };
  };
}
