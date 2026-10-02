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
{lib, ...}: let
  contract = import ../../../api/contract.nix;
in {
  # The public constructor keeps only common flake capability here. The
  # consumer selects daemon trust, garbage collection and channel policy.
  modules.nixos.environment = {
    nix.settings.experimental-features = ["nix-command" "flakes"];
    system.stateVersion = lib.mkDefault contract.compatibilityDefaults.nixos;
  };

  modules.homeManager.standalone = {pkgs, ...}: {
    nix = {
      package = pkgs.nix;
      settings.experimental-features = ["nix-command" "flakes"];
    };
  };
}
