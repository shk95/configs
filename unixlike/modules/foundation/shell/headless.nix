# The account of a host that boots itself logs into the zsh that
# modules/shell/shared.nix configures, selected the way modules/shell/wsl.nix
# selects it and for the reasons recorded there: `shell` writes the passwd
# entry and puts zsh in the system profile, `environment.shells` writes
# /etc/shells, and `programs.zsh.enable` stays off because the Home Manager
# zsh wants neither a global /etc/zshrc nor a second compinit. What that file
# read back on NixOS-WSL is not yet read back on a host of this class.
_: {
  modules.nixos.headless = {
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
