# Non-secret repository inventory. Pure flake evaluation needs these values in
# tracked source; usernames and host names are desired-state identifiers, not
# credentials. The typed contract is declared separately in `identity.nix`.
_: {
  identity = {
    gitName = "shk";
    gitEmail = "101378576+shk95@users.noreply.github.com";
    wsl.user = "user1";
    darwin = {
      user = "shk";
      hostName = "shk-macbook";
      system = "aarch64-darwin";
    };
  };
}
