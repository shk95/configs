local module = {}

-- Light is this repository's declared default for the terminals it owns, so
-- the colour choices made elsewhere stop guessing at a background. Modus
-- Operandi is the light member of the same family modules/ghostty.nix
-- selects, which is what keeps the two terminals on a graphical host looking
-- like one setup rather than two.
--
-- Unlike the Catppuccin scheme this file once carried, and like the Flexoki
-- one it carried after that, WezTerm does not ship Modus built in, so the
-- scheme is defined here rather than merely named. Values are taken from the
-- pinned nixpkgs ghostty package's `share/ghostty/themes/Modus Operandi`,
-- which is the same file modules/ghostty.nix selects by name; that port
-- traces through mbadolato/iTerm2-Color-Schemes to the canonical palette at
-- https://github.com/protesilaos/modus-themes.
--
-- One property of that port is recorded here rather than corrected: ANSI 15,
-- nominally "bright white", is #595959 — darker than ANSI 7's #a6a6a6 — so
-- the bright half does not brighten at the neutral poles. On this white page
-- that is the more readable of the two rather than a defect (#595959 reaches
-- 7.0:1 against #ffffff, #a6a6a6 only 2.43:1), and reproducing the pinned
-- file exactly is what keeps this table and Ghostty's built-in theme the same
-- scheme. Swapping the two here would make a graphical host render two
-- palettes that merely share a name.
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
  config.color_schemes = config.color_schemes or {}
  config.color_schemes["Modus Operandi"] = modus_operandi
  config.color_scheme = "Modus Operandi"
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

  -- De-emphasis has to run the other way round on a light background, and on
  -- this scheme it barely runs at all — which is worth writing down rather
  -- than leaving to be discovered. The transform is multiplicative in HSV, so
  -- the previous brightness of 0.65 dimmed an inactive pane toward black: on a
  -- dark scheme that reads as receding, but against a white page it darkens
  -- text that is already dark, raising contrast rather than lowering it, and
  -- drags the accents toward mud. Multiplying brightness up instead is the
  -- correct direction, and it stays.
  --
  -- What it cannot do on this scheme is move either of the two colours the eye
  -- reads most. Modus Operandi's foreground is #000000, whose V is 0 and is
  -- therefore invariant under any multiplier, and its background is #ffffff,
  -- whose V is already 1 and clips. An inactive pane's text and page come out
  -- byte-identical to an active pane's. Only the sixteen ANSI accents move:
  -- saturation 0.7 drains them toward grey, and brightness 1.25 lifts the ones
  -- not already pinned at an extreme. De-emphasis here is therefore carried by
  -- the accents alone, which is a weaker effect than on a scheme whose
  -- background sits somewhere in the middle, and that is accepted rather than
  -- worked around: the values are still the right direction, and a stronger
  -- effect would have to come from a setting that repaints the page instead of
  -- scaling it.
  config.inactive_pane_hsb = {
    saturation = 0.7,
    brightness = 1.25,
  }

  config.window_frame = {
    font_size = 13.0,
  }
end

return module
