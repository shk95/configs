{config, ...}: let
  user = config.identity.darwin.user;
in {
  modules.darwin.system = _: {
    # Add ability to used TouchID for sudo authentication
    security.pam.services.sudo_local.touchIdAuth = true;

    # Set your time zone.
    time.timeZone = "Asia/Seoul";

    ###################################################################################
    #
    #  macOS's System configuration
    #
    #  All the configuration options are documented here:
    #    https://daiderd.com/nix-darwin/manual/index.html#sec-options
    #  Incomplete list of macOS `defaults` commands :
    #    https://github.com/yannbertrand/macos-defaults
    #
    ###################################################################################
    system = {
      stateVersion = 6;

      primaryUser = user;

      defaults = {
        # ".GlobalPreferences" = {
        #   "com.apple.sound.beep.sound" = "/System/Library/Sounds/Frog.aiff";
        # };

        NSGlobalDomain = {
          AppleICUForce24HourTime = true;
          # AppleInterfaceStyle = "Dark"; # dark mode
          AppleKeyboardUIMode = 2; # Mode 3 enables full keyboard control.
          AppleMeasurementUnits = "Centimeters";
          AppleMetricUnits = 1;
          ApplePressAndHoldEnabled = false; # enable press and hold
          AppleScrollerPagingBehavior = true; # Jump to the spot that’s clicked on the scroll bar. The default is false.
          AppleShowScrollBars = "WhenScrolling"; # When to show the scrollbars. Options are ‘WhenScrolling’, ‘Automatic’ and ‘Always’. Type: null or one of “WhenScrolling”, “Automatic”, “Always”
          AppleSpacesSwitchOnActivate = true; # automatically switch to a new space when switching to the application
          AppleWindowTabbingMode = "always"; # Sets the window tabbing when opening a new document: ‘manual’, ‘always’, or ‘fullscreen’. The default is ‘fullscreen’. Type: null or one of “manual”, “always”, “fullscreen”
          AppleShowAllExtensions = true;
          AppleTemperatureUnit = "Celsius";

          InitialKeyRepeat = 15; # normal minimum is 15 (225 ms), maximum is 120 (1800 ms). If you press and hold certain keyboard keys when in a text area, the key’s character begins to repeat.  This is very useful for vim users, they use `hjkl` to move cursor.  sets how long it takes before it starts repeating.
          KeyRepeat = 3; # sets how fast it repeats once it starts. normal minimum is 2 (30 ms), maximum is 120 (1800 ms)

          NSAutomaticCapitalizationEnabled = false; # disable auto capitalization
          NSAutomaticDashSubstitutionEnabled = false; # disable auto dash substitution
          NSAutomaticInlinePredictionEnabled = false;
          NSAutomaticPeriodSubstitutionEnabled = false; # disable auto period substitution
          NSAutomaticQuoteSubstitutionEnabled = false; # disable auto quote substitution
          NSAutomaticSpellingCorrectionEnabled = false; # disable auto spelling correction

          NSNavPanelExpandedStateForSaveMode = true; # expand save panel by default
          NSNavPanelExpandedStateForSaveMode2 = true;

          "com.apple.mouse.tapBehavior" = 1; # Configures the trackpad tap behavior. Mode 1 enables tap to click.
          "com.apple.sound.beep.feedback" = 1; # Make a feedback sound when the system volume changed. This setting accepts the integers 0 or 1. Defaults to 1.
          "com.apple.sound.beep.volume" = 0.7788008; # Apple menu > System Preferences > Sound Sets the beep/alert volume level from 0.000 (muted) to 1.000 (100% volume). 75% = 0.7788008 50% = 0.6065307 25% = 0.4723665 Type: null or floating point number
          "com.apple.trackpad.enableSecondaryClick" = true;
          "com.apple.trackpad.forceClick" = null; # Whether to enable trackpad force click. Type: null or boolean
          "com.apple.trackpad.scaling" = 2.5; # Configures the trackpad tracking speed (0 to 3). The default is “1”. Type: null or floating point number
        };

        # customize dock
        /*
        dock = {
          appswitcher-all-displays = true;
          # autohide = true;
          show-recents = false; # disable recent apps
          launchanim = true;
          mouse-over-hilite-stack = true;
          # orientation = "bottom"; # Type: null or one of “bottom”, “left”, “right”
          # tilesize = 36; # The default is 64.
          mineffect = "suck"; # Set the minImize/maximize window effect. The default is genie.  Type: null or one of “genie”, “suck”, “scale”
          autohide-delay = 0.0;
          expose-group-apps = true;
          # largesize = 60;
          # magnification = true;
          minimize-to-application = false;
          mru-spaces = false;
          scroll-to-open = true; # Scroll up on a Dock icon to show all Space’s opened windows for an app, or open stack. The default is false.
          show-process-indicators = true;
          showAppExposeGestureEnabled = true; # Whether to enable trackpad gestures (three- or four-finger vertical swipe) to show App Exposé. The default is false. This feature interacts with system.defaults.trackpad.TrackpadFourFingerVertSwipeGesture and system.defaults.trackpad.TrackpadThreeFingerVertSwipeGesture to determine which gesture triggers App Exposé.
          showDesktopGestureEnabled = true; # Whether to enable four-finger spread gesture to show the Desktop. The default is false.
          showLaunchpadGestureEnabled = true; # Whether to enable four-finger pinch gesture to show the Launchpad. The default is false.
          showMissionControlGestureEnabled = true; # Whether to enable trackpad gestures (three- or four-finger vertical swipe) to show Mission Control. The default is false. This feature interacts with system.defaults.trackpad.TrackpadFourFingerVertSwipeGesture and system.defaults.trackpad.TrackpadThreeFingerVertSwipeGesture to determine which gesture triggers Mission Control.
          showhidden = true; # Whether to make icons of hidden applications tranclucent. The default is false.

          # Persistent applications, spacers, files, and folders in the dock.
          persistent-apps = [
            "/System/Volumes/Preboot/Cryptexes/App/System/Applications/Safari.app"
            "/Applications/Brave Browser.app"
            "/Applications/Zen.app"
            "/System/Applications/News.app"
            "/System/Applications/Maps.app"
            "/System/Applications/Books.app"
            "/System/Applications/Mail.app"
            "/System/Applications/Freeform.app"
            "/System/Applications/Notes.app"
            "/System/Applications/Stickies.app"
            "/Applications/Obsidian.app"
            "/Applications/KeePassXC.app"
            "/Applications/ChatGPT.app"
            "/Applications/Claude.app"
            "/Applications/Visual Studio Code.app"
            "/Applications/Ghostty.app"
            "${config.users.users.${user}.home}/Applications/Home Manager Apps/WezTerm.app"
            "/System/Applications/Utilities/Activity Monitor.app"
          ]; # Type: null or (list of (attribute-tagged union or (string or absolute path) convertible to it))

          # customize Hot Corners
          # 1: Disabled
          # 2: Mission Control
          # 3: Application Windows
          # 4: Desktop
          # 5: Start Screen Saver
          # 6: Disable Screen Saver
          # 7: Dashboard
          # 10: Put Display to Sleep
          # 11: Launchpad
          # 12: Notification Center
          # 13: Lock Screen
          # 14: Quick Note
          # wvous-tl-corner = 2;  # top-lef
          # wvous-tr-corner = 13;  # top-right
          wvous-bl-corner = 3; # bottom-left
          wvous-br-corner = 4; # bottom-right
        };
        */

        # customize finder
        finder = {
          _FXShowPosixPathInTitle = true; # show full path in finder title
          _FXSortFoldersFirst = true; # keep folders on top
          AppleShowAllExtensions = true; # show all file extensions
          FXEnableExtensionChangeWarning = false; # disable warning when changing file extension
          FXDefaultSearchScope = "SCcf"; # search the current folder(SCcf), use the previous search scope(SCsp), search this Mac(SCev)
          QuitMenuItem = true; # enable quit menu item
          ShowPathbar = true; # show path bar
          ShowStatusBar = true; # show status bar
          CreateDesktop = true;
          FXPreferredViewStyle = "Nlsv"; # Change the default finder view. “icnv” = Icon view, “Nlsv” = List view, “clmv” = Column View, “Flwv” = Gallery View The default is icnv.
          FXRemoveOldTrashItems = false;
          NewWindowTarget = "Home"; # Change the default folder shown in Finder windows. “Other” corresponds to the value of NewWindowTargetPath. The default is unset (“Recents”). Type: null or one of “Computer”, “OS volume”, “Home”, “Desktop”, “Documents”, “Recents”, “iCloud Drive”, “Other”
          _FXEnableColumnAutoSizing = true; # Resize columns to fit filenames. The default is false.

          # desktop
          _FXSortFoldersFirstOnDesktop = true; # keep folders on top
          ShowHardDrivesOnDesktop = true; # show hard disksju
          ShowMountedServersOnDesktop = true; # show connected servers
        };

        hitoolbox.AppleFnUsageType = "Show Emoji & Symbols"; # Chooses what happens when you press the Fn key on the keyboard. A restart is required for this setting to take effect.  The default is unset (“Show Emoji & Symbols”). Type: null or one of “Do Nothing”, “Change Input Source”, “Show Emoji & Symbols”, “Start Dictation”

        loginwindow = {
          GuestEnabled = false; # disable guest user
          SHOWFULLNAME = false; # show full name in login window
          PowerOffDisabledWhileLoggedIn = false; # If set to true, the Power Off menu item will be disabled when the user is logged in. Default is false.
          RestartDisabledWhileLoggedIn = false; # Disables the “Restart” option when users are logged in. Default is false.
          ShutDownDisabledWhileLoggedIn = false; # Disables the “Shutdown” option when users are logged in. Default is false.
        };

        menuExtraClock = {
          Show24Hour = true; # show 24 hour clock
          FlashDateSeparators = true; # When enabled, the clock indicator (which by default is the colon) will flash on and off each second. Default is null.
          IsAnalog = false;
          ShowDate = 1; # Show the full date. Default is null. 0 = When space allows 1 = Always 2 = Never
          ShowDayOfMonth = true;
          ShowDayOfWeek = true;
          ShowSeconds = true;
        };

        screencapture = {
          disable-shadow = true;
          location = "~/Desktop";
          type = "png";
        };

        screensaver = {
          askForPassword = true;
          askForPasswordDelay = 0;
        };

        spaces.spans-displays = false;

        # customize trackpad
        trackpad = {
          ActuateDetents = true;
          Clicking = true; # enable tap to click
          DragLock = false;
          Dragging = false;
          FirstClickThreshold = 0; # For normal click: 0 for light clicking, 1 for medium, 2 for firm. The default is 1.
          ForceSuppressed = false;
          SecondClickThreshold = 0; # For force touch: 0 for light clicking, 1 for medium, 2 for firm. The default is 1.
          TrackpadCornerSecondaryClick = 0; # Whether to enable secondary click: 0 to disable, 1 to set bottom-left corner, 2 to set bottom-right corner. The default is 0.
          TrackpadFourFingerHorizSwipeGesture = 2; # Whether to enable four-finger horizontal swipe gesture: 0 to disable, 2 to swipe between full-screen applications. The default is 0. Type: null or one of 0, 2
          TrackpadFourFingerPinchGesture = 2; # Whether to enable four-finger pinch gesture (spread shows the Desktop, pinch shows the Launchpad): 0 to disable, 2 to enable. The default is 0. This setting interacts with system.defaults.dock.showDesktopGestureEnabled and system.defaults.dock.showLaunchpadGestureEnabled to determine whether gestures are enabled for the Desktop, Launchpad, or both.
          TrackpadFourFingerVertSwipeGesture = 2; # 0 to disable four finger vertical swipe gestures, 2 to enable (down for Mission Control, up for App Exposé). The default is 2. When both three- and four-finger vertical swipe gestures are enabled, the three-finger variant takes precedence. This setting interacts with system.defaults.dock.showAppExposeGestureEnabled and system.defaults.dock.showMissionControlGestureEnabled to determine whether vertical swipe gestures are enabled for App Exposé, Mission Control, or both.
          TrackpadMomentumScroll = true; # Whether to use inertia when scrolling. The default is true.
          TrackpadPinch = true; # Whether to enable two-finger pinch gesture for zooming in and out. The default is false.
          TrackpadRightClick = true; # Whether to enable trackpad right click (two-finger tap/click). The default is false.
          TrackpadRotate = true; # Whether to enable two-finger rotation gesture. The default is false.
          TrackpadThreeFingerDrag = true; # Whether to enable three-finger drag. The default is false.
          TrackpadThreeFingerHorizSwipeGesture = 0; # Whether to enable three-finger horizontal swipe gesture: 0 to disable, 1 to swipe between pages, 2 to swipe between full-screen applications. The default is 2.
          TrackpadThreeFingerTapGesture = 2; # Whether to enable three-finger tap gesture: 0 to disable, 2 to trigger Look up & data detectors. The default is 2.
          TrackpadThreeFingerVertSwipeGesture = 0; # Whether to enable three-finger vertical swipe gesture (down for Mission Control, up for App Exposé): 0 to disable, 2 to enable. The default is 2. This setting interacts with system.defaults.dock.showAppExposeGestureEnabled and system.defaults.dock.showMissionControlGestureEnabled to determine whether vertical swipe gestures are enabled for App Exposé, Mission Control, or both.
          TrackpadTwoFingerDoubleTapGesture = true; # Whether to enable smart zoom when double-tapping with two fingers. The default is false.
          TrackpadTwoFingerFromRightEdgeSwipeGesture = 3; # Whether to enable two-finger swipe-from-right-edge gesture: 0 to disable, 3 to open Notification Center. The default is 0.
        };

        universalaccess = {
          mouseDriverCursorSize = 2.628076553344727;
        };

        WindowManager = {
          AppWindowGroupingBehavior = true;
          EnableStandardClickToShowDesktop = false; #Click wallpaper to reveal desktop Clicking your wallpaper will move all windows out of the way to allow access to your desktop items and widgets. Default is true. false means “Only in Stage Manager” true means “Always”
          EnableTiledWindowMargins = false;
          EnableTilingByEdgeDrag = true;
          EnableTilingOptionAccelerator = true;
          EnableTopTilingByEdgeDrag = true;
          GloballyEnabled = false; # Enable Stage Manager Stage Manager arranges your recent windows into a single strip for reduced clutter and quick access. Default is false.
          HideDesktop = false;
          StageManagerHideWidgets = false;
          StandardHideDesktopIcons = false;
          StandardHideWidgets = false;
        };

        # Customize settings that not supported by nix-darwin directly
        # see the source code of this project to get more undocumented options:
        #    https://github.com/rgcr/m-cli
        #
        # All custom entries can be found by running `defaults read` command.
        # or `defaults read xxx` to read a specific domain.
        CustomUserPreferences = {
          NSGlobalDomain = {
            # Add a context menu item for showing the Web Inspector in web views
            WebKitDeveloperExtras = true;
            NSQuitAlwaysKeepsWindows = true; # true for disable 'close windows when quitting an application'.
          };
          "com.apple.desktopservices" = {
            # Avoid creating .DS_Store files on network or USB volumes
            DSDontWriteNetworkStores = true;
            DSDontWriteUSBStores = true;
          };
          "com.apple.AdLib" = {
            allowApplePersonalizedAdvertising = false;
          };
          # Prevent Photos from opening automatically when devices are plugged in
          "com.apple.ImageCapture".disableHotPlug = true;
          "com.apple.TextEdit" = {
            SmartQuotes = false;
            RichText = false;
          };
          "com.apple.ActivityMonitor" = {
            UpdatePeriod = 1;
          };
        };
      };
    };
  };
}
