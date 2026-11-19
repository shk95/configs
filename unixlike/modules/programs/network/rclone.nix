_: {
  programCatalog.rclone = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "rclone";
      packageOnly = true;
    };
  };
}
