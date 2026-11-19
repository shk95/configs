_: {
  programCatalog.hyperfine = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "hyperfine";
      packageOnly = true;
    };
  };
}
