_: {
  programCatalog.pstree = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "pstree";
      packageOnly = true;
    };
  };
}
