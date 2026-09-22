# What is true of a NixOS guest under UTM, of the QEMU `virt` machine and of
# no particular disk. Nothing detected on a machine is stored here or in the
# inventory — no UUID, no MAC address, no generated
# `hardware-configuration.nix`: the module list is a fact about the
# hypervisor's machine type, which is a kind, and the file systems are named
# by the labels the installing step creates them under (CONTRIBUTING.md).
#
# The guest is headless, so a serial console is what reaches it before the
# network does. `virt` wires its first serial port as a PL011, `ttyAMA0`;
# named last, it is the console the kernel logs to and systemd starts a getty
# on. What makes the host reachable afterwards — the account, sshd, the
# firewall — is `nixos.headless`, written for every host that boots itself.
#
# INV unixlike/nixos-host-inventory
_: {
  modules.nixos.utm = {
    config,
    modulesPath,
    ...
  }: {
    # The virtio disk, network and SCSI modules the initrd needs to find the
    # labelled file systems, as nixpkgs keeps them for a QEMU guest.
    imports = ["${modulesPath}/profiles/qemu-guest.nix"];

    boot = {
      kernelParams = ["console=tty0" "console=ttyAMA0"];
    };

    services.qemuGuest.enable = true;

    # UTM's shared network hands out an address; nothing about it is fixed.
    networking.useDHCP = true;

    # INV unixlike/graphical-guests-keep-recovery
    assertions = [
      {
        assertion =
          config.services.qemuGuest.enable
          && builtins.elem "console=tty0" config.boot.kernelParams
          && builtins.elem "console=ttyAMA0" config.boot.kernelParams
          && config.programs.niri.enable
          && config.services.greetd.enable
          && config.services.pipewire.enable
          && config.services.openssh.enable
          && config.networking.firewall.allowedTCPPorts == [22];
        message = "INV unixlike/graphical-guests-keep-recovery: the UTM guest must retain QEMU and serial integration, the graphical profile and key-only recovery";
      }
    ];
  };
}
