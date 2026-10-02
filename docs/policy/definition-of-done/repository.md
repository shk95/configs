# Definition of done

Evidence is domain-scoped. A successful check in one domain says nothing about
an unrelated domain, and evaluation is not activation. Report unavailable
native checks instead of treating them as passed.

This file holds what every change and the repository scope owe; each domain's
own list is the file named for it beside this one (`unixlike.md`,
`windows.md`).

## Every change

- [ ] The owning scope is identified as `unixlike`, `windows`, `common`,
      `repository`, or an explicit `adopt` transfer.
- [ ] Formatting, lint, and narrow checks relevant to the changed files pass.
- [ ] User-facing behavior and expensive decisions are documented.
- [ ] The final diff contains no unrelated changes.
- [ ] A changed or added invariant has a registry entry under
      `docs/policy/invariants/<scope>/` whose declared locators name it, and the tagged
      fixture was read to confirm it exercises the statement.
- [ ] Evaluation, build, native runtime check, and deployment evidence are
      reported separately where they apply.
- [ ] A change that belongs to a spec verifies at least one of its criteria
      and carries the report rows, status and report end that produces; one
      that carries only bookkeeping names where its evidence was produced
      (INV repository/pull-request-spans-an-evidence-lane).
- [ ] No commit, push, tag, branch change, activation, or Apply occurred without
      explicit authorization.
- [ ] The source edit was authored in its task-dedicated linked worktree
      (INV repository/change-authoring-in-linked-worktree).

## Repository governance

- [ ] The change affects only version-control policy, check dispatch, hooks,
      CI wiring, or reusable agent workflow mechanics.
- [ ] It creates no configuration output and receives no domain release tag.
- [ ] Version-control fixture tests cover every changed invariant.
- [ ] A Windows-only change can be prepared and checked without Nix.
- [ ] An unrelated domain failure is not required to validate a domain change.
- [ ] CI exposes the stable `Required checks` gate and branch protection
      requires it instead of conditional domain job names.
- [ ] Model-specific skill locations only discover the canonical Agent Skills
      workflow and do not duplicate its policy (INV repository/adapters-pointer-only).
- [ ] A reviewer confirms documented repository operator commands use
      `tool/configs`, hooks and CI call implementation tools directly, and
      neither operator entry point crosses into another domain's deployment
      (INV repository/operator-entry-boundary).
- [ ] Committed desired state carries no undeclared user or host name, no
      absolute home path, no tracked runtime state, and no machine-unique
      identifier, and every exclusion is declared with its reason
      (INV repository/hygiene-home-paths, INV repository/hygiene-declared-names,
      INV repository/hygiene-runtime-state, INV repository/hygiene-machine-identity).
- [ ] Prose in the diff was read for a bare account name, which no scanner
      decides, and that reading is reported as the manual evidence (INV repository/hygiene-prose-account-name).
- [ ] Every fixture unit this change touches names an invariant
      (INV repository/fixtures-name-invariants), and every gate job converts
      unverified into failure (INV repository/merge-gate-requires-native).
- [ ] Every temporary measure the change adds is registered under
      `docs/provisional/` with an exit condition, a review date and a tag on each
      disposable line, and a measure it removes loses its entry and its tags in
      the same commit (INV repository/provisional-registry-coverage).

## Governance rule design

- [ ] The prevented failure, owning scope, rationale, and decision owner are
      explicit.
- [ ] Policy is expressed as tool-independent invariants with one authority.
- [ ] Procedure contains prerequisites, ordered actions, recovery, and approval
      boundaries but introduces no new obligation.
- [ ] Skills orchestrate; deterministic tools and remote settings enforce.
- [ ] Enforceable invariants have positive and negative fixtures; manual
      invariants name their required evidence.
- [ ] Current adoption and migration gaps are recorded separately from policy.
- [ ] A cross-project skill contains no consuming repository identity, policy,
      path convention, or current state; adoption remains explicit.

## Dev-to-master promotion

- [ ] The pull request is from this repository's `dev` to `master`, and no
      other promotion pull request is open.
- [ ] `tool/configs plan-promotion` reports all commits and scopes.
- [ ] The promotion contains no source fix authored only for the promotion.
- [ ] `Required checks` passes and conversations are resolved.
- [ ] The pull request uses a merge commit and explicit merge authorization.
- [ ] The merge is source acceptance, not domain certification or deployment.
- [ ] Local and remote audits pass after merge; `master` is not reverse-merged
      into `dev` merely to carry the promotion merge commit.

## Common domain

- [ ] Existing independent implementations demonstrate stable,
      platform-neutral semantics; similarity alone was not used as evidence.
- [ ] The material lives under an explicit `common/` boundary.
- [ ] Its contract, intended consumers, exclusions, and compatibility policy
      are documented.
- [ ] It contains no platform path, package-manager behavior, host inventory,
      or deployment policy.
- [ ] Consumer-independent checks pass.
- [ ] A `common-v...` tag is assigned independently and deploys nothing.
- [ ] Consumer adoption is a later, separate change in the consuming domain.
- [ ] A copied adoption becomes destination-owned, or a direct import pins the
      common version and documents why coupling is justified.

## Cross-domain adoption

- [ ] The source and destination domains are explicit.
- [ ] Adoption is separate from producing the source-domain release.
- [ ] The destination performs its own native checks.
- [ ] No expectation of future byte equality is implied for a copied adoption.
- [ ] An unrelated domain is not made a release prerequisite.

## Context and workflow

- [ ] Stable judgement belongs in `AGENTS.md`, not a model-specific adapter.
- [ ] Domain ownership belongs in `docs/policy/architecture.md`.
- [ ] Procedure belongs in `CONTRIBUTING.md`.
- [ ] Important current state belongs in `docs/status/<scope>.md`; a decision
      expensive to reverse belongs in its own record under `docs/policy/decisions/`.
- [ ] A decision record's header carries `date`, `scope` (repeated for a
      decision spanning domains) and `status`; a citation of a record names
      an existing path; a `decision:` pointer names a record whose status is
      `accepted`.
- [ ] A recurring issue is indexed in `docs/reference/troubleshooting.md` by its literal
      symptom.
- [ ] A canonical skill lives in the owning project or an explicitly adopted
      shared-skill project; model-specific adapters contain no independent
      project judgement.

## Release evidence

- [ ] The release tag is annotated, matches the domain naming convention, and
      targets a commit reachable from `master`.
- [ ] The annotation names the domain and reports evaluation, build, and native
      runtime evidence separately: per host for Windows, and once for Unix-like
      provider or common releases.
- [ ] The annotation was read before the tag was created for a machine name,
      an account name or a machine-unique identifier in a host label or a
      reference, which no scanner decides, and that reading is reported as
      the manual evidence (INV repository/release-tag-contract).
- [ ] Missing native evidence is recorded as unavailable, never inferred from
      foreign evaluation.
- [ ] The tag is new and immutable; an existing tag is never moved or reused.
- [ ] Tag creation and push each have explicit authorization.
- [ ] Activation or Apply is reported separately and is not implied by the tag.

## Agent delivery and recovery

- [ ] A reviewer confirms the worker hands off a remote feature branch and PR,
      integration enumerates GitHub candidates, and dev protection still
      requires PR/check admission without an agent bypass
      (INV repository/pr-integration-authority).
- [ ] Interrupted workers have a useful checkpoint; local liveness is not
      inferred from age, and cleanup considers unpushed and ignored data.
