_: {
  programCatalog.just = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "just";
      packageOnly = true;
    };
  };
}
