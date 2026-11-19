_: {
  programCatalog.orbstack = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "orbstack";
      kind = "cask";
    };
  };
}
