# The NixOS hosts that are declared and not yet installed. Each class is the
# least that evaluates to a system for its kind, so that every combination
# the typed inventory accepts is a real output the evaluation check reaches.
# None of them has been built, booted or installed: a placeholder is
# evaluation evidence and nothing more, and the order of docs/work/roadmap.md
# that installs a host replaces its class here with files of its own.
#
# A host that boots from a disk is given systemd-boot and two file systems
# named by label. The labels are the convention the installing order creates
# the partitions under, not a description of a disk: hardware detection is
# never stored in the inventory or here. A placeholder creates no account
# either: the entry's user is only the name modules/nix/shared.nix trusts,
# until the installing order declares the account.
#
# INV unixlike/nixos-host-inventory
_: let
  bootsFromLabelledDisk = {
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
  };
in {
  modules.nixos = {
    vmware = {
      imports = [bootsFromLabelledDisk];
      virtualisation.vmware.guest.enable = true;
    };

    utm = {
      imports = [bootsFromLabelledDisk];
      services.qemuGuest.enable = true;
    };

    # An OrbStack machine is a container: the host supplies the kernel and
    # there is no boot loader or disk to declare, as on WSL.
    orbstack = {modulesPath, ...}: {
      imports = ["${modulesPath}/virtualisation/lxc-container.nix"];
    };

    # Nothing of its own yet: what the machine is made of is the installing
    # order's to declare.
    desktop = {
      imports = [bootsFromLabelledDisk];
    };
  };
}
