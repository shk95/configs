# Systems that build repository tooling or host configurations. Windows is a
# target bundle, not a Nix build platform; it is rendered on the Unix-like
# development hosts listed here and consumed without Nix on Windows.
#
# `aarch64-linux` is here for the aarch64 NixOS hosts the typed inventory
# declares. It is evaluated on the other systems and built natively or on a
# remote builder, never under emulation: binfmt_misc on a WSL distribution is
# shared by every distribution, so none is registered there.
_: {
  systems = [
    "x86_64-linux"
    "aarch64-linux"
    "aarch64-darwin"
  ];
}
