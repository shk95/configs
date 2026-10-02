# Current state: repository

This file states what is observably true of the repository scope today: hosts and
classes in use, schema and version facts, and open conditions. Every decision
is recorded under `docs/policy/decisions/`; the model those decisions implement
is `docs/policy/architecture.md`, and the three-domain direction is
`docs/policy/architecture.md` § Decision. The other scopes' state is in the
files beside this one.

Branch protection is enabled on both `dev` and `master`: pull requests and
current-branch checks are required, administrators are enforced,
conversations must be resolved, force pushes and deletions are disabled, and
both branches require only the `Required checks` gate.

`dev` requires a pull request and an up-to-date base; `master` accepts only
`dev` through a pull request with a merge commit; squash and rebase merges
are disabled.

Source authoring now uses a task-dedicated linked worktree. The primary
checkout remains available for inspection and integration. The routine
commit helper refuses the primary checkout before editing, and the local
pre-commit hook refuses a primary-checkout commit when tracked hooks are
enabled. Editor writes have no Git hook; the start workflow and reviewer
check cover that part. CI cannot infer an editor's worktree from a commit.

`tool/configs` now lists repository operations intended for an operator or
an agent acting for one. It forwards to the existing implementation scripts
without adding policy or domain deployment. Hooks and CI call implementation
tools directly. Windows keeps `windows/win-env.ps1` as its domain operator
entry point; Unix-like users continue to use the `Justfile`.

The merge gate is CI's `Required checks`, demanded whenever a change falls
in a domain that check covers.

