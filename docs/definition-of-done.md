# Definition of done

Evidence is domain-scoped. A successful check in one domain says nothing about
an unrelated domain, and evaluation is not activation. Report unavailable
native checks instead of treating them as passed.

## Every change

- [ ] The owning scope is identified as `unixlike`, `windows`, `common`,
      `repository`, or an explicit `adopt` transfer.
- [ ] Formatting, lint, and narrow checks relevant to the changed files pass.
- [ ] User-facing behavior and expensive decisions are documented.
- [ ] The final diff contains no unrelated changes.
- [ ] Evaluation, build, native runtime check, and deployment evidence are
      reported separately where they apply.
- [ ] No commit, push, tag, branch change, activation, or Apply occurred without
      explicit authorization.

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
      workflow and do not duplicate its policy.

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
- [ ] `tool/version-control/plan-promotion` reports all commits and scopes.
- [ ] The promotion contains no source fix authored only for the promotion.
- [ ] `Required checks` passes and conversations are resolved.
- [ ] The pull request uses a merge commit and explicit merge authorization.
- [ ] The merge is source acceptance, not domain certification or deployment.
- [ ] Local and remote audits pass after merge; `master` is not reverse-merged
      into `dev` merely to carry the promotion merge commit.

## Unix-like domain

- [ ] The change is owned by the flake, a Unix-like module, or a Unix-like
      payload rather than a cross-platform abstraction.
- [ ] The affected Home Manager, NixOS, or nix-darwin toplevel derivation
      evaluates.
- [ ] A native build is performed on a matching system when sources or packages
      changed.
- [ ] Foreign evaluation is reported as evaluation, not native build evidence.
- [ ] Activation is performed only when explicitly requested.
- [ ] Runtime claims name the host on which they were observed.
- [ ] A `unixlike-v...` tag is assigned only after required native evidence is
      available.

## Windows domain

- [ ] The change is owned and semantically validated by the Windows domain.
- [ ] `windows/tools/check-desired-state.ps1` validates the manifest and every
      PowerShell, JSON, INI, KDL, and Lua source with native tooling.
- [ ] Pester passes under native PowerShell when reconciliation behavior changed.
- [ ] `windows/bootstrap.ps1 -Check` is observed on native Windows when package
      detection, target paths, registry behavior, fonts, configuration parsing,
      or application lifecycle behavior changed.
- [ ] Missing native tooling is reported as unverified rather than valid.
- [ ] Apply is run only when explicitly requested, followed by another
      read-only check.
- [ ] A `windows-v...` tag is assigned only after required native evidence is
      available.
- [ ] The source change lives in `windows/desired/`, `windows/src/`, Windows
      tests, or Windows-native tooling rather than a Nix module.

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
- [ ] Domain ownership belongs in `docs/architecture.md`.
- [ ] Procedure belongs in `CONTRIBUTING.md`.
- [ ] A decision expensive to reverse or important current state belongs in
      `docs/status.md`.
- [ ] A recurring issue is indexed in `docs/troubleshooting.md` by its literal
      symptom.
- [ ] A canonical skill lives in the owning project or an explicitly adopted
      shared-skill project; model-specific adapters contain no independent
      project judgement.

## Release evidence

- [ ] The release tag is annotated, matches the domain naming convention, and
      targets a commit reachable from `master`.
- [ ] The annotation names the domain and reports evaluation, build, and native
      runtime evidence separately.
- [ ] Missing native evidence is recorded as unavailable, never inferred from
      foreign evaluation.
- [ ] The tag is new and immutable; an existing tag is never moved or reused.
- [ ] Tag creation and push each have explicit authorization.
- [ ] Activation or Apply is reported separately and is not implied by the tag.
