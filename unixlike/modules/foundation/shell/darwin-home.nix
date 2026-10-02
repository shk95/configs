_: {
  modules.homeManager.darwin = {pkgs, ...}: {
    # The shared shell module owns zsh. This fragment contains only the macOS
    # command and alias that have no portable equivalent.
    home = {
      packages = [pkgs.darwin.trash];
      shellAliases.rm = "trash";
    };
  };
}
