# Every NixOS host uses the same local zone. WSL and OrbStack get their clocks
# from the surrounding host, but still need the zone declared here. The Darwin
# layer declares the same zone in modules/defaults.nix.
_: {
  modules.nixos.shared.time.timeZone = "Asia/Seoul";
}
