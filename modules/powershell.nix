# PowerShell is a configured interactive program, so this module owns both its
# package and its CurrentUserAllHosts profile. The profile is a Unix-like-owned
# adoption of the same platform-neutral policy used by Windows; neither domain
# imports or generates the other one's payload.
_: {
  modules.homeManager.shared = {pkgs, ...}: {
    home.packages = [pkgs.powershell];

    home.file.".config/powershell/profile.ps1".source =
      ../assets/powershell/profile.ps1;
  };
}