The invariant registry has no pending entry and no untagged fixture unit, and
`tool/version-control/invariants` enforces C10 (no untagged fixture unit) by
default; `tool/configs invariants --table` prints the entries and
their number, which this file does not repeat. Enforced is not the same as held: the manual
`INV windows/support-boundary-named` records that the terminal delegation
item still passes its read-back below the Windows 10 boundary (#53).

Content before a shell suite's first banner is in no fixture unit and
invisible to C10 (`docs/policy/decisions/repository/fixture-tags-name-proven-invariants.md`).

The provisional registry exists since 2026-09-05, when #175 registered its
first entry; `docs/provisional/README.md` is the contract and
`tool/configs provisional --table` prints the entries.
`tool/version-control/provisional` checks it in both directions on every
commit and in the CI scan job. The exit criteria `unixlike/flake.nix` states in
comments are the known gap: moving them into the registry is a separate
decision and has not been made.

`tool/version-control/domain-reads` runs on every commit and in CI beside
the hygiene scan; the Windows CI job no longer walks the checkout for
PowerShell files. CI and pre-push call the Windows validation and test
implementations under `windows/tool/` directly; the test implementation is
the one place every script under the Windows tree is parsed for syntax
(`check-desired-state.ps1`
still parses the PowerShell payload it validates). `pre-push` runs the
history form of the audit, which judges `dev`, `master` and release-tag
reachability against `origin/dev` and `origin/master` when a fetch left
them (#240), and the subjects of the commits each pushed tip carries;
the CI audit names `HEAD`, so a pull request's own commits are judged
before it merges (#243). It still reads every local tag, so a stray local `*-v*` tag
the push does not carry fails the push; judging only the tags a push
carries has not been done.

Since 2026-09-13 the Unix-like domain owns one tree. `unixlike/` holds the
flake, the modules, the payloads and the domain's own tooling; `.envrc` and
the `Justfile` stay at the root, and `tool/` holds repository tooling without
exception. Inside the domain the first level of the module tree names a
concern: five concerns that had fragments in more than one class became
directories, five files that carried a platform in their name lost it, and
each payload and the one script a module interpolates now sit beside that
module. The classifier answers the domain with one arm for the tree, with
`.envrc` and the `Justfile` as the two root exceptions, where it had eight
patterns, and the three tools that enumerated Unix-like locations no longer
repeat a list (`docs/policy/decisions/unixlike/unixlike-domain-owns-its-tree.md`,
`docs/policy/decisions/unixlike/concern-first-inside-the-domain.md`).

On 2026-10-01, historical master-to-dev classification was restored for the
old Unix-like roots and exact Nix editor settings under
`docs/provisional/repository/classify-unixlike-old-roots.md`. These temporary
answers cover migration history; new domain material still belongs under
`unixlike/`. The retained editor settings now live byte-identically under
`unixlike/.vscode/settings.json` after their domain-owned relocation. The measure remains until master no longer retains those paths.

On 2026-09-24 the physical module tree was regrouped under `flake`,
`machines`, `platforms`, `foundation`, `desktop`, and `programs`. The concern
remains the unit inside each group; group names do not choose module classes.

On the same day the Unix-like provider API reached `dev`. The public
`shk95/configs-host-template` evaluates a synthetic pinned consumer in CI and
is marked as a GitHub template. One private repository,
`shk95/configs-hosts`, was generated from it and then held the seven host
flakes with separate locks. The template is a one-time copy, not a continuing
composition authority. The original provider outputs remained while the private
consumers collected host-specific native and runtime evidence
(`docs/policy/decisions/repository/one-private-host-repository-from-public-template.md`).
The repository-wide hygiene scanner now reads its admitted names from
`tool/version-control/hygiene.names` in the Git index. After the seven private
consumers were verified, the provider replaced its real inventory and final
outputs with synthetic fixtures. The name declaration admits the synthetic
fixtures and the remaining independently owned desired state.

## Provider boundary and consumer transfer (2026-09-30)

Initial PR #421 delivered the Unix-like public environment/host boundary to dev at
`3d6d945f1a7c32428ae506586eb5b644129e5614`. The provider now owns typed public
constructors, synthetic examples, API metadata and read-only contract and
standalone prerequisite tools. Host realization, safety assertions and
installation tools belong to consumers
(`docs/policy/decisions/unixlike/public-environment-host-boundary.md`).

The repository adopts one root consumer flake and lock with explicit host
declarations and shared selected inputs
(`docs/policy/decisions/repository/single-flake-host-consumers.md`). This
replaces the per-host-lock direction. The required template adaptation and
separately owned private source migration entered their main branches in the
initial pair below. At that checkpoint both root flakes and both original
and locked `configs` inputs selected
`github:shk95/configs/3d6d945f1a7c32428ae506586eb5b644129e5614?dir=unixlike`.
Both use `flake-modules/hosts/` declarations and a shared root input set.

| Initial consumer source delivery | Actual main merge | Exact merge-head evaluation |
| --- | --- | --- |
| [Public template PR #1](https://github.com/shk95/configs-host-template/pull/1) | `bd72568b4fd7fd740dc21d0a8fe8927cc9934e4b` | [Post-merge CI 36655493199](https://github.com/shk95/configs-host-template/actions/runs/36655493199): passed |
| [Private source PR #21](https://github.com/shk95/configs-hosts/pull/21) | `9b04a7635b8eb3e1c6e179827b87efcea9aa5672` | [Post-merge CI 36655638053](https://github.com/shk95/configs-hosts/actions/runs/36655638053): passed |

The earlier `e11bd136` bootstrap candidates and local override evaluations are
historical preparation checkpoints. The `3d6d945f` provider and initial pair
above retain evidence for those original source/lock selections; their CI does
not certify a later pin or establish native host runtime/activation.

Provider [repair PR #435](https://github.com/shk95/configs/pull/435), continuing
[issue #434](https://github.com/shk95/configs/issues/434), entered dev at
`c76752dc1ec285dce721ae02a2f139c9f32dcb76`. It preserves existing defaults,
support and API data while repairing ordinary native Darwin preference overrides
and finite contract inspection of forbidden Darwin/WSL declarations. Its exact
head and [post-merge CI 36667972274](https://github.com/shk95/configs/actions/runs/36667972274)
passed their own Required checks and selected native provider lanes.

Current source/lock review confirms both companion root flakes and original/
locked `configs` inputs select
`github:shk95/configs/c76752dc1ec285dce721ae02a2f139c9f32dcb76?dir=unixlike`
with the same `sha256-nOEpwuFlBKCUlZtLZA7MNYip9viU9ihARWuIravKMvc=` NAR
hash. Only the configs lock node changed in each adoption, separately committed
from the source pin and handoff documentation; host declarations/modules are
unchanged.

| Current companion source delivery | Actual main merge | Exact merge-head evaluation |
| --- | --- | --- |
| [Public template PR #2](https://github.com/shk95/configs-host-template/pull/2) | `2cbf41be904448354f413e6156e8e83c0e4c445a` | [Post-merge CI 36669451868](https://github.com/shk95/configs-host-template/actions/runs/36669451868): passed |
| [Private source PR #22](https://github.com/shk95/configs-hosts/pull/22) | `f5c205d942ddc6f4b51dffc0b218d72d040d7a49` | [Post-merge CI 36669541101](https://github.com/shk95/configs-hosts/actions/runs/36669541101): passed |

Immutable merged-source checks, without an override, evaluated the public example
and all seven private outputs. The packaged reader verified actual merged
consumer locks/declarations against both old and newly adopted provider source
roots; input compatibility has no required edits or metadata/default drift.
Arbitrary module effects remain a separate evaluation obligation, covered by the
final-output evaluations. No private input values or module contents are copied
into this repository.

The private candidate's selected native Darwin build invocation succeeded on
macOS 26.6.2/Nix 2.34.8 by realizing an existing store result. Equal candidate/
merge trees, candidate ancestry and freshly matching Darwin derivation/output
paths bind that result to the delivered consumer. This is neither a new derivation
rebuild nor a second build invocation at the merge. The public example and other
six private outputs have evaluation-only evidence; transferred safety/refusal
and bounded installation-plan fixtures passed without installation or activation.

Provider integration and this companion source delivery are recorded outcomes.
U1 parent acceptance and API release readiness remain pending; U2 Darwin capture
is separate unfinished work. Applicable release evidence remains separately
required. Neither provider/companion delivery nor cached build provenance implies
host runtime or activation. Private activation
is individually selected and is not a provider completion condition.

## Earlier repository evolution

Two things changed with it. The payload declaration moved to
`unixlike/payloads.json` and the scanned tree became the module tree, so the
Karabiner script is declared and parsed like the data payloads, in a `shell`
format `sh -n` provides; payloads went from fifteen to sixteen. And the Darwin
toplevel derivation path moved once, when the rearrangement renamed the files
that activation interpolates; the relocation itself left all three paths
byte-identical, which is why the two were separate changes. Native evidence
for the moved tree was taken on an Ubuntu WSL host on 2026-09-13:
`home-manager build --flake ./unixlike#user1` succeeds, and the Home Manager
generation built from `unixlike/` is byte-identical to the one activated
before the move, so the maintainer's `just home-switch` reused it rather than
creating a new one (#223).

Since 2026-09-12 the repository has an external layer: `docs/design/` (since
2026-09-19 `docs/work/`) holds the argument for a direction and carries no authority, and
`tool/version-control/design-citations` refuses a citation of a document
there from anything that does, on every commit and in the CI scan job, which
now carries ten repository-wide scans
(`docs/policy/decisions/repository/design-documents-outside-the-authority-model.md`). It held
four documents, ported the same day from the HTML artefacts they were
written as: a map of the tree as read at `dev` fc57495, the restructure
study, the restructure plan, and the commit-granularity study; all four are
closed or superseded since 2026-09-19. The two records the
study produced landed as the migration the preceding paragraph describes.

Also since 2026-09-12 a commit marks a judgement point rather than a step
(`docs/policy/decisions/repository/commit-marks-a-judgement-point.md`), and from then
until 2026-09-19 a branch belonged to a milestone and merged through one pull
request when that work was complete
(`docs/policy/decisions/repository/branch-lives-as-long-as-its-milestone.md`, superseded).
No milestone-length branch ever ran, so what one costs stayed unmeasured and
the study behind the decision closed as superseded. Two candidates promoted
with it, the catch-up procedure and what a two-scope commit may contain, and
both are still sentences in `CONTRIBUTING.md`.

Since 2026-09-19 work is planned and verified in documents
(`docs/policy/decisions/repository/work-planned-and-verified-in-documents.md`): a spec
and the report that answers it under `docs/work/<scope>/<slug>/`, checked by
`tool/version-control/work` on every commit and in CI, with issues holding
execution state only and `docs/work/roadmap.md` stating lanes and order.
The canonical agent workflow now calls for a local preflight of a new spec
and pending report before implementation. `tool/configs work
--working-tree docs/work/<scope>/<slug>` reads that one item, including
untracked files, for early W1-W6 feedback; it does not replace the index,
staged or commit-range checks.
GitHub milestones are no longer used. Since 2026-09-26 a branch delivers one
coherent same-scope outcome, which may span several evidence lanes, with the
report rows and status it produces in the same pull request. This replaces
the 2026-09-20 lane-per-PR interpretation; a reviewer holds the rule and no
tool does (`INV repository/pull-request-spans-an-evidence-lane`). No commit
message on its way to `dev` and no promotion body carries a closing keyword. A push to
`dev` that ends a report closes the issue its
spec names (`.github/workflows/work-closure.yml`), `tool/version-control/audit`
warns about a spec past its review-by, and `tool/version-control/audit-remote`
reports an issue left open beside a terminal report; the workflow closed its
first issue, #259, on 2026-09-19. The document layout is done
(`docs/work/repository/docs-layout/report.md`); what it left is the
classifier's handling of the registries' old roots, a provisional measure
that ends when the move reaches `master` (#275). The work model is done too
(`docs/work/repository/work-model/report.md`), and so is the in-place
NixOS-WSL update (`docs/work/unixlike/nixos-wsl-in-place-update/report.md`),
whose issue the workflow also closed. A Windows release tag annotation states
each host's evidence in a block of its own. New Unix-like provider tags state
provider API and fixture evidence once, without certifying a private host;
the audit retains the two tags of 2026-08-31 as historical exceptions
(`docs/work/repository/release-tag-contract/report.md`); no tag has been
created in that form yet. The CI reconsideration work item is done
(`docs/work/repository/ci-headless-runtime/report.md`): the existing required
Unix-like job now boots the generic headless class and exercises its account,
ssh and firewall contract without adding a runner or workflow.

## Adopted agent workflow (2026-09-26)

The GitHub-centered operating contract reached dev in PR #416 on 2026-09-26.
Planning, execution, integration, inspection and reclamation have canonical
project skills. The session helper
records local handoffs; it does not enforce process liveness or credentials.
See docs/policy/decisions/repository/github-agent-workflow.md.

Observed dev protection already requires PRs, strict Required checks, resolved
conversations and administrator enforcement; force pushes and deletion are
forbidden. No remote settings were changed. No blanket required human review
or CODEOWNERS identities were introduced. Native stacks remain unsupported in
production pending trunk CI and admission verification; Merge Queue is not used.
CI effect selection reached dev in PR #413. Documentation retains its owning
scope and repository-wide policy scans while selecting no platform or
repository fixture suite. Executable platform inputs still select the whole
platform suite; shared dispatch and gate inputs select all suites. Unknown
inputs and unsupported native-stack events fail selection. See
docs/policy/decisions/repository/local-gate-selects-by-effect.md.

The independent domain follow-ups also reached dev: PR #415 reduces repeated
Unix-like verification work, and PR #414 adds Windows suite and slow-test
timing without removing tests or demonstrating a speedup. Their reports retain
the measured evidence and its limits. Post-merge validation remains until safe
equivalence is demonstrated; no cross-run result reuse is implemented.

## Common

No `common/` component exists.
`docs/policy/decisions/repository/powershell-copied-per-domain.md` names what would justify
one: both the PowerShell and the Zellij keymap copies showing stable
semantics across independent platform validation and release cycles.

## Open conditions

- `docs/policy/decisions/repository/ci-evidence-without-hosted-runners.md`: the
  installed VMware guest triggered review on 2026-09-21, and the maintainer
  accepted one minimal booted headless check in the existing required
  Unix-like job. It reopens if that check becomes unreliable or impractical,
  another installed host gains runtime behaviour a hosted test can assert, or
  a defect class an additional hosted runner would have caught occurs twice.
- `docs/policy/decisions/repository/powershell-copied-per-domain.md`: reopens when both
  implementations show stable semantics that would justify a common
  component.
- `docs/policy/decisions/repository/hygiene-tool-owns-enforcement.md`: reopens when the same
  four axes are decided from a typed declaration rather than from text.
- `docs/policy/decisions/repository/annotated-tag-is-the-release-record.md`: reopens when a
  consumer needs a release artifact or a note the tag annotation cannot
  carry.

Production-mode offline qualification now has explicit complete-tree mappings,
source-bound public surfaces, exact tool requirements and separate native evidence
obligations (`docs/policy/decisions/repository/production-release-qualification.md`).
Its bootstrap proposal is unselected and its receipts remain offline assertions.
A separate private operating repository has been selected. The maintainer stored
a dedicated Environment credential directly. A master-only finite GET probe
observed the selected private identity, required read access and denied Secrets
metadata access. Manual/scheduled proof, bootstrap adoption, mutation permission,
actual release and activation or Apply remain separate pending gates.

Authenticated finite transport source and its unresolved-input manual template
are verified separately from retained preview semantics (docs/policy/decisions/repository/authenticated-release-transport.md).
Its finite library binds actual API observations and original history, while the
operator/workflow stays disabled. A single-job writer topology is required before
any cancellation. The separate provisioning probe is deployed on accepted master source; routine
writer/inspector orchestration remains disabled. The bridge has source-only durable
start/claim proposals through original retained packages. Bootstrap, write
permissions, actual isolation and manual/scheduled proof remain unresolved; source
fixtures certify no actual operating cycle.
