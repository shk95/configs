_: {
  programCatalog.pup = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "pup";
      packageOnly = true;
    };
  };
}
