# Use the session's lock command after idle and before sleep.
_: {
  modules.homeManager.linuxGraphical = {lib, ...}: {
    services.hypridle = {
      enable = true;
      settings = {
        general = {
          lock_cmd = lib.mkDefault "noctalia msg session lock";
          before_sleep_cmd = lib.mkDefault "noctalia msg session lock";
        };
        listener = lib.mkDefault [
          {
            timeout = 900;
            on-timeout = "noctalia msg session lock";
          }
        ];
      };
    };
  };
}
