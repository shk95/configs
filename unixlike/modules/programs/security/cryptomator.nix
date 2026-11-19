_: {
  programCatalog.cryptomator = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "cryptomator";
      kind = "cask";
    };
  };
}
