_: {
  programCatalog.android-commandlinetools = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "android-commandlinetools";
      kind = "cask";
    };
  };
}
