# Darwin user service, package and Lua configuration have one owner.
{inputs, ...}: {
  modules.homeManager.darwin = {
    imports = [inputs.paneru.homeModules.paneru];

    services.paneru = {
      enable = true;
      luaConfig.enable = true;
      config = ./init.lua;
    };
  };
}
