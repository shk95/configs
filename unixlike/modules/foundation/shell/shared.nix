_: {
  # Shared shell initialization and command precedence for Unix-like homes.
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: let
    # INV unixlike/version-manager-last — the two assertions below are the
    # schema half of the rule; tool/checks/flake-test holds both directions.
    #
    # The version manager rewrites PATH, so it runs after every declarative
    # PATH entry: that is what lets a declared package keep precedence on a
    # name collision. The hook is contributed at `lib.mkAfter` below, and the
    # first assertion reads the merged initialisation text, not this file's
    # own string, so a PATH line another module contributes at a later order
    # is refused at evaluation rather than found on a host. A PATH line is a
    # declarative assignment — `path+=(`, `path=(`, `path[1,0]=` or `PATH=`,
    # bare or behind `export`, `typeset` or `declare` and their flags;
    # `fpath+=` is not one. A script sourced or `eval`ed at a later order
    # may also rewrite PATH, and no lexical rule can read it; such a line is
    # not a declarative entry and is the reviewer's to notice.
    initLines = lib.splitString "\n" config.programs.zsh.initContent;
    isPathLine = line: builtins.match "[[:space:]]*((export|typeset|declare)([[:space:]]+-[A-Za-z]+)*[[:space:]]+)?(path|PATH)([[][0-9,]*[]])?\\+?=.*" line != null;
    isHookLine = line: builtins.match ".*sdkman-init\\.sh.*" line != null;
    positions =
      lib.foldl' (
        acc: line: {
          index = acc.index + 1;
          lastPath =
            if isPathLine line
            then acc.index
            else acc.lastPath;
          hook =
            if acc.hook == null && isHookLine line
            then acc.index
            else acc.hook;
        }
      ) {
        index = 0;
        lastPath = null;
        hook = null;
      }
      initLines;
    hookIsLast =
      positions.hook != null && (positions.lastPath == null || positions.lastPath < positions.hook);

    # The toolchain the version manager owns is never also a package, or two
    # version authorities share one PATH. The names are the nixpkgs spellings
    # of the JDK distributions SDKMAN installs, and SDKMAN itself.
    toolchainName = "^(sdkman|openjdk[0-9]*|jdk[0-9]*|jre[0-9]*|zulu[0-9]*|temurin[a-z0-9-]*|graalvm[a-z0-9-]*|corretto[0-9]*|semeru[a-z0-9-]*|jetbrains-jdk[a-z0-9-]*)$";
    declaredToolchains =
      builtins.filter (p: lib.isDerivation p && builtins.match toolchainName (lib.getName p) != null)
      config.home.packages;
  in {
    assertions = [
      {
        assertion = hookIsLast;
        message =
          if positions.hook == null
          then "INV unixlike/version-manager-last: the generated zsh initialisation no longer sources the SDKMAN hook."
          else "INV unixlike/version-manager-last: a PATH entry at line ${toString (positions.lastPath + 1)} of the generated zsh initialisation follows the SDKMAN hook at line ${toString (positions.hook + 1)}; the hook must run after every declarative PATH entry.";
      }
      {
        assertion = declaredToolchains == [];
        message = "INV unixlike/version-manager-last: ${lib.concatMapStringsSep ", " lib.getName declaredToolchains} is declared as a package; the JDK toolchain is the version manager's and is never a nixpkgs package.";
      }
    ];

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

      initContent = lib.mkMerge [
        (lib.mkOrder 1000 ''
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
        '')

        # INV unixlike/version-manager-last — SDKMAN is an imperative
        # shell-function installer rather than a nixpkgs package. It owns JDK
        # distributions and their version switching; `gradle` stays a
        # declarative package in packages.nix, and a Nix JDK would put a second
        # version authority on the same PATH. It is sourced optionally and last
        # because it rewrites PATH: `mkAfter` places it after every default-order
        # contribution, and the assertion above refuses a PATH line that any
        # module puts later still.
        (lib.mkAfter ''
          export SDKMAN_DIR="$HOME/.sdkman"
          [ -s "$SDKMAN_DIR/bin/sdkman-init.sh" ] && . "$SDKMAN_DIR/bin/sdkman-init.sh"
        '')
      ];
    };
  };
}
