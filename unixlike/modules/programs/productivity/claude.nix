_: {
  programCatalog.claude = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "claude";
      kind = "cask";
    };
  };
}
