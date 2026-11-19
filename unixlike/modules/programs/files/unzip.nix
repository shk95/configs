_: {
  programCatalog.unzip = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "unzip";
      packageOnly = true;
    };
  };
}
