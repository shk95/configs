# Use Fcitx5 in the shared Wayland session.
_: {
  modules.homeManager.linuxGraphical = {
    lib,
    pkgs,
    ...
  }: {
    i18n.inputMethod = {
      enable = true;
      type = "fcitx5";
      fcitx5 = {
        # Niri runs the packaged XDG autostart entry; avoid a second daemon.
        systemd.enable = false;
        waylandFrontend = true;
        addons = lib.mkDefault (with pkgs; [
          fcitx5-gtk
          qt6Packages.fcitx5-configtool
        ]);
      };
    };
  };
}
