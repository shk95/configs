_: {
  programCatalog.curl = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "curl";
      packageOnly = true;
    };
  };
}
