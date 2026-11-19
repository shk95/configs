_: {
  programCatalog.maccy = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "maccy";
      kind = "cask";
    };
  };
}
