# A profile font for desktop applications and Linux-side WSL text renderers.
_: {
  programCatalog.d2coding-nerd-font = {
    profiles = [];
    requiredClasses = ["desktop" "wsl"];
    kind = "font";
    providers.nix = {
      identifier = "nerd-fonts.d2coding";
      packageOnly = true;
    };
  };
}
