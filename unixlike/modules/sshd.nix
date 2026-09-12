# The one service the headless host runs: sshd, so the host is reachable
# without a Windows terminal in front of it. A home cannot run a system
# daemon, which is what puts it in the system layer
# (docs/decisions/nixos-wsl-system-layer-ownership.md).
#
# The port is the port Windows sees. WSL2's NAT mode relays every port the
# VM listens on to the Windows loopback, and every distribution shares the
# VM's network namespace, so one number has to be free in three places at
# once: Windows itself holds 22 (its own OpenSSH server), Ubuntu holds 2222,
# and this host takes 2223. Exposure beyond the Windows host — a
# `tailscale serve` mapping of the same port — is Windows state and lives in
# the Windows domain, not here.
#
# Keys are host-owned, as everywhere in this repository (modules/ssh.nix):
# `~/.ssh/authorized_keys` on the host rather than
# `users.users.<user>.openssh.authorizedKeys`, which would put a public key
# into tracked desired state. A fresh import therefore starts with no
# authorized key; CONTRIBUTING.md § Import the NixOS-WSL distribution lists
# copying one among the steps. Host keys are generated at first start.
_: {
  modules.nixos.wsl.services.openssh = {
    enable = true;
    ports = [2223];
    settings = {
      PasswordAuthentication = false;
      KbdInteractiveAuthentication = false;
      PermitRootLogin = "no";
    };
  };
}
