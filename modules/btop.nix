_: {
  modules.homeManager.shared = {
    # `programs.btop` contributes its own package, so INV
    # unixlike/package-ownership keeps btop out of modules/packages.nix — the
    # same shape modules/bat.nix and modules/lazygit.nix use for their
    # packages (docs/decisions/package-ownership-by-generating-module.md).
    #
    # btop cannot defer to the terminal's sixteen ANSI colours the way
    # modules/bat.nix (`theme = "ansi"`) and modules/skim.nix (`--color=16`)
    # do: every bundled btop theme is a full palette, `--tty`/`force_tty`
    # degrades the whole interface to 16 colours and ANSI graph symbols
    # rather than picking a theme from them, and btop's own internal
    # `Default`/`TTY` fallback themes paint main_bg black (`btop_theme.cpp`:
    # `Default_theme["main_bg"] = "#00"`, `TTY_theme["main_bg"] =
    # "\x1b[0;40m"` unless `theme_background` is false). Naming a light
    # theme here rests on
    # docs/decisions/composed-homes-render-in-declared-terminals.md: every
    # home this repository composes renders in a terminal the repository
    # itself declares, and every one of those is light, so `homeManager.shared`
    # is no longer a guess about a background this flake cannot read.
    #
    # The pinned btop 1.4.7 bundles no Modus theme (its `share/btop/themes/`
    # carries `flexoki-light`/`flexoki-dark` among others, but nothing named
    # for Modus), so the theme below is a file `programs.btop.themes`
    # writes to `~/.config/btop/themes/modus-operandi.theme`; btop matches a
    # `color_theme` name against a theme file's stem
    # (`btop_theme.cpp:setTheme`), so the name here and the attribute name
    # below must agree, which they do.
    #
    # Key mapping: `flexoki-light.theme` is the template (same 48 `theme[...]`
    # keys, in the same order); every value below is one of the Modus
    # Operandi ANSI 0-15 colours, background, foreground, or selection grey,
    # verified in the pinned nixpkgs ghostty package's
    # `share/ghostty/themes/Modus Operandi` — background `#FFFFFF`,
    # foreground `#000000`, selection `#BDBDBD` — the same file the whole
    # Modus Operandi adoption copies from and the same citation style
    # `assets/wezterm/config/appearance.lua` uses for its own Flexoki
    # palette. `modules/ghostty.nix` and that WezTerm file carry these same
    # values once #163 lands. No invented hex. `hi_fg` and the four box outlines
    # (`cpu_box`/`mem_box`/`net_box`/`proc_box`) are ANSI 4/2/5/6, matching
    # `shown_boxes` below. `selected_bg`, `meter_bg`, `div_line` and
    # `free_start` share the selection grey rather than an ANSI index,
    # because dividers and meters read as UI chrome rather than data.
    # `inactive_fg`/`graph_text`/`free_mid` are ANSI 8 (ANSI 15 is the same
    # value in this port). Every `*_start`/`_mid`/`_end` gradient is drawn
    # from ANSI indices, per key rather than by one uniform rule: `cpu` and
    # `process` run ANSI 6 or 2 (cyan/green) → ANSI 3 (yellow) → ANSI 1
    # (red); `used` runs ANSI 2 → ANSI 9 → ANSI 1; `temp` runs ANSI 4 →
    # ANSI 13 → ANSI 1, the same cool-to-hot direction the template itself
    # uses for temperature; `free` runs the selection grey → ANSI 8 → ANSI
    # 2; `cached` and `download` both run ANSI 12 → ANSI 4 → ANSI 6;
    # `upload` runs ANSI 13 → ANSI 5 → ANSI 11; `available` runs ANSI 11 →
    # ANSI 3 → ANSI 9. `flexoki-light.theme` supplied only its 48-key list
    # here, not this colour logic — its own comments name what each
    # gradient is for, not a rule connecting a worse or better reading to a
    # direction. `main_bg` below is `#FFFFFF`, but with `theme_background =
    # false` set, btop overrides it at runtime with `\x1b[49m` — the
    # terminal's own default background (`btop_theme.cpp:246-250`) — so that
    # value only ever paints if the flag is later flipped to true.
    # `proc_banner_fg` and `followed_fg` read the same `#FFFFFF` for a
    # different reason: banner text needs to read against the solid banner
    # colour rather than against whatever `main_bg` would otherwise be.
    #
    # Values carried from the host's hand-written `~/.config/btop/btop.conf`
    # (11 KiB, dated 2026-09-04, selecting a light theme by an absolute
    # store path that breaks on the next btop rebuild): `update_ms`,
    # `proc_sorting`. Both already match btop's own defaults — as do
    # `truecolor`, `rounded_corners` and `graph_symbol` above — so writing
    # them here pins them against upstream drift rather than reflecting an
    # unusual host choice. `shown_boxes` is widened on purpose from the host's
    # `"cpu"` — a one-box view — to all four; the maintainer can shrink it
    # back. Everything else is left at btop's own default
    # (`btop --default-config`), so this module writes only the keys it
    # decided.
    #
    # Activation note: Home Manager refuses to overwrite a file it does not
    # already manage. The host's `~/.config/btop/btop.conf` is exactly such
    # a file, so it must be moved aside (or the activation run with
    # `-b backup`) before the next `home-manager switch` on that host;
    # `~/.config/btop/themes/` is empty there today, so no theme file needs
    # the same treatment.
    programs.btop = {
      enable = true;
      settings = {
        color_theme = "modus-operandi";
        theme_background = false;
        truecolor = true;
        vim_keys = true;
        rounded_corners = true;
        graph_symbol = "braille";
        update_ms = 2000;
        proc_sorting = "cpu lazy";
        shown_boxes = "cpu mem net proc";
      };
      themes.modus-operandi = ''
        theme[main_bg]="#FFFFFF"
        theme[main_fg]="#000000"
        theme[title]="#000000"
        theme[hi_fg]="#0031A9"
        theme[selected_bg]="#BDBDBD"
        theme[selected_fg]="#000000"
        theme[inactive_fg]="#595959"
        theme[graph_text]="#595959"
        theme[meter_bg]="#BDBDBD"
        theme[proc_misc]="#006800"
        theme[cpu_box]="#0031A9"
        theme[mem_box]="#006800"
        theme[net_box]="#721045"
        theme[proc_box]="#005E8B"
        theme[div_line]="#BDBDBD"
        theme[temp_start]="#0031A9"
        theme[temp_mid]="#531AB6"
        theme[temp_end]="#A60000"
        theme[cpu_start]="#005E8B"
        theme[cpu_mid]="#6F5500"
        theme[cpu_end]="#A60000"
        theme[free_start]="#BDBDBD"
        theme[free_mid]="#595959"
        theme[free_end]="#006800"
        theme[cached_start]="#3548CF"
        theme[cached_mid]="#0031A9"
        theme[cached_end]="#005E8B"
        theme[available_start]="#884900"
        theme[available_mid]="#6F5500"
        theme[available_end]="#972500"
        theme[used_start]="#006800"
        theme[used_mid]="#972500"
        theme[used_end]="#A60000"
        theme[download_start]="#3548CF"
        theme[download_mid]="#0031A9"
        theme[download_end]="#005E8B"
        theme[upload_start]="#531AB6"
        theme[upload_mid]="#721045"
        theme[upload_end]="#884900"
        theme[process_start]="#006800"
        theme[process_mid]="#6F5500"
        theme[process_end]="#A60000"
        theme[proc_pause_bg]="#A60000"
        theme[proc_follow_bg]="#0031A9"
        theme[proc_banner_bg]="#531AB6"
        theme[proc_banner_fg]="#FFFFFF"
        theme[followed_bg]="#0031A9"
        theme[followed_fg]="#FFFFFF"
      '';
    };
  };
}
