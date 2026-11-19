_: {
  programCatalog.mkcert = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "mkcert";
      packageOnly = true;
    };
  };
}
