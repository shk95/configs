_: {
  programCatalog.doggo = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "doggo";
      packageOnly = true;
    };
  };
}
