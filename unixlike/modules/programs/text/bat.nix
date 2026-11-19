_: {
  modules.homeManager.shared = {pkgs, ...}: {
    # Declared as a program rather than a package, which is what writes the config
    # below — and `programs.bat` contributes the package itself, so it does not
    # also belong in modules/foundation/packages.nix.
    programs.bat = {
      enable = true;

      config = {
        # Follow the terminal's ANSI palette, including Bluegray Light and
        # Ghostty's system-selected dark theme. This also works through SSH:
        # bat emits colour indices and the local terminal resolves them.
        theme = "ansi";

        # Default is `full`, which adds a grid, a file header and a line-number
        # column to every invocation. Keeping `numbers` and `header` keeps what is
        # useful when reading; dropping the grid is what makes the output paste
        # cleanly somewhere else.
        style = "numbers,changes,header";
      };

      # batman only, and the omissions are the decision. `man` itself is left
      # alone: the usual recipe pipes it through bat with a MANPAGER built out of
      # `col`, which means putting util-linux on PATH ahead of Ubuntu's, and that
      # shadows a great deal more than it fixes. batman gets the same coloured man
      # pages as a separate command that nothing else depends on.
      #
      # `batgrep` and `batdiff` are deliberately absent. They wrap `rg` and
      # `git diff`, both of which are already declared and already known, and they
      # are not free: batdiff pulls git-minimal into the closure, which measured at
      # 53 MiB for a command that is `git diff` with a pager.
      extraPackages = [pkgs.bat-extras.batman];
    };
  };
}
