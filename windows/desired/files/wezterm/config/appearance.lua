local module = {}

function module.apply_to_config(config)
  config.color_scheme = "Catppuccin Latte"
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

  config.inactive_pane_hsb = {
    saturation = 0.8,
    brightness = 0.65,
  }

  config.window_frame = {
    font_size = 12.0,
  }
end

return module
