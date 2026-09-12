local wezterm = require("wezterm")
local mux = wezterm.mux

local module = {}

-- Fraction of the active screen the startup window covers.
local coverage = 0.7

-- Seconds to wait before re-asserting the position. The resize is queued and
-- Lua gets no resize-complete event, so this is a pragmatic completion signal
-- rather than a synchronisation.
local settle = 0.25

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
    local _, _, window = mux.spawn_window(cmd or {})

    -- wezterm.gui.screens() raises off the GUI thread and window:gui_window()
    -- raises when no GUI window is associated yet; neither returns nil. An
    -- error escaping this handler is logged and shown as a persistent toast,
    -- so guard the geometry work and log instead. The window is spawned above,
    -- outside the guard, and therefore appears either way.
    local placed, err = pcall(function()
      -- Every number here is a device pixel: screens() reports device pixels,
      -- set_inner_size takes device pixels, and set_position passes its
      -- arguments through to set_window_position unscaled. No conversion is
      -- needed. screen.scale and screen.effective_dpi are available if that
      -- ever changes.
      local screen = wezterm.gui.screens().active
      local width = round(screen.width * coverage)
      local height = round(screen.height * coverage)
      local x = screen.x + round((screen.width - width) / 2)
      local y = screen.y + round((screen.height - height) / 2)

      local gui = window:gui_window()

      -- set_inner_size sets the content size. Decorations add to the outer
      -- window, so the outer size exceeds the fraction above and a window
      -- centred on its content sits slightly high of the true centre.
      gui:set_inner_size(width, height)
      gui:set_position(x, y)

      -- set_inner_size is queued through the TermWindow notification path
      -- while set_position reaches the window directly, so the resize always
      -- lands after the position. Re-assert the position once the resize has
      -- had time to settle.
      wezterm.time.call_after(settle, function()
        local again, reason = pcall(function()
          gui:set_position(x, y)
        end)

        if not again then
          wezterm.log_error("startup geometry re-assert: " .. tostring(reason))
        end
      end)
    end)

    if not placed then
      wezterm.log_error("startup geometry: " .. tostring(err))
    end
  end)
end

-- Two limitations remain open and are for the first macOS run to measure;
-- neither is solved here.
--
-- Stacked or mixed-DPI layouts may mislocate the window. The rect screens()
-- reports is bottom-left-origin backing pixels, while set_position is
-- top-left-origin, and the two are only reconciled when the screens share a
-- scale and a bottom edge. Nothing in this repository can observe it.
--
-- If the window still sits high by roughly the height delta after the
-- re-assert above, AppKit's setContentSize: anchors the bottom-left and
-- WezTerm adds no frame-origin compensation. The size would then have to be
-- established when the window is created rather than by resizing a placed
-- window.

return module
