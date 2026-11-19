_: {
  programCatalog.wl-clipboard = {
    profiles = ["linuxGraphical"];
    requiredClasses = ["linuxGraphical"];
    platforms = ["x86_64-linux" "aarch64-linux"];
    providers.nix = {
      identifier = "wl-clipboard";
      packageOnly = true;
    };
  };
}
