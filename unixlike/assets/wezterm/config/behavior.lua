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

  -- macOS stores filenames in decomposed (NFD) form, so `ls` and similar
  -- output conjoining jamo (U+1100 block) for Hangul filenames instead of
  -- precomposed syllables (U+AC00 block); WezTerm does not compose them on
  -- its own, so composed-looking glyphs render as separated jamo. Normalizing
  -- output to NFC fixes that. This is off by default, and upstream documents
  -- it as an imperfect option: depending on the application running inside
  -- the terminal, enabling it may introduce discrepancies in the
  -- understanding of text positioning, trading some display glitches for
  -- others rather than only removing them.
  config.normalize_output_to_unicode_nfc = true

  config.adjust_window_size_when_changing_font_size = false
  config.window_close_confirmation = "AlwaysPrompt"
end

return module
