_: {
  programCatalog.croc = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "croc";
      packageOnly = true;
    };
  };
}
