_: {
  programCatalog.nix-output-monitor = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "nix-output-monitor";
      packageOnly = true;
    };
  };
}
