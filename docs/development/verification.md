# Verify and integrate a change

## Development feedback before a commit

Choose the source state and effect, then use existing checks. Continuing work
does not need workflow initialization, a clean checkout or commit permission.

| Source/task | Development feedback | Final boundary |
| --- | --- | --- |
| Repository prose | Review the changed text and applicable document/global scans. For a new work pair, `tool/configs work --working-tree docs/work/<scope>/<slug>` checks that pair, including untracked files. | Default global scans read the index; their success does not verify unstaged prose. No artificial behavior suite is needed for explanatory corrections. |
| Unix-like payload | Run `unixlike/tool/checks/payloads` and the fixture for the affected behavior. | These read the working tree. Run the provider suite for a final implementation result; consumer build/runtime stays separate. |
| Unix-like Nix behavior | Run `unixlike/tool/checks/format`, `lint` and the affected fixture under the same checks directory. | The final provider suite is `unixlike/tool/checks/test`. |
| Windows behavior | Use the native `windows/win-env.ps1 validate` and `test` verbs; use read-only `check` for relevant host observations. | A foreign host leaves native evidence unavailable. Setup installs tools; Apply is a separate requested deployment. |
| Staged-only delivery | Stage only authorized source, inspect `git diff --cached`, and run the applicable index scans listed below; use `tool/configs work --staged` for work records. | Do not commit to make workflow check available. On a later authorized commit, the hook runs selected quick domain checks against an index snapshot, preserving unstaged work. Working-tree parser evidence must be labeled separately. |
| Clean committed candidate | Use workflow check, or workflow merge when integration is requested, with reviewed full base/head SHA. | These alternatives run selected final suites and bind evidence to the candidate. Plan is optional inspection. |

The index scans are `tool/configs hygiene`, `invariants`, `provisional`,
`domain-reads`, `design-citations`, `records` and `work --staged`; select those
applicable to the requested feedback. They do not run native parsers. The
commit hook runs its required global scans once; do not repeat successful
checks merely to reproduce its checklist. Final candidate verification still
has its own exact-source subject.

## Local verification and integration

Record the reviewed full master/base and candidate SHA. Commit only when
authorized. On the exact clean topic checkout, run:

```sh
# Verify only, without integration:
tool/configs workflow check --base <full-master-SHA> --head <full-candidate-SHA>
# Or, when integration is authorized, verify and merge in one operation:
tool/configs workflow merge --base <full-master-SHA> --head <full-candidate-SHA>
```

These are alternatives; running check before merge repeats verification.
To inspect the same selected command sequence without executing checks, use
`tool/configs workflow plan --base <full-master-SHA> --head <full-candidate-SHA>`.
Plan requires the same clean committed candidate, reports `not-run` commands,
source subjects and known native/hosted blockers, and queries no hosted proof.
It is optional, provides no verification/readiness/authorization evidence and
is rebuilt by check; no saved plan is accepted as proof. Global scans remain
local when `--ci-run` supplies suites. Dirty source uses narrow development
checks instead of this exact-candidate operation.

The staged quick checks materialize the index once and execute the staged
checker implementations there. They exclude unstaged and untracked content
and leave the caller's worktree/index intact. This applies only to the selected
quick checks; it does not turn a hook pass into final suite or native runtime
evidence.

Merge requires authorization covering the commit-producing integration. Existing
authorization for that operation remains valid within the agreed task. It runs the
checks itself, requires the candidate to contain the selected current master,
and creates a no-ff merge with those exact first and second parents. It uses
an existing master checkout or switches the chosen checkout back to master.
A dirty checkout, missing evidence, conflict or changed base stops integration;
reflect the new master in the topic, resolve there and verify again. No helper
resets, force-pushes or discards work. An interrupted Git merge is preserved
for inspection and normal explicit recovery.

For direct master work, run the same check command against the pre-change
master SHA and exact committed HEAD before publication. Pre-commit supplies
quick staged checks; full suites are selected by tracked dispatch. `workflow
check` refuses unavailable selected checks instead of calling them passed.
Foreign native evidence may require the native Windows clone or hosted CI;
record that boundary and do not claim a successful local integration check.

Source preparation may stop staged when requested. Commit, topic merge, push,
publication and activation are distinct operations: obtain authorization for
those requested, and reuse it within the agreed scope rather than asking again
at every step. Workspace selection supplies none of those authorizations.
Ordinary push
rejection preserves local work; inspect and reconcile, never retry with force.
`tool/configs commit` supports master and topics, commits only after confirmation,
and never publishes or prunes. Its `--dry-run` writes nothing; retired
`--publish`, `prune` and dev promotion invocations refuse.

Domain releases retain immutable annotated tags reachable from master.
`tool/configs plan-release` prints an evidence template and `tool/configs audit`
validates it. Report evaluation, build and native runtime separately, per host
for Windows and at provider/domain level for Unix-like/common. Review labels
and references for private machine/account identity before tag creation.
Tags and tag pushes require explicit requests. No GitHub Release or host
activation/Apply is implied.

## Verify

Run checks in proportion to the affected domain.

For Unix-like changes:

```sh
unixlike/tool/checks/format
unixlike/tool/checks/lint
unixlike/tool/checks/test
```

`unixlike/tool/checks/test` is the complete provider suite used by local
verification and CI. It checks the public constructor contract, native-module
extensions, an independently locked synthetic consumer, payloads, provider
scripts, evaluation coverage and import-order independence. Run an individual
fixture while working on its implementation; run the suite on the final result.

Every synthetic configuration is evaluated to its toplevel derivation. Host
closures and VM sessions are not built by default. Flake checks realize focused
provider-owned source transformations such as carried patches, plus native parser validation of generated
Niri and Noctalia configuration files. Host reproductions run in the consumer and are not provider release
qualification. Real host builds and runtime belong to the
consumer. The public configs-host-template is checked on its own source and pin;
provider verification does not fetch a moving template or private consumer.

Payload parsers use the provider's locked Nix input. Evaluation does not cover
payload syntax because Nix copies these files without reading them.

For Windows changes, use [Windows changes](../../CONTRIBUTING.md#windows-changes).
Unix-like Nix evaluation is not part of Windows verification.

For common changes, run the checks owned by that common component. Do not make
Unix-like and Windows deployments prerequisites for a common release. Consumer
adoption validates integration later in the consuming domain.

For repository-governance changes, run the version-control fixture tests and
only the domain checks whose dispatch or enforcement behavior changed. Secret
scanning remains repository-wide. A governance change does not receive a
domain tag.

`tool/version-control/invariants` checks the invariant registry in both
directions and runs on every commit beside the hygiene scan, whatever the
scope of the change, because a renamed fixture in any scope can orphan the tag
an entry depends on.

```sh
tool/configs test
tool/configs invariants
tool/configs provisional
tool/configs domain-reads
tool/configs design-citations
tool/configs records
tool/configs audit
tool/configs audit-remote  # for a requested remote inspection
tool/configs hook-evidence
```

Push runs bounded `audit --range <base> <tip>` for transmitted commits and
`audit --tag <name>` for a transmitted release tag. It does not rerun native
suites from the current checkout. Final candidate verification precedes local
integration; master-push, optional PR and candidate-dispatch CI report their
actual tested source independently.

The full audit and `audit --history` remain explicit diagnostics for clone
and integration history. The history diagnostic uses fetched remote snapshots
when available; it is not proof of the current local candidate. Release
planning uses selected local master. Refresh snapshots explicitly for remote
operations. An unrelated local tag is not part of a branch push check.
