_: {
  programCatalog.rstudio = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "rstudio";
      kind = "cask";
    };
  };
}
