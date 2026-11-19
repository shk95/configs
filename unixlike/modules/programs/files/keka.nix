_: {
  programCatalog.keka = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "keka";
      kind = "cask";
    };
  };
}
