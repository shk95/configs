_: {
  programCatalog.nix-tree = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "nix-tree";
      packageOnly = true;
    };
  };
}
