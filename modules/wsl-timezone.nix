# The clock comes from Windows; the zone does not. Without this the host
# reports UTC (observed on the imported distribution). The Darwin layer
# declares the same zone in modules/darwin-defaults.nix.
_: {
  modules.nixos.wsl.time.timeZone = "Asia/Seoul";
}
