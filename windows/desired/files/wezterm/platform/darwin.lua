local module = {}

function module.apply_to_config(config)
  -- The login shell and fonts are owned by the consuming nix-darwin setup.
  config.font_size = 14.0
  config.native_macos_fullscreen_mode = true
  config.window_decorations = "INTEGRATED_BUTTONS|RESIZE"
end

return module
