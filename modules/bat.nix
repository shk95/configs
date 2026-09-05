_: {
  modules.homeManager.shared = {pkgs, ...}: {
    # Declared as a program rather than a package, which is what writes the config
    # below — and `programs.bat` contributes the package itself, so it does not
    # also belong in modules/packages.nix.
    programs.bat = {
      enable = true;

      config = {
        # `ansi` renders with the terminal's own sixteen colours instead of a
        # palette bat carries itself. It was chosen rather than a named theme
        # because the colour scheme was a Windows Terminal setting this flake
        # could not read, so any named theme was a guess about a value declared
        # somewhere else, and it was wrong in exactly the case that hurts — a
        # light scheme under a theme built for a dark one. `ansi` cannot
        # disagree with the terminal because it has no opinion of its own.
        #
        # The premise moved; the conclusion did not move with it. `programs.bat`
        # is in `homeManager.shared`, so it reaches both WSL homes, and their
        # shells render inside Windows Terminal —
        # `windows/desired/files/terminal/settings.json`, owned by the Windows
        # domain, which has declared a light scheme since #97. Every home this
        # repository composes now renders in a terminal it declares itself, and
        # every one of those is light
        # (`docs/decisions/composed-homes-render-in-declared-terminals.md`), so
        # a named light theme here would no longer be the guess the paragraph
        # above calls it, and `homeManager.desktop` — the class that excludes
        # the WSL homes — is no longer where it would have to go.
        #
        # `ansi` stays anyway, for the reason that does not depend on any of
        # that: deferral needs no theme at all. It resolves to whatever palette
        # the terminal declares — Flexoki Light in WezTerm and in the WSL
        # homes' Windows Terminal, and whichever half of its pair Ghostty is
        # currently on — so it cannot disagree with a declared terminal, and it
        # needs no revision when one of them changes. A named theme would.
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
