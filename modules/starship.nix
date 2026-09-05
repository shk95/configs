# Every key below changes a starship default, and that is the point of the
# rewrite rather than a coincidence. The version this replaces set 28 keys of
# which 20 restated the default exactly — it read as a configured prompt while
# doing nothing, and the noise hid two real defects among the eight lines that
# did have an effect.
#
# The check is mechanical, because starship will print its computed
# configuration with the defaults filled in:
#
#   STARSHIP_CONFIG=/dev/null starship print-config > default.toml
#   starship print-config                           > ours.toml
#   diff default.toml ours.toml
#
# Anything absent from that diff can be deleted without changing the prompt.
# Worth re-running after a starship upgrade: a moved default turns a line here
# into a no-op, or a deletion into a change.
_: {
  modules.homeManager.shared = {
    programs.starship = {
      enable = true;
      enableZshIntegration = true;

      settings = {
        # Default is `❯` in red for both states. A different glyph reads faster
        # than a colour change on a prompt that is already coloured, and it
        # survives a terminal palette where red and green sit close together.
        character.error_symbol = "[✗](bold red)";

        directory = {
          style = "bold blue";
          # Default is the empty string, which makes a truncated path
          # indistinguishable from a short one: `configs` could be the repo root
          # or four levels down inside it.
          truncation_symbol = "…/";
        };

        # Emoji, not the default ``, which is a Nerd Font glyph. The terminal
        # here is Windows Terminal and its font is a Windows setting this flake
        # cannot reach, so relying on a Nerd Font would mean relying on a value
        # declared somewhere this repository does not own. See modules/fonts.nix.
        git_branch.symbol = "🌿 ";

        git_status = {
          # Counts, which the defaults omit: `⇡` says the branch is ahead, `⇡3`
          # says how much work is waiting to be pushed.
          ahead = "⇡$count";
          behind = "⇣$count";
          diverged = "⇕⇡$ahead_count⇣$behind_count";

          # The backslash is load-bearing, and its absence was a real bug. `$`
          # opens a variable reference in a starship format string, so the bare
          # `"$"` here before was parsed as one, resolved to nothing, and dropped
          # the stash indicator entirely — `[?]` with a stash present, where
          # starship's own default `'\$'` gives `[$?]`.
          stashed = "\\$$count";
        };

        # Default is `bold yellow`. Magenta was legible but thin once the
        # background went light — Catppuccin Latte's is #ea76cb on a #eff1f5
        # page — and yellow is worse, because a yellow that reads on black is
        # by construction a pale tint. Cyan is a mid-tone in both directions —
        # #179299 on Latte, dark enough to read against a light page and bright
        # enough against a dark one — which is what a style in
        # `homeManager.shared` has to be. The premise has since narrowed: the
        # WSL homes this class also reaches render inside a Windows Terminal
        # the Windows domain declares light
        # (`docs/decisions/composed-homes-render-in-declared-terminals.md`).
        # `bold cyan` stands on the same reason it always did — a mid-tone
        # needs no declaration to be right — rather than on a terminal being
        # dark.
        cmd_duration.style = "bold cyan";

        # This module was configured, dead, *and* wrong — two independent defects
        # that hid each other. `disabled = true` is its default, so nothing here
        # ever rendered; and the format it carried was `[$hour:$minute]($style)`,
        # referring to two variables the module does not have. It exposes `$time`
        # and nothing else, so once enabled that format resolved to a bare `:`.
        # The clock shape belongs in `time_format`, which is strftime — `%R` is
        # `%H:%M`.
        #
        # A third defect, and the one this repository's light default exposes:
        # the style was a bold `white`, which is invisible on a light
        # background — Latte's ANSI white is #acb0be on a #eff1f5 page — and
        # starship's own default here, `bold yellow`, is barely better. `bold`
        # with no colour is the fix rather than a half-written style: it uses
        # the terminal's own foreground, which is the one colour guaranteed to
        # contrast with the terminal's own background, whichever background
        # that turns out to be. That is the same deference `modules/bat.nix`
        # makes with its `ansi` theme, and the only kind this class can
        # honestly make while it also reaches the WSL homes. `format`,
        # `time_format` and `disabled` are untouched; only the colour was
        # wrong.
        time = {
          disabled = false;
          format = "[$time]($style) ";
          time_format = "%R";
          style = "bold";
        };

        # By default this module reads IN_NIX_SHELL and nothing else, and the two
        # ways into a nix shell do not agree on setting it:
        #
        #   nix develop            IN_NIX_SHELL=impure   shown either way
        #   nix shell nixpkgs#hello  (unset)             shown only with this
        #
        # So the gap is `nix shell` — the form used to try a package for five
        # minutes, which is exactly when forgetting you are inside one is easy.
        nix_shell.heuristic = true;
      };
    };
  };
}
