_: {
  programCatalog.wget = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "wget";
      packageOnly = true;
    };
  };
}
