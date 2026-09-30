# Default-on flake input refresh
kind: spec
date: 2026-09-26
scope: unixlike
status: approved
review-by: 2026-10-10
issue: #450

## Pickup amendment, 2026-09-30

Amended 2026-09-30: AC1-AC4 and their evidence lanes are unchanged. This
amendment makes the next tooling pickup concrete after U1's input ownership
transfer. It supersedes the older pickup owner and stage-design deferral below;
the 2026-09-28 schedule correction remains the latest schedule interpretation.
The current lane delivers this plan pair only. Its continuation owner is D
(`d_repository_docs`), assigned by the main orchestrator under issue #450.
Tool implementation needs a new assignment; this plan grants no input-refresh,
publication, scheduling or host authority.

### Reviewed input inventory

Pickup base: `86abcea4eadd1e4403ec9025eedb7009daf54886` on origin/dev.
The six independently locked direct inputs of `unixlike/flake.nix` are
`nixpkgs`, `flake-parts`, `import-tree`, `home-manager`, `nixos-wsl` and
`nix-darwin`. The latter three follow the root `nixpkgs` input. Transitive
`nixpkgs-lib` and `flake-compat` nodes are not direct selection names.
Installer inputs removed during machine-ownership transfer are not restored.
This inventory is pickup evidence, not an allowlist: a newly added independent
direct input must participate without editing the tool.

### Source and operator contract

The implementation belongs in `unixlike/tool/refresh-inputs`, with its tracked
configuration at `unixlike/flake-refresh-exclusions.json`. The existing `just up`
recipe delegates to this entry point. The tool derives the provider flake path
from its own location and explicitly passes that path to Nix; caller working
directory must not select a different flake. Runtime packaging and required
command checks stay inside Unix-like ownership. Do not add a domain-behavior
verb to repository `tool/configs`. The implementation PR documents its actual
runtime prerequisites and refuses unavailable capabilities without installing
software on the operator's host.

The exclusion file starts as `{"formatVersion":1,"exclusions":[]}`. Entries
contain an `input` name and a nonblank `reason`. Validate the format, unknown
names, duplicate names and follows aliases before publishing any lock change.
Selection is every independently locked direct input minus those exclusions,
not a fixed list or a recursive list of transitive dependencies. Preserve the
excluded input's own locked source, while allowing followed owners to change.
An excluded newly added input without an existing locked source cannot satisfy
preservation and must fail clearly without publishing a lock.

Use a Nix-derived input graph rather than parsing Nix source text. The observed
local CLI is Nix 2.34.8: `nix flake metadata --json` exposes the lock graph, and
`nix flake update` accepts explicit input names, `--flake`,
`--reference-lock-file` and `--output-lock-file`. A zero-name update means
update-all, so empty selection must return before invoking update. The worker
must prove the chosen graph-discovery and temporary-output sequence with the
actual supported CLI, including newly introduced inputs and follows aliases;
this plan does not treat help output as implementation proof.

### Write and failure contract

Snapshot the original lock and relevant source/configuration before work.
Generate a candidate lock at a temporary path, validate the graph and excluded
sources, and verify the original lock/source/configuration have not changed
before publication. Reject a stale candidate. Serialize cooperating refreshes
and replace the original lock atomically only after all checks pass. An
unchanged candidate preserves original bytes; an empty selection invokes no
update. Every failed operation before publication leaves the original intact
and cleans up its own temporary output. A fixture must demonstrate stale-input
rejection and failures in update and validation. Do not promise filesystem
compare-and-swap against arbitrary noncooperating writers; stop and replan if
the implementation cannot meet AC3 at its publication boundary.

The only repository file the running tool may change is
`unixlike/flake.lock`. Nix store/cache or network activity is a separate runtime
effect, not permission to change another source file. Fixtures compare all
fixture repository source files before and after success, no-op and failure,
and prove no commit, tag, push or deployment occurs. They use disposable local
flake sources and controlled upstream changes, not private host locks or real
provider input refreshes.

### Implementation pickup and evidence

The next assigned worker pins fresh origin/dev and the reviewed revision of
this pair in a new dedicated worktree. One coherent Unix-like PR owns the tool,
initially empty exclusion configuration, `Justfile` delegation, runtime
packaging/documentation and deterministic fixtures. The same PR can prove
current provider input wiring read-only; a separate wiring PR is not required.
An actual first update of the provider lock is not an implementation acceptance
condition and requires explicitly assigned refresh scope. Keep source and lock
change auditing intact if such a later refresh is authorized.

