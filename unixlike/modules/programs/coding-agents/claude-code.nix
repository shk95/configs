_: {
  programCatalog.claude-code = {
    profiles = ["agents"];
    defaults = {
      linux = "mise";
      darwin = "nix";
    };
    providers = {
      nix = {
        identifier = "claude-code";
        packageOnly = true;
      };
      mise.identifier = "aqua:anthropics/claude-code";
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
