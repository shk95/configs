# System services every Niri graphical host needs independently of its
# hardware and hypervisor.
_: {
  modules.nixos.graphical = {
    hardware.graphics.enable = true;
    programs.dconf.enable = true;
    security.polkit.enable = true;

    services = {
      dbus.enable = true;
      gnome.gnome-keyring.enable = true;
      gvfs.enable = true;
      tumbler.enable = true;
      udisks2.enable = true;
    };

    xdg.portal.xdgOpenUsePortal = true;
  };
}
