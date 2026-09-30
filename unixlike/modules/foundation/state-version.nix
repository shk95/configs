# Home Manager's provider compatibility default. An existing host may retain
# its effective value with a plain native module definition during adoption.
{lib, ...}: let
  contract = import ../../api/contract.nix;
in {
  # Tracks home-manager's option defaults. The 25.11 migration replaces
  # symlinked Darwin applications with Spotlight-compatible copied bundles.
  # Its other state change affects password-store, which is not enabled here.
  modules.homeManager.shared.home.stateVersion = lib.mkDefault contract.compatibilityDefaults.homeManager;
}
