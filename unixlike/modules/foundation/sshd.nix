# The one service a headless host runs: sshd, so the host is reachable
# without its hypervisor's terminal in front of it. A home cannot run a
# system daemon, which is what puts it in the system layer
# (docs/policy/decisions/unixlike/nixos-wsl-system-layer-ownership.md).
#
# On NixOS-WSL the port is the port Windows sees. WSL2's NAT mode relays
# every port the VM listens on to the Windows loopback, and every
# distribution shares the VM's network namespace, so one number has to be
# free in three places at once: Windows itself holds 22 (its own OpenSSH
# server), Ubuntu holds 2222, and this host takes 2223. Exposure beyond the
# Windows host — a `tailscale serve` mapping of the same port — is Windows
# state and lives in the Windows domain, not here.
#
# A host that boots itself shares none of that — its network is its own — so
# `nixos.headless` takes 22, and the rest is the same daemon. The two
# fragments stay apart because the port is the point of each.
#
# Keys are host-owned, as everywhere in this repository (modules/foundation/ssh.nix):
# `~/.ssh/authorized_keys` on the host rather than
# `users.users.<user>.openssh.authorizedKeys`, which would put a public key
# into tracked desired state. A fresh import or installation therefore starts
# with no authorized key; CONTRIBUTING.md § Import the NixOS-WSL distribution
# lists copying one among the steps. Host keys are generated at first start.
#
# An OrbStack machine runs none: OrbStack reaches it through an agent of its
# own and turns sshd off in the configuration it generates, so the class
# states the same (modules/machines/orbstack.nix).
#
# INV unixlike/headless-key-only — the assertions below are the daemon's
# half of the rule; modules/foundation/firewall.nix holds the port's and
# modules/foundation/account.nix the account's. tool/checks/flake-test holds both
# directions.
_: {
  modules.nixos = {
    wsl.services.openssh = {
      enable = true;
      ports = [2223];
      settings = {
        PasswordAuthentication = false;
        KbdInteractiveAuthentication = false;
        PermitRootLogin = "no";
      };
    };

    orbstack.services.openssh.enable = false;

    headless = {
      lib,
      config,
      ...
    }: let
      sshd = config.services.openssh;
      keyed =
        lib.filterAttrs (
          _: account:
            account.openssh.authorizedKeys.keys != [] || account.openssh.authorizedKeys.keyFiles != []
        )
        config.users.users;
    in {
      services.openssh = {
        enable = true;
        ports = [22];
        settings = {
          PasswordAuthentication = false;
          KbdInteractiveAuthentication = false;
          PermitRootLogin = "no";
        };
      };

      assertions = [
        {
          assertion =
            sshd.enable
            && !sshd.settings.PasswordAuthentication
            && !sshd.settings.KbdInteractiveAuthentication
            && sshd.settings.PermitRootLogin == "no";
          message = "INV unixlike/headless-key-only: sshd on a headless host accepts a key and nothing else, and never a root login.";
        }
        {
          assertion = keyed == {};
          message = "INV unixlike/headless-key-only: an authorized key is tracked for ${lib.concatStringsSep ", " (lib.attrNames keyed)}; keys are host-owned, in ~/.ssh/authorized_keys.";
        }
      ];
    };
  };
}
