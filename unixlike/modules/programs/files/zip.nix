_: {
  programCatalog.zip = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "zip";
      packageOnly = true;
    };
  };
}
