_: {
  programCatalog.cowsay = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "cowsay";
      kind = "formula";
    };
  };
}
