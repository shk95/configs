_: {
  programCatalog.caddy = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "caddy";
      packageOnly = true;
    };
  };
}
