# INV unixlike/composition-in-one-place
_: let
  # A bare `zellij` starts the asset's `session_name` with
  # `attach_to_session`, and Zellij takes that path through
  # `attach_by_name`, which asks only whether a live session of that
  # name exists: an exited one is not consulted, so a new session starts under
  # the old name instead of resurrecting it. `zellij attach --create <name>`
  # also reads the serialised layout and resurrects before it creates, so the
  # shell sends a bare call there. Read the deployed KDL at invocation time so
  # editing its session_name does not require rebuilding the shell function.
  kdl = builtins.readFile ./config.kdl;
in {
  programCatalog.zellij = {
    profiles = ["shared"];
    nativeEnable = ["programs" "zellij" "enable"];
    providers.nix.identifier = "zellij";
  };
  modules.homeManager.shared = {
    config,
    lib,
    pkgs,
    ...
  }: let
    sessionReader = pkgs.python3.withPackages (packages: [packages.kdl-py]);
  in {
    configs.editableFiles = lib.mkIf config.programs.zellij.enable {
      "${config.xdg.configHome}/zellij/config.kdl" = lib.mkDefault true;
    };
    programs.zellij = {
      enable = lib.mkDefault config.providerTools.programs.zellij.enable;
      package = pkgs.zellij;
      extraConfig = lib.mkDefault kdl;
    };

    programs.zsh.initContent = lib.mkIf config.programs.zellij.enable ''
      zellij() {
        if (( $# == 0 )); then
          ${sessionReader}/bin/python3 ${../../../../tool/zellij-session} ${lib.escapeShellArg "${config.xdg.configHome}/zellij/config.kdl"}
        else
          command zellij "$@"
        fi
      }
    '';
  };
}
