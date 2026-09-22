{inputs, ...}: {
  perSystem = {system, ...}: {
    packages.nixos-anywhere = inputs.nixos-anywhere.packages.${system}.default;
  };
}
