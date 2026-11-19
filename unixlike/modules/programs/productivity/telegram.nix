_: {
  programCatalog.telegram = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "telegram";
      kind = "cask";
    };
  };
}
