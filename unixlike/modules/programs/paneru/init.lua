-- ============================================================
-- Paneru Lua Configuration Reference
-- Target: Paneru v0.5.2+ / macOS 26+
--
-- Purpose:
-- - Keep the active configuration near the top of each section.
-- - Document each setting by its meaning, not by the value currently selected.
-- - Keep optional/reference settings commented out so this file can also serve
--   as a catalog of supported configuration options.
--
-- IMPORTANT:
-- - Paneru reads TOML or Lua configuration, never both at the same time.
-- - If an init.lua is present in a recognized Lua configuration location, it
--   takes over and any paneru.toml is ignored.
-- - Configuration is normally reloaded when this file is saved.
-- - Confirm options against the documentation for the exact installed version:
--   https://github.com/karinushka/paneru/blob/main/CONFIGURATION.md
-- - Commented examples are inactive. Uncomment them only when you want to test
--   that behavior. Add fields to the existing Lua table; duplicate keys
--   overwrite earlier ones.
-- ============================================================


paneru.setup {
  -- ============================================================
  -- 1. Virtual Workspace Initialization
  -- ============================================================

  -- Number of virtual workspace rows created for each native macOS Space.
  -- Virtual workspaces are Paneru-managed rows inside one native macOS Space;
  -- they are not the same thing as macOS Mission Control Spaces.
  -- The current upstream configuration guide may not document this key in every
  -- release. The pinned version supports this optional root-level setting.
  -- default_workspaces = 1,


  -- ============================================================
  -- 2. Global Options
  -- ============================================================

  options = {

    -- ------------------------------------------------------------
    -- Focus and Pointer Behavior
    -- ------------------------------------------------------------

    -- When enabled, the window under the pointer receives focus automatically.
    focus_follows_mouse = false,

    -- When enabled, keyboard-driven focus changes move the pointer to the center
    -- of the newly focused window.
    mouse_follows_focus = true,

    -- When enabled, the focused window is automatically centered in the viewport
    -- whenever focus changes.
    -- auto_center = true,

    -- Optional: warp the pointer between displays when it reaches the left or
    -- right edge. The sign selects the virtual vertical direction of the target
    -- display arrangement. Valid documented values are -1 and 1.
    -- horizontal_mouse_warp = 1,

    -- Optional: vertical pixel offset applied to the landing point of
    -- horizontal_mouse_warp. Use this to compensate for a physical monitor
    -- arrangement that differs from the arrangement in macOS Displays settings.
    -- horizontal_mouse_warp_offset = 0,


    -- ------------------------------------------------------------
    -- Animation
    -- ------------------------------------------------------------

    -- Controls the speed of window movement animations. The documented comfortable
    -- range is approximately 8–20. Unset the option or use a sufficiently high
    -- value to effectively disable animations. Lower values can feel less abrupt
    -- on some systems, but tune by testing the actual interaction.
    animation_speed = 13.0,


    -- ------------------------------------------------------------
    -- Window Width and Stack Height Presets
    -- ------------------------------------------------------------

    -- Screen-width ratios used by the window resize command and menu-bar width
    -- picker. Values above 1.0 create horizontally scrollable oversized windows.
    preset_column_widths = {
      0.25,
      0.33,
      0.50,
      0.66,
      0.75,
      1.00,
    },

    -- Viewport-height ratios used by vertical resize commands for windows inside
    -- a stack. Paneru keeps each stacked window at least 200 px tall and clamps
    -- ratios that would leave a neighboring window too little space.
    preset_stack_heights = {
      0.25,
      0.33,
      0.50,
      0.66,
      0.75,
    },

    -- When enabled, cycling past the final resize preset wraps around to the first
    -- preset. When disabled, resizing stops at the largest or smallest preset.
    window_resize_cycle = true,

    -- Controls how much of a window may remain hidden before Paneru forces it into
    -- view during a focus change. 0.0 is eager visibility; 1.0 is lazy visibility.
    window_hidden_ratio = 0.0,

    -- Modifier keys held while moving the pointer near a window edge resize that
    -- window. The edge nearest the pointer determines which side is adjusted.
    -- Example modifier strings include "cmd + shift" and "ctrl + alt + shift".
    mouse_resize_modifier = "ctrl + alt + shift",

    -- Optional: manually override Paneru's detected macOS menu-bar height.
    -- Use only if automatic detection produces incorrect screen geometry.
    -- menubar_height = 24,


    -- ------------------------------------------------------------
    -- Off-screen Window Visibility
    -- ------------------------------------------------------------

    -- Vertical fraction of an off-screen window kept visible. The allowed range
    -- is 0.1–1.0; a visible sliver helps prevent macOS from relocating windows.
    sliver_height = 1,

    -- Width in pixels of the visible horizontal portion retained for off-screen
    -- windows. This helps keep neighboring windows discoverable and prevents
    -- macOS from unexpectedly repositioning them.
    sliver_width = 5,


    -- ------------------------------------------------------------
    -- Virtual Workspace Behavior (Experimental)
    -- ------------------------------------------------------------

    -- When enabled, Paneru creates a new virtual workspace row automatically when
    -- moving south using the relevant keyboard command or gesture.
    create_virtual_workspace_automatically = true,

    -- When enabled, empty virtual workspace rows are removed. When disabled, empty
    -- rows may remain available for later use. Check the exact type/behavior in
    -- the documentation for the installed release.
    reap_empty_workspaces = true,

    -- When enabled, virtual workspace row changes are animated. Disable this if
    -- the animation adds latency or feels slower than direct row switching.
    virtual_workspace_animations = false,

    -- When enabled, a window moved to another virtual workspace is inserted at the
    -- column corresponding to its current on-screen position. Otherwise, it is
    -- appended to the destination strip.
    insert_windows_mid_strip = true,


    -- ------------------------------------------------------------
    -- Native macOS Tabs
    -- ------------------------------------------------------------

    -- When enabled, Paneru avoids automatically merging same-app windows that
    -- share a frame into a native macOS tab group. Enable this if unrelated
    -- windows are being grouped together unexpectedly.
    disable_native_tabs = true,


  },
  -- ============================================================
  -- 3. Screen Padding
  -- ============================================================

  padding = {

    -- Empty margin between the top edge of the display and the managed layout.
    top = 5,

    -- Empty margin between the bottom edge of the display and the managed layout.
    bottom = 5,

    -- Empty margin between the left edge of the display and the managed layout.
    left = 5,

    -- Empty margin between the right edge of the display and the managed layout.
    right = 5,


  },
  -- ============================================================
  -- 4. Scrolling and Trackpad Gestures
  -- ============================================================

  swipe = {

    -- Multiplier for swipe distance. Higher values move the window strip farther
    -- for the same physical gesture. The documented range is 0.1–2.0.
    sensitivity = 0.4,

    -- Rate at which inertial movement slows after a swipe. Higher values stop
    -- momentum sooner; the documented range is 1.0–10.0.
    deceleration = 3.0,

    -- Controls whether the window strip may move beyond its first/last window.
    -- true allows movement into empty desktop space; false constrains the strip
    -- to its outermost windows and snaps the outermost window to the display edge
    -- during relevant focus navigation.
    continuous = false,


    -- ------------------------------------------------------------
    -- Mouse Wheel / Modified Scrolling
    -- ------------------------------------------------------------

    scroll = {

      -- Modifier required while scrolling to move the horizontal window strip.
      -- Supported modifier names include alt, cmd, ctrl, shift and left/right forms;
      -- multiple modifiers can be combined, for example "ralt + cmd".
      modifier = "alt",

      -- Additional modifier used together with `modifier` to switch virtual
      -- workspace rows vertically instead of scrolling the strip horizontally.
      -- For example, modifier = "alt" and vertical_modifier = "shift" means:
      -- Option + scroll = horizontal strip; Option + Shift + scroll = workspace row.
      vertical_modifier = "shift",

      -- Optional: use discrete one-window-at-a-time steps rather than continuous
      -- scroll distance, if supported by the installed release.
      window_step = true,


    },
    -- ------------------------------------------------------------
    -- Native Trackpad Gestures
    -- ------------------------------------------------------------

    -- When omitted or set below 3, Paneru does not intercept native macOS gestures.
    -- Set to 3 or 4 to enable Paneru swipe handling. A vertical swipe can change
    -- virtual workspace rows when `vertical = true`.
    -- gesture = {
      -- fingers_count = 4,

      -- Defines whether gesture direction follows the natural direction of the
      -- fingers or is reversed. Valid documented values are "Natural" and "Reversed".
      -- direction = "Natural",

      -- Enables vertical gesture handling for virtual workspace navigation.
      -- Disable this to leave vertical gestures to macOS.
      -- vertical = true,

      -- Note: the documented gesture table does not expose a modifier-key condition
      -- for trackpad swipes. Modifier combinations are available for scroll-wheel
      -- navigation under swipe.scroll, not for gating native swipe gestures.


    -- },
  },
  -- ============================================================
  -- 5. Decorations
  -- ============================================================

  decorations = {

    -- Controls the virtual-workspace indicator in the menu bar. Disabling it may
    -- require restarting Paneru before the change becomes visible.
    workspace_menu_status = true,

    -- Controls the brief popup shown when switching virtual workspace rows.
    workspace_popup_status = true,


    -- ------------------------------------------------------------
    -- Menu Bar Appearance
    -- ------------------------------------------------------------

    menu = {

      -- Order of the menu-bar components. "default" shows the descriptor first;
      -- "flipped" places the workspace indicator first.
      orientation = "default",

      -- Optional: hex colors used to draw the menu-bar display as a left-to-right
      -- linear gradient. Use one color for a solid appearance.
      colors = {"#89b4fa", "#cba6f7"},

      -- Optional: angle in degrees for the menu-bar color gradient.
      -- angle = 90.0,


      -- ------------------------------------------------------------
      -- Menu Bar Descriptor
      -- ------------------------------------------------------------

      descriptor = {

        -- Visual form of the descriptor: "symbol", "text", "both", or "hidden".
        style = "hidden",

        -- Text displayed when descriptor style is "text" or "both".
        -- text = "VW",

        -- SF Symbol displayed when descriptor style is "symbol" or "both".
        -- symbol = "fish.fill",


      },
      -- ------------------------------------------------------------
      -- Menu Bar Workspace Indicator
      -- ------------------------------------------------------------

      indicator = {

        -- Indicator layout: "multi" shows all workspaces, "mono" shows only the
        -- current workspace, and "paged" shows the current index and total count.
        style = "paged",

        -- Representation of workspace indicators: "default" uses numbers, "roman"
        -- uses Roman numerals, "unicode" uses active/inactive characters, and "marked"
        -- marks the active workspace with its number. "unicode" and "marked" require
        -- multiple workspaces to be displayed and fall back when used with mono/paged.
        format = "default",

        -- Font size, in points, used for the workspace indicator. Documented range:
        -- 2.0–24.0.
        font_size = 13.0,

        -- Character used for the active workspace when format="unicode".
        -- active_character = "☉",

        -- Character used for inactive workspaces when format="unicode".
        -- inactive_character = "○",


      },
    },
    -- ------------------------------------------------------------
    -- Active Window Border (Experimental)
    -- ------------------------------------------------------------

    -- Draws a border around the focused window. This relies on undocumented
    -- macOS window-server behavior and may have visual glitches or layer-order
    -- issues. SIP does not need to be disabled; without disabling it, Paneru has
    -- more limited control over window layering.

    -- active = {
      -- border = {
        -- enabled = true,
        -- color = "#B98282",
        -- opacity = 0.80,
        -- width = 3.0,
        -- radius = "auto", -- Number of pixels or "auto" to match the system corner radius.


      -- },
    -- },
    -- ------------------------------------------------------------
    -- Inactive Window Dimming
    -- ------------------------------------------------------------

    -- Native macOS dimming mode: set opacity (and optionally opacity_night), and
    -- do not set color in this mode. Values range from -1.0 (black) to 1.0 (white).
    -- This mode can affect native window appearance without drawing a separate
    -- overlay. Test carefully with the apps and macOS appearance you use.

    -- inactive = {
      -- dim = {
        -- opacity = -0.1,
        -- opacity_night = -0.15,

      -- },
    -- },

    -- Experimental overlay dimming mode: set BOTH opacity and color. This draws a
    -- translucent overlay over inactive windows and can cause issues with
    -- picture-in-picture windows or window layering. Here opacity ranges from
    -- 0.0 (transparent) to 1.0 (opaque).
    -- Choose one dimming mode; add only one inactive table to decorations.

    -- inactive = {
      -- dim = {
        -- opacity = 0.25,
        -- color = "#000000",

      -- },
    -- },
  },
  -- ============================================================
  -- 6. Keybindings
  -- ============================================================

  bindings = {

    -- Keybindings use the form "modifiers - key"; multiple modifiers are joined
    -- with "+". Supported modifier families include alt, ctrl, cmd, shift, fn and
    -- left/right-specific variants. Each setup binding maps a command string to
    -- one chord. For alternative chords (TOML also accepts an array), call
    -- paneru.bind(chord, command) once per chord. Avoid assigning the same
    -- combination to multiple actions.


    -- ------------------------------------------------------------
    -- 6.1 Focus Navigation
    -- ------------------------------------------------------------

    -- Move focus to the neighboring window in the indicated direction.
    ["window focus west"] = "ctrl + alt - h",
    -- ["window focus south"] = "ctrl + alt - j",
    -- ["window focus north"] = "ctrl + alt - k",
    ["window focus east"] = "ctrl + alt - l",

    -- Optional: jump directly to the first or last window in the horizontal strip.
    -- ["window focus first"] = "ctrl + alt - home",
    -- ["window focus last"] = "ctrl + alt - end",

    -- Optional: return focus to the previously focused managed window or floating
    -- window on the current workspace.
    ["window focus managed"] = "ctrl + alt - tab",
    ["window focus unmanaged"] = "ctrl + alt + shift - tab",


    -- ------------------------------------------------------------
    -- 6.2 Window Movement and Reordering
    -- ------------------------------------------------------------

    -- Swap the focused window with its left or right neighbor in the strip.
    ["window swap west"] = "ctrl + alt + shift - h",
    ["window swap east"] = "ctrl + alt + shift - l",

    -- Optional: swap with the window above/below in a stack. If there is no
    -- matching stacked neighbor, the command can move the window to another display.
    ["window swap north"] = "ctrl + alt + shift - u",
    ["window swap south"] = "ctrl + alt + shift - d",

    -- Optional: move the focused window to the first or last position in the strip.
    -- ["window swap first"] = "ctrl + alt + shift - home",
    -- ["window swap last"] = "ctrl + alt + shift - end",


    -- ------------------------------------------------------------
    -- 6.3 Column Width
    -- ------------------------------------------------------------

    -- Cycle the focused window through configured width presets in the larger
    -- direction; window_grow is an alias for window_resize.
    -- ["window grow"] = "ctrl + alt - ]",

    -- Cycle the focused window through configured width presets in the smaller
    -- direction.
    ["window shrink"] = "ctrl + alt - [",

    -- Optional explicit action name for cycling width presets.
    ["window resize"] = "ctrl + alt - ]",


    -- ------------------------------------------------------------
    -- 6.4 Vertical Stack Height
    -- ------------------------------------------------------------

    -- Increase the height preset of a window inside a stack. This is a no-op for
    -- windows that are not part of a stack.
    -- ["window vertical grow"] = "ctrl + alt - rightbracket",

    -- Decrease the height preset of a window inside a stack.
    ["window vertical shrink"] = "ctrl + alt - ,",

    -- Optional explicit action name for the upward height-preset cycle.
    ["window vertical resize"] = "ctrl + alt - .",


    -- ------------------------------------------------------------
    -- 6.5 Window Position and Layout
    -- ------------------------------------------------------------

    -- Center the focused window in the viewport.
    ["window center"] = "ctrl + alt - c",

    -- Toggle the focused window between normal width and full-width mode.
    ["window fullwidth"] = "ctrl + alt - ;",

    -- Bring an overflowing window into the visible viewport.
    ["window snap"] = "ctrl + alt - v",

    -- Set all columns in the strip to the same width as the focused window.
    ["window balance"] = "ctrl + alt - b",

    -- Set all windows in the current stack to equal heights.
    ["window equalize"] = "ctrl + alt + shift - b",


    -- ------------------------------------------------------------
    -- 6.6 Stack and Tab Management
    -- ------------------------------------------------------------

    -- Add the focused window to the column immediately to its left as a stack.
    ["window stack"] = "ctrl + alt - s",

    -- Remove the focused window from its stack and place it in its own column.
    ["window unstack"] = "ctrl + alt + shift - s",

    -- Toggle the display of a native tab group for windows that share a tab group.
    ["window tabbeddisplay"] = "ctrl + alt - t",


    -- ------------------------------------------------------------
    -- 6.7 Floating and Tiling
    -- ------------------------------------------------------------

    -- Toggle the focused window between Paneru-managed tiling and floating state.
    ["window manage"] = "ctrl + alt - space",

    -- Optional: bring the floating-window layer to the front for the current
    -- workspace, or toggle the floating layer's position relative to tiled windows.
    ["window raise floating"] = "ctrl + alt - g",
    ["window togglefloatlayer"] = "ctrl + alt + shift - g",


    -- ------------------------------------------------------------
    -- 6.8 Virtual Workspace Navigation (Experimental)
    -- ------------------------------------------------------------

    -- Switch to the previous/next virtual workspace row unconditionally.
    ["window virtual north"] = "ctrl + alt - k",
    ["window virtual south"] = "ctrl + alt - j",

    -- Optional: switch to the first or last virtual workspace row.
    -- ["window virtual first"] = "ctrl + alt - pageup",
    -- ["window virtual last"] = "ctrl + alt - pagedown",

    -- Optional: move focus vertically within a stack first; switch workspace rows
    -- only when there is no stacked neighbor in that direction.
    -- ["window virtualfocus north"] = "ctrl + alt + shift - u",
    -- ["window virtualfocus south"] = "ctrl + alt + shift - d",


    -- ------------------------------------------------------------
    -- 6.9 Move a Window Between Virtual Workspaces
    -- ------------------------------------------------------------

    -- Move the focused window to the adjacent virtual workspace and follow it.
    ["window virtualmove north"] = "ctrl + alt + shift - k",
    ["window virtualmove south"] = "ctrl + alt + shift - j",

    -- Optional: send a window to another row while leaving the current row active.
    ["window virtualsend north"] = "ctrl + alt + cmd - k",
    ["window virtualsend south"] = "ctrl + alt + cmd - j",

    -- Optional: move a window to the first or last virtual workspace and follow it.
    -- ["window virtualmove first"] = "ctrl + alt + shift - pageup",
    -- ["window virtualmove last"] = "ctrl + alt + shift - pagedown",

    -- Optional: send a window to the first or last virtual workspace without
    -- switching away from the current row.
    -- ["window virtualsend first"] = "ctrl + alt + cmd - pageup",
    -- ["window virtualsend last"] = "ctrl + alt + cmd - pagedown",


    -- ------------------------------------------------------------
    -- 6.10 Direct Virtual Workspace Selection
    -- ------------------------------------------------------------

    -- Jump directly to a numbered virtual workspace row.
    -- ["window virtualnum 1"] = "ctrl + alt - 1",
    -- ["window virtualnum 2"] = "ctrl + alt - 2",
    -- ["window virtualnum 3"] = "ctrl + alt - 3",

    -- Optional: send the focused window to a numbered row and follow it.
    -- ["window virtualmovenum 1"] = "ctrl + alt + shift - 1",
    -- ["window virtualmovenum 2"] = "ctrl + alt + shift - 2",
    -- ["window virtualmovenum 3"] = "ctrl + alt + shift - 3",

    -- Optional: send the focused window to a numbered row but remain on the
    -- current row.
    -- ["window virtualsendnum 1"] = "ctrl + alt + cmd - 1",
    -- ["window virtualsendnum 2"] = "ctrl + alt + cmd - 2",
    -- ["window virtualsendnum 3"] = "ctrl + alt + cmd - 3",


    -- ------------------------------------------------------------
    -- 6.11 Multi-monitor Navigation
    -- ------------------------------------------------------------

    -- Move the focused window to the next display and follow the window.
    ["window nextdisplay"] = "ctrl + alt - m",

    -- Optional: move the focused window to the next display but remain on the
    -- current display/workspace.
    ["window nextdisplaysend"] = "ctrl + alt + shift - m",

    -- Optional: move the pointer to the next display without moving a window.
    ["mouse nextdisplay"] = "ctrl + alt - n",


    -- ------------------------------------------------------------
    -- 6.12 Utilities
    -- ------------------------------------------------------------

    -- Copy a template rule for the focused window to the clipboard.
    ["window copyrule"] = "ctrl + alt - p",

    -- Restart Paneru's service.
    -- ["restart"] = "ctrl + alt + shift - r",

    -- Exit Paneru.
    -- ["quit"] = "ctrl + alt + shift - q",


  },
  -- ============================================================
  -- 7. Session Restoration
  -- ============================================================

  restore = {

    -- Enables restoring the previous managed-window layout when Paneru starts.
    enabled = true,

    -- Duration, in milliseconds, during which Paneru waits for application windows
    -- to appear and attempts to match them to saved session entries.
    startup_grace_ms = 2000,

    -- Policy for saved windows that do not exist at startup. The currently
    -- documented supported value is "ignore"; missing entries are dropped and the
    -- restored layout is compacted.
    missing_windows = "ignore",


  },
  -- ============================================================
  -- 8. Application Window Rules
  -- ============================================================

  -- Window rules match application windows by title regular expression and,
  -- optionally, bundle ID. `title` is required. Rules can set initial placement,
  -- size, padding, focus behavior, floating/managed state, and key passthrough.
  -- Saved-session state takes precedence over some static rule values for matched
  -- windows during the startup restore phase.

  windows = {
    -- dialogs = {
      -- title = ".*",
      -- role = "AXWindow",
      -- subrole = "AXDialog",
      -- floating = true,

    -- },
    -- floating_window = {
      -- title = ".*",
      -- role = "AXWindow",
      -- subrole = "AXFloatingWindow",
      -- floating = true,

    -- },
    all = {
      title = ".*",
      horizontal_padding = 3,
      -- vertical_padding = 5,

    },
    -- ------------------------------------------------------------
    -- WezTerm
    -- ------------------------------------------------------------

    wezterm = {

      -- Regular expression matched against the window title. ".*" matches all titles.
      title = ".*",

      -- macOS bundle identifier used to restrict this rule to WezTerm.
      bundle_id = "com.github.wez.wezterm",

      -- Initial width ratio. Values above 1.0 make the window wider than the viewport.
      width = 0.5,

      -- Horizontal gap around this window, in pixels.
      -- horizontal_padding = 5,

      -- Vertical gap around this window, in pixels.
      -- vertical_padding = 5,

      -- Optional: place the window at a specific position in the strip when created.
      index = 0,

      -- Optional: keep the new window from taking focus when it appears.
      -- dont_focus = true,

      -- Optional: force a matching window to float rather than be tiled.
      -- floating = true,

      -- Optional: force Paneru to manage windows that macOS reports as unobservable
      -- or that use non-standard accessibility roles/subroles.
      -- manage = true,

      -- Optional: grid placement for floating windows, in "cols:rows:x:y:w:h" form.
      -- Example: "2:2:0:0:1:1"
      -- grid = "2:2:0:0:1:1",

      -- Optional: key combinations that Paneru should pass directly to the app
      -- instead of handling as Paneru shortcuts.
      -- bindings_passthrough = {"ctrl-h", "ctrl-l"},


    },
    -- ------------------------------------------------------------
    -- Alacritty
    -- ------------------------------------------------------------

    -- alacritty = {

      -- Regular expression matched against the window title.
      -- title = ".*",

      -- macOS bundle identifier used to restrict this rule to Alacritty.
      -- bundle_id = "org.alacritty",

      -- Initial width ratio relative to the display width.
      -- width = 1.0,

      -- Horizontal and vertical spacing around the window, in pixels.
      -- horizontal_padding = 5,
      -- vertical_padding = 5,

      -- Optional rule fields are documented in the WezTerm section above:
      -- index, dont_focus, floating, manage, grid, bindings_passthrough.


    -- },
    -- ------------------------------------------------------------
    -- Safari
    -- ------------------------------------------------------------

    safari = {

      -- Regular expression matched against the window title.
      title = ".*",

      -- macOS bundle identifier used to restrict this rule to Safari.
      bundle_id = "com.apple.Safari",

      -- Special width value that uses the remaining width beside the focused window.
      width = "complement_focused",

      -- Horizontal and vertical spacing around the window, in pixels.
      -- horizontal_padding = 5,
      -- vertical_padding = 5,

      -- Optional rule fields are documented in the WezTerm section above:
      -- index, dont_focus, floating, manage, grid, bindings_passthrough.
      index = 1,

      -- manage = true,


    },
    -- ------------------------------------------------------------
    -- Terminal
    -- ------------------------------------------------------------

    terminal = {

      title = ".*",
      bundle_id = "com.apple.Terminal",
      floating = true,
      manage = true,
      width = 0.5,


    },
    -- ------------------------------------------------------------
    -- Stickies
    -- ------------------------------------------------------------

    stickies = {
      bundle_id = "com.apple.Stickies",
      title = ".*",
      floating = true,
      manage = true,
      -- width = 0.5,


    },
    -- ------------------------------------------------------------
    -- Finder
    -- ------------------------------------------------------------

    finder = {
      bundle_id = "com.apple.finder",
      title = "^Copy$",
      -- app: Finder  role: AXWindow  subrole: AXStandardWindow
      floating = true,
      -- manage = true,
      -- width = 0.5,


    },
    -- ------------------------------------------------------------
    -- Calculator
    -- ------------------------------------------------------------

    calculator = {
      title = ".*",
      bundle_id = "com.apple.calculator",
      floating = true,


    },
    -- ------------------------------------------------------------
    -- Example: floating utility window
    -- ------------------------------------------------------------

    -- Add a separate uniquely named table in windows for each additional rule. Use a title
    -- regex and bundle ID that match the intended app/window. `floating = true`
    -- keeps the matched window outside the managed tiled strip.
    --
    -- example_utility = {
      -- title = "Preferences|Settings",
      -- bundle_id = "com.example.application",
      -- floating = true,
      -- dont_focus = true,
      -- width = 0.5,
      -- horizontal_padding = 8,
      -- vertical_padding = 8,
      -- bindings_passthrough = {"ctrl-h", "ctrl-l"},
    -- },
  },
}
