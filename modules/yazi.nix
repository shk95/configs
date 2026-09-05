_: {
  # terminal file manager
  modules.homeManager.shared = {pkgs, ...}: {
    programs.yazi = {
      enable = true;
      enableZshIntegration = true;
      shellWrapperName = "yy";

      settings = {
        # Upstream's table is `mgr`, not `manager`. The lock now pins yazi
        # 26.8.15; 26.5.6 was the pin until the 2026-08-31 lock refresh, and
        # is still the host's currently activated version — a fact about
        # the host, not evidence about what the lock resolves to today. The
        # pinned preset `yazi-config/preset/yazi-default.toml` has a `[mgr]`
        # table and no `[manager]`; `yazi-config/src` contains no occurrence
        # of the string `manager` at all. Yazi ignores an unknown table
        # instead of refusing it, so the two settings this module used to
        # declare under `manager` rendered into `yazi.toml` but were
        # silently dropped at load on the pinned version. The pinned Home
        # Manager module's own `settings` example (line 154 of
        # `modules/programs/yazi.nix`) writes `mgr = { show_hidden = ...;
        # }` directly — the closer witness, since it is the same option
        # this module sets — and its `keymap` example likewise uses
        # `mgr.prepend_keymap`, confirming the same rename on the keymap
        # side. `show_hidden` and `sort_dir_first` are carried over under
        # the corrected table name; `sort_by` and `linemode` are new, added
        # as part of the same baseline.
        mgr = {
          show_hidden = true;
          sort_dir_first = true;
          sort_by = "natural";
          linemode = "size";
        };

        # `git.yazi` (declared under `plugins` below) registers itself as a
        # fetcher; without these two entries the plugin still loads and its
        # `setup()` still runs, but the manager never asks it for a status,
        # so no git column ever appears. Both entries — one for files, the
        # trailing `/` one for directories — come from the plugin's own
        # README.
        plugin.prepend_fetchers = [
          {
            url = "*";
            run = "git";
            group = "git";
          }
          {
            url = "*/";
            run = "git";
            group = "git";
          }
        ];
      };

      # Plugins come from the pinned nixpkgs `yaziPlugins` set (packages
      # `git.yazi`, `full-border.yazi`, `smart-enter.yazi`). Home Manager
      # links each package to `~/.config/yazi/plugins/<name>.yazi` and, for
      # an entry with `setup = true`, writes a `require("<name>"):setup()`
      # call into `init.lua`.
      plugins = {
        # Per-file git status in the list, fed by the fetcher entries
        # above; the plugin's README asks for both the setup call and those
        # two entries, and the default column order is kept as-is.
        git = {
          package = pkgs.yaziPlugins.git;
          setup = true;
        };

        # Draws the full frame around the manager rather than yazi's plain
        # single-line borders. Its default border type is rounded — the
        # pinned plugin's `main.lua` reads `local type = opts and opts.type
        # or ui.Border.ROUNDED` — and `settings.type` is how that default
        # would be changed, not set here. On the light preset its colour is
        # the preset's own border colour — whether that reads clearly is a
        # runtime check on the terminal, not something evaluation can
        # confirm.
        full-border = {
          package = pkgs.yaziPlugins.full-border;
          setup = true;
        };

        # No setup call: `smart-enter` is invoked directly from the keymap
        # below rather than through init.lua. Its `entry()` function reads
        # the hovered item and emits `enter` when it is a directory or
        # `open` otherwise (`h and h.cha.is_dir and "enter" or "open"`); the
        # unified key comes from that branch, not from `--hovered`, which
        # only narrows the `open` it emits to the hovered file. That has a
        # cost: the pinned preset binds `<Enter>` to plain `open` ("Open
        # selected files"), so once this entry is in place, `<Enter>` stops
        # opening a multi-file selection — `o`, still bound to plain
        # `open`, is what opens the whole selection now.
        smart-enter = pkgs.yaziPlugins.smart-enter;
      };

      keymap.mgr.prepend_keymap = [
        {
          on = "l";
          run = "plugin smart-enter";
          desc = "Enter the child directory, or open the file";
        }
        {
          on = "<Enter>";
          run = "plugin smart-enter";
          desc = "Enter the child directory, or open the file";
        }
      ];

      # Neither `theme` nor `flavors` is set. Both pinned presets still open
      # with "If the user's terminal is in dark mode, Yazi will load
      # `theme-dark.toml` on startup; otherwise, `theme-light.toml`" — the
      # decision itself is made in `yazi-emulator/src/emulator.rs`:
      # `light()` returns the terminal's own colour-scheme report (`CSI
      # ? 997 ; 2 n` answering "light") when one arrives, otherwise falls
      # back to the luma of the terminal's `OSC 11` background-colour reply
      # (> 0.6 counts as light), and returns `None` when neither answer
      # comes back at all; `build_flavor(emulator.light().unwrap_or_default())`
      # then treats that `None` as dark.
      #
      # Windows Terminal 1.23.20211.0 does not answer the colour-scheme
      # query — probed by the maintainer on 2026-09-05, only the terminal's
      # DA1 response came back — so inside Windows Terminal the light
      # preset depends entirely on the `OSC 11` reply, and that reply has
      # not been observed yet. This module does not claim Windows Terminal
      # gets the light preset; that observation belongs here once it
      # exists, recorded after activation, and only then is `theme` or
      # `flavors` worth revisiting.
      #
      # Also deliberately absent: a Modus flavor (none is packaged in the
      # pinned nixpkgs, and nothing should be fetched from the network at
      # evaluation time), openers, previewers, `vfs`, the `lazygit` yazi
      # plugin (lazygit is its own issue), and any image-preview
      # configuration — sixel support in Windows Terminal is that
      # terminal's decision, not this module's.
    };
  };
}
