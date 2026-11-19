_: {
  programCatalog.discord = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "discord";
      kind = "cask";
    };
  };
}
