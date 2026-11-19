_: {
  programCatalog.gnupg = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "gnupg";
      packageOnly = true;
    };
  };
}
