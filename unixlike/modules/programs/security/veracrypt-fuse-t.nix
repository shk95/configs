_: {
  programCatalog.veracrypt-fuse-t = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "veracrypt-fuse-t";
      kind = "cask";
    };
  };
}
