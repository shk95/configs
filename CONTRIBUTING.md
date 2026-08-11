# Contributing

This is the shared workflow for people and tools. `AGENTS.md` contains the
stable judgement and safety contract; `README.md` contains usage.

## Prepare a clone

```sh
tool/setup
tool/setup --fix
tool/doctor.sh
```

`tool/setup` changes only the clone-local hooks setting and only with
`--fix`. `tool/doctor.sh` is read-only.

## Branch flow

```text
master (released) <- dev (integration) <- feature/<name> or fix/<name>
```

Use merge commits for completed work; do not squash or rebase published work.
Do not commit directly to `master`.

`dev` means the repository-level checks pass. `master` means the same state has
also been exercised on the affected real hosts. Promote `dev` with a release
pull request only after collecting the platform evidence required by
`docs/definition-of-done.md`.

Tag validated snapshots on `master` as `vYYYY.MM.DD`; append `.N` when more
than one snapshot is released on the same day. Keep `flake.lock` refreshes in
dedicated `chore(deps)` commits so input movement is reviewable on its own.

## Change configuration

1. Put feature-oriented declarations under `modules/`.
2. Put source payloads that are consumed by a module under `assets/`.
3. Keep host composition in `modules/flake/configurations.nix`.
4. Render the Windows consumer after any relevant source change:

   ```sh
   tool/render-windows
   ```

5. Commit the source and `windows/generated/` in the same commit.

Never fix a generated diff by editing `windows/generated/` directly.
When it conflicts, resolve the source declarations and render it again.

## Verify

```sh
tool/checks/format
tool/checks/lint
tool/checks/windows-generated
tool/checks/test
```

`tool/checks/test` evaluates every declared Unix-like configuration and builds
the configurations native to the current host when appropriate. A foreign
configuration can be evaluated but must be built or activated on a matching
host before claiming native verification.

For Windows changes, run the Pester suite and the read-only host check from
native Windows:

```powershell
Invoke-Pester .\windows\tests
.\windows\bootstrap.ps1 -Check
```

Applying configuration is not routine verification. It changes state outside
the repository and must be separately requested.

## Documentation ownership

| Location | Responsibility |
| --- | --- |
| `README.md` | Setup, outputs, and everyday use |
| `CONTRIBUTING.md` | Shared workflow |
| `AGENTS.md` | Stable judgement and safety boundaries |
| `docs/status.md` | Current state and expensive decisions |
| `docs/troubleshooting.md` | Recurring problems indexed by symptom |
| `docs/definition-of-done.md` | Platform-specific evidence requirements |
| `tool/`, hooks, CI | Executable policy |

Repository text is English because the repository is public.
