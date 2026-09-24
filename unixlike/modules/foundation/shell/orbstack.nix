# The OrbStack machine's account logs into the zsh that
# modules/shell/shared.nix configures, selected the way modules/shell/wsl.nix
# selects it and for the reasons recorded there. OrbStack's agent starts the
# account's passwd shell, so the entry is what a session gets.
_: {
  modules.nixos.orbstack = {
    pkgs,
    config,
    ...
  }: {
    users.users.${config.host.user} = {
      shell = pkgs.zsh;
      ignoreShellProgramCheck = true;
    };
    environment.shells = [pkgs.zsh];
  };
}
