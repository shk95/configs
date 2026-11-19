_: {
  programCatalog.dbeaver-community = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "dbeaver-community";
      kind = "cask";
    };
  };
}
