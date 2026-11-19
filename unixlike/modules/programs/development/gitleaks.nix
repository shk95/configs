# The repository hooks use this CLI for secret scanning.
_: {
  programCatalog.gitleaks = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "gitleaks";
      packageOnly = true;
    };
  };
}
