# System-wide EDITOR for what runs as root — `sudoedit`, `systemctl edit`,
# `visudo` — without putting the interactive CLI inventory in
# systemPackages. The store path keeps the command available to the system
# while Home Manager owns the user-facing Neovim package and configuration;
# modules/darwin-editor.nix is the same declaration for the Darwin layer.
_: {
  modules.nixos.wsl = {
    lib,
    pkgs,
    ...
  }: {
    environment.variables.EDITOR = "${lib.getExe pkgs.neovim} --clean";
  };
}
