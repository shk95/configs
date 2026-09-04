# PowerShell is a configured interactive program, so this module owns both its
# package and its CurrentUserAllHosts profile. The profile is a Unix-like-owned
# adoption of the same platform-neutral policy used by Windows; neither domain
# imports or generates the other one's payload.
#
# Pester is here as well, because it is PowerShell module content rather than a
# package of its own: nixpkgs carries no Pester, so this fetches the PSGallery
# package — a zip with the module at its root — and places it where pwsh looks
# first on a Unix-like host. That is what lets `windows/tools/test.ps1` find the
# exact version it requires and lets `pre-push` run the Windows suite under this
# home's own pwsh instead of reporting it unverified. The version is the same
# 5.7.1 that `windows/toolchain.json` declares for Windows contributors, as an
# independent copy: each domain pins its own and may move on its own schedule.
_: {
  modules.homeManager.shared = {pkgs, ...}: let
    pester = pkgs.fetchzip {
      name = "pester-5.7.1";
      url = "https://www.powershellgallery.com/api/v2/package/Pester/5.7.1";
      extension = "zip";
      stripRoot = false;
      hash = "sha256-IZIzFFLVStnb/zy/Mo06bqw/1cejN2BFHWgOEUDRZY8=";
    };
  in {
    home = {
      packages = [pkgs.powershell];

      file = {
        ".config/powershell/profile.ps1".source = ../assets/powershell/profile.ps1;

        # pwsh resolves a versioned module directory by name, so the version is
        # part of the path and a bump here is visible as a path change.
        ".local/share/powershell/Modules/Pester/5.7.1".source = pester;
      };
    };
  };
}
