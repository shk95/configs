# Fontconfig exposes fonts selected by the consumer to Linux-side text
# renderers, including in WSL homes without the desktop class.
# This does not enable WSL GUI support. Windows Terminal renders WSL text with
# a Windows font configured on Windows, not with fonts from the Linux profile.
_: {
  modules.homeManager.wsl = {
    fonts.fontconfig.enable = true;
  };
}
