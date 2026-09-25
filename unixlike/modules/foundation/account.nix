# The account of a NixOS host that boots itself: the one its inventory entry
# names, read from what modules/foundation/nixos.nix tells the host about itself,
# so no host is named here. The NixOS-WSL account is not this one — its UID
# is a fact about WSL's shared cgroups and stays in modules/platforms/wsl.nix.
#
# The account is created without a password. `users.mutableUsers` stays at
# its default, so the installing step sets one with `passwd` and every later
# activation keeps it; until then the account is locked, and sshd takes a key
# only (modules/foundation/sshd.nix). sudo asks for that password: with sshd reachable,
# a passwordless wheel would make any accepted key equal to root. The login
# shell is modules/foundation/shell/headless.nix.
#
# INV unixlike/headless-key-only — the assertion below is the account's half
# of the rule; tool/checks/flake-test holds both directions.
_: {
  modules.nixos.headless = {
    lib,
    config,
    ...
  }: let
    inherit (config.host) user;
    account = config.users.users.${user};
    secrets = [
      "password"
      "hashedPassword"
      "hashedPasswordFile"
      "initialPassword"
      "initialHashedPassword"
    ];
  in {
    users.users.${user} = {
      isNormalUser = true;
      extraGroups = ["wheel"];
    };

    security.sudo.wheelNeedsPassword = true;

    assertions = [
      {
        assertion = lib.all (name: account.${name} == null) secrets && config.security.sudo.wheelNeedsPassword;
        message = "INV unixlike/headless-key-only: the account of a headless host carries no password in tracked state, and sudo asks for the one the host holds.";
      }
    ];
  };

  # The account OrbStack enters a machine as. OrbStack's sessions come from
  # an agent it injects, with no authentication of their own, so the account
  # has no password to ask for: it is created locked, users are immutable —
  # OrbStack generates that and warns against the alternative — and sudo asks
  # for nothing. The UID is the one OrbStack generated, 501: it gives the
  # account the UID of the Mac account that created the machine, and 501 is
  # what macOS gives a Mac's first account. A machine created for an account
  # of another name got 501 too, so it is the UID and not the name that is
  # carried over; that it would be another number on a Mac whose account has
  # another UID is inferred, not observed, and the procedure's reading after
  # an OrbStack update is where it would show. It is also why the account is
  # a system user given the shape of a normal one: NixOS keeps normal users
  # at 1000 and above. The login shell is modules/foundation/shell/orbstack.nix.
  modules.nixos.orbstack = {config, ...}: let
    inherit (config.host) user;
  in {
    users = {
      mutableUsers = false;
      users.${user} = {
        uid = 501;
        isSystemUser = true;
        group = "users";
        extraGroups = ["wheel" "orbstack"];
        createHome = true;
        home = "/home/${user}";
        homeMode = "700";
      };
    };

    security.sudo.wheelNeedsPassword = false;
  };
}
