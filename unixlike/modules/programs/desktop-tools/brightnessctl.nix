_: {
  programCatalog.brightnessctl = {
    profiles = ["linuxGraphical"];
    requiredClasses = ["linuxGraphical"];
    platforms = ["x86_64-linux" "aarch64-linux"];
    providers.nix = {
      identifier = "brightnessctl";
      packageOnly = true;
    };
  };
}
