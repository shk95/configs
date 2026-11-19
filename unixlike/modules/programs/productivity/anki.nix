_: {
  programCatalog.anki = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "anki";
      kind = "cask";
    };
  };
}
