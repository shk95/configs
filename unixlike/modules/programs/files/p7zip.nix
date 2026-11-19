_: {
  programCatalog.p7zip = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "p7zip";
      packageOnly = true;
    };
  };
}
