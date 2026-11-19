_: {
  programCatalog.gping = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "gping";
      packageOnly = true;
    };
  };
}
