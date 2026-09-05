_: {
  modules.homeManager.shared = {
    # `programs.lazygit` contributes its own package, so INV
    # unixlike/package-ownership keeps lazygit out of modules/packages.nix —
    # the same shape modules/bat.nix uses for bat. `settings` below is the
    # pinned Home Manager module's freeform passthrough; it renders to
    # ~/.config/lazygit/config.yml (Darwin without xdg:
    # Library/Application Support/lazygit/config.yml). lazygit itself is
    # 0.64.1 in the locked nixpkgs, which is the version the
    # `selectedLineBgColor` comment below cites.
    #
    # The keys below must match 0.64.1's current config schema exactly, not a
    # remembered or a documented-elsewhere shape. lazygit normally migrates a
    # legacy key forward in place and writes the migrated file back to disk,
    # but under Home Manager that file is a symlink into the read-only Nix
    # store: the write-back fails and lazygit exits 1 instead of starting, so
    # a key it would otherwise have quietly migrated is fatal here instead. A
    # future nixpkgs bump that retires a key needs the same check before it
    # lands in this file (see `git.diffRenderers` below, which used to be
    # `git.paging` for exactly this reason).
    #
    # Deliberately absent: custom keybindings, custom commands, the yazi
    # lazygit plugin, `gui.theme.inactiveViewSelectedLineBgColor` (0.64.1
    # already defaults it to `["bold"]`, so setting it here would only
    # restate a default rather than decide anything), and any hex colour in
    # the theme. Removing `tig` from modules/packages.nix is a separate
    # decision the maintainer has not made; both stay until then.
    programs.lazygit = {
      enable = true;

      # Writes the `lg` shell function into the generated zsh initialisation
      # — the same wrapper shape modules/yazi.nix uses for `yy`.
      # `shellWrapperName` is left at its default (`lg`) rather than renamed.
      enableZshIntegration = true;

      settings = {
        gui = {
          # Both sides of the domain boundary declare a Nerd Font for the
          # terminals this repository configures: modules/ghostty.nix and
          # WezTerm's font list (assets/wezterm/fonts.json) set
          # D2KodingLigature Nerd Font Mono on the Unix-like side, and the
          # Windows Terminal payload
          # (windows/desired/files/terminal/settings.json) sets the same
          # face on the Windows side — true only once that domain's own
          # Apply has run there, which this file cannot verify for itself.
          # Declaring nerdFontsVersion here in `shared`, which also reaches
          # the WSL homes rendering inside that Windows-owned terminal, is
          # therefore safe: every terminal this repository configures, on
          # either side of the domain boundary, already declares that face
          # lazygit assumes.
          nerdFontsVersion = "3";

          theme = {
            # lazygit's own default paints the selected row with a `blue`
            # background under the terminal's default foreground; under
            # Flexoki Light that background is #205EA6 and the foreground is
            # #100F0F, which works out to a contrast of roughly 2.9:1 by the
            # WCAG relative-luminance formula, below the 3:1 floor even for
            # large text. `reverse` sidesteps the question rather than
            # answering it with another guess: it swaps the terminal's own
            # foreground and background for the row instead of naming a
            # colour of its own, the same bargain modules/skim.nix makes with
            # `--color=16` for its selected line. lazygit 0.64.1's
            # docs/Config.md lists `reverse` as a valid theme attribute and
            # calls it out as "useful for high-contrast".
            selectedLineBgColor = ["reverse"];
          };
        };

        # 0.64.1 has no `git.paging`; the key this repository first shipped
        # here was already retired in favour of `git.diffRenderers`; a
        # config carrying the old key is exactly the migrate-then-write-back
        # failure the header comment describes, which is what makes this the
        # current shape rather than a style preference.
        git.diffRenderers = [
          {
            # `type` defaults to `stdinFilter` and `colorArg` to `always`,
            # which is what delta wants; both are left at their defaults.
            #
            # No `--dark` or `--light` flag on the command itself.
            # `programs.delta` already carries a `[delta]` section in git
            # config (modules/git.nix) that answers that question per Home
            # Manager class — `light = true` in `homeManager.desktop`, left
            # unset in `shared` because the WSL homes render inside a
            # Windows-owned terminal this flake cannot inspect. delta reads
            # that section whether git or lazygit invokes it, so this
            # command inherits the same per-class decision without deciding
            # anything about the background itself.
            command = "delta --paging=never";
          }
        ];
      };
    };
  };
}
