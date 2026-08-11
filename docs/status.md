# Status and decisions

## Three-domain direction

The repository now treats `unixlike`, `windows`, and `common` as independent
configuration domains. This supersedes the initial goal of using the flake as
the composition authority for native Windows.

The decision is driven by the evaluation boundary: Linux and macOS can consume
Nix configuration directly, while Windows previously depended on a Unix-like
host to render its committed desired state. That dependency forced platform
differences into shared modules, made Windows compatibility a foreign-host
concern, and coupled otherwise independent development and release work.

The durable direction is:

- the flake remains authoritative for Unix-like hosts;
- Windows owns a native source manifest, payloads, tests, and deployment flow;
- common material exists only inside an explicit `common/` domain;
- common is exceptional, independently versioned, and never deployed directly;
- platforms adopt common work asynchronously, preferably by copying it and
  taking local ownership;
- similar platform implementations may diverge without creating drift debt.

The complete model is in `docs/architecture.md`.

## Windows authority split

The Windows domain is independent:

- `windows/desired/manifest.json` is its single source manifest.
- `windows/desired/files/` contains Windows-owned payloads.
- PowerShell reads and hashes that desired-state tree directly.
- Native desired-state validation, Pester, and `bootstrap.ps1 -Check` provide
  Windows evidence.
- Nix has no Windows options, package output, renderer, or generated consumer.
- Unix-like and Windows WezTerm and Zellij payloads are independent copies and
  may diverge.
- Hooks and CI no longer make a Windows artifact depend on Unix-like evaluation.

No explicit `common/` component has yet been justified or created.

The Unix-like Zellij keymap was adopted by copying the Windows implementation.
The copies intentionally differ in platform-owned shell and session values and
have no synchronization dependency. Promotion to `common` remains deferred
until both implementations demonstrate stable semantics across independent
version and validation cycles.

## Versioning and deployment decision

The repository retains `dev` and `master` for shared source integration, but a
branch no longer represents simultaneous deployment readiness for all domains.
Releases are identified independently:

- `unixlike-vYYYY.MM.DD[.N]`;
- `windows-vYYYY.MM.DD[.N]`;
- `common-vYYYY.MM.DD[.N]`.

Unix-like activation and Windows Apply consume their respective domain
releases. A common release deploys nowhere and is adopted later by a separate
consumer change. A tag certifies only its domain, even when unrelated domain
history exists at the same commit.

## Initial monorepo convergence

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

## History boundary

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

## Verification observed during initial convergence

- The standalone WSL Home Manager activation derivation evaluates.
- The NixOS-WSL system derivation evaluates.
- The nix-darwin system derivation evaluates for `aarch64-darwin`.
- The former Windows bundle built and its JSON/Lua payload was checked in the
  derivation before the authority split.
- No Unix-like configuration was activated.
- No native-Windows Apply was performed; native Pester and `-Check` remain
  required evidence for Windows runtime behavior.

These observations are historical evidence, not certification under the new
domain release model.

## Import-order caveat

Auto-imported deferred Unix-like modules do not preserve the former hand-written
import order. List-valued options can therefore produce different store hashes
even when their element set is unchanged. Features whose list order carries
meaning must use explicit ordering or a keyed attribute model instead of
relying on file collection order.
