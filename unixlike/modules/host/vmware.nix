# What is true of a NixOS guest under VMware Workstation and of no particular
# disk, on a Linux host and on a Windows one alike: nothing here depends on
# the host's operating system, which is what the hypervisor was chosen for
# (docs/policy/decisions/unixlike/x86-64-guest-runs-on-vmware-workstation.md).
# Nothing detected on a machine is stored here or in the inventory — no UUID,
# no MAC address, no generated `hardware-configuration.nix` — and the file
# systems are named by the labels the installing step creates them under
# (CONTRIBUTING.md).
#
# No initrd module list is written. nixpkgs' guest module puts the LSI Logic
# and paravirtual SCSI drivers (`mptspi`, `vmw_pvscsi`) in the initrd, and the
# NVMe and SATA drivers are in every NixOS initrd, so whichever disk
# controller the machine is created with is found.
#
# The console is the machine's own screen in VMware: a VMware machine has no
# serial port unless one is added by hand, so none is declared. What makes
# the host reachable afterwards — the account, sshd, the firewall — is
# `nixos.headless`, written for every host that boots itself.
#
# INV unixlike/nixos-host-inventory
_: {
  modules.nixos.vmware = {
    # The machine must be created with UEFI firmware; systemd-boot does not
    # start from the BIOS one.
    boot.loader = {
      systemd-boot.enable = true;
      efi.canTouchEfiVariables = true;
    };

    fileSystems = {
      "/" = {
        device = "/dev/disk/by-label/nixos";
        fsType = "ext4";
      };
      "/boot" = {
        device = "/dev/disk/by-label/boot";
        fsType = "vfat";
      };
    };

    # open-vm-tools without its X11 half. nixpkgs derives the same value from
    # the absent X server; it is written here because the installed-host
    # graphical order is the one that means to change it.
    virtualisation.vmware.guest = {
      enable = true;
      headless = true;
    };

    # VMware's NAT and bridged networks both hand out an address; nothing
    # about it is fixed.
    networking.useDHCP = true;
  };
}
