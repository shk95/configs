# Fonts rendered by Unix-like desktop applications. A Windows terminal draws
# WSL text with Windows fonts, so putting this in `shared` would only add a font
# to the Linux closure that the terminal cannot see.
_: {
  modules.homeManager.desktop = {pkgs, ...}: {
    # On Darwin, Home Manager copies profile fonts into
    # ~/Library/Fonts/HomeManager because macOS cannot use store symlinks. On
    # Linux, fontconfig exposes the same package from the home profile.
    home.packages = [pkgs.nerd-fonts.d2coding];
    fonts.fontconfig.enable = true;
  };
}
