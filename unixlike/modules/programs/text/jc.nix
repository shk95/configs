_: {
  programCatalog.jc = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "jc";
      packageOnly = true;
    };
  };
}
