# Default-on flake input refresh
kind: spec
date: 2026-09-26
scope: unixlike
status: approved
review-by: 2026-10-10

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
Continuation owner: the root agent after explicit Git authorization.

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
