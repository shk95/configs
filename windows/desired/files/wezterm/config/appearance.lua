local module = {}

function module.apply_to_config(config)
  -- Inline scheme, not the built-in WezTerm preset of the same name; this
  -- domain owns its own copy of the Flexoki Light port from
  -- https://github.com/kepano/flexoki/blob/main/wezterm/Flexoki%20Light.toml.
  config.color_schemes = {
    ["Flexoki Light"] = {
      foreground = "#100F0F",
      background = "#FFFCF0",

      cursor_bg = "#403E3C",
      cursor_fg = "#FFFCF0",
      cursor_border = "#403E3C",

      selection_fg = "#100F0F",
      selection_bg = "#E6E4D9",

      ansi = {
        "#100F0F",
        "#AF3029",
        "#66800B",
        "#AD8301",
        "#205EA6",
        "#A02F6F",
        "#24837B",
        "#DAD8CE",
      },
      brights = {
        "#B7B5AC",
        "#D14D41",
        "#879A39",
        "#D0A215",
        "#4385BE",
        "#CE5D97",
        "#3AA99F",
        "#E6E4D9",
      },
    },
  }
  config.color_scheme = "Flexoki Light"
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
