# Definition of done

Evidence is domain-scoped. A successful check in one domain says nothing about
an unrelated domain, and evaluation is not activation. Report unavailable
native checks instead of treating them as passed.

## Every change

- [ ] The owning domain is identified as `unixlike`, `windows`, or `common`.
- [ ] Formatting, lint, and narrow checks relevant to the changed files pass.
- [ ] User-facing behavior and expensive decisions are documented.
- [ ] The final diff contains no unrelated changes.
- [ ] Evaluation, build, native runtime check, and deployment evidence are
      reported separately where they apply.
- [ ] No commit, push, tag, branch change, activation, or Apply occurred without
      explicit authorization.

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
