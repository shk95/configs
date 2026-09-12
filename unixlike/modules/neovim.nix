_: {
  modules.homeManager.shared = {
    programs.neovim = {
      enable = true;
      defaultEditor = true;
      vimAlias = true;
      withRuby = false;
      withPython3 = false;

      # No `background` and no colourscheme, and that is a decision rather than
      # an omission. The pinned Neovim is 0.12.5, whose `:help 'background'`
      # reads "The |TUI| or other UI sets this on startup if it can detect the
      # background color" — the terminal is asked and its answer is used, so
      # `nvim` follows whichever terminal it opens in instead of this flake
      # declaring a background on the terminal's behalf.
      #
      # That is the same deference `modules/bat.nix` chooses with `ansi`, and
      # it survives the premise that used to be given for it. This module is in
      # `homeManager.shared`, which also reaches the WSL homes, and those render
      # inside Windows Terminal — a scheme the Windows domain declares, which
      # code here may not read but which has been light since #97, so every home
      # this repository composes now renders in a terminal it declares itself
      # (`docs/decisions/composed-homes-render-in-declared-terminals.md`).
      # Deference is not chosen because that scheme is unreadable; it is chosen
      # because asking the terminal needs no declaration at all, and so needs no
      # revision when one of them changes. A pinned `background` would.
      #
      # The documented default, `dark`, is only the fallback for a terminal that
      # never answers Neovim's background query. That query is an OSC 11 request
      # for the background colour, which is not the CSI 996 colour-scheme report
      # zellij's theme pair depends on and Windows Terminal 1.23 was probed not
      # to send (see assets/zellij/config.kdl). Whether Windows Terminal answers
      # OSC 11 has not been observed from here; it is the one open question in
      # this comment, and it is a native runtime check on the WSL host rather
      # than something to assert either way.
    };
  };
}
