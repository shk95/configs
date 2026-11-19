_: {
  programCatalog.yq-go = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "yq-go";
      packageOnly = true;
    };
  };
}
