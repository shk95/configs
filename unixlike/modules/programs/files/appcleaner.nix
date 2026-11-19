_: {
  programCatalog.appcleaner = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "appcleaner";
      kind = "cask";
    };
  };
}
