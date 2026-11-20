_: {
  programCatalog.btop = {
    profiles = ["shared"];
    nativeEnable = ["programs" "btop" "enable"];
    providers.nix.identifier = "btop";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    # `programs.btop` contributes its own package, so INV
    # The native module owns the package and settings together, as do bat and
    # lazygit for their
    # packages (docs/policy/decisions/unixlike/package-ownership-by-generating-module.md).
    #
    # btop uses a truecolour theme rather than the terminal ANSI palette.
    # Keep its light UI and accents aligned with Bluegray Light. With
    # theme_background=false the terminal still owns the page background.
    # Reserve ochre for elevated temperature; ordinary graphs stay cool.
    programs.btop = {
      enable = lib.mkDefault config.providerTools.programs.btop.enable;
    };
  };
}
