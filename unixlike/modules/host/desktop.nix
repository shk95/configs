# The physical desktop's portable machine contract. Labels and Btrfs
# subvolumes are values the installation procedure creates; no observed disk,
# UUID, controller or monitor fact is invented here.
#
# The LUKS device has no key file, token or crypttab option, so systemd stage 1
# asks for its passphrase. The EFI partition remains outside the container;
# root, home and the Nix store are separate subvolumes of the one encrypted
# Btrfs file system.
_: {
  modules.nixos.desktop = {config, ...}: let
    contains = value: list: builtins.elem value list;
    mountHolds = path: subvolume:
      config.fileSystems.${path}.device
      == "/dev/mapper/cryptroot"
      && config.fileSystems.${path}.fsType == "btrfs"
      && contains "subvol=${subvolume}" config.fileSystems.${path}.options
      && contains "compress=zstd" config.fileSystems.${path}.options
      && contains "noatime" config.fileSystems.${path}.options;
    luks = config.boot.initrd.luks.devices.cryptroot;
  in {
    boot = {
      loader = {
        systemd-boot.enable = true;
        efi.canTouchEfiVariables = true;
      };

      initrd.luks.devices.cryptroot.device = "/dev/disk/by-label/cryptroot";
    };

    fileSystems = {
      "/" = {
        device = "/dev/mapper/cryptroot";
        fsType = "btrfs";
        options = ["subvol=@" "compress=zstd" "noatime"];
      };
      "/home" = {
        device = "/dev/mapper/cryptroot";
        fsType = "btrfs";
        options = ["subvol=@home" "compress=zstd" "noatime"];
      };
      "/nix" = {
        device = "/dev/mapper/cryptroot";
        fsType = "btrfs";
        options = ["subvol=@nix" "compress=zstd" "noatime"];
      };
      "/boot" = {
        device = "/dev/disk/by-label/boot";
        fsType = "vfat";
        options = ["umask=0077"];
      };
    };

    # The physical host has no disk swap in desired state. The zram module's
    # defaults use one zstd-compressed device capped at half of RAM.
    swapDevices = [];
    zramSwap.enable = true;

    networking = {
      useDHCP = false;
      networkmanager.enable = true;
    };

    # INV unixlike/amd-apu-desktop-portable-base
    assertions = [
      {
        assertion =
          config.boot.loader.systemd-boot.enable
          && config.boot.loader.efi.canTouchEfiVariables
          && luks.device == "/dev/disk/by-label/cryptroot"
          && luks.keyFile == null
          && luks.crypttabExtraOpts == []
          && mountHolds "/" "@"
          && mountHolds "/home" "@home"
          && mountHolds "/nix" "@nix"
          && config.fileSystems."/boot".device == "/dev/disk/by-label/boot"
          && config.fileSystems."/boot".fsType == "vfat"
          && contains "umask=0077" config.fileSystems."/boot".options
          && config.swapDevices == []
          && config.zramSwap.enable
          && config.zramSwap.algorithm == "zstd"
          && config.zramSwap.memoryPercent == 50
          && config.networking.networkmanager.enable
          && !config.networking.useDHCP;
        message = "INV unixlike/amd-apu-desktop-portable-base: the physical desktop must retain its reviewed encrypted storage, swap and networking contract";
      }
    ];
  };
}
