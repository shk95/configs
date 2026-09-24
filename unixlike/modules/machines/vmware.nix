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
  modules.nixos.vmware = {config, ...}: {
    # The graphical guest uses nixpkgs' full open-vm-tools integration. This
    # adds the vmblock mount and user wrapper used for desktop integration;
    # the shared graphical class still owns the session itself.
    virtualisation.vmware.guest = {
      enable = true;
      headless = false;
    };

    # VMware's NAT and bridged networks both hand out an address; nothing
    # about it is fixed.
    networking.useDHCP = true;

    home-manager.users.${config.host.user} = {
      lib,
      pkgs,
      ...
    }: {
      # A headless rollback removes dconf's service while the user bus can
      # remain alive. Refresh it before applying the graphical home again.
      home.activation.reloadDconfServices = lib.hm.dag.entryBefore ["dconfSettings"] ''
        if [[ -v DBUS_SESSION_BUS_ADDRESS ]]; then
          ${pkgs.systemd}/bin/busctl --user call \
            org.freedesktop.DBus /org/freedesktop/DBus \
            org.freedesktop.DBus ReloadConfig
        fi
      '';

      # The stopped Xwayland session can also leave an obsolete DISPLAY in
      # the user manager. Do not send Xresources to an unreachable server.
      home.activation.discardStaleXDisplay = lib.hm.dag.entryBefore ["onFilesChange"] ''
        if [[ -v DISPLAY ]] && ! ${pkgs.xrdb}/bin/xrdb -query >/dev/null 2>&1; then
          unset DISPLAY
        fi
      '';
    };

    # INV unixlike/graphical-guests-keep-recovery
    assertions = [
      {
        assertion =
          config.virtualisation.vmware.guest.enable
          && !config.virtualisation.vmware.guest.headless
          && (config.virtualisation.vmware.guest.package.pname or "") == "open-vm-tools"
          && config.programs.niri.enable
          && config.services.greetd.enable
          && config.services.pipewire.enable
          && config.services.openssh.enable
          && config.networking.firewall.allowedTCPPorts == [22];
        message = "INV unixlike/graphical-guests-keep-recovery: the VMware guest must retain full hypervisor integration, the graphical profile and key-only recovery";
      }
    ];
  };
}
