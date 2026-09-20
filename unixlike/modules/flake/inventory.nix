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

      # Composed (modules/host/utm.nix and the headless class) and not yet
      # installed. The account and the state version stay provisional: the
      # installing session confirms or corrects both before anything is
      # activated, and the state version is the release of the installation
      # medium's NixOS, not of the pinned nixpkgs if the two differ.
      utm = {
        system = "aarch64-linux";
        kind = "vm";
        hypervisor = "utm";
        user = "shk";
        stateVersion = "26.11";
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
