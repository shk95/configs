_: {
  modules.darwin.system = {
    pkgs,
    config,
    ...
  }: {
    # Create /etc/zshrc that loads the nix-darwin environment.
    # this is required if you want to use darwin's default shell - zsh
    programs.zsh.enable = true;
    environment = {
      shells = [
        pkgs.zsh
      ];
      variables = {
        # Fix https://github.com/LnL7/nix-darwin/wiki/Terminfo-issues
        TERMINFO_DIRS =
          map (path: path + "/share/terminfo") config.environment.profiles
          ++ [
            "/usr/share/terminfo"
          ];
      };
    };
  };
}
