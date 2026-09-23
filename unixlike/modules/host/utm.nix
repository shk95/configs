# What is true of a NixOS guest under UTM, of the QEMU `virt` machine and of
# no particular disk. Nothing detected on a machine is stored here or in the
# inventory — no UUID, no MAC address, no generated
# `hardware-configuration.nix`: the module list is a fact about the
# hypervisor's machine type, which is a kind, and the file systems are named
# by the labels the installing step creates them under (CONTRIBUTING.md).
#
# The serial console reaches the guest before the network does, even when its
# graphical session cannot render. `virt` wires its first serial port as a
# PL011, `ttyAMA0`;
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

    # UTM's VirGL display runs Niri, but GTK cannot give Ghostty an EGL
    # configuration there. Keep software GL local to the UTM guest so
    # other graphical hosts still use their GPU for Ghostty.
    home-manager.users.${config.host.user} = {
      lib,
      pkgs,
      ...
    }: {
      programs.ghostty.package = pkgs.symlinkJoin {
        name = "ghostty-utm-software";
        paths = [pkgs.ghostty];
        nativeBuildInputs = [pkgs.makeWrapper];
        meta.mainProgram = "ghostty";
        postBuild = ''
          wrapProgram "$out/bin/ghostty" --set LIBGL_ALWAYS_SOFTWARE 1
        '';
      };
      configs.niri.repeatDelayMs = 150;

      # After a headless rollback, the still-running user bus could not
      # activate dconf on the immediate graphical re-switch. Refresh its
      # service list before Home Manager applies dconf settings.
      home.activation.reloadDconfServices = lib.hm.dag.entryBefore ["dconfSettings"] ''
        if [[ -v DBUS_SESSION_BUS_ADDRESS ]]; then
          ${pkgs.systemd}/bin/busctl --user call \
            org.freedesktop.DBus /org/freedesktop/DBus \
            org.freedesktop.DBus ReloadConfig
        fi
      '';

      # The same rollback can leave DISPLAY=:0 in the user manager after the
      # Xwayland server stops. Home Manager's Xresources hook checks only that
      # DISPLAY is set, so clear it when the server cannot be reached.
      home.activation.discardStaleXDisplay = lib.hm.dag.entryBefore ["onFilesChange"] ''
        if [[ -v DISPLAY ]] && ! ${pkgs.xrdb}/bin/xrdb -query >/dev/null 2>&1; then
          unset DISPLAY
        fi
      '';
    };

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
