local module = {}

function module.apply_to_config(config)
  -- Light is this repository's declared default for the terminals it owns, so
  -- the colour choices made elsewhere stop guessing at a background. Latte is
  -- the light member of the same Catppuccin family modules/ghostty.nix
  -- selects, which is what keeps the two terminals on a graphical host looking
  -- like one setup rather than two. WezTerm ships the scheme built in, so
  -- naming it needs no extra file.
  config.color_scheme = "Catppuccin Latte"
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
