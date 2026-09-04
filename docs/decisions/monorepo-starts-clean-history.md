# The monorepo starts a clean history

date: 2026-08-11
scope: repository
status: accepted
source: 9f1e8ce:docs/status.md § Initial monorepo convergence
source: 9f1e8ce:docs/status.md § History boundary

The repository originally converged four projects into one flake-composed
configuration model. The dendritic Unix-like structure remains useful:
flake-parts evaluates feature files collected by import-tree, deferred module
classes merge feature contributions, and one composition module assigns those
fragments to Unix-like hosts.

Content and findings came from:

- `nix-wsl`: dendritic Unix-like structure, verification boundaries, and WSL
  findings;
- `term-config`: WezTerm behavior that was initially shared across platforms;
- `win-env`: Windows drift detection, backup, safe Apply, and reconciliation;
- `nix-config`: Darwin setting values, without preserving its prototype wiring.

`win-env` reconciliation semantics remain in the Windows domain. The
cross-domain flake composition introduced during convergence was removed when
Windows desired state became directly owned under `windows/desired/`.

This monorepo started a clean history because convergence changed ownership and
composition rather than merely moving four directory trees. The initial source
revisions were:

- `term-config` `master`: `9282d19`
- `win-env` `master`: `dc5d27d` (`v0.1.0`)
- `win-env` `dev`: `64f0b90`
- `win-env` local `draft`: `dd13282`
- `nix-wsl` `dev`: `1875f8f`
- `nix-config` `master`: `84c05c2`
- `nix-config` remote `darwin`: `5f94d5d`

These identifiers are provenance, not Git parents. The old repository-wide
`vYYYY.MM.DD` release convention is superseded by domain-prefixed tags.
