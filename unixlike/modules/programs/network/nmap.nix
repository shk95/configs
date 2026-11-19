_: {
  programCatalog.nmap = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "nmap";
      packageOnly = true;
    };
  };
}
