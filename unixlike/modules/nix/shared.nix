# One feature, two evaluators: the settings that make flakes work, declared
# where each host's nix.conf is actually generated.
#
# Standalone: this writes ~/.config/nix/nix.conf, which is what makes flakes
# work on a host where Nix came from the plain upstream installer and nothing
# system-wide enabled them.
#
# The file it generates is also the reason the first activation on a fresh machine
# is delicate: home-manager refuses to clobber an unmanaged
# ~/.config/nix/nix.conf, so hand-writing one to get flakes working turns the
# first switch into a failure. Export NIX_CONFIG for that shell instead.
{config, ...}: let
  user = config.identity.wsl.user;
in {
  modules.homeManager.wslStandalone = {pkgs, ...}: {
    nix = {
      package = pkgs.nix;
      settings.experimental-features = ["nix-command" "flakes"];
    };
  };

  # NixOS: /etc/nix/nix.conf is generated from `nix.settings`, and the
  # standalone class above is not composed into this flavour, so nothing else
  # declares it. Found on the imported host, whose whole configuration is a
  # flake and whose daemon refused `nix-command`
  # (docs/policy/decisions/unixlike/nixos-wsl-system-layer-ownership.md). The rest mirrors
  # modules/darwin-nix.nix: the account that rebuilds the host is trusted,
  # and the store is collected weekly — generations older than two weeks go
  # with the garbage, so that is the rollback window.
  #
  # INV unixlike/nixos-no-channel — the assertion below is the schema half of
  # the rule; tool/checks/flake-test holds both directions. The host is
  # rebuilt from this flake and from nothing else, so it has no channel:
  # turning channels off takes the channel directory out of `nix.nixPath`,
  # removes the `nix-channel` command, and keeps the tarball builder from
  # registering one at import. A rebuild that names no flake then stops on the
  # search path instead of reaching for a configuration nobody maintains.
  modules.nixos.wsl = {config, ...}: {
    nix = {
      settings = {
        experimental-features = ["nix-command" "flakes"];
        trusted-users = [user];
      };
      gc = {
        automatic = true;
        dates = "weekly";
        options = "--delete-older-than 14d";
      };
      channel.enable = false;
    };

    assertions = [
      {
        assertion = !config.nix.channel.enable;
        message = "INV unixlike/nixos-no-channel: nix.channel.enable is on; this host is rebuilt from the flake alone and carries no channel.";
      }
    ];
  };
}
