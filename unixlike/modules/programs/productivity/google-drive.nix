_: {
  programCatalog.google-drive = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "google-drive";
      kind = "cask";
    };
  };
}
