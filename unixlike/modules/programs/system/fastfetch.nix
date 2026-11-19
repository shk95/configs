_: {
  programCatalog.fastfetch = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers.homebrew = {
      identifier = "fastfetch";
      kind = "formula";
    };
  };
}
