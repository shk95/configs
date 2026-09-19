# The identity contract and its values are separate

date: 2026-08-12
scope: unixlike
status: accepted
source: 9f1e8ce:docs/status.md § Unix-like Home Manager and package ownership

The typed identity contract and its values are separate. `identity.nix`
declares the flake-parts options, while `inventory.nix` contains the
tracked, non-secret usernames, Git identity, host name, and target system
needed for pure and reproducible flake outputs. Moving those values to
environment variables would require impure evaluation and would make output
names depend on the invoking shell.
