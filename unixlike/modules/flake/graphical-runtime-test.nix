{
  config,
  inputs,
  lib,
  ...
}: let
  vmHost = config.identity.nixosHosts.vm;
  testUser = vmHost.user;
  home = config.modules.homeManager;
  inherit (config.identity) gitName gitEmail;
in {
  perSystem = {
    pkgs,
    system,
    ...
  }:
    lib.optionalAttrs (system == vmHost.system) {
      checks.graphical-runtime = pkgs.testers.runNixOSTest {
        name = "configs-graphical-runtime";

        # Hosted runners may use TCG. The test boots services and validates
        # generated configuration; it does not need accelerated rendering.
        requiredFeatures.kvm = false;

        nodes.machine = {pkgs, ...}: {
          imports = [
            inputs.home-manager.nixosModules.home-manager
            config.modules.nixos.shared
            config.modules.nixos.graphical
          ];

          host = vmHost // {name = "graphical-test";};

          home-manager = {
            useGlobalPkgs = true;
            useUserPackages = true;
            users.${testUser}.imports = [
              home.shared
              home.desktop
              home.linuxGraphical
              # This runtime fixture composes classes directly rather than
              # calling a host constructor, so it supplies the same typed
              # host-owned values that a constructor normally provides.
              ({lib, ...}: {
                options.providerIdentity = {
                  user = lib.mkOption {
                    type = lib.types.str;
                    readOnly = true;
                  };
                  gitName = lib.mkOption {
                    type = lib.types.str;
                    readOnly = true;
                  };
                  gitEmail = lib.mkOption {
                    type = lib.types.str;
                    readOnly = true;
                  };
                };
                config.providerIdentity = {
                  user = testUser;
                  inherit gitName gitEmail;
                };
              })
            ];
          };

          # The serial test driver does not open a display. greetd still owns
          # tty1 and reaches its ready state without a login. Two virtual CPUs
          # keep the larger graphical closure below the driver's five-minute
          # connection limit when QEMU has to fall back to TCG.
          virtualisation = {
            cores = 2;
            memorySize = 2048;
          };
          # Networking is outside this test's contract. Avoid a DHCP wait on
          # hosted runners and on local machines without nested networking.
          networking.useDHCP = false;

          # Account, SSH and firewall integration belongs to headless-runtime.
          # This fixture supplies only the account Home Manager needs so its
          # runtime cost stays attributable to the graphical classes.
          users.users.${testUser}.isNormalUser = true;

          environment.systemPackages = [pkgs.gnugrep];
        };

        testScript = ''
          machine.start()
          machine.wait_for_unit("multi-user.target")
          machine.wait_for_unit("graphical.target")
          machine.wait_for_unit("greetd.service")

          # These services are D-Bus activated on a normal desktop. Start them
          # explicitly so this test proves their units can run.
          machine.succeed("systemctl start polkit.service udisks2.service")
          machine.wait_for_unit("polkit.service")
          machine.wait_for_unit("udisks2.service")

          machine.succeed("systemctl is-enabled greetd.service")
          machine.succeed("sed -n 's|^ExecStart=.* --config ||p' /etc/systemd/system/greetd.service | xargs grep -F -- '--cmd niri-session'")
          machine.succeed("test -x /run/current-system/sw/bin/niri")
          machine.succeed("test -r /etc/systemd/user/pipewire.service")
          machine.succeed("test -r /etc/systemd/user/wireplumber.service")
          machine.succeed("test -r /etc/systemd/user/niri.service")

          machine.succeed("su - ${testUser} -c 'test -r ~/.config/niri/config.kdl'")
          machine.succeed("su - ${testUser} -c 'niri validate -c ~/.config/niri/config.kdl'")
          machine.succeed("su - ${testUser} -c 'test -r ~/.config/noctalia/config.toml'")
          machine.succeed("su - ${testUser} -c 'noctalia config validate ~/.config/noctalia/config.toml'")
          machine.succeed("su - ${testUser} -c 'grep -F hangul ~/.config/fcitx5/profile'")
          machine.succeed("su - ${testUser} -c 'test -r ~/.config/hypr/hypridle.conf'")

          # One login shell keeps the no-KVM run cheap while still proving
          # that the installed user's PATH exposes every accepted command.
          machine.succeed("su - ${testUser} -c 'for command in brightnessctl fcitx5 firefox ghostty imv mpv noctalia pavucontrol remmina wezterm wf-recorder wl-copy wlfreerdp xwayland-satellite; do command -v \"$command\" >/dev/null || exit 1; done'")
          machine.succeed("su - ${testUser} -c 'for command in croc dig doggo duf dust gping hyperfine jc mtr nix-index nix-tree nom procs rsync sad tldr trash zoxide; do command -v \"$command\" >/dev/null || exit 1; done'")

          machine.succeed("test -z \"$(systemctl --failed --no-legend)\"")
        '';
      };
    };
}
