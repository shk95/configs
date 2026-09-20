# What is true of a NixOS machine under OrbStack, of any Mac. OrbStack writes
# its own `/etc/nixos/configuration.nix` and `orbstack.nix` into a new
# machine, outside this flake and mixed with facts about the Mac that made it
# — its account, its time zone, its certificate authority — and says the
# second file will be overwritten. Neither is imported or copied: what
# OrbStack needs from the guest is declared here by hand, read from the files
# OrbStack 2.2.3 generated on 2026-09-20, and CONTRIBUTING.md has the step
# that reads them again after an OrbStack update.
#
# The machine is a container: OrbStack supplies the kernel, there is no boot
# loader or disk to declare, and sessions come from an agent OrbStack injects
# beside systemd, not from a login. The account it enters as is
# modules/account.nix's, and sshd is off in modules/sshd.nix.
#
# Left out on purpose. Because this machine is an isolated sandbox: the
# certificates OrbStack adds to a machine that is not isolated — it writes
# none into one created isolated — its ssh client fragment for the Mac's
# agent, the `audio` group it puts the account in, and the x86 platforms it
# declares for emulated builds. Because they restate a default or configure
# what is off: the three `documentation.*` options, the dhcpcd options, and
# `useDefaultShell`, which modules/shell/orbstack.nix replaces.
#
# INV unixlike/orbstack-shared-kernel — every OrbStack machine and OrbStack's
# Docker run on one kernel, UIDs are mapped one to one, so root here is UID 0
# on that kernel, and emulation on it is OrbStack's: it masks
# systemd-binfmt.service in the machine at every boot observed and mounts no
# binfmt_misc. Each machine runs in a user namespace of its own, not the
# kernel's initial one (two machines read side by side on 2026-09-20), so a
# registration made here would probably stay here. That was not tried:
# trying it means writing to a registry whose reach is the question. This
# class registers nothing either way and asserts it, the same care
# modules/wsl.nix takes for WSL's shared registry. tool/checks/flake-test
# holds both directions.
_: {
  modules.nixos.orbstack = {
    lib,
    config,
    modulesPath,
    ...
  }: let
    # Every systemd service OrbStack turns the watchdog off for: the
    # container is frozen with the Mac, and a watchdog that wakes to find its
    # deadline long past kills a healthy service.
    unwatched = [
      "systemd-oomd"
      "systemd-userdbd"
      "systemd-udevd"
      "systemd-timesyncd"
      "systemd-timedated"
      "systemd-portabled"
      "systemd-nspawn@"
      "systemd-machined"
      "systemd-localed"
      "systemd-logind"
      "systemd-journald@"
      "systemd-journald"
      "systemd-journal-remote"
      "systemd-journal-upload"
      "systemd-importd"
      "systemd-hostnamed"
      "systemd-homed"
      "systemd-networkd"
    ];
  in {
    imports = ["${modulesPath}/virtualisation/lxc-container.nix"];

    # OrbStack's network: one interface, IPv4 by DHCP and IPv6 by router
    # advertisement, under systemd-networkd.
    networking = {
      dhcpcd.enable = false;
      useDHCP = false;
      useHostResolvConf = false;
      resolvconf.enable = false;
    };
    systemd = {
      network = {
        enable = true;
        networks."50-eth0" = {
          matchConfig.Name = "eth0";
          networkConfig = {
            DHCP = "ipv4";
            IPv6AcceptRA = true;
          };
          linkConfig.RequiredForOnline = "routable";
        };
      };

      services = lib.genAttrs unwatched (_: {serviceConfig.WatchdogSec = 0;});

      # The debug file system cannot be mounted in the machine: under the
      # first generation of this flake `sys-kernel-debug.mount` failed with
      # "permission denied" at the switch and at every boot, and left the
      # system degraded (observed 2026-09-20, OrbStack 2.2.3). It fails the
      # same way under OrbStack's own image in a machine created isolated;
      # the machine is not in the kernel's initial user namespace. The unit is
      # one of systemd's upstream defaults, which the container module keeps.
      suppressedSystemUnits = ["sys-kernel-debug.mount"];
    };

    # Names are resolved by the Mac, through the file OrbStack mounts.
    services.resolved.enable = false;
    environment.etc."resolv.conf".source = "/opt/orbstack-guest/etc/resolv.conf";

    # OrbStack's own profile fragments, for the shells that read /etc/profile.
    environment.shellInit = ''
      . /opt/orbstack-guest/etc/profile-early
      . /opt/orbstack-guest/etc/profile-late
    '';

    users.groups.orbstack.gid = 67278;

    assertions = [
      {
        assertion = config.boot.binfmt.emulatedSystems == [] && config.boot.binfmt.registrations == {};
        message = "INV unixlike/orbstack-shared-kernel: a binfmt registration is declared; emulation on the kernel every OrbStack machine and OrbStack's Docker share is OrbStack's.";
      }
    ];
  };
}
