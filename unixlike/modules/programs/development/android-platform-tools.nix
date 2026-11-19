_: {
  programCatalog.android-platform-tools = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "android-platform-tools";
      kind = "cask";
    };
  };
}
