local wezterm = require("wezterm")

local module = {}

local function read_manifest()
  local path = wezterm.config_dir .. "/fonts.json"
  local file = io.open(path, "r")

  if not file then
    wezterm.log_warn("font manifest was not found: " .. path)
    return nil
  end

  local contents = file:read("*a")
  file:close()

  local ok, manifest = pcall(wezterm.json_parse, contents)
  if not ok then
    wezterm.log_error("unable to parse font manifest: " .. tostring(manifest))
    return nil
  end

  return manifest
end

function module.apply_to_config(config)
  local manifest = read_manifest()
  if not manifest or not manifest.families then
    return
  end

  config.font = wezterm.font_with_fallback(manifest.families)
end

return module
