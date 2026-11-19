_: {
  programCatalog.fd = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "fd";
      packageOnly = true;
    };
  };
}
