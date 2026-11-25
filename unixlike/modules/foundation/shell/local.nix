_: {
  modules.homeManager.shared = {
    config,
    lib,
    ...
  }:
    lib.mkIf config.programs.zsh.enable {
      home.file.".zshrc.local".text = lib.mkDefault "";
      configs.editableFiles.".zshrc.local" = lib.mkDefault true;

      programs.zsh.initContent = lib.mkAfter ''
        if [[ -f "$HOME/.zshrc.local" && -r "$HOME/.zshrc.local" ]]; then
          source "$HOME/.zshrc.local"
        fi
      '';
    };
}
