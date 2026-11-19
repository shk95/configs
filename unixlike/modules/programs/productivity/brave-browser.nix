_: {
  programCatalog.brave-browser = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "brave-browser";
      kind = "cask";
    };
  };
}
