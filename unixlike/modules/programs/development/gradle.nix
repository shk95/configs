_: {
  programCatalog.gradle = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "gradle";
      packageOnly = true;
    };
  };
}
