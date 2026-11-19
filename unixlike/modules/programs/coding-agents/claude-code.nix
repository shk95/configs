_: {
  programCatalog.claude-code = {
    profiles = ["agents"];
    defaults = {
      linux = "mise";
      darwin = "homebrew";
    };
    providers = {
      mise.identifier = "aqua:anthropics/claude-code";
      homebrew = {
        identifier = "claude-code";
        kind = "cask";
      };
    };
  };
  modules.homeManager.agents = {
    config,
    lib,
    ...
  }: {
    home.sessionVariables = lib.mkIf config.providerTools.programs.claude-code.enable {
      DISABLE_AUTOUPDATER = "1";
    };
  };
}
