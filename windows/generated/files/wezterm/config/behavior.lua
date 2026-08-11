local module = {}

function module.apply_to_config(config)
  -- Keep the broadly available terminfo entry for SSH, containers and rescue hosts.
  config.term = "xterm-256color"

  config.automatically_reload_config = true
  config.check_for_updates = false
  config.exit_behavior = "CloseOnCleanExit"
  config.scrollback_lines = 20000

  config.audible_bell = "Disabled"
  config.default_cursor_style = "SteadyBar"
  config.detect_password_input = true
  config.warn_about_missing_glyphs = true

  config.adjust_window_size_when_changing_font_size = false
  config.window_close_confirmation = "AlwaysPrompt"
end

return module
