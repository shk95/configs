{lib, ...}: let
  contract = import ../../../api/contract.nix;
in {
  modules.darwin.environment.system = {
    stateVersion = lib.mkDefault contract.compatibilityDefaults.nixDarwin;
    defaults = {
      NSGlobalDomain = {
        AppleShowAllExtensions = lib.mkDefault true;
        NSNavPanelExpandedStateForSaveMode = lib.mkDefault true;
        NSNavPanelExpandedStateForSaveMode2 = lib.mkDefault true;
      };
      finder = {
        AppleShowAllExtensions = lib.mkDefault true;
        ShowPathbar = lib.mkDefault true;
        ShowStatusBar = lib.mkDefault true;
      };
      loginwindow.GuestEnabled = lib.mkDefault false;
      screensaver = {
        askForPassword = lib.mkDefault true;
        askForPasswordDelay = lib.mkDefault 0;
      };
      CustomUserPreferences = {
        "com.apple.desktopservices".DSDontWriteNetworkStores = lib.mkDefault true;
        "com.apple.TextEdit".SmartQuotes = lib.mkDefault false;
      };
    };
  };
}