Required evaluation fixtures cover: all direct inputs and a newly added input;
one excluded input; a followed owner changing while the excluded dependent's
own source stays fixed; unknown/duplicate/alias exclusions; invalid config;
all-excluded selection; unchanged upstreams; failed update; rejected candidate;
stale original; and lock-only writes. Both success and refusal cases must be
real CLI executions where the claim concerns Nix behavior. Review evidence
names the actual input graph, configuration, command/runtime prerequisites and
write boundary. Register fixtures and any resulting invariant honestly under
the owning scope; this work spec is not a durable policy source.

Dependencies: no release controller, credentials, schedule or private-host
activation. The repository scheduler consumes the delivered tool later under
its own work item; it does not change this tool's source authority. Stop and
return to planning for overridden follows, another repository's locks,
deployment, additional writes, or a changed AC/evidence lane. Compatibility
baselines remain provider-owned and unchanged by input refresh.

CLI references: [Nix flake update](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-update.html),
[Nix flake metadata](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-metadata.html)
and [flake inputs and locks](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake.html).
These are the upstream 2.34-series reference; pickup evidence above identifies
the installed 2.34.8 CLI separately.

## Current pickup interpretation

Reconciled 2026-09-28: the tool's AC1-AC4 remain unchanged; refresh selection and
atomic lock-file writes require no schedule, credential, host adoption or release
controller implementation. Earlier stage-design deferral is historical. A worker
may implement deterministic tool fixtures independently once assigned, but final
provider input wiring must reflect U1's machine-ownership transfer rather than
preserve removed installer/adapter inputs. Fresh dev and reviewed-plan pickup still
apply; no worker is assigned by this document. The repository scheduler alone owns
the accepted 05:00 KST daily opportunity (06:00 promotion, 07:00 wait cutoff).
The older 08:00 note below is superseded. No personal host lock is refreshed.

Amended 2026-09-28 (later schedule correction): the daily cycle now uses
05:00 Asia/Seoul refresh (20:00 UTC on the preceding day), 06:00 promotion and
fixed 07:00 cutoff. This supersedes earlier clock times. Follow the provider
release spec's later operating agreement for takeover, candidate identity,
recovery, delayed/missed runs and failure fixtures. Missed-run alerts are detected
upon returning execution; no separate watchdog is required.

Amended 2026-09-27: AC1-AC4 retain their original acceptance text, but pickup
is deferred until stages 2 and 3 of
`docs/work/repository/provider-release-contract/study.md` are completed.
This draft is a stage-3 input. Default-on input updates with opt out remain
agreed; they are unrelated to Windows feature opt in. The central stateVersion
baseline is not changed by this updater. Reconcile implementation details with
the adopted release contract before worker assignment.

Planning clarification 2026-09-28: the repository scheduler now runs daily at
08:00 Asia/Seoul before the daily promotion opportunity, replacing the earlier
twelve-hour direction. This tool owns no schedule or Git admission; AC1-AC4
remain unchanged. The updater preserves provider-owned compatibility baselines
and private host locks. Review the provider input set after machine-realization
ownership changes before implementation; host installer/adapter inputs must not
remain here merely to keep the former refresh inventory.

Refresh every independently locked direct input of unixlike/flake.nix by
default. A tracked Unix-like configuration lists only excluded input names
and reasons; initially it is empty. New inputs participate automatically.
The refresh writes only unixlike/flake.lock.

An exclusion preserves the input's own locked source. Dependencies expressed
with follows still follow their owner: excluding home-manager does not freeze
its followed nixpkgs. Validate unknown names, duplicates and alias exclusions
before writing. Verify excluded sources remain unchanged. An empty selection
is a no-op, never a command that updates everything. Failed refreshes leave
the original lock intact.

## Pickup lane

Outcome: a Unix-like refresh tool, exclusion configuration, scope-owned
documentation and deterministic local fixture flakes. Scope: unixlike.
Inputs: current origin/dev, reviewed spec and current Nix CLI. Dependencies:
none. PR boundary: one tooling PR without a dependency lock refresh.
Verification: local fixture evaluation for default selection, newly added
inputs, exclusions, follows, empty selection, no-op and failure recovery.
Continuation owner: superseded by the assigned plan owner in the 2026-09-30
amendment. A tool implementation owner is assigned separately at pickup.

Stop and replan if exclusions require overriding follows, additional
repositories are requested, or deployment is added. Private host flakes and
individual package pins are outside this provider-input refresh.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | All independently locked direct inputs, including new inputs, refresh by default; only declared exclusions are omitted. | evaluation, review |
| AC2 | Excluded sources remain unchanged; follows semantics are documented and invalid exclusions fail before writing. | evaluation, review |
| AC3 | Empty selection, unchanged upstreams and failed refreshes cannot produce partial or unintended lock changes. | evaluation |
| AC4 | The tool writes only flake.lock, never commits or deploys, and has a documented initially empty exclusion configuration. | review |
