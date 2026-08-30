local wezterm = require("wezterm")
local mux = wezterm.mux

local module = {}

-- Fraction of the active screen the startup window covers.
local coverage = 0.7

function module.apply_to_config(_)
  -- Placement is an event, not a config key, so this module registers a
  -- handler instead of writing to config. gui-startup fires only for the
  -- window created at startup; windows opened later keep whatever geometry
  -- the window manager gives them.
  wezterm.on("gui-startup", function(cmd)
    local _, _, window = mux.spawn_window(cmd or {})

    -- wezterm.gui.screens() reports pixels and carries no scale field, so the
    -- arithmetic below is in device pixels. macOS HiDPI scaling is the case
    -- most likely to make it wrong, and macOS is where this configuration
    -- runs WezTerm today, so confirm the result there.
    local screen = wezterm.gui.screens().active
    local width = math.floor(screen.width * coverage)
    local height = math.floor(screen.height * coverage)

    local gui = window:gui_window()
    gui:set_inner_size(width, height)

    -- set_inner_size sets the content size. Decorations add to the outer
    -- window, so the outer size exceeds the fraction above and centring
    -- computed from the inner size sits slightly high of the true centre.
    gui:set_position(
      screen.x + math.floor((screen.width - width) / 2),
      screen.y + math.floor((screen.height - height) / 2)
    )
  end)
end

return module
