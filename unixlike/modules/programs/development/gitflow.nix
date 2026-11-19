_: {
  programCatalog.gitflow = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "gitflow";
      packageOnly = true;
    };
  };
}
