_: {
  programCatalog.glow = {
    profiles = ["shared"];
    providers.nix.identifier = "glow";
  };
  modules.homeManager.shared = {
    config,
    lib,
    pkgs,
    ...
  }: let
    # Glow 3.0.0's TUI reads GLAMOUR_STYLE ahead of its YAML/CLI style.
    # Clear it only in this process so its own configuration controls both views.
    glow = pkgs.symlinkJoin {
      name = "glow-${pkgs.glow.version}";
      paths = [pkgs.glow];
      nativeBuildInputs = [pkgs.makeWrapper];
      postBuild = ''
        wrapProgram "$out/bin/glow" --unset GLAMOUR_STYLE
      '';
    };
  in {
    home.packages = lib.optional config.providerTools.programs.glow.enable glow;
  };
}
