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
    imports = [inputs.paneru.homeModules.paneru];

    services.paneru = {
      enable = lib.mkDefault config.providerTools.programs.paneru.enable;
      luaConfig.enable = true;
      config = lib.mkDefault ./init.lua;
    };
  };
}
