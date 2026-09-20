# The account of a NixOS host that boots itself: the one its inventory entry
# names, read from what modules/host/nixos.nix tells the host about itself,
# so no host is named here. The NixOS-WSL account is not this one — its UID
# is a fact about WSL's shared cgroups and stays in modules/wsl.nix.
#
# The account is created without a password. `users.mutableUsers` stays at
# its default, so the installing step sets one with `passwd` and every later
# activation keeps it; until then the account is locked, and sshd takes a key
# only (modules/sshd.nix). sudo asks for that password: with sshd reachable,
# a passwordless wheel would make any accepted key equal to root. The login
# shell is modules/shell/headless.nix.
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
}
