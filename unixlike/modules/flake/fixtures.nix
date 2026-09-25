# Synthetic instances exercise every provider machine kind. They are never
# deployed; real identities and final host outputs live in configs-hosts.
_: {
  identity = {
    gitName = "Example";
    gitEmail = "example@example.invalid";
    wsl.user = "example";
    nixosHosts = {
      fixture-wsl = {
        system = "x86_64-linux";
        kind = "wsl";
        user = "example";
        stateVersion = "26.05";
      };
      fixture-utm = {
        system = "aarch64-linux";
        kind = "vm";
        hypervisor = "utm";
        user = "example";
        stateVersion = "25.11";
      };
      fixture-orbstack = {
        system = "aarch64-linux";
        kind = "orbstack";
        user = "example";
        stateVersion = "25.11";
      };
      fixture-vm = {
        system = "x86_64-linux";
        kind = "vm";
        hypervisor = "vmware";
        user = "example";
        stateVersion = "26.05";
      };
      fixture-desktop = {
        system = "x86_64-linux";
        kind = "desktop";
        user = "example";
        stateVersion = "26.11";
      };
    };
    darwin = {
      user = "example";
      hostName = "fixture-mac";
      system = "aarch64-darwin";
    };
  };

  hostSelections.nixos = {
    fixture-wsl.profiles = ["agents"];
    fixture-utm.profiles = [];
    fixture-orbstack.profiles = [];
    fixture-vm.profiles = [];
    fixture-desktop.profiles = [];
  };
}
