_: {
  programCatalog.qlmarkdown = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "qlmarkdown";
      kind = "cask";
    };
  };
}
