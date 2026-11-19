_: {
  programCatalog.dust = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "dust";
      packageOnly = true;
    };
  };
}
