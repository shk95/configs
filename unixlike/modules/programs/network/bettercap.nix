_: {
  programCatalog.bettercap = {
    profiles = ["shared"];
    defaults = {
      linux = "nix";
      darwin = "homebrew";
    };
    providers = {
      nix = {
        identifier = "bettercap";
        packageOnly = true;
        platforms = ["x86_64-linux" "aarch64-linux"];
      };
      homebrew = {
        identifier = "bettercap";
        kind = "formula";
      };
    };
  };
}
