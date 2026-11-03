# Definition of done

Evidence is domain-scoped. A successful check in one domain says nothing about
an unrelated domain, and evaluation is not activation. Report unavailable
native checks instead of treating them as passed.

This file holds what every change and the repository scope owe; each domain's
own list is the file named for it beside this one (`unixlike.md`,
`windows.md`).

Apply only the sections and items relevant to the requested change. Mechanical
checks provide their results once; reviewers assess the remaining judgement
and evidence rather than repeating each check by hand. Unrequested release,
maintenance, archival, plugin or deployment operations are not completion
requirements for ordinary source work.

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
      explicit authorization; existing authorization within the agreed task
      was honored and staged-only work remains uncommitted
      (INV repository/local-development-integration).

## Repository governance

- [ ] The change affects only version-control policy, check dispatch, hooks,
      CI wiring, or reusable agent workflow mechanics.
- [ ] It creates no configuration output and receives no domain release tag.
- [ ] Version-control fixtures cover changed mechanical behavior; explanatory
      corrections receive review without artificial behavior tests.
- [ ] A Windows-only change can be prepared and checked without Nix.
- [ ] An unrelated domain failure is not required to validate a domain change.
- [ ] Master push and topic PR CI expose the stable `Required checks` result;
      direct master commits need no mandatory PR/status admission.
- [ ] Model-specific context, command and skill files point to authoritative
      project guidance or explicitly adopted skill sources and add no
      independent policy (INV repository/adapters-pointer-only).
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

## Master and topic work

- [ ] The workspace follows the user's existing answer for this task, with
      isolated parallel authors (INV repository/workspace-choice).
- [ ] One logical commit normally used master; multiple logical commits or a
      selected linked workspace used a topic, merged no-ff when requested.
      If work grew after a master commit, that commit was preserved and the
      remaining work moved to a topic.
- [ ] CI source identities and selected check results are reported separately
      from actual remote protection adoption.

## Unix-like input patch

- [ ] The same-repository patch head is one commit on the current master and
      changes only permitted Unix-like lock data and its next patch declaration.
- [ ] Exact PR CI evidence and the actual merge parents/tree agree; the writer
      defers for other master PRs and uses ordinary protected history rules.
- [ ] The patch remains based on current published master and stops on source
      drift; no Windows publication occurs in the patch controller.
- [ ] The immutable annotation and interrupted-publication recovery satisfy the
      release evidence items below; no host adoption or activation is inferred.

## Common domain

- [ ] Existing independent implementations demonstrate stable,
      platform-neutral semantics; similarity alone was not used as evidence.
- [ ] The material lives under an explicit `common/` boundary.
- [ ] Its contract, intended consumers, exclusions, and compatibility policy
      are documented.
- [ ] It contains no platform path, package-manager behavior, host inventory,
      or deployment policy.
- [ ] Consumer-independent checks pass.
- [ ] When publication is requested, a `common-v...` tag is assigned
      independently and deploys nothing.
- [ ] Consumer adoption is a later, separate change in the consuming domain.
- [ ] A copied adoption becomes destination-owned, or a direct import pins the
      common version and documents why coupling is justified.

## Cross-domain adoption

- [ ] The source and destination domains are explicit.
- [ ] Adoption is separate from producing the source-domain release.
- [ ] The destination performs its own native checks.
- [ ] No expectation of future byte equality is implied for a copied adoption.
- [ ] An unrelated domain is not made a release prerequisite.

## Context changes

- [ ] New context follows the document ownership map and states each
      obligation once; adapters and optional orchestration add no policy.
- [ ] Current state, adopted decisions and historical work evidence are
      distinguished. Agent guidance requires no unrelated reading, role
      assignment, repeated authorization or plugin installation.

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
- [ ] The tag is new and immutable. The only initial 1.0.0 reissue is the
      one-time maintainer-authorized history-refinement exception in
      `docs/policy/decisions/repository/minimal-release-automation.md`; routine
      existing tags are never moved or reused.
- [ ] Tag creation and push each have explicit authorization.
- [ ] Activation or Apply is reported separately and is not implied by the tag.

## Terminal work archival

- [ ] The repository maintainer reviewed the fixed remote original and absence
      of active references before archiving a valid terminal spec/report pair
      (INV repository/work-spec-has-report).

## Mechanical operation and exception review

- [ ] Requested integration or workspace removal used the tracked checks and
      preservation review; missing notes or uncertain liveness supplied no
      permission to discard data.
- [ ] Before maintenance adoption, the maintainer confirms the dedicated App alone
      bypasses an active exact-master non-fast-forward ruleset, its key exists
      only in the reviewed environment, minimum API grants and preflight pass,
      human reviewers cannot be bypassed, and actual execution/recovery evidence
      is recorded separately (INV repository/approved-history-rewrite).
