_: {
  programCatalog.codex = {
    profiles = ["agents"];
    defaults = {
      linux = "mise";
      darwin = "nix";
    };
    providers = {
      nix = {
        identifier = "codex";
        packageOnly = true;
      };
      mise.identifier = "aqua:openai/codex";
    };
  };
}
