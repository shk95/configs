# Develop a provider with a local consumer

`just dev-info` reads existing local state without connecting or initializing
a session. With no records it reports `uninitialized` and creates no directory
or lock. Existing records are read under a nonblocking shared lock; an active
writer, records without their lock, or malformed connection data refuse and
preserve the files. Git status observations suppress index refresh. Info runs
neither Nix nor the consumer adapter, and reports observations rather than
runtime readiness or permission to apply/promote.

Mutators retain their exclusive lock and explicitly initialize local records.
`dev-promote --plan` still writes its requested local plan; it is a different
effect boundary from info.

This Unix-like tool connects the current provider checkout to an explicitly
selected consumer checkout. Connections, actual host names, local publication
commands, source snapshots and receipts live in this checkout's Git directory
(`git rev-parse --absolute-git-dir`, then `configs-dev/`). They are never flake
inputs, tracked provider configuration or a prerequisite for provider CI.
Python 3.9+, Git, Nix with flakes and Just are required. No software is installed.

## Edit, apply and test without a release

The consumer implements protocol 1 through its own executable
`tool/configs-dev`; see the protocol below. From the provider root:

```sh
just dev-connect /path/to/consumer fixture-home
just dev-info
just dev-eval
just dev-build
just dev-apply
just dev-verify --note 'Confirmed shell startup, terminal rendering and input.'
```

The path and host above are placeholders. Select a real consumer and host
locally. `dev-apply` is an explicit host activation, not a validation alias.
It builds a frozen source pair, then asks the consumer adapter to check the
running target and activate that exact output. Development does not update
consumer pins or locks and requires no provider commit, push or release.
`dev-eval other-host` and `dev-build other-host` make a one-command selection;
reconnect to change the default. `--pinned` uses the consumer's adopted pin.

Snapshots contain tracked files and nonignored new files, including unstaged
changes. They omit ignored material and every `notes/` directory. Symlinks and
submodules are refused rather than following an external mutable dependency.
Dependencies intentionally excluded by Git need an explicit source adoption.
The consumer source is frozen as well as the provider; changing either source
invalidates application evidence. Snapshot files are checked before reuse.

`dev-verify` first checks the active generation through the consumer adapter,
then runs an optional local verification command. The required `--note` records
functional checks actually performed by the developer; it does not manufacture
runtime evidence from a successful build. A failed application invalidates the
previous receipt before activation starts. Successful verification is tied to
one host, source pair and built package.

To extract a reusable setting, edit the provider module/API and the connected
consumer together, leaving actual accounts, devices, identities and host
selection with the consumer. Use the consumer's existing experimental lane for
unpublished provider dependencies. Repeat apply and verification on that pair.
Neither connection nor any command changes branches automatically.

## Publish the tested change in one resumable operation

Prepare the source-owned release declaration *before* the final development
application, so the released provider content can match the tested source.
Configure a private recipe from a file outside tracked source:

```json
{
  "version": 1,
  "release": "unixlike-v1.2.3",
  "provider_publish": ["/path/to/provider-publication-procedure"],
  "consumer_publish": ["/path/to/consumer-publication-procedure"],
  "verify": ["/path/to/host-functional-check"]
}
```

These executable paths are placeholders, not installed commands. Set `verify`
to `[]` if functional checks are manual. Commands are argv arrays, run directly
without shell interpolation. Configure the recipe before final verification:

```sh
just dev-configure /path/to/private-recipe.json
just dev-verify --note 'Completed the functional checks for this source pair.'
just dev-promote --plan
just dev-promote --execute
```

`--plan` writes and prints only a local reviewable plan; it does not publish or
activate. `--execute` explicitly requests the listed checks, repository
publication procedures, exact release adoption and final host activation.
This command is not authority for an agent to invoke it without the user's
commit/integration/push/tag/activation authorization. That authorization can
cover the whole reviewed operation. Configuring a recipe does not execute it.

The provider publication command runs in the provider checkout and implements
its existing commit/integration, evidence, annotated tag and push procedure.
Use `tool/configs workflow check/merge`, `plan-release` and `audit` as applicable;
do not use the input-patch workflow to release ordinary development changes.
Before final application/verification, prepare the consumer's isolated accepted
candidate through its existing extraction procedure. Broad experimental-lane
exploration can use this development loop, but its unrelated files cannot be
silently removed during promotion: the tested consumer content must survive
publication unchanged, apart from the exact pin/lock adoption.

The consumer publication command runs in the consumer checkout, integrates
that already prepared host candidate and pin adoption under its existing
procedure, and publishes master. It must not promote an entire experimental
lane or edit the tested configuration during publication. Both
commands must be safe to rerun after an ambiguous or partial remote success.
This tool does not replace either repository's version-control procedures.

