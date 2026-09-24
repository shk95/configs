# Declarative layouts for hosts that boot from their own disk. The device is
# deliberately unusable until unixlike/tool/install-plan writes a reviewed,
# throwaway wrapper flake with one explicit /dev/disk/by-id target.
#
# Disko owns formatting and the disposable install test. Runtime mounts remain
# explicit below so existing guests keep their label-based paths and adopting
# the module cannot silently reinterpret an already installed disk.
{
  inputs,
  lib,
  ...
}: let
  installTarget = lib.mkDefault "/dev/disk/by-id/INSTALL_TARGET_REQUIRED";
  portableInstallTest = test:
    test.extend {
      modules = [
        {
          # The generated QEMU command already tries KVM before TCG. Dropping
          # only the scheduler requirement lets the same test run where nested
          # KVM is unavailable. Two installer CPUs keep that fallback useful.
          requiredFeatures.kvm = false;
          nodes.machine.virtualisation = {
            cores = 2;
            memorySize = 2048;
          };
          globalTimeout = 1200;
        }
      ];
    };
  efiPartition = {
    size = "1G";
    type = "EF00";
    content = {
      type = "filesystem";
      format = "vfat";
      extraArgs = ["-n" "boot"];
      mountpoint = "/boot";
      mountOptions = ["umask=0077"];
    };
  };
in {
  modules.nixos.installExt4 = {config, ...}: let
    configsInstallTest = config._module.args.configsInstallTest or false;
  in {
    imports = [inputs.disko.nixosModules.disko];

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
        options = ["umask=0077"];
      };
    };

    disko = {
      enableConfig = false;
      devices.disk.main = {
        type = "disk";
        device = installTarget;
        content = {
          type = "gpt";
          partitions = {
            ESP = efiPartition;
            root = {
              size = "100%";
              content = {
                type = "filesystem";
                format = "ext4";
                extraArgs = ["-L" "nixos"];
                mountpoint = "/";
              };
            };
          };
        };
      };

      tests.extraChecks = ''
        machine.succeed("test $(hostname) = ${config.networking.hostName}")
        machine.succeed("test $(findmnt -n -o LABEL /) = nixos")
        machine.succeed("test $(findmnt -n -o LABEL /boot) = boot")
        machine.wait_for_unit("sshd.service")
        machine.succeed("grep -Fx 'PasswordAuthentication no' /etc/ssh/sshd_config")
        machine.succeed("grep -Fx 'PermitRootLogin no' /etc/ssh/sshd_config")
        machine.succeed("test -z \"$(systemctl --failed --no-legend)\"")
      '';
      tests.extraConfig = _: {
        _module.args.configsInstallTest = true;
        # The installation contract does not depend on RSA key generation.
        # Keeping one cheap host key removes several minutes from a TCG boot
        # while sshd still reads the real authentication and network policy.
        services.openssh.hostKeys = [
          {
            path = "/etc/ssh/ssh_host_ed25519_key";
            type = "ed25519";
          }
        ];
        # Disko bind-mounts the store through 9p in this test. Home Manager's
        # first-boot service asks the daemon to adjust store ownership, which
        # 9p cannot represent; its behavior is covered by the graphical
        # runtime test, so keep this installation proof scoped to the system.
        systemd.services."home-manager-${config.host.user}".enable = false;
      };
    };

    # nixos-anywhere --vm-test builds system.build.installTest directly.
    # Disko leaves the NixOS test framework's KVM scheduler requirement at its
    # default even though its QEMU command already falls back to TCG. Expose
    # the same test without that scheduling requirement so hosted runners and
    # development hosts without nested KVM can still execute it.
    system.build.installTestPortable = portableInstallTest config.system.build.installTest;

    # INV unixlike/install-target-explicit
    assertions = [
      {
        assertion =
          configsInstallTest
          || (
            !config.disko.enableConfig
            && lib.hasPrefix "/dev/disk/by-id/" config.disko.devices.disk.main.device
            && config.fileSystems."/".device == "/dev/disk/by-label/nixos"
            && config.fileSystems."/boot".device == "/dev/disk/by-label/boot"
          );
        message = "INV unixlike/install-target-explicit: an ext4 installation must retain the inert target and labelled runtime mounts";
      }
    ];
  };

  modules.nixos.installLuksBtrfs = {config, ...}: let
    configsInstallTest = config._module.args.configsInstallTest or false;
    contains = value: list: builtins.elem value list;
    mountHolds = path: subvolume:
      config.fileSystems.${path}.device
      == "/dev/mapper/cryptroot"
      && config.fileSystems.${path}.fsType == "btrfs"
      && contains "subvol=${subvolume}" config.fileSystems.${path}.options
      && contains "compress=zstd" config.fileSystems.${path}.options
      && contains "noatime" config.fileSystems.${path}.options;
  in {
    imports = [inputs.disko.nixosModules.disko];

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

    disko = {
      enableConfig = false;
      devices.disk.main = {
        type = "disk";
        device = installTarget;
        content = {
          type = "gpt";
          partitions = {
            ESP = efiPartition;
            cryptroot = {
              size = "100%";
              content = {
                type = "luks";
                name = "cryptroot";
                extraFormatArgs = ["--label" "cryptroot"];
                content = {
                  type = "btrfs";
                  extraArgs = ["-f" "-L" "nixos"];
                  subvolumes = {
                    "@" = {
                      mountpoint = "/";
                      mountOptions = ["compress=zstd" "noatime"];
                    };
                    "@home" = {
                      mountpoint = "/home";
                      mountOptions = ["compress=zstd" "noatime"];
                    };
                    "@nix" = {
                      mountpoint = "/nix";
                      mountOptions = ["compress=zstd" "noatime"];
                    };
                  };
                };
              };
            };
          };
        };
      };

      tests = {
        enableOCR = true;
        extraConfig._module.args.configsInstallTest = true;
        bootCommands = ''
          machine.wait_for_text("[Pp]assphrase for")
          machine.send_chars("disko\n")
        '';
      };
    };

    system.build.installTestPortable = portableInstallTest config.system.build.installTest;

    # INV unixlike/install-target-explicit
    # INV unixlike/amd-apu-desktop-portable-base
    assertions = [
      {
        assertion =
          configsInstallTest
          || (
            !config.disko.enableConfig
            && lib.hasPrefix "/dev/disk/by-id/" config.disko.devices.disk.main.device
            && config.boot.initrd.luks.devices.cryptroot.device == "/dev/disk/by-label/cryptroot"
            && config.boot.initrd.luks.devices.cryptroot.keyFile == null
            && mountHolds "/" "@"
            && mountHolds "/home" "@home"
            && mountHolds "/nix" "@nix"
            && config.fileSystems."/boot".device == "/dev/disk/by-label/boot"
          );
        message = "INV unixlike/install-target-explicit: an encrypted installation must retain the inert target and labelled LUKS/Btrfs runtime contract";
      }
    ];
  };
}
