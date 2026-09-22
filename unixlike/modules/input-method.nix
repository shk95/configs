# The graphical Linux input method. Only Korean is included; the reference
# configuration's Rime and Mozc dictionaries are personal language choices.
_: {
  modules.homeManager.linuxGraphical = {pkgs, ...}: {
    i18n.inputMethod = {
      enable = true;
      type = "fcitx5";
      fcitx5 = {
        waylandFrontend = true;
        addons = with pkgs; [
          fcitx5-gtk
          fcitx5-hangul
          qt6Packages.fcitx5-configtool
        ];
        settings.inputMethod = {
          "GroupOrder"."0" = "Default";
          "Groups/0" = {
            Name = "Default";
            "Default Layout" = "us";
            DefaultIM = "hangul";
          };
          "Groups/0/Items/0".Name = "keyboard-us";
          "Groups/0/Items/1".Name = "hangul";
        };
      };
    };
  };
}
