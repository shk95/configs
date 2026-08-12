local wezterm = require("wezterm")

local module = {}

function module.apply_to_config(config)
  -- Home Manager owns the font files. Its Darwin target preserves the Nix
  -- share/fonts hierarchy below ~/Library/Fonts/HomeManager, which CoreText
  -- does not discover recursively, so point WezTerm at the owned directory.
  config.font_dirs = {
    wezterm.home_dir .. "/Library/Fonts/HomeManager/truetype/NerdFonts/D2KodingLigature",
  }

  -- The login shell is owned by the consuming nix-darwin setup.
  config.font_size = 14.0
  config.native_macos_fullscreen_mode = true
  config.window_decorations = "INTEGRATED_BUTTONS|RESIZE"
end

return module
