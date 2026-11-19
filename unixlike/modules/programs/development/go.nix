_: {
  programCatalog.go = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "go";
      packageOnly = true;
    };
  };
}
