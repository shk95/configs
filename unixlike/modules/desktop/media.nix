# Media and removable-volume integration for the graphical session.
_: {
  modules.homeManager.linuxGraphical = {
    services = {
      playerctld.enable = true;
      udiskie.enable = true;
    };
  };
}
