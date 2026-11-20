# Use the session's lock command before sleep.
_: {
  modules.homeManager.linuxGraphical = {lib, ...}: {
    services.hypridle = {
      enable = true;
      settings.general = {
        lock_cmd = lib.mkDefault "noctalia msg session lock";
        before_sleep_cmd = lib.mkDefault "noctalia msg session lock";
      };
    };
  };
}
