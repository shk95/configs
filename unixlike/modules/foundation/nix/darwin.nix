# Flake support in the provider environment. Host modules select the daemon,
# trusted users, collection policy and installer integration.
_: {
  modules.darwin.environment.nix.settings.experimental-features = ["nix-command" "flakes"];
}
