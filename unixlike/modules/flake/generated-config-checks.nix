# INV unixlike/generated-config-key-in-schema: native generated-file validators
# and parser-specific refusal fixtures. No host closure or session is realized.
{
  config,
  inputs,
  lib,
  ...
}: {
  perSystem = {
    pkgs,
    system,
    ...
  }:
    lib.optionalAttrs (lib.hasSuffix "-linux" system) (let
      provider = {
        lib = config.flake.lib;
        inherit inputs;
        outPath = inputs.self.outPath;
      };
      witness = (import ../../tool/checks/composition-witnesses.nix {inherit provider;})
        .witnesses."mkNixos/${system}/graphical";
      home = witness.configuration.config.home-manager.users.example;
      repeated =
        (provider.lib.mkNixos (witness.args
          // {
            homeModules = [{configs.niri.repeatDelayMs = 250;}];
          })).config.home-manager.users.example;
      badNiri = pkgs.writeText "malformed-niri-config.kdl" "input {";
      badNoctalia = pkgs.writeText "malformed-noctalia-config.toml" "[shell";
      validateNiri = name: source:
        pkgs.runCommand name {} ''
          ${lib.getExe pkgs.niri} validate -c ${source}
          cp ${source} "$out"
        '';
    in {
      checks = {
        generated-niri-config = validateNiri "checked-niri-config" home.xdg.configFile."niri/config.kdl".source;
        generated-niri-repeat-config = validateNiri "checked-niri-repeat-config" repeated.xdg.configFile."niri/config.kdl".source;
        generated-noctalia-config = pkgs.runCommand "checked-noctalia-config" {} ''
          ${lib.getExe home.programs.noctalia.package} config validate ${home.xdg.configFile."noctalia/config.toml".source}
          cp ${home.xdg.configFile."noctalia/config.toml".source} "$out"
        '';
        generated-niri-refuses-malformed = pkgs.runCommand "niri-refuses-malformed-config" {} ''
          if ${lib.getExe pkgs.niri} validate -c ${badNiri} >diagnostic 2>&1; then
            echo "niri accepted malformed KDL" >&2
            exit 1
          fi
          grep -Ei 'parsing|parse|KDL|kdl' diagnostic || { cat diagnostic >&2; exit 1; }
          touch "$out"
        '';
        generated-noctalia-refuses-malformed = pkgs.runCommand "noctalia-refuses-malformed-config" {} ''
          if ${lib.getExe home.programs.noctalia.package} config validate ${badNoctalia} >diagnostic 2>&1; then
            echo "noctalia accepted malformed TOML" >&2
            exit 1
          fi
          grep -Ei 'parsing|parse|TOML|toml' diagnostic || { cat diagnostic >&2; exit 1; }
          touch "$out"
        '';
      };
    });
}
