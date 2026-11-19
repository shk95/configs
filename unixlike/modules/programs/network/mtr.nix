_: {
  programCatalog.mtr = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "mtr";
      packageOnly = true;
    };
  };
}
