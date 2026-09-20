# The clock comes from the host — Windows for WSL, the Mac for OrbStack; the
# zone does not. Without this the host reports UTC (observed on the imported
# WSL distribution). OrbStack writes the Mac's zone into the configuration it
# generates, which this flake does not import (modules/host/orbstack.nix).
# The Darwin layer declares the same zone in modules/darwin-defaults.nix.
_: {
  modules.nixos.wsl.time.timeZone = "Asia/Seoul";
  modules.nixos.orbstack.time.timeZone = "Asia/Seoul";
}
