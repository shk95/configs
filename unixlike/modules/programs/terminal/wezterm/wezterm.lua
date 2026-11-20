local wezterm = require("wezterm")
local config = wezterm.config_builder()

-- Prefer a widely available terminfo entry for remote systems.
config.term = "xterm-256color"
-- The package supplier manages updates.
config.check_for_updates = false

return config
