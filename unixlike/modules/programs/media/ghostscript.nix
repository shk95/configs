_: {
  programCatalog.ghostscript = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "ghostscript";
      packageOnly = true;
    };
  };
}
