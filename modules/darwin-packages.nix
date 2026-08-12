_: {
  modules.darwin.system = {pkgs, ...}: {
    environment = {
      systemPackages = with pkgs; [
        darwin.trash
      ];
    };
  };
}
