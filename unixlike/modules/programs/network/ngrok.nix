_: {
  programCatalog.ngrok = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "ngrok";
      kind = "cask";
    };
  };
}
