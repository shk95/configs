_: {
  programCatalog.poppler = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "poppler";
      packageOnly = true;
    };
  };
}
