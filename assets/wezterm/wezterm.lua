local wezterm = require("wezterm")

local config = wezterm.config_builder()

local modules = {
  "config.behavior",
  "config.appearance",
  "config.fonts",
  "config.bindings",
}

for _, name in ipairs(modules) do
  require(name).apply_to_config(config)
end

local triple = wezterm.target_triple
local platform

if triple:find("windows") then
  platform = "platform.windows"
elseif triple:find("darwin") then
  platform = "platform.darwin"
else
  platform = "platform.linux"
end

require(platform).apply_to_config(config)

local local_ok, local_config = pcall(require, "local")
if local_ok and type(local_config) == "table" and local_config.apply_to_config then
  local_config.apply_to_config(config)
elseif not local_ok and not tostring(local_config):find("module 'local' not found", 1, true) then
  wezterm.log_error("unable to load local.lua: " .. tostring(local_config))
end

return config
