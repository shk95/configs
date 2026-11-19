_: {
  programCatalog.syntax-highlight = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "syntax-highlight";
      kind = "cask";
    };
  };
}
