_: {
  programCatalog.procs = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "procs";
      packageOnly = true;
    };
  };
}
