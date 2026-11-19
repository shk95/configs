_: {
  programCatalog.trash-cli = {
    profiles = ["shared"];
    platforms = ["x86_64-linux" "aarch64-linux"];
    providers.nix = {
      identifier = "trash-cli";
      packageOnly = true;
    };
  };
}
