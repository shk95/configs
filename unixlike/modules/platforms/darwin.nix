_: {
  modules.homeManager.darwin = {
    config,
    lib,
    ...
  }: let
    user = config.providerIdentity.user;
  in {
    options.providerDarwin = {
      selectedApps = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        readOnly = true;
        description = "Names selected in the final native Homebrew configuration.";
      };
      appSettings = {
        enable = lib.mkOption {
          type = lib.types.bool;
          default = true;
        };
        ghostty = lib.mkOption {
          type = lib.types.bool;
          default = true;
        };
        karabiner = lib.mkOption {
          type = lib.types.bool;
          default = true;
        };
      };
    };
    config.home.username = user;
  };
}
