_: {
  modules.homeManager.shared = {
    programs.neovim = {
      enable = true;
      defaultEditor = true;
      vimAlias = true;
      withRuby = false;
      withPython3 = false;

      # No `background` and no colourscheme, and that is a decision rather than
      # an omission. The pinned Neovim is 0.12.4, whose `:help 'background'`
      # reads "The |TUI| or other UI sets this on startup if it can detect the
      # background color" — the terminal is asked and its answer is used, so
      # `nvim` follows whichever terminal it opens in instead of this flake
      # declaring a background on the terminal's behalf.
      #
      # That is the same deference `modules/bat.nix` chooses with `ansi`, and
      # it is chosen for the same reason: this module is in
      # `homeManager.shared`, which also reaches the WSL homes, and those
      # render inside Windows Terminal — a scheme declared in the Windows
      # domain and unreadable from here. Writing `set background=light` would
      # pin those homes to a background they do not have, which is the failure
      # this repository's light default is supposed to end, not relocate.
      #
      # The documented default, `dark`, is only the fallback for a terminal
      # that never answers the query, and the one terminal here that might not
      # answer is the one that is still dark.
    };
  };
}
