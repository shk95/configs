_: {
  modules.darwin.system = _: {
    homebrew = {
      # nix-darwin manages the Brewfile and activation behavior. Homebrew itself
      # remains host-owned; this flake intentionally has no nix-homebrew input.
      enable = true;
      enableZshIntegration = true;
      global.autoUpdate = true;
      onActivation = {
        autoUpdate = true; # Fetch the newest stable branch of Homebrew's git repo
        upgrade = true; # Upgrade outdated casks, formulae, and App Store apps
        # Keep manually installed items. This inventory installs and upgrades
        # declarations, but deliberately does not assert exclusive ownership.
        cleanup = "none";
      };

      # These app IDs are from using the mas CLI app
      # mas = mac app store
      # https://github.com/mas-cli/mas
      #
      # $ nix shell nixpkgs#mas
      # $ mas search <app name>
      #
      # Applications to install from Mac App Store using mas.
      # You need to install all these Apps manually first so that your apple account have records for them.
      # otherwise Apple Store will refuse to install them.
      # For details, see https://github.com/mas-cli/mas
      masApps = {
        folderpeek = 1615988943;
        hidden-bar = 1452453066;
        imovie = 408981434;
        keynote = 409183694;
        markdown-editor = 1458220908;
        microsoft-onedrive = 823766827;
        microsoft-onenote = 784801555;
        microsoft-excel = 462058435;
        microsoft-powerpoint = 462062816;
        microsoft-word = 462054704;
        microsoft-windows_app = 1295203466;
        numbers = 409203825;
        pages = 409201541;
        pdfgear = 6469021132;
        tot = 1491071483;
        wireguard = 1451685025;

        # safari extensions
        bitwarden = 1352778147;
        hush = 1544743900;
        obsidian-web-clipper = 6720708363;
        refined-github = 1519867270;
        rightclick-fixer = 6745181406;
        rsshub-radar = 1610744717;
        singlefile = 6444322545;
        userscripts = 1463298887;
        vimlike = 1584519802;
        wayback-machine = 1472432422;
        wblock = 6746388723;
      };

      # Portable command-line tools belong to homeManager.shared. Keep formulae
      # here only when their behavior is specifically tied to macOS/Homebrew.
      brews = [
        # Broken on Darwin in the locked nixpkgs; Linux uses the shared HM list.
        "bettercap"
        "cmatrix"
        "cowsay"
        "displayplacer"
        "fastfetch"
        "mas"
      ];

      # `brew install --cask`
      casks = [
        "anki"
        "android-commandlinetools"
        "android-platform-tools"
        "appcleaner"
        "betterzip"
        "brave-browser"
        "chatgpt"
        "claude"
        "cryptomator"
        "dbeaver-community"
        "discord"
        "flutter"
        "font-hack-nerd-font"
        "ghostty"
        "google-drive"
        "grandperspective"
        "hammerspoon"
        "heynote"
        "iina"
        "insomnia"
        "karabiner-elements"
        "keepassxc"
        "keka"
        "keyboardcleantool"
        "maccy"
        "ngrok"
        "obsidian"
        "orbstack"
        "qlmarkdown"
        "rstudio"
        "swift-shift"
        "syntax-highlight"
        "tailscale-app"
        "telegram"
        "utm"
        "veracrypt-fuse-t"
        "visual-studio-code"
        "wireshark-app"
        "zen"
      ];
    };
  };
}
