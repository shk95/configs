# System-wide EDITOR is used by privileged macOS tooling, but that does not
# require putting the whole interactive CLI inventory in systemPackages. The
# store path keeps the command available to the system while Home Manager owns
# the normal user-facing Neovim package and configuration.
_: {
  modules.darwin.system = {
    lib,
    pkgs,
    ...
  }: {
    environment.variables.EDITOR = "${lib.getExe pkgs.neovim} --clean";
  };
}
