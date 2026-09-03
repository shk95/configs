# Unix-like Zellij configuration. This began as an explicit adoption of the
# Windows keymap; each domain owns its copy and may change it independently.
#
# Colours are split by class, and the split is forced by how this module
# delivers the configuration. `programs.zellij.themes` and `settings.theme`
# exist, but this module deliberately copies the KDL asset verbatim rather than
# letting Home Manager render one, so a per-class theme has to be a per-class
# copy of that asset:
#
#   shared   the asset as committed. It carries `theme_dark`/`theme_light`,
#            which zellij switches between from the host terminal's own
#            colour-scheme report (CSI 2031 / DSR 997). The reasoning for that
#            pair is recorded in the asset itself.
#   desktop  the same bytes plus a static `theme`, pinning Flexoki Light.
#
# The desktop copy exists because the report is not universal, and the terminal
# that does not send it is the one this class is for. Ghostty answers the
# query; the pinned WezTerm has no colour-scheme private mode at all, so it
# never answers, and an unanswered query leaves zellij on its dark fallback —
# dark pane frames, tab bar and status line inside the light WezTerm this
# repository declares two files away. A static `theme` is authoritative only
# until a report arrives, so pinning it here costs Ghostty nothing: Ghostty
# still drives its own palette through the pair, and WezTerm gets a light one
# without having to ask.
#
# `homeManager.shared` keeps the pair alone because its extra reach is the WSL
# homes, whose terminal is declared in the Windows domain and is still dark;
# pinning light there would be the guess `modules/bat.nix` refuses to make.
_: {
  modules.homeManager.shared = {pkgs, ...}: {
    programs.zellij = {
      enable = true;
      package = pkgs.zellij;
    };

    xdg.configFile."zellij/config.kdl".source = ../assets/zellij/config.kdl;
  };

  modules.homeManager.desktop = {
    lib,
    pkgs,
    ...
  }: {
    # INV unixlike/composition-in-one-place — this is the known leak (#127):
    # `desktop` forces a file `shared` already declares, so this feature file
    # decides which class wins. Until a class-level shape expresses it, the
    # generated copy is the asset byte for byte with one node appended, so the
    # keymap stays in exactly one place and no second payload appears under
    # assets/.
    xdg.configFile."zellij/config.kdl".source =
      lib.mkForce
      (pkgs.writeText "zellij-config.kdl" (
        builtins.readFile ../assets/zellij/config.kdl
        + ''

          // Appended by modules/zellij.nix for `homeManager.desktop` only,
          // because WezTerm never answers the colour-scheme query the pair
          // above depends on. See that file for the full reasoning.
          theme "flexoki-light"
        ''
      ));
  };
}
