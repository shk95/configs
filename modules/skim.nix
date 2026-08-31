_: {
  # skim provides a single executable, `sk`, plus shell keybindings
  # (ctrl-r / ctrl-t / alt-c) compatible with fzf's integration scripts.
  modules.homeManager.shared = {
    programs.skim = {
      enable = true;
      enableZshIntegration = true;

      # skim's default theme is `dark`, and it is 256-colour indices chosen for
      # a dark background — 236 behind the current line, 144 for the match
      # count — so it is wrong the moment the terminal is light. Base `16` is
      # the deferring alternative: it sets ANSI colour *names* as foregrounds
      # and never sets a background at all, so the terminal's palette decides,
      # which is the same bargain `modules/bat.nix` makes with `ansi`. That is
      # what lets a colour choice live in `homeManager.shared` at all, since
      # this class also reaches the WSL homes, whose terminal scheme is
      # declared in the Windows domain.
      #
      # The three overrides are the components base `16` gets wrong at one end
      # or the other. `info` is ANSI white, invisible on a light background —
      # the same defect `modules/starship.nix` carried in its clock — while
      # `border` and `scrollbar` are ANSI black, invisible on a dark one. ANSI
      # 6 (cyan) and ANSI 8 (bright black) are mid-tones in both directions.
      defaultOptions = ["--color=16,info:6,border:8,scrollbar:8"];
    };
  };
}
