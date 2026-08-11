_: {
  modules.darwin.system = _: {
    homebrew = {
      # This is a module from nix-darwin
      # Homebrew is *installed* via the flake input nix-homebrew
      enable = true;
      global.autoUpdate = true;
      onActivation = {
        autoUpdate = true; # Fetch the newest stable branch of Homebrew's git repo
        upgrade = true; # Upgrade outdated casks, formulae, and App Store apps
        cleanup = "zap"; # 'zap': uninstalls all formulae(and related files) not listed in the generated Brewfile
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
      # masApps = {
      #   folderpeek = 1615988943;
      #   hidden-bar = 1452453066;
      #   imovie = 408981434;
      #   keynote = 361285480; # error
      #   markdown-editor = 1458220908;
      #   microsoft-onedrive = 823766827;
      #   microsoft-onenote = 410395246; # error
      #   microsoft-excel = 462058435; # error
      #   microsoft-powerpoint = 462062816; # error
      #   microsoft-word = 462054704;
      #   microsoft-todo = 1274495053;
      #   microsoft-windows_app = 1295203466; # error
      #   numbers = 361304891; # error
      #   pages = 409201541;
      #   pdfgear = 6465897558; # error
      #   tot = 1491071483;

      #   # safari extensions
      #   adguard = 1440147259;
      #   bitwarden = 1352778147; # error
      #   obsidian-web-clipper = 6720708363;
      #   refined-github = 1519867270;
      #   rightclick-fixer = 6745181406;
      #   rsshub-radar = 1610744717;
      #   vimlike = 1584519802;
      #   wayback-machine = 1201888313; # error
      #   userscripts = 1463298887;
      # };

      # taps = [
      # ];

      # `brew install`
      brews = [
        "gradle"
        "node"
        "pocketbase"
      ];

      # `brew install --cask`
      casks = [
        "anki"
        "appcleaner"
        "chatgpt"
        "dbeaver-community"
        "discord"
        "font-hack-nerd-font"
        "github"
        "grandperspective"
        "heynote"
        "iina"
        "insomnia"
        "keepassxc"
        "keka"
        "keyboardcleantool"
        "lunar"
        "maccy"
        "microsoft-edge"
        "ngrok"
        "obsidian"
        "orbstack"
        "openineditor-lite"
        "openinterminal-lite"
        "postman"
        "protonvpn"
        "qlmarkdown"
        "qlzipinfo"
        "rstudio"
        "swift-shift"
        "syntax-highlight"
        "telegram"
        "ungoogled-chromium"
        "utm"
        "visual-studio-code"
        "wireshark-app"
      ];
    };
  };
}
