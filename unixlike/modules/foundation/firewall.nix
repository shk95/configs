# INV unixlike/headless-key-only — the assertion below is the port's half of
# the rule; tool/checks/flake-test holds both directions.
_: {
  modules.darwin.system = _: {
    networking.applicationFirewall = {
      enable = true;
      enableStealthMode = true;
      allowSigned = true;
      allowSignedApp = true;
      blockAllIncoming = false;
    };
  };

  # A host that boots itself admits the ssh port and nothing else. The port is
  # not written here: sshd opens what it listens on (modules/foundation/sshd.nix), and
  # the assertion holds the firewall to exactly that, on every interface, so a
  # service added later that opens its own port is refused until this rule is
  # changed on purpose.
  modules.nixos.headless = {
    lib,
    config,
    ...
  }: let
    firewall = config.networking.firewall;
    opens = rules:
      rules.allowedTCPPorts
      ++ rules.allowedUDPPorts
      ++ rules.allowedTCPPortRanges
      ++ rules.allowedUDPPortRanges;
  in {
    networking.firewall.enable = true;

    assertions = [
      {
        assertion =
          firewall.enable
          && firewall.allowedTCPPorts == config.services.openssh.ports
          && opens (firewall // {allowedTCPPorts = [];}) == []
          && lib.all (rules: opens rules == []) (lib.attrValues firewall.interfaces);
        message = "INV unixlike/headless-key-only: the firewall of a headless host is on and admits the ssh port and nothing else.";
      }
    ];
  };
}
