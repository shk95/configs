# Non-secret repository inventory. Pure flake evaluation needs these values in
# tracked source; usernames and host names are desired-state identifiers, not
# credentials. The typed contract is declared separately in `identity.nix`.
_: {
  identity = {
    gitName = "shk";
    gitEmail = "101378576+shk95@users.noreply.github.com";
    wsl = {
      user = "user1";
    };
    nixosHosts = {
      nixos = {
        system = "x86_64-linux";
        kind = "wsl";
        user = "user1";
        stateVersion = "26.05";
      };

      # Composed from modules/host/utm.nix and the headless class. The state
      # version is the release the guest was installed with, 25.11, read on
      # the installed system on 2026-09-20; it is not the pinned nixpkgs'.
      utm = {
        system = "aarch64-linux";
        kind = "vm";
        hypervisor = "utm";
        user = "shk";
        stateVersion = "25.11";
      };

      # Declared and not yet installed (modules/host/placeholder.nix). Each
      # state version is the pinned nixpkgs release, which the order that
      # installs the host confirms or corrects before anything is activated.
      vm = {
        system = "x86_64-linux";
        kind = "vm";
        hypervisor = "vmware";
        user = "user1";
        stateVersion = "26.11";
      };
      orbstack = {
        system = "aarch64-linux";
        kind = "orbstack";
        user = "shk";
        stateVersion = "26.11";
      };
      desktop = {
        system = "x86_64-linux";
        kind = "desktop";
        user = "user1";
        stateVersion = "26.11";
      };
    };
    darwin = {
      user = "shk";
      hostName = "shk-macbook";
      system = "aarch64-darwin";
    };
  };
}
