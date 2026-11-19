_: {
  programCatalog.tmux = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "tmux";
      packageOnly = true;
    };
  };
}
