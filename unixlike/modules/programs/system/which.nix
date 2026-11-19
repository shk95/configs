_: {
  programCatalog.which = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "which";
      packageOnly = true;
    };
  };
}
