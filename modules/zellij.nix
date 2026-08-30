# Unix-like Zellij configuration. This began as an explicit adoption of the
# Windows keymap; each domain owns its copy and may change it independently.
#
# Colours are not declared here. `programs.zellij.themes` and `settings.theme`
# exist, but this module deliberately copies the KDL asset verbatim instead of
# letting Home Manager render one, so the theme decision lives with the rest of
# the configuration in assets/zellij/config.kdl and is recorded there.
_: {
  modules.homeManager.shared = {pkgs, ...}: {
    programs.zellij = {
      enable = true;
      package = pkgs.zellij;
    };

    xdg.configFile."zellij/config.kdl".source = ../assets/zellij/config.kdl;
  };
}
