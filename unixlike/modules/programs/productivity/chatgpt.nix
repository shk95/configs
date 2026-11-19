_: {
  programCatalog.chatgpt = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "chatgpt";
      kind = "cask";
    };
  };
}
