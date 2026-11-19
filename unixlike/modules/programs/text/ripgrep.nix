_: {
  programCatalog.ripgrep = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "ripgrep";
      packageOnly = true;
    };
  };
}
