_: {
  # Interactive shell behavior is user state, so every Unix-like home consumes
  # one module. Platform modules add only genuine platform deltas such as the
  # Darwin trash command.
  modules.homeManager.shared = {lib, ...}: {
    home.sessionVariables = {
      # Keep locale behavior independent of the login shell. Ubuntu provides
      # this locale through its system archive; macOS supports it natively.
      LANG = "en_US.UTF-8";
    };

    programs.zsh = {
      enable = true;
      enableCompletion = true;
      syntaxHighlighting.enable = true;

      # Completion behaviour belongs here rather than in initContent. `zstyle` is
      # read by the completion system when a completion actually runs, so the two
      # are identical in effect — but this option only exists when
      # `enableCompletion` is on, which makes the dependency structural instead of
      # something a reader has to notice.
      completionInit = ''
        autoload -Uz compinit
        compinit

        # Lowercase input matches uppercase names: `~/dow<tab>` finds `Downloads`.
        # One-directional on purpose — uppercase input stays exact, so a name
        # typed in full case still means what it says.
        zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'
      '';

      initContent = lib.mkOrder 1000 ''
        # Standalone installers may place commands here. Append instead of
        # prepend so declarative packages keep precedence when names overlap.
        typeset -U path
        path+=("$HOME/.local/bin")
        path+=("$HOME/.opencode/bin")

        # SDKMAN is an imperative shell-function installer rather than a
        # nixpkgs package. Keep it optional and last because it rewrites PATH.
        # It owns JDK distributions and their version switching; `gradle` stays
        # a declarative package in packages.nix. Adding a Nix JDK would put a
        # second version authority on the same PATH. See docs/status.md,
        # "Unix-like Home Manager and package ownership".
        export SDKMAN_DIR="$HOME/.sdkman"
        [ -s "$SDKMAN_DIR/bin/sdkman-init.sh" ] && . "$SDKMAN_DIR/bin/sdkman-init.sh"
      '';
    };
  };
}
