_: {
  # terminal file manager
  modules.homeManager.shared = {
    programs.yazi = {
      enable = true;
      enableZshIntegration = true;
      shellWrapperName = "yy";
      settings = {
        manager = {
          show_hidden = true;
          sort_dir_first = true;
        };
      };

      # Neither `theme` nor `flavors` is set, and the default is already right
      # on a light background. The pinned yazi 26.5.6 ships both
      # `theme-dark.toml` and `theme-light.toml` and picks between them from
      # the terminal it starts in; its own preset says so in as many words —
      # "If the user's terminal is in dark mode, Yazi will load
      # `theme-dark.toml` on startup; otherwise, `theme-light.toml`." The file
      # manager therefore already follows the terminal, which is what this
      # repository's light default asks for and the only promise
      # `homeManager.shared` can make while the WSL homes render inside a
      # Windows-owned terminal.
      #
      # `programs.yazi.theme` writes $XDG_CONFIG_HOME/yazi/theme.toml, which
      # overrides *both* presets. Declaring a light theme there would replace a
      # correct automatic choice with a fixed guess, so the knob is left alone
      # on purpose.
    };
  };
}
