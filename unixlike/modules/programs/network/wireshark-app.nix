_: {
  programCatalog.wireshark-app = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "wireshark-app";
      kind = "cask";
    };
  };
}
