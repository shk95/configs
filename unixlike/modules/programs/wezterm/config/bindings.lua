local wezterm = require("wezterm")
local act = wezterm.action

local module = {}

function module.apply_to_config(config)
  local primary = wezterm.target_triple:find("darwin") and "CMD" or "CTRL|SHIFT"

  config.leader = { key = "Space", mods = "CTRL|SHIFT", timeout_milliseconds = 1500 }

  config.keys = {
    { key = "p", mods = primary, action = act.ActivateCommandPalette },
    { key = "f", mods = primary, action = act.Search("CurrentSelectionOrEmptyString") },
    { key = "k", mods = primary, action = act.ClearScrollback("ScrollbackAndViewport") },
    { key = "Enter", mods = "ALT", action = act.ToggleFullScreen },

    { key = "\\", mods = "LEADER", action = act.SplitHorizontal({ domain = "CurrentPaneDomain" }) },
    { key = "-", mods = "LEADER", action = act.SplitVertical({ domain = "CurrentPaneDomain" }) },
    { key = "z", mods = "LEADER", action = act.TogglePaneZoomState },
    { key = "x", mods = "LEADER", action = act.CloseCurrentPane({ confirm = true }) },

    { key = "h", mods = "LEADER", action = act.ActivatePaneDirection("Left") },
    { key = "j", mods = "LEADER", action = act.ActivatePaneDirection("Down") },
    { key = "k", mods = "LEADER", action = act.ActivatePaneDirection("Up") },
    { key = "l", mods = "LEADER", action = act.ActivatePaneDirection("Right") },

    { key = "H", mods = "LEADER", action = act.AdjustPaneSize({ "Left", 5 }) },
    { key = "J", mods = "LEADER", action = act.AdjustPaneSize({ "Down", 5 }) },
    { key = "K", mods = "LEADER", action = act.AdjustPaneSize({ "Up", 5 }) },
    { key = "L", mods = "LEADER", action = act.AdjustPaneSize({ "Right", 5 }) },
  }
end

return module
