_: {
  programCatalog.visual-studio-code = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "visual-studio-code";
      kind = "cask";
    };
  };
}
