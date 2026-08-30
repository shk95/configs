_: {
  # a modern replacement for `ls`
  modules.homeManager.shared = {
    programs.eza = {
      enable = true;
      git = true;
      icons = "auto";
      enableZshIntegration = true;

      # Neither `theme` nor `colors` is set, and the default is already right
      # on a light background. eza's built-in palette emits nothing but the
      # sixteen ANSI SGR codes: `eza --color=always -l` on the pinned eza
      # 0.23.5 produces `1;34` for a directory, `33`/`31`/`32` across the
      # permission bits, `1;90` for their placeholders and `34` for the date.
      # Every one of those is an index into the terminal's own palette, so eza
      # renders in whatever colours the terminal declares — the same deference
      # `modules/bat.nix` makes with its `ansi` theme. The familiar "dark blue
      # directories on white" complaint is about a terminal whose ANSI blue is
      # #0000ee; under Catppuccin Latte it is #1e66f5.
      #
      # `programs.eza.theme` would write $XDG_CONFIG_HOME/eza/theme.yml with
      # fixed values and end that deference, which is precisely what a module
      # in `homeManager.shared` cannot honestly do: this class also reaches the
      # WSL homes, whose terminal scheme is declared in the Windows domain.
    };
  };
}
