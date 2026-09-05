local module = {}

-- Copied from the Unix-like asset `assets/wezterm/config/appearance.lua` on
-- 2026-09-05, when the Unix-like domain replaced Flexoki Light with Modus
-- Operandi (#163). This is a copy, not a shared source: the Windows domain
-- owns it from here and may diverge from the Unix-like palette without that
-- being a failure, the way every other Windows copy of Unix-like material is
-- owned. The palette is carried inline rather than named as a WezTerm preset
-- so the rendered scheme does not depend on which schemes the installed
-- WezTerm build happens to bundle. The pinned Ghostty `Modus Operandi` file
-- is the source of the background, the foreground, the selection background
-- and ANSI 0-15. It names nothing for the three cursor keys or the selection
-- foreground, so those reuse the two colours it does name — cursor fill,
-- cursor border and selection foreground take the foreground, cursor text
-- takes the background — rather than introducing a colour the source palette
-- never chose.
--
-- ANSI 15 (`#595959`) is darker than ANSI 7 (`#A6A6A6`) in this port. That
-- inversion is upstream's and is copied as-is rather than corrected, because
-- a local correction would make this payload disagree with the Unix-like
-- terminals rendering the same sessions. It is also the readable half: on the
-- white background ANSI 15 reaches 7.0:1 while ANSI 7 reaches 2.43:1, so text
-- painted in ANSI 7 is effectively invisible either way.
local modus_operandi = {
  background = "#FFFFFF",
  foreground = "#000000",
  cursor_bg = "#000000",
  cursor_border = "#000000",
  cursor_fg = "#FFFFFF",
  selection_bg = "#BDBDBD",
  selection_fg = "#000000",
  ansi = {
    "#000000", -- black
    "#A60000", -- red
    "#006800", -- green
    "#6F5500", -- yellow
    "#0031A9", -- blue
    "#721045", -- magenta
    "#005E8B", -- cyan
    "#A6A6A6", -- white
  },
  brights = {
    "#595959", -- bright black
    "#972500", -- bright red
    "#00663F", -- bright green
    "#884900", -- bright yellow
    "#3548CF", -- bright blue
    "#531AB6", -- bright magenta
    "#005F5F", -- bright cyan
    "#595959", -- bright white
  },
}

function module.apply_to_config(config)
  config.color_schemes = {
    ["Modus Operandi"] = modus_operandi,
  }
  config.color_scheme = "Modus Operandi"
  config.font_size = 13.0
  config.line_height = 1.05

  config.window_padding = {
    left = 10,
    right = 10,
    top = 8,
    bottom = 8,
  }

  config.use_fancy_tab_bar = false
  config.hide_tab_bar_if_only_one_tab = false
  config.show_new_tab_button_in_tab_bar = false
  config.tab_max_width = 28

  -- Copied from #35's Unix-like Catppuccin Latte tuning
  -- (assets/wezterm/config/appearance.lua); this domain owns the copy from here.
  config.inactive_pane_hsb = {
    saturation = 0.7,
    brightness = 1.25,
  }

  config.window_frame = {
    font_size = 12.0,
  }
end

return module
