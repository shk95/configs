_: {
  programCatalog.dnsutils = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "dnsutils";
      packageOnly = true;
    };
  };
}
