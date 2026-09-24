# Home Manager's state version only. NixOS's is unrelated to it — a different
# evaluator on a different release schedule — and is a fact about a host, the
# release that host was first installed with, so each host declares its own
# in the typed inventory and modules/host/nixos.nix applies it.
_: {
  # Tracks home-manager's option defaults. The 25.11 migration replaces
  # symlinked Darwin applications with Spotlight-compatible copied bundles.
  # Its other state change affects password-store, which is not enabled here.
  modules.homeManager.shared.home.stateVersion = "25.11";
}
