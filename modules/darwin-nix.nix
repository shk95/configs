{config, ...}: let
  user = config.identity.darwin.user;
in {
  modules.darwin.system = {
    pkgs,
    lib,
    ...
  }: {
    nix = {
      # Determinate uses its own daemon to manage the Nix installation that
      # conflicts with nix-darwin's native Nix management.
      #
      # set this to false if you're using Determinate Nix.
      # NOTE: Turning off this option will invalidate all of the following nix configurations,
      enable = true;

      package = pkgs.nix;

      settings = {
        # enable flakes globally
        experimental-features = [
          "nix-command"
          "flakes"
        ];

        trusted-users = [user];

        # Disable auto-optimise-store because of this issue:
        #   https://github.com/NixOS/nix/issues/7273
        # "error: cannot link '/nix/store/.tmp-link-xxxxx-xxxxx' to '/nix/store/.links/xxxx': File exists"
        auto-optimise-store = false;
      };

      # do garbage collection weekly to keep disk usage low
      gc = {
        automatic = lib.mkDefault true;
        options = lib.mkDefault "--delete-older-than 14d";
      };
    };
  };
}
