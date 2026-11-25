_: {
  # Shared shell initialization and command precedence for Unix-like homes.
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.readline = {
      enable = lib.mkDefault true;
      # Retain the platform-provided inputrc alongside Home Manager.
      includeSystemConfig = lib.mkDefault true;
    };

    programs.zsh = {
      enable = lib.mkDefault true;
      enableCompletion = true;
      completionInit = lib.mkDefault ''
        autoload -Uz compinit
        compinit

        # Lowercase input can also complete uppercase names.
        zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'
      '';
      syntaxHighlighting.enable = true;

      # Preserve the state-version 25.11 location explicitly before Home
      # Manager changes its default. Existing homes keep ~/.zshrc in place.
      dotDir = config.home.homeDirectory;

      initContent = lib.mkOrder 1000 ''
        # zsh's KEYTIMEOUT defaults to 40 (hundredths of a second = 400ms):
        # the delay after Esc before zsh decides no more keys of an escape
        # sequence are coming. Lowered to 20 (200ms) to cut the felt lag when
        # leaving insert mode, while staying comfortably above the few
        # milliseconds a local terminal, WSL, or an SSH/zellij hop needs to
        # deliver a full multi-byte sequence, so arrow and function keys keep
        # working. Matched by readline's keyseq-timeout=200 above so the two
        # editors feel the same.
        KEYTIMEOUT=20

        # modules/programs/text/fzf.nix supplies Ctrl-R in viins and vicmd after the
        # default keymap is selected. Command-mode / and n/N retain zsh's
        # native vi history search; no later bindkey -v resets the widgets.

        # Standalone installers may place commands here. Append instead of
        # prepend so declarative packages keep precedence when names overlap.
        # INV unixlike/import-order-independence — this string sits at the
        # default order; the class imports are keyed by file and
        # tool/checks/import-order proves no host depends on the walk.
        typeset -U path
        path+=("$HOME/.local/bin")
      '';
    };
  };
}
