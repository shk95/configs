_: {
  programCatalog.rsync = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "rsync";
      packageOnly = true;
    };
  };
}
