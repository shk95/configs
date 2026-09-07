# The coding agents, as a class of their own. Composed only where they are
# wanted: modules/flake/configurations.nix gives `homeManager.agents` to the
# NixOS-WSL home and to no other, so the standalone Ubuntu home and the
# Darwin home are unchanged by this file — the mechanism that keeps
# `homeManager.desktop` out of the WSL homes, used the other way round
# (#195; docs/decisions/home-manager-platform-classes.md).
#
# Both come from the flake's nixpkgs input, which already tracks
# nixos-unstable; a newer version arrives with the next `flake.lock` refresh
# rather than from a second input. claude-code is unfree, and
# modules/flake/nixpkgs.nix allows that for every flavour.
_: {
  modules.homeManager.agents = {pkgs, ...}: {
    home.packages = [
      pkgs.claude-code
      pkgs.codex
    ];
  };
}
