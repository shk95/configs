# Contributing

This is the workflow for people and tools. `AGENTS.md` contains stable
judgement and safety rules, `docs/architecture.md` defines domain ownership,
and `README.md` contains usage.

## Prepare a clone

```sh
tool/setup
tool/setup --fix
tool/doctor.sh
```

`tool/setup` changes only the clone-local hooks setting and only with `--fix`.
`tool/doctor.sh` is read-only. A missing foreign-platform capability does not
block work confined to another domain.

## Classify the change

Every change belongs to one of these scopes:

- `unixlike`: Nix, Home Manager, NixOS, WSL guest, or nix-darwin behavior.
- `windows`: native Windows desired state and reconciliation.
- `common`: explicitly platform-neutral material with its own contract.
- `adopt`: an explicit copy or pinned import from one domain into another.

Prefer a single scope per branch and pull request. If a common change and its
platform adoption are both needed, land them separately so neither release is
synchronously coupled to the other.

## Branch and commit flow

```text
master <- dev <- feature/<domain>-<topic> or fix/<domain>-<topic>
```

Examples are `feature/unixlike-shell`, `fix/windows-zellij`, and
`feature/common-terminal-colors`.

Use merge commits for completed work; do not squash or rebase published work.
Do not commit directly to `master`. Scope commits where practical, for example
`feat(unixlike):`, `fix(windows):`, or `chore(common):`.

`dev` means the affected domain's repository checks pass. `master` means the
source change has been accepted; it no longer means every platform at that
commit has been exercised. Native readiness is represented by domain tags and
the evidence in `docs/definition-of-done.md`.

Use independent release tags:

- `unixlike-vYYYY.MM.DD`, with `.N` for another release that day;
- `windows-vYYYY.MM.DD`, with `.N` for another release that day;
- `common-vYYYY.MM.DD`, with `.N` for another release that day.

Keep `flake.lock` refreshes in dedicated `chore(unixlike-deps)` commits. A
domain tag certifies only the named domain even though the commit may contain
accepted history from the others.

## Unix-like changes

1. Put feature-oriented declarations under `modules/`.
2. Put Unix-like source payloads in their owning Unix-like asset location.
3. Keep host composition in `modules/flake/configurations.nix`.
4. Run narrow formatting, lint, evaluation, and native build checks.
5. Create a Unix-like release tag only after the required matching-host
   evidence exists.
6. Activate only when explicitly requested, from the intended Unix-like
   release.

Do not add Windows desired state to a Nix module merely because the same tool
also runs on Windows.

## Windows changes

Windows declarations, payloads, checks, and Apply logic live inside `windows/`
and are validated on native Windows.

1. Edit `windows/desired/manifest.json` for packages and managed-file policy.
2. Edit owned payloads below `windows/desired/files/`.
3. Update PowerShell under `windows/src/` when reconciliation semantics change.
4. Run native Windows tests and read-only host verification.
5. Create a Windows release tag only after the required native evidence exists.

Native read-only verification is:

```powershell
.\windows\tools\check-desired-state.ps1
.\windows\tools\test.ps1
.\windows\bootstrap.ps1 -Check
```

The test entrypoint requires Pester 5.7.1 so local Windows and CI use the same
discovery, scope, and assertion semantics. Install that exact version once with
`Install-Module Pester -RequiredVersion 5.7.1 -Scope CurrentUser`.

Apply is a deployment, not verification, and requires an explicit request:

```powershell
.\windows\bootstrap.ps1
```

## Common changes

Do not create common material by default. First show that independently owned
Unix-like and Windows implementations have stable, genuinely platform-neutral
semantics.

When common ownership is justified:

1. Put it under `common/`, not under either platform domain.
2. Document its contract, supported consumers, and exclusions.
3. Give it consumer-independent checks.
4. Release it with a `common-v...` tag. It deploys nowhere.
5. Adopt it later through a separate Unix-like or Windows change.

Copying is the default adoption mechanism. Record provenance when useful, but
the destination owns the copy and does not owe future byte equality. A direct
import requires a pinned common version and an explicit decision explaining
why the coupling is acceptable.

## Verify

Run checks in proportion to the affected domain.

For Unix-like changes:

```sh
tool/checks/format
tool/checks/lint
tool/checks/test
```

`tool/checks/test` evaluates every declared Unix-like configuration and builds
configurations native to the current host when appropriate. Foreign evaluation
is not native build or activation evidence.

For Windows changes, run the native Windows commands above. Unix-like Nix
evaluation is not part of Windows verification.

For common changes, run the checks owned by that common component. Do not make
Unix-like and Windows deployments prerequisites for a common release. Consumer
adoption validates integration later in the consuming domain.

## Documentation ownership

| Location | Responsibility |
| --- | --- |
| `README.md` | Setup, outputs, and everyday use |
| `CONTRIBUTING.md` | Domain-scoped workflow and releases |
| `AGENTS.md` | Stable judgement and safety boundaries |
| `docs/architecture.md` | Domain authority and dependency policy |
| `docs/status.md` | Current state and expensive decisions |
| `docs/troubleshooting.md` | Recurring problems indexed by symptom |
| `docs/definition-of-done.md` | Domain-specific evidence requirements |
| `tool/`, hooks, CI | Executable policy |

Repository text is English because the repository is public.
