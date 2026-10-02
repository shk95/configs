# One nixpkgs configuration, declared once and read by both flavours.
#
# This is the structural version of a fix that was already made once by hand.
# `allowUnfree = true` used to be written inline where the standalone flavour
# built its pkgs, and the NixOS flavour builds its own from `nixpkgs.config` —
# so the *shared* home-manager modules were evaluated under two different
# nixpkgs configurations, and nothing said so:
#
#   standalone  true
#   nixos-wsl   false
#
# Deduplicating the value fixed that instance. Declaring it as an option is what
# stops the next one: there is a single name to read, and both places that
# consume it are reachable from here.
#
# `nixpkgsOverlays` is that same shape for overlays: a package fact one
# flavour needs and every flavour must evaluate under is declared once here
# and read from `perSystem` below and from `flake/configurations.nix`, rather
# than repeated per class under `useGlobalPkgs`. It is keyed by name —
# `lazyAttrsOf`, not a list — so `attrValues config.nixpkgsOverlays` below
# yields the overlays in a deterministic, name-sorted order regardless of
# which module contributed which key. A list-typed option would instead
# concatenate overlays in module-walk order, which is exactly the dependency
# `INV unixlike/import-order-independence` (tool/checks/import-order) forbids:
# a value two feature files contribute to must not change when the directory
# walk that collects them changes.
{
  lib,
  config,
  inputs,
  ...
}: let
  inherit (lib) attrValues mkOption types;
  inherit (lib.types) lazyAttrsOf functionTo attrs;
  # Bound here so the `config = …` below reads as nixpkgs' argument rather than
  # as something recursive.
  nixpkgsArgConfig = config.nixpkgsConfig;
in {
  options.nixpkgsConfig = mkOption {
    type = types.attrs;
    default = {};
    description = ''
      The `config` passed to nixpkgs, for every flavour. It is consumed twice and
      both are needed: `pkgs` below is what the standalone flavour evaluates
      against, and `nixpkgs.config` in `flake/configurations.nix` is what the
      NixOS flavour uses — `useGlobalPkgs` makes home-manager take the system's
      pkgs and refuses its own `nixpkgs.*` options outright.
    '';
  };

  options.nixpkgsOverlays = mkOption {
    type = lazyAttrsOf (functionTo (functionTo attrs));
    default = {};
    description = ''
      The overlays passed to nixpkgs, for every flavour, keyed by name so
      `attrValues` reads them back in a deterministic order. It is consumed
      twice and both are needed, the same way `nixpkgsConfig` is: `pkgs`
      below is what the standalone flavour evaluates against, and
      `nixpkgs.overlays` in `flake/configurations.nix` is what the NixOS and
      darwin flavours use under `useGlobalPkgs`. A flavour-specific overlay
      still lands here, not in a class module, and restricts itself with
      `lib.optionalAttrs prev.stdenv.hostPlatform.isDarwin` or the like.
    '';
  };

  config = {
    nixpkgsConfig.allowUnfree = true;

    # flake-parts defaults `pkgs` to `inputs.nixpkgs.legacyPackages`, which
    # carries no config at all. It sets that with `mkOptionDefault`, so replacing
    # it here needs no `mkForce`.
    perSystem = {system, ...}: {
      _module.args.pkgs = import inputs.nixpkgs {
        inherit system;
        config = nixpkgsArgConfig;
        overlays = attrValues config.nixpkgsOverlays;
      };
    };
  };
}
