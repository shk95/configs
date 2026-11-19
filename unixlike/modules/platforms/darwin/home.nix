_: {
  modules.homeManager.darwin = {
    config,
    lib,
    ...
  }: let
    user = config.providerIdentity.user;
  in {
    options.providerDarwin = {
      homebrew = lib.mkOption {
        type = lib.types.attrs;
        readOnly = true;
        internal = true;
        description = "Effective package names from the Darwin system configuration.";
      };
      selectedApps = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        readOnly = true;
        description = "Compatibility names derived from final program selection.";
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
    config.providerDarwin.selectedApps = let
      inherit (config.providerDarwin) homebrew;
    in
      lib.unique (
        map (name: lib.toLower (builtins.baseNameOf name)) (homebrew.brews ++ homebrew.casks)
        ++ map lib.toLower (builtins.attrNames homebrew.masApps)
      );
  };
}
