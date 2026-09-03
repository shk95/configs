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

    # Modal (vi) editing, declared rather than inherited by accident.
    #
    # Previously nothing declared it: neither `bindkey -e` nor `bindkey -v`
    # ran, so zsh fell back to inspecting $VISUAL/$EDITOR and picked `viins`
    # because modules/neovim.nix sets `programs.neovim.defaultEditor = true`,
    # exporting EDITOR=nvim, and "nvim" contains the substring "vi".
    # Replacing Neovim with an editor whose name lacks "vi" would silently
    # revert the shell to emacs bindings, with no error and nothing in the
    # repository to explain the change. `defaultKeymap` below makes the
    # choice structural instead of an accident of $EDITOR's spelling.
    #
    # zsh only edits zsh, and this repository never chooses a login shell:
    # `git grep -nE 'defaultUserShell|users\.users\..*\.shell|programs\.bash'`
    # over `modules/` is empty, and `modules/darwin-shell.nix` only registers
    # zsh as a permitted shell — it does not select it. Choosing the login
    # shell is `chsh`, run out-of-band by `Justfile`'s `switch-shell` recipe
    # (see docs/troubleshooting.md); this repository does not own that act.
    # Until it has run, `nixosConfigurations.wsl` logs into NixOS's default
    # `bashInteractive` and the Ubuntu standalone host logs into whatever bash
    # the account already had, so the zsh keymap alone would not reach every
    # host. `programs.readline` below is the one declaration that reaches
    # bash — and every other readline-linked program, such as python3, psql,
    # sqlite3, gdb, and bc — regardless of which shell a host happens to log
    # into, which is why it is declared next to the zsh keymap rather than in
    # a file of its own: their two ergonomic knobs (zsh's KEYTIMEOUT below,
    # and readline's keyseq-timeout/show-mode-in-prompt) are decided together
    # here so the two editors do not drift into silently different behaviour.
    programs.readline = {
      enable = true;
      variables = {
        editing-mode = "vi";

        # readline's analogue of zsh's KEYTIMEOUT (see the comment on it
        # below), already expressed in milliseconds (default 500). Matched to
        # zsh's 200ms rather than decided separately.
        keyseq-timeout = 200;

        # Neither zsh nor readline shows the current mode by default, so
        # there is no on-screen answer to "insert or normal". zsh's answer (a
        # prompt segment) is excluded from this change — it belongs in
        # modules/starship.nix, whose header requires every key to change a
        # default, and starship only sets `enableZshIntegration` here, so
        # bash has no starship segment to add a glyph to anyway. readline's
        # own `show-mode-in-prompt` has no such dependency: it is the only
        # on-screen indicator bash and other readline programs get from this
        # change, so it is turned on.
        show-mode-in-prompt = true;
      };

      # Kept at its default (true): it emits `$include /etc/inputrc`, which is
      # how the Ubuntu host keeps its distribution's own readline bindings
      # alongside the two variables above.
      includeSystemConfig = true;
    };

    programs.zsh = {
      enable = true;
      enableCompletion = true;
      syntaxHighlighting.enable = true;

      # Replaces the implicit $EDITOR-derived selection described above.
      defaultKeymap = "viins";

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
        # zsh's KEYTIMEOUT defaults to 40 (hundredths of a second = 400ms):
        # the delay after Esc before zsh decides no more keys of an escape
        # sequence are coming. Lowered to 20 (200ms) to cut the felt lag when
        # leaving insert mode, while staying comfortably above the few
        # milliseconds a local terminal, WSL, or an SSH/zellij hop needs to
        # deliver a full multi-byte sequence, so arrow and function keys keep
        # working. Matched by readline's keyseq-timeout=200 above so the two
        # editors feel the same.
        KEYTIMEOUT=20

        # Reverse history search was confirmed reachable, not assumed: the
        # default viins keymap that `defaultKeymap` activates rebinds ^R to
        # `redisplay`, not `history-incremental-search-backward` (checked
        # with `bindkey -v; bindkey -M viins`), but the companion vicmd
        # (command-mode) keymap keeps its own default `/` ->
        # vi-history-search-backward with `n`/`N` to repeat (checked with
        # `bindkey -v; bindkey -M vicmd`). Reverse search stays reachable via
        # Esc then `/`, so no explicit rebinding is added here.

        # Standalone installers may place commands here. Append instead of
        # prepend so declarative packages keep precedence when names overlap.
        # INV unixlike/import-order-independence — this string sits at the
        # default order, so another module's PATH line at that order merges in
        # directory-walk order; pending #128 tracks the check.
        typeset -U path
        path+=("$HOME/.local/bin")

        # INV unixlike/version-manager-last — SDKMAN is an imperative
        # shell-function installer rather than a nixpkgs package. It owns JDK
        # distributions and their version switching; `gradle` stays a
        # declarative package in packages.nix, and a Nix JDK would put a second
        # version authority on the same PATH. It is sourced optionally and last
        # because it rewrites PATH. "Last" rests on this block's position in
        # one string and on no other module adding PATH later; pending #129
        # tracks the check.
        export SDKMAN_DIR="$HOME/.sdkman"
        [ -s "$SDKMAN_DIR/bin/sdkman-init.sh" ] && . "$SDKMAN_DIR/bin/sdkman-init.sh"
      '';
    };
  };
}
