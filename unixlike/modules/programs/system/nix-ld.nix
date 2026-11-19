# Run unpatched dynamically linked Linux binaries on NixOS.
_: {
  programCatalog.nix-ld = {
    profiles = ["system-common"];
    platforms = ["x86_64-linux" "aarch64-linux"];
    requiredClasses = ["nixos"];
    deployment = "system";
    nativeEnable = ["programs" "nix-ld" "enable"];
    providers.nix.identifier = "nix-ld";
  };
  modules.nixos.environment = {
    config,
    lib,
    ...
  }: {
    programs.nix-ld.enable = lib.mkDefault config.home-manager.users.${config.providerIdentity.user}.providerTools.programs.nix-ld.enable;
  };
}
