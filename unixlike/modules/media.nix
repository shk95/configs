# Configured media applications. Unconfigured graphical tools remain in the
# package concern.
_: {
  modules.homeManager.linuxGraphical = {pkgs, ...}: {
    programs.mpv = {
      enable = true;
      defaultProfiles = ["gpu-hq"];
      scripts = [pkgs.mpvScripts.mpris];
    };

    services = {
      playerctld.enable = true;
      udiskie.enable = true;
    };
  };
}
