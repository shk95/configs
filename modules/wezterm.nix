# One terminal feature, projected into both Unix-like Home Manager
# configurations and the generated native-Windows bundle.
_: {
  modules.homeManager.shared = {pkgs, ...}: {
    programs.wezterm = {
      enable = true;
      package = pkgs.wezterm;
      enableZshIntegration = true;
    };

    xdg.configFile = {
      "wezterm/wezterm.lua".source = ../assets/wezterm/wezterm.lua;
      "wezterm/config".source = ../assets/wezterm/config;
      "wezterm/platform".source = ../assets/wezterm/platform;
      "wezterm/fonts.json".source = ../assets/wezterm/fonts.json;
    };
  };

  windows = {
    packages.wezterm = {
      name = "WezTerm";
      id = "wez.wezterm";
      detection = "Command";
      command = "wezterm.exe";
    };

    managedFiles = {
      weztermRoot = {
        source = "files/wezterm/wezterm.lua";
        target = "{USERPROFILE}\\.config\\wezterm\\wezterm.lua";
        parser = "Lua";
        compare = "Text";
      };
      weztermAppearance = {
        source = "files/wezterm/config/appearance.lua";
        target = "{USERPROFILE}\\.config\\wezterm\\config\\appearance.lua";
        parser = "Lua";
        compare = "Text";
      };
      weztermBehavior = {
        source = "files/wezterm/config/behavior.lua";
        target = "{USERPROFILE}\\.config\\wezterm\\config\\behavior.lua";
        parser = "Lua";
        compare = "Text";
      };
      weztermBindings = {
        source = "files/wezterm/config/bindings.lua";
        target = "{USERPROFILE}\\.config\\wezterm\\config\\bindings.lua";
        parser = "Lua";
        compare = "Text";
      };
      weztermFonts = {
        source = "files/wezterm/config/fonts.lua";
        target = "{USERPROFILE}\\.config\\wezterm\\config\\fonts.lua";
        parser = "Lua";
        compare = "Text";
      };
      weztermDarwin = {
        source = "files/wezterm/platform/darwin.lua";
        target = "{USERPROFILE}\\.config\\wezterm\\platform\\darwin.lua";
        parser = "Lua";
        compare = "Text";
      };
      weztermLinux = {
        source = "files/wezterm/platform/linux.lua";
        target = "{USERPROFILE}\\.config\\wezterm\\platform\\linux.lua";
        parser = "Lua";
        compare = "Text";
      };
      weztermWindows = {
        source = "files/wezterm/platform/windows.lua";
        target = "{USERPROFILE}\\.config\\wezterm\\platform\\windows.lua";
        parser = "Lua";
        compare = "Text";
      };
      weztermFontManifest = {
        source = "files/wezterm/fonts.json";
        target = "{USERPROFILE}\\.config\\wezterm\\fonts.json";
        parser = "Json";
        compare = "ExactJson";
      };
    };
  };
}
