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

On 2026-09-24 the physical module tree was regrouped under `flake`,
`machines`, `platforms`, `foundation`, `desktop`, and `programs`. The concern
remains the unit inside each group; group names do not choose module classes.

On the same day the Unix-like provider API reached `dev`. The public
`shk95/configs-host-template` evaluates a synthetic pinned consumer in CI and
is marked as a GitHub template. One private repository,
`shk95/configs-hosts`, was generated from it and holds the seven current host
flakes with separate locks. The template is a one-time copy, not a continuing
composition authority. The original provider outputs remained while the private
consumers collected host-specific native and runtime evidence
(`docs/policy/decisions/repository/one-private-host-repository-from-public-template.md`).
The repository-wide hygiene scanner now reads its admitted names from
`tool/version-control/hygiene.names` in the Git index. After the seven private
consumers were verified, the provider replaced its real inventory and final
outputs with synthetic fixtures. The name declaration admits the synthetic
fixtures and the remaining independently owned desired state.

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
GitHub milestones are no longer used, a branch is one reviewable increment —
since 2026-09-20 what one evidence lane verifies, with its report rows and
status in the same pull request, a rule a reviewer holds and no tool does
(`INV repository/pull-request-spans-an-evidence-lane`); no commit message on
its way to `dev` and no promotion body carries a closing keyword. A push to
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

## Agent workflow transition (2026-09-26)

The GitHub-centered operating contract is prepared in the agent-workflow PR;
it takes effect when integrated into dev. Planning, execution, integration,
inspection and reclamation have canonical project skills. The session helper
records local handoffs; it does not enforce process liveness or credentials.
See docs/policy/decisions/repository/github-agent-workflow.md.

Observed dev protection already requires PRs, strict Required checks, resolved
conversations and administrator enforcement; force pushes and deletion are
forbidden. No remote settings were changed. No blanket required human review
or CODEOWNERS identities were introduced. Native stacks remain unsupported in
production pending trunk CI and admission verification; Merge Queue is not used.
CI effect selection and domain test-efficiency changes are separate delivery
PRs, and post-merge validation remains until safe equivalence is demonstrated.

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
