_: {
  programCatalog.R = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "R";
      packageOnly = true;
    };
  };
}
