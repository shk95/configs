{config, ...}: let
  inherit (config.identity) gitName gitEmail;
in {
  modules.homeManager.shared = {lib, ...}: {
    # `programs.git` generates ~/.config/git/config; for it to take effect,
    # ~/.gitconfig must not exist (git reads both, and the later one wins).
    #
    # Moved rather than deleted. home-manager refuses to clobber unmanaged files
    # everywhere else, and this activation script is the one place that escapes
    # that rule — the file it removes is exactly the kind nobody has a copy of.
    # The inventory before M2 found a gh credential helper in it that nothing
    # here reproduced; the next surprise will not be caught by reading.
    home.activation.backupExistingGitconfig = lib.hm.dag.entryBefore ["checkLinkTargets"] ''
      if [ -e "$HOME/.gitconfig" ]; then
        backup="$HOME/.gitconfig.before-home-manager.$(date +%Y%m%d%H%M%S)"
        run mv $VERBOSE_ARG "$HOME/.gitconfig" "$backup"
        echo "Moved an unmanaged ~/.gitconfig to $backup"
      fi
    '';

    programs = {
      git = {
        enable = true;
        lfs.enable = false;

        ignores = [
          ".direnv"
          "*.pem"

          # Carried over from an unmanaged ~/.config/git/ignore, which
          # programs.git generates and would otherwise have replaced wholesale.
          "**/.claude/settings.local.json"
          "**/.claude/.cc-writes/"
        ];

        settings = {
          user = {
            name = gitName;
            email = gitEmail;
          };

          # Carried over from the unmanaged ~/.gitconfig this replaces: without
          # it git escapes non-ASCII paths as octal in status and diff output.
          core.quotepath = false;

          init.defaultBranch = "master";
          push.autoSetupRemote = true;
          pull.rebase = true;
          log.date = "iso";

          # `programs.git.settings` is a freeform passthrough: the attribute
          # name here becomes the gitconfig section header verbatim, so this
          # key must be `alias`, singular — the name Git itself reads. A
          # previous `aliases` here rendered a `[aliases]` section instead of
          # `[alias]` and left every entry below inert; `git st` failed with
          # "'st' is not a git command." `programs.git.aliases` also reaches
          # `[alias]`, but only through a deprecation shim, so declare the
          # canonical name directly instead.
          alias = {
            br = "branch";
            co = "checkout";
            st = "status";
            # The hash is `%C(bold cyan)` rather than `%C(yellow)`. A yellow
            # legible on a dark terminal is by construction a pale tint, and
            # this format string now has to survive a light one as well —
            # Catppuccin Latte's yellow is #df8e1d on a #eff1f5 page. Cyan is a
            # mid-tone in both directions and stays distinct from the `%Cred`
            # refs and the `%Cblue` author beside it.
            ls = ''log --pretty=format:"%C(bold cyan)%h%Cred%d\\ %Creset%s%Cblue\\ [%cn]" --decorate'';
            cm = "commit -m";
            ca = "commit -am";
            dc = "diff --cached";
            amend = "commit --amend -m";

            # Whole-repository graph. `--all` is Git's own definition of
            # "every ref under refs/, including refs/tags/, plus HEAD", so
            # `--tags` alongside it would add nothing — it is intentionally
            # left off rather than added and left inert. `--decorate` is
            # named explicitly because its default is `auto`: ref names show
            # on a terminal and silently disappear once the output is piped.
            lg = "log --all --oneline --graph --decorate";
            # What the last commit actually changed.
            last = "log -1 --stat";
            # File-level summary: usually the right first answer to "what
            # changed" before reading a full patch.
            ds = "diff --stat";
            # The inverse of `git add`, under a name that says so.
            unstage = "reset HEAD --";
            # Makes the alias set discoverable from inside Git rather than by
            # reading this file. It doubles as the regression check for the
            # defect above: it returns nothing while this section is
            # misnamed `[aliases]`.
            aliases = ''config --get-regexp ^alias\.'';
          };
        };
      };

      # Git commands that deliberately get no alias, because knowing them is
      # more useful than shortening them (see README.md, "Develop", for the
      # maintainer-facing version of this list):
      #
      # - `git show`: the last commit with its patch; `git show --stat` for
      #   just the summary; `git show <ref>` for any other commit.
      # - `git diff` (unstaged) vs. `git diff --cached` (staged, aliased
      #   `dc` above) vs. `git diff HEAD` (both at once) — the three-way
      #   distinction behind most "the diff looks wrong" confusion.
      # - `git log -p -1`, and `git log -p -- <path>` to follow one file.
      # - `git show HEAD@{1}` with `git reflog` to recover a previous
      #   position.
      # - `git range-diff` to compare two versions of a series.

      delta = {
        enable = true;
        enableGitIntegration = true;
        options = {
          line-numbers = true;

          # Kept, and now a decision rather than an inherited line. delta
          # paints the added and removed backgrounds itself instead of
          # deferring to the terminal's sixteen colours, because no ANSI colour
          # is faint enough to sit behind a whole diff line; `true-color` is
          # what lets it choose one. That is the opposite bargain from
          # modules/bat.nix, and the difference is deliberate: bat can defer
          # because syntax highlighting is foreground-only, delta cannot
          # because its subject is a background.
          true-color = "always";

          # Deliberately no `light` and no `syntax-theme` in this class.
          # `programs.delta` is in `homeManager.shared`, which also reaches the
          # WSL homes, and those render inside Windows Terminal — a scheme
          # declared in the Windows domain, unreadable from here, and still
          # dark. delta's own defaults are tuned for a dark background, so they
          # remain the honest choice for this class. The light half is declared
          # in `homeManager.desktop` below, where the terminal is one this
          # repository sets.
        };
      };
    };
  };

  # The graphical Unix-like homes. Here the background is a value this flake
  # declares — WezTerm and Ghostty are both set to Flexoki Light — rather than
  # one it has to guess, which is what makes a light-tuned pager legal here
  # and not in `shared`.
  modules.homeManager.desktop = {
    programs.delta.options = {
      # Not cosmetic: `light` is how delta picks the backgrounds it paints for
      # added and removed lines. Left unset it assumes dark and lays dark green
      # and dark red bands across a pale page, which is the highest-traffic
      # coloured output in this repository getting it wrong on every `git
      # diff`, `git show` and `git log -p`.
      light = true;

      # The syntax colours that sit on top of those bands used to name a
      # bundled bat theme from the same family as the two terminals, the way
      # `light` above still does for the diff bands. Flexoki has no such
      # bundled delta/bat theme to name, and modules/bat.nix already declines
      # to guess a named theme for the same reason: `ansi` defers to the
      # terminal's own sixteen colours instead, which on this class is Flexoki
      # Light because WezTerm and Ghostty declare it, and needs no bundled
      # theme to track it.
      syntax-theme = "ansi";
    };
  };
}
