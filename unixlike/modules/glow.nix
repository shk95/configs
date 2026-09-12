_: {
  modules.homeManager.shared = {
    lib,
    pkgs,
    ...
  }: let
    settings = (pkgs.formats.yaml {}).generate "glow.yml" {style = "light";};
    # Glow 3.0.0's TUI reads GLAMOUR_STYLE ahead of its YAML/CLI style.
    # Clear it only in this process so both views honour glow's own settings.
    glow = pkgs.symlinkJoin {
      name = "glow-${pkgs.glow.version}";
      paths = [pkgs.glow];
      nativeBuildInputs = [pkgs.makeWrapper];
      postBuild = ''
        wrapProgram "$out/bin/glow" --unset GLAMOUR_STYLE
      '';
    };
  in {
    home.packages = [glow];
    # XDG takes precedence on both platforms. go-app-paths 0.2.2 also
    # searches ~/Library/Preferences/glow on Darwin when XDG is unset.
    xdg.configFile."glow/glow.yml".source = settings;
    home.file."Library/Preferences/glow/glow.yml" = lib.mkIf pkgs.stdenv.hostPlatform.isDarwin {
      source = settings;
    };
  };
}
