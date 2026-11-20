_: {
  programCatalog.lazygit = {
    profiles = ["shared"];
    nativeEnable = ["programs" "lazygit" "enable"];
    providers.nix.identifier = "lazygit";
  };
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }: {
    programs.lazygit = {
      enable = lib.mkDefault config.providerTools.programs.lazygit.enable;
      enableZshIntegration = lib.mkDefault true;
      # Reverse the terminal's own foreground and background on the selected row.
      settings.gui.theme.selectedLineBgColor = lib.mkDefault ["reverse"];
      # This is the key supported by the pinned schema.
      settings.git.diffRenderers = lib.mkDefault [{command = "delta --paging=never";}];
    };
  };
}
