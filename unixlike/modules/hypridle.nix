# Idle handling for Niri delegates locking to Noctalia and monitor power to
# the compositor. Hardware-specific keyboard backlights stay out of the shared
# class.
_: {
  modules.homeManager.linuxGraphical.services.hypridle = {
    enable = true;
    settings = {
      general = {
        lock_cmd = "noctalia msg session lock";
        before_sleep_cmd = "noctalia msg session lock";
        ignore_dbus_inhibit = true;
      };
      listener = [
        {
          timeout = 600;
          on-timeout = "niri msg action power-off-monitors";
          on-resume = "niri msg action power-on-monitors";
        }
        {
          timeout = 900;
          on-timeout = "noctalia msg session lock";
        }
      ];
    };
  };
}
