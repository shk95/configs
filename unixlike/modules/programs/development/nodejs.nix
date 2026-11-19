_: {
  programCatalog.nodejs = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "nodejs";
      packageOnly = true;
    };
  };
}
