_: {
  programCatalog.socat = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "socat";
      packageOnly = true;
    };
  };
}
