local module = {}

-- Light is this repository's declared default for the terminals it owns, so
-- the colour choices made elsewhere stop guessing at a background. Flexoki
-- Light is the light member of the same family modules/ghostty.nix selects,
-- which is what keeps the two terminals on a graphical host looking like one
-- setup rather than two.
--
-- Unlike the Catppuccin scheme this replaces, WezTerm does not ship Flexoki
-- built in, so the scheme is defined here rather than merely named. Values
-- are taken from Ghostty's own built-in "Flexoki Light" theme (verified in
-- the pinned nixpkgs ghostty package's `share/ghostty/themes/Flexoki Light`),
-- which traces to the canonical palette at https://github.com/kepano/flexoki.
-- ANSI 5/13 carry Flexoki's own "magenta" accent rather than "purple" — the
-- palette keeps purple for non-ANSI, scheme-level accents (see
-- modules/git.nix and the zellij asset) and fills the magenta slot with its
-- own colour instead of aliasing it to purple.
local flexoki_light = {
  background = "#FFFCF0", -- paper
  foreground = "#100F0F", -- black
  cursor_bg = "#100F0F",
  cursor_border = "#100F0F",
  cursor_fg = "#FFFCF0",
  selection_bg = "#CECDC3", -- base-200
  selection_fg = "#100F0F",
  ansi = {
    "#100F0F", -- black
    "#AF3029", -- red (600)
    "#66800B", -- green (600)
    "#AD8301", -- yellow (600)
    "#205EA6", -- blue (600)
    "#A02F6F", -- magenta (600)
    "#24837B", -- cyan (600)
    "#6F6E69", -- white / base-600
  },
  brights = {
    "#B7B5AC", -- bright black / base-300
    "#D14D41", -- bright red (400)
    "#879A39", -- bright green (400)
    "#D0A215", -- bright yellow (400)
    "#4385BE", -- bright blue (400)
    "#CE5D97", -- bright magenta (400)
    "#3AA99F", -- bright cyan (400)
    "#CECDC3", -- bright white / base-200
  },
}

function module.apply_to_config(config)
  config.color_schemes = config.color_schemes or {}
  config.color_schemes["Flexoki Light"] = flexoki_light
  config.color_scheme = "Flexoki Light"
  config.font_size = 15.0
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

  -- De-emphasis has to run the other way round on a light background. The
  -- previous brightness of 0.65 dimmed an inactive pane toward black: on a
  -- dark scheme that reads as receding, on Latte it darkens dark text against
  -- a pale page, which raises contrast rather than lowering it, and drags the
  -- pastels toward mud. Multiplying brightness up instead fades the pane
  -- toward the page (Latte's text lightens and its base clips to white)
  -- while the lower saturation drains the accents, so an inactive pane loses
  -- contrast rather than gaining grime.
  config.inactive_pane_hsb = {
    saturation = 0.7,
    brightness = 1.25,
  }

  config.window_frame = {
    font_size = 13.0,
  }
end

return module
