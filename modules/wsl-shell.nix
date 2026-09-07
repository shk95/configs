# The NixOS-WSL account logs into the zsh that modules/shell.nix configures.
# Selecting a login shell is something a home cannot do: under NixOS the
# account's shell and /etc/shells are both generated from declarations. The
# standalone Ubuntu flavour has no such layer and keeps `just switch-shell`
# (docs/decisions/nixos-wsl-system-layer-ownership.md).
#
# The two lines below do different things, and both were read back on the
# host after the first activation. `shell` writes the passwd entry and, by
# way of nixpkgs installing every declared user shell, puts zsh in the system
# profile — which is what makes the login work at all, because nixos-wsl
# substitutes a wrapper of its own for the passwd shell, and that wrapper
# waits for the activation script to finish and then execs
# `/run/current-system/sw/bin/<shell>`. `environment.shells` writes
# /etc/shells, the permitted list `chsh` reads, so the account's own shell is
# in it rather than only in its passwd entry. zsh therefore reaches both the
# system profile and the managed home; that is one evaluator-owned package
# rather than two declarations
# (docs/decisions/package-ownership-by-generating-module.md).
#
# Not `programs.zsh.enable`: that writes a global /etc/zshrc and runs a second
# compinit the Home Manager zsh does not want, and it is not needed for the
# environment either. NixOS refuses a zsh login shell without it, on the
# ground that the shell "will lack the basic nix directories in its PATH",
# and offers `ignoreShellProgramCheck` for a shell made functional another
# way. This one is: the wrapper above sets the environment, the nixpkgs zsh
# ships its own compiled global zshenv which sources /etc/set-environment,
# and pam_env gives a login its PATH before any shell runs. Read back on the
# host through the passwd shell itself — zsh 5.9.2 with the system profile,
# the per-user profile and the wrappers all on PATH.
# modules/darwin-shell.nix takes the `programs.zsh` route because nix-darwin's
# environment is loaded from /etc/zshrc.
{config, ...}: let
  user = config.identity.wsl.user;
in {
  modules.nixos.wsl = {pkgs, ...}: {
    users.users.${user} = {
      shell = pkgs.zsh;
      ignoreShellProgramCheck = true;
    };
    environment.shells = [pkgs.zsh];
  };
}
