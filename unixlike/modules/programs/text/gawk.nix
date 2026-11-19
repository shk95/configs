_: {
  programCatalog.gawk = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "gawk";
      packageOnly = true;
    };
  };
}
