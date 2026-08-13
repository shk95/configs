# Unix-like Zellij configuration. This began as an explicit adoption of the
# Windows keymap; each domain owns its copy and may change it independently.
_: {
  modules.homeManager.shared = {pkgs, ...}: {
    programs.zellij = {
      enable = true;
      package = pkgs.zellij;
    };

    xdg.configFile."zellij/config.kdl".source = ../assets/zellij/config.kdl;
  };
}
