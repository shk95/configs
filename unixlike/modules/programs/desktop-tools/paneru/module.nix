# Darwin user service, package and Lua configuration have one owner.
{inputs, ...}: {
  programCatalog.paneru = {
    profiles = ["darwin"];
    platforms = ["aarch64-darwin"];
    requiredClasses = ["darwin"];
    nativeEnable = ["services" "paneru" "enable"];
    kind = "service";
    providers.nix.identifier = "paneru";
  };
  modules.homeManager.darwin = {
    config,
    lib,
    ...
  }: {
    configs.editableFiles = lib.mkIf (config.services.paneru.enable && config.services.paneru.config != null) {
      ${
        if config.xdg.enable
        then "${config.xdg.configHome}/paneru/init.lua"
        else ".paneru.lua"
      } =
        lib.mkDefault true;
    };
    imports = [
      inputs.paneru.homeModules.paneru
      # PROV unixlike/paneru-unwrapped
      ({
        config,
        lib,
        ...
      }: let
        cfg = config.services.paneru;
      in {
        options.services.paneru.finalPackage = lib.mkOption {
          # Keep the upstream read-only default; transform its result instead
          # of defining it twice. Both PATH and launchd use this same package.
          apply = _:
            if cfg.extraPackages != [] || cfg.extraLuaPackages cfg.lua.pkgs != []
            then throw "Paneru's unwrapped package requires empty extraPackages and extraLuaPackages; environment additions need a native wrapper."
            else
              cfg.package.override {
                enableLua = cfg.luaConfig.enable;
                inherit (cfg) lua;
              };
        };
      })
    ];

    services.paneru = {
      enable = lib.mkDefault config.providerTools.programs.paneru.enable;
      luaConfig.enable = true;
      config = ./init.lua;
    };
  };
}
