_: {
  programCatalog.bitwarden-cli = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "bitwarden-cli";
      packageOnly = true;
    };
  };
}
