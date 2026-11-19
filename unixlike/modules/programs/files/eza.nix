_: {
  # a modern replacement for `ls`
  modules.homeManager.shared = {
    programs.eza = {
      enable = true;
      git = true;
      icons = "auto";
      enableZshIntegration = true;

      # Keep the terminal's ANSI palette rather than fixing RGB colours here.
      # This also follows the local terminal when the shell runs over SSH.
    };

    # eza 0.23.5 puts red on yellow behind multiple-hardlink counts. Retain
    # their emphasis without a filled rectangle, including with --links.
    # Use EZA_COLORS separately: its `tw`/`su` mean permission characters,
    # whereas GNU LS_COLORS uses those names for directory/file categories.
    home.sessionVariables.EZA_COLORS = "lm=1;35";

    # GNU ls otherwise adds backgrounds for writable/sticky directories,
    # special permissions, devices and broken links. Preserve file-extension
    # colours and signal exceptional entries with foreground/bold/underline.
    # No TERM override: these ANSI styles work inside and outside Zellij,
    # with both xterm-ghostty and xterm-256color.
    programs.dircolors = {
      enable = true;
      settings = {
        FIFO = "33";
        BLK = "01;33";
        CHR = "01;33";
        ORPHAN = "01;31";
        MISSING = "01;31";
        SETUID = "01;31";
        SETGID = "01;35";
        CAPABILITY = "01;31";
        STICKY_OTHER_WRITABLE = "01;04;34";
        OTHER_WRITABLE = "01;04;34";
        STICKY = "04;34";
      };
    };
  };

  modules.homeManager.darwin = {
    # macOS /bin/ls reads LSCOLORS instead of LS_COLORS. Every pair uses
    # `x` for the default background, including special permissions,
    # writable directories and the final macOS dataless-file category.
    home.sessionVariables.LSCOLORS = "ExgxfxdxCxDxDxBxFxExExfx";
  };
}
