# Noctalia is started by Niri and validates its declarative configuration.
_: {
  modules.homeManager.linuxGraphical = {lib, ...}: {
    programs.noctalia = {
      enable = true;
      systemd.enable = false;
      checkConfig = true;
      settings.shell.setup_wizard_enabled = lib.mkDefault false;
    };
  };
}
