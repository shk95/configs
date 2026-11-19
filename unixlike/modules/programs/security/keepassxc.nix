_: {
  programCatalog.keepassxc = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "keepassxc";
      kind = "cask";
    };
  };
}
