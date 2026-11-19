_: {
  programCatalog.gnutar = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "gnutar";
      packageOnly = true;
    };
  };
}
