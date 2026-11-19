_: {
  programCatalog.zstd = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "zstd";
      packageOnly = true;
    };
  };
}
