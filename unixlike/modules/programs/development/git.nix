_: {
  programCatalog.git = {
    profiles = ["shared"];
    nativeEnable = ["programs" "git" "enable"];
    providers.nix.identifier = "git";
  };
  modules.homeManager.shared = {
    lib,
    config,
    ...
  }: let
    inherit (config.providerIdentity) gitName gitEmail;
  in {
    # Preserve a previous standalone Git config before taking over its path.
    home.activation = lib.mkIf config.programs.git.enable {
      backupExistingGitconfig = lib.hm.dag.entryBefore ["checkLinkTargets"] ''
        if [ -e "$HOME/.gitconfig" ]; then
          backup="$HOME/.gitconfig.before-home-manager.$(date +%Y%m%d%H%M%S)"
          run mv $VERBOSE_ARG "$HOME/.gitconfig" "$backup"
          echo "Moved an unmanaged ~/.gitconfig to $backup"
        fi
      '';
    };

    programs.git = {
      enable = lib.mkDefault config.providerTools.programs.git.enable;
      settings = {
        user = {
          name = gitName;
          email = gitEmail;
        };
        # Render paths such as Korean filenames without octal escapes.
        core.quotepath = lib.mkDefault false;
        log.date = lib.mkDefault "iso";
      };
    };
    programs.delta = {
      enable = lib.mkDefault true;
      enableGitIntegration = lib.mkDefault true;
      options.line-numbers = lib.mkDefault true;
    };
  };
}
