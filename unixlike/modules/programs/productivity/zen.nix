_: {
  programCatalog.zen = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "zen";
      kind = "cask";
    };
  };
}
