# Run unpatched dynamically linked Linux binaries on NixOS. The NixOS module
# supplies the loader and its default libraries; other platforms keep their own.
_: {
  modules.nixos.shared.programs.nix-ld.enable = true;
}
