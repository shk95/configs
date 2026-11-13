local module = {}

-- Same light palette as Ghostty's Bluegray Light theme. All ANSI foregrounds,
-- including white and the bright variants, remain readable on the cool page.
local bluegray_light = {
  background = "#ECEFF3",
  foreground = "#303640",
  cursor_bg = "#303640",
  cursor_border = "#303640",
  cursor_fg = "#ECEFF3",
  selection_bg = "#D6E1F0",
  selection_fg = "#303640",
  split = "#576474",
  tab_bar = {
    background = "#E1E6ED",
    active_tab = { bg_color = "#D6E1F0", fg_color = "#355A87", intensity = "Bold" },
    inactive_tab = { bg_color = "#E1E6ED", fg_color = "#576474" },
    inactive_tab_hover = { bg_color = "#D6E1F0", fg_color = "#303640" },
    new_tab = { bg_color = "#E1E6ED", fg_color = "#576474" },
    new_tab_hover = { bg_color = "#D6E1F0", fg_color = "#355A87" },
  },
  ansi = {
    "#303640",
    "#9A3F4A",
    "#35604A",
    "#76561F",
    "#355A87",
    "#664C82",
    "#2D626D",
    "#576474",
  },
  brights = {
    "#576474",
    "#9A3F4A",
    "#35604A",
    "#76561F",
    "#355A87",
    "#664C82",
    "#2D626D",
    "#303640",
  },
}

function module.apply_to_config(config)
  config.color_schemes = config.color_schemes or {}
  config.color_schemes["Bluegray Light"] = bluegray_light
  config.color_scheme = "Bluegray Light"
  config.window_background_opacity = 0.90
  config.macos_window_background_blur = 20
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

  -- Lift and desaturate inactive panes slightly on a light background.
  config.inactive_pane_hsb = {
    saturation = 0.7,
    brightness = 1.25,
  }

  config.window_frame = {
    font_size = 13.0,
  }
end

return module
