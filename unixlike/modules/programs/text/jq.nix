_: {
  programCatalog.jq = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "jq";
      packageOnly = true;
    };
  };
}
