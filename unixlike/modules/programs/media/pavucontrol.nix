_: {
  programCatalog.pavucontrol = {
    profiles = ["linuxGraphical"];
    requiredClasses = ["linuxGraphical"];
    platforms = ["x86_64-linux" "aarch64-linux"];
    providers.nix = {
      identifier = "pavucontrol";
      packageOnly = true;
    };
  };
}
