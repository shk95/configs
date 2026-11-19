_: {
  programCatalog.aria2 = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "aria2";
      packageOnly = true;
    };
  };
}
