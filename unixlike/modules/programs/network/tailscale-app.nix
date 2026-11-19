_: {
  programCatalog.tailscale-app = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "tailscale-app";
      kind = "cask";
    };
  };
}
