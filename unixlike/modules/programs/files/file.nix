_: {
  programCatalog.file = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "file";
      packageOnly = true;
    };
  };
}
