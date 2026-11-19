_: {
  programCatalog.codex = {
    profiles = ["agents"];
    defaults = {
      linux = "mise";
      darwin = "homebrew";
    };
    providers = {
      mise.identifier = "aqua:openai/codex";
      homebrew = {
        identifier = "codex";
        kind = "cask";
      };
    };
  };
}
