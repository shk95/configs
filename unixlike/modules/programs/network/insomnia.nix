_: {
  programCatalog.insomnia = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "insomnia";
      kind = "cask";
    };
  };
}
