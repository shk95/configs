_: {
  programCatalog.monolith = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "monolith";
      packageOnly = true;
    };
  };
}
