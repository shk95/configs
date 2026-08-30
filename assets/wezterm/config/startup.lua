local wezterm = require("wezterm")
local mux = wezterm.mux

local module = {}

-- Fraction of the active screen the startup window covers.
local coverage = 0.7

-- 1440 * 0.7 is 1007.999... in binary floating point, so truncating loses a
-- pixel. Round to the nearest instead.
local function round(value)
  return math.floor(value + 0.5)
end

function module.apply_to_config(_)
  -- Placement is an event, not a config key, so this module registers a
  -- handler instead of writing to config. gui-startup fires only for the
  -- window created at startup; windows opened later keep whatever geometry
  -- the window manager gives them.
  wezterm.on("gui-startup", function(cmd)
    local spawn = cmd or {}

    -- wezterm.gui.screens() raises off the GUI thread and window:gui_window()
    -- raises when no GUI window is associated yet; neither returns nil. An
    -- error escaping this handler is logged and shown as a persistent toast,
    -- so guard both and log instead, and spawn the window either way.
    --
    -- screens() reports device pixels and set_inner_size takes device pixels,
    -- so no scale conversion is needed here. screen.scale and
    -- screen.effective_dpi are available if that ever changes.
    local measured, geometry = pcall(function()
      local screen = wezterm.gui.screens().active
      local width = round(screen.width * coverage)
      local height = round(screen.height * coverage)

      return {
        width = width,
        height = height,
        x = round((screen.width - width) / 2),
        y = round((screen.height - height) / 2),
      }
    end)

    if measured then
      -- Position at spawn rather than afterwards. set_inner_size is posted
      -- through the TermWindow queue while set_position reaches the window
      -- directly, so their order is not guaranteed, and set_position converts
      -- the requested top-left using the window's current content height.
      -- Spawning with the position also keeps x and y relative to the active
      -- screen: the rects screens() reports and the coordinates set_position
      -- takes are not the same space on a stacked or mixed-DPI macOS layout.
      spawn.position = { x = geometry.x, y = geometry.y, origin = "ActiveScreen" }
    else
      wezterm.log_error("startup geometry: " .. tostring(geometry))
    end

    local _, _, window = mux.spawn_window(spawn)

    if not measured then
      return
    end

    -- set_inner_size sets the content size. Decorations add to the outer
    -- window, so the outer size exceeds the fraction above and a window
    -- centred on its content sits slightly high of the true centre.
    local sized, err = pcall(function()
      window:gui_window():set_inner_size(geometry.width, geometry.height)
    end)

    if not sized then
      wezterm.log_error("startup geometry: " .. tostring(err))
    end
  end)
end

return module
