# Systems that build repository tooling or host configurations. Windows is a
# target bundle, not a Nix build platform; it is rendered on the Unix-like
# development hosts listed here and consumed without Nix on Windows.
_: {
  systems = [
    "x86_64-linux"
    "aarch64-darwin"
  ];
}
