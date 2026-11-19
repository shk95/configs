_: {
  programCatalog.betterzip = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "betterzip";
      kind = "cask";
    };
  };
}
