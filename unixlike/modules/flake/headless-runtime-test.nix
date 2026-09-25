{
  config,
  lib,
  ...
}: let
  vmHost = config.identity.nixosHosts.fixture-vm;
  testUser = vmHost.user;
in {
  perSystem = {
    pkgs,
    system,
    ...
  }:
    lib.optionalAttrs (system == vmHost.system) {
      # INV unixlike/headless-key-only — the evaluation fixture holds the
      # declaration and every refusal. This VM test boots the same headless
      # class and exercises its account, ssh daemon and firewall together.
      checks.headless-runtime = pkgs.testers.runNixOSTest {
        name = "configs-headless-runtime";

        # Hosted runners do not promise nested KVM. QEMU still uses KVM when
        # it is available and falls back to TCG when it is not.
        requiredFeatures.kvm = false;

        nodes.server = {pkgs, ...}: {
          imports = [
            config.modules.nixos.shared
            config.modules.nixos.headless
          ];

          host = vmHost // {name = "fixture-vm";};

          # Neither DHCP nor an RSA host key is part of this fixture's
          # contract. Avoid their timeouts and key generation cost so a TCG
          # boot keeps enough margin below the driver's connection timeout.
          networking.useDHCP = false;
          services.openssh.hostKeys = [
            {
              path = "/etc/ssh/ssh_host_ed25519_key";
              type = "ed25519";
            }
          ];

          environment.systemPackages = [
            pkgs.iproute2
            pkgs.netcat
            pkgs.openssh
            pkgs.python3
            pkgs.sshpass
          ];
        };

        testScript = ''
          import shlex

          server.start()
          server.wait_for_unit("multi-user.target")
          server.wait_for_unit("sshd.service")

          server.succeed("getent passwd ${testUser} | cut -d: -f7 | grep -Fx /run/current-system/sw/bin/zsh")
          server.succeed("id -nG ${testUser} | tr ' ' '\\n' | grep -Fx wheel")
          server.fail("su - ${testUser} -c 'sudo -n true'")

          # Reach the server through a veth from another network namespace so
          # packets traverse the input firewall rather than the loopback path.
          server.succeed("ip netns add test-client")
          server.succeed("ip link add server-veth type veth peer name client-veth")
          server.succeed("ip address add 192.0.2.1/24 dev server-veth")
          server.succeed("ip link set server-veth up")
          server.succeed("ip link set client-veth netns test-client")
          server.succeed("ip netns exec test-client ip address add 192.0.2.2/24 dev client-veth")
          server.succeed("ip netns exec test-client ip link set lo up")
          server.succeed("ip netns exec test-client ip link set client-veth up")

          # Keys and the password are written only into this disposable VM,
          # matching the host-owned state an installation creates.
          server.succeed('ssh-keygen -q -t ed25519 -N "" -f /tmp/test-key')
          public_key = server.succeed("cat /tmp/test-key.pub").strip()
          quoted_key = shlex.quote(public_key)
          server.succeed("install -d -m 700 -o ${testUser} -g users /home/${testUser}/.ssh")
          server.succeed(f"printf '%s\\n' {quoted_key} > /home/${testUser}/.ssh/authorized_keys")
          server.succeed("chown ${testUser}:users /home/${testUser}/.ssh/authorized_keys && chmod 600 /home/${testUser}/.ssh/authorized_keys")
          server.succeed("printf '%s:%s\\n' ${testUser} test-password | chpasswd")

          ssh_options = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5"
          # Nested KVM can leave `ip netns exec` waiting after sshd has closed
          # a successful session. The remote marker proves that the key ran a
          # command; the timeout bounds cleanup of the namespace wrapper.
          server.succeed(f"timeout --kill-after=5s 60s ip netns exec test-client ssh {ssh_options} -i /tmp/test-key ${testUser}@192.0.2.1 'touch /tmp/key-login-ok' || test -e /tmp/key-login-ok")
          server.succeed("test -e /tmp/key-login-ok")
          server.fail(f"ip netns exec test-client sshpass -p test-password ssh {ssh_options} -o PubkeyAuthentication=no -o PreferredAuthentications=password -o NumberOfPasswordPrompts=1 ${testUser}@192.0.2.1 true")

          server.succeed("install -d -m 700 /root/.ssh")
          server.succeed(f"printf '%s\\n' {quoted_key} > /root/.ssh/authorized_keys")
          server.succeed("chmod 600 /root/.ssh/authorized_keys")
          server.fail(f"ip netns exec test-client ssh {ssh_options} -i /tmp/test-key root@192.0.2.1 true")

          server.succeed("systemd-run --unit blocked-probe --service-type=simple python -m http.server 8080 --bind 0.0.0.0")
          server.wait_for_open_port(8080)
          server.fail("ip netns exec test-client nc -z -w 2 192.0.2.1 8080")
        '';
      };
    };
}
