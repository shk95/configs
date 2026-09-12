local module = {}

function module.apply_to_config(config)
  config.default_prog = { "pwsh.exe", "-NoLogo" }
  config.font_size = 12.0
  config.window_decorations = "INTEGRATED_BUTTONS|RESIZE"

  config.launch_menu = {
    {
      label = "PowerShell 7",
      args = { "pwsh.exe", "-NoLogo" },
    },
    {
      label = "Windows PowerShell",
      args = { "powershell.exe", "-NoLogo" },
    },
  }
end

return module