Commands receive `CONFIGS_DEV_PROVIDER`, `CONFIGS_DEV_CONSUMER`,
`CONFIGS_DEV_HOST`, `CONFIGS_DEV_PACKAGE`, `CONFIGS_DEV_PROVIDER_SOURCE`,
`CONFIGS_DEV_CONSUMER_SOURCE` and `CONFIGS_DEV_RELEASE`. The private scripts
use these explicit values to implement the maintainer's selected procedure.
No default script commits, pushes or tags on the maintainer's behalf.

Execution proceeds through these checkpoints:

1. Run provider checks with `just check`.
2. Run provider publication; require an audited annotated release reachable
   from master, published to origin, whose Unix-like content matches the test.
3. Ask the consumer to adopt that *exact* tag and source, never the latest tag.
   Only its `flake.nix` and `flake.lock` may change in this step.
4. Evaluate and build without the local override; require the store output to
   equal the successfully tested development package.
5. Run consumer publication; require clean source and HEAD published as master.
6. Apply from the frozen pinned consumer source, without an override.
7. Verify the active package and rerun the configured functional check.

A manual functional note still describes the tested package, which must match
exactly; the final automated generation check does not imply a new manual
runtime check. Provider checks, consumer evaluation, build, runtime and
activation remain separate evidence lanes.

Re-run `just dev-promote --execute` to resume. Completed checkpoints are not
repeated. Adoption failures preserve partial pin/lock updates and can retry;
unknown source changes stop execution. A closure mismatch stops before consumer
publication and final activation. Inspect the difference and explicitly test
the new source before planning its acceptance; equivalence is never assumed.
No failure triggers a reset, source deletion, rollback, branch deletion or tag
rewrite. An in-progress publication journal cannot be overwritten by connect,
configure, apply or disconnect. After an irreconcilable failure, inspect and
preserve the local journal and repository/remote state before manually retiring
that local operation; the tool does not infer abandonment.

`just dev-disconnect` removes the connection and its active receipts. Source
snapshots and the recipe remain private in Git metadata for inspection.

## Consumer adapter protocol 1

The consumer owns this executable and all actual deployment facts. It prints
only the documented response on stdout for `protocol` and `resolve`; diagnostics
belong on stderr. Nonzero status stops the provider operation.

| Invocation | Contract |
| --- | --- |
| `protocol` | Print `1`. |
| `resolve HOST --flake REF [--provider REF]` | Print JSON with `constructor` (`mkNixos`, `mkDarwin`, `mkHome`) and `output` (derivation attribute path). |
| `apply HOST --flake REF [--provider REF] --package PATH` | Check native host/account, resolve using the same input override, require the selected output to equal the built package, and activate it. |
| `verify HOST --flake REF [--provider REF] --package PATH` | Repeat identity/output checks and require the active generation to equal the package. |
| `adopt --release TAG --source SHA` | Validate exact published release, update the consumer pin/lock and run final consumer evaluation without overrides. Idempotent; only `flake.nix` and `flake.lock` may change. |

The provider overrides the public input named `configs`. A consumer with a
different input name needs an explicit adapter/tool contract extension.
No host list, private repository URL, account mapping or consumer internal
module path is built into the provider. Tests use synthetic consumers.

## Automated verification without accepting test configuration

Run `unixlike/tool/checks/dev-host-test` for the provider checks. In addition to
unit fixtures, two subprocess-only integration cases exercise both directions:

- Provider change to consumer: change reusable behavior, apply and verify the
  synthetic consumer, refuse stale evidence, then publish/adopt the exact pair.
- Consumer extraction to provider: first exercise consumer-owned behavior,
  move it to the provider, require an identical built output, then publish/adopt.

The integration cases use real Git, Nix evaluation/builds, annotated fixture
tags and pushes to local bare remotes. Their consumer activation and release
audit are synthetic protocol implementations; they do not certify the production
audit, private adoption adapter or a native host. A repeat promotion must not
publish twice. All candidate source and history belong to temporary repositories;
the real checkout, pins and remotes are not changed.

A consumer can provide a separate opt-in native runner. The adjacent consumer's
`tool/configs-dev-test --provider /path/to/provider --host HOST` copies both
current source trees into its private Git metadata, adds a disposable marker,
and evaluates/builds both development directions. It compares the override
build with an explicit local source pin without an override, and requires
consumer-to-provider extraction to preserve the complete system store path.
This local pin check makes no claim about a real remote release.

Its explicit `--switch` mode supports the running matching NixOS host. It
records the original active/default generation, roots the original closure,
writes a recovery script before activation, and restores and checks that
generation after each case, including failures and handled interrupts. It
checks the actual marker under `/etc` and the active generation before accepting
runtime evidence. A separate fixture suite intercepts privileged calls to test
partial activation, interruption, and failed restoration. SIGKILL or machine
failure can prevent automatic recovery; the recorded script remains available.
The runner retains private evidence and system generations for inspection and
never prunes them. Original source, index, HEAD and status must match their
initial fingerprints. Native tests are never an implicit provider CI step.
