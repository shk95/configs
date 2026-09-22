# The physical desktop's portable machine contract. The installation class
# owns its UEFI, labelled LUKS and Btrfs layout; this class keeps the physical
# host's swap and network choices and asserts the combined result.
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
