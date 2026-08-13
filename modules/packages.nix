# Packages with nothing to configure. Anything that has a home-manager module —
# and so a config file to generate — gets its own file instead; `bat` moved out of
# here for exactly that reason, and `programs.bat` contributes the package itself.
#
# These are Home Manager packages rather than `environment.systemPackages`.
# That makes the same interactive tool set available to Darwin, NixOS-WSL, and
# standalone Home Manager on Ubuntu WSL. Under system-integrated Home Manager,
# `useUserPackages = true` still folds the packages into the host generation.
#
# Put a package in a system module only when a service, activation script, or
# root/system account needs it. Put macOS applications and tools whose behavior
# depends on Homebrew in `darwin-homebrew.nix`. Everything else belongs here so
# adding a system layer never removes it from the standalone configuration.
_: {
  modules.homeManager.shared = {
    lib,
    pkgs,
    ...
  }: {
    home.packages = with pkgs;
      [
        # search / text
        ripgrep
        fd
        fzf
        jq
        yq-go
        file
        gawk
        gnused
        pup

        # git tooling beyond programs.git — gh is modules/gh.nix, which also
        # generates the credential helper
        tig
        gitflow

        # the pre-commit hook's secret scan is a no-op without this, and on a
        # public repository CI only catches a leak after it is already published
        gitleaks
        bitwarden-cli

        # archives
        p7zip
        unzip
        zip
        xz
        zstd

        # network
        aria2
        caddy
        curl
        mkcert
        nmap
        rclone
        socat
        wget

        # languages / build tools
        go
        gradle
        nodejs
        R

        # documents / media / data
        ghostscript
        glow
        gnutar
        monolith
        pocketbase
        poppler
        yt-dlp

        # session / monitoring
        tmux
        btop
        pstree

        tree
        just
        gnupg
        which
      ]
      # The locked nixpkgs marks bettercap broken on Darwin. Homebrew owns the
      # macOS formula while Linux homes still receive the same command from Nix.
      ++ lib.optionals pkgs.stdenv.hostPlatform.isLinux [pkgs.bettercap];
  };
}
