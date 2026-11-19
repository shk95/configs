_: {
  programCatalog.pocketbase = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "pocketbase";
      packageOnly = true;
    };
  };
}
