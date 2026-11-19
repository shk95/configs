_: {
  programCatalog.python3 = {
    profiles = ["shared"];
    platforms = ["x86_64-linux" "aarch64-linux"];
    providers.nix = {
      identifier = "python3";
      packageOnly = true;
    };
  };
}
