_: {
  modules.darwin.system = {pkgs, ...}: {
    environment = {
      systemPackages = with pkgs; [
        alacritty
        darwin.trash
        wezterm
      ];
    };
  };
}
