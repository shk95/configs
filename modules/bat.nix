_: {
  modules.homeManager.shared = {pkgs, ...}: {
    # Declared as a program rather than a package, which is what writes the config
    # below — and `programs.bat` contributes the package itself, so it does not
    # also belong in modules/packages.nix.
    programs.bat = {
      enable = true;

      config = {
        # `ansi` renders with the terminal's own sixteen colours instead of a
        # palette bat carries itself. That is the right default here rather than a
        # taste: the colour scheme is a Windows Terminal setting this flake cannot
        # read, so any named theme is a guess about a value declared somewhere
        # else, and it is wrong in exactly the case that hurts — a light scheme
        # under a theme built for a dark one. `ansi` cannot disagree with the
        # terminal because it has no opinion of its own.
        #
        # That premise survived this repository adopting a light default; it was
        # not removed by it. `programs.bat` is in `homeManager.shared`, so it
        # reaches both WSL homes, and their shells render inside Windows
        # Terminal — `windows/desired/files/terminal/settings.json`, owned by
        # the Windows domain and still selecting a dark scheme. Setting WezTerm
        # and Ghostty to Catppuccin Latte says nothing about those hosts, so a
        # named light theme here would be the same guess it always was. If one
        # is ever wanted it belongs in a class that excludes the WSL homes, not
        # in this one.
        #
        # It is also still the right answer on the terminals this change does
        # fix: `ansi` resolves to whatever palette the terminal declares, which
        # on Latte is Latte. Deferring costs nothing here.
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
