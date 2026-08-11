_: {
  modules.darwin.system = {pkgs, ...}: {
    # Allow unfree packages
    nixpkgs.config.allowUnfree = true;

    # Install packages from nix's official package repository.
    #
    # The packages installed here are available to all users, and are reproducible across machines, and are rollbackable.
    # But on macOS, it's less stable than homebrew.
    #
    # Related Discussion: https://discourse.nixos.org/t/darwin-again/29331
    environment = {
      # for security reasons, do not load neovim's user config
      # since EDITOR may be used to edit some critical files
      variables.EDITOR = "nvim --clean";

      systemPackages = with pkgs; [
        aria2
        bat
        caddy
        curl
        fzf
        gh
        git
        gnupg
        go
        jq
        just
        neovim
        nmap
        p7zip
        poppler
        powershell
        pstree
        ripgrep
        socat
        tig
        tmux
        tree
        unzip
        wget
        which
        xz
        yt-dlp
        zip
        zstd
      ];
    };
  };
}
