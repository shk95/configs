# Linux-side tools that render text into files use fontconfig. Give both WSL
# homes the same D2Coding package as graphical Unix-like homes, while keeping
# the WSL configuration independent of the desktop class. NixOS-WSL has no
# system font packages; Ubuntu WSL may have distribution fonts of its own.
# This does not enable WSL GUI support. Windows Terminal renders WSL text with
# a Windows font configured on Windows, not with fonts from the Linux profile.
_: {
  modules.homeManager.wsl = {pkgs, ...}: {
    fonts.fontconfig.enable = true;

    home.packages = [pkgs.nerd-fonts.d2coding];
  };
}
