# Contributing

This is the workflow for people and tools. `AGENTS.md` contains stable
judgement and safety rules, `docs/policy/architecture.md` defines domain ownership,
and `README.md` contains usage.

Repository text is English because the repository is public.

## Prepare a clone

```sh
tool/setup
tool/setup --fix
tool/doctor.sh
```

`tool/setup` changes only the clone-local hooks setting and only with `--fix`.
`tool/doctor.sh` is read-only. `tool/doctor.sh` also prints a one-line
summary of the outcomes the hooks have recorded on this clone;
`tool/version-control/hook-evidence` prints the full count. Pass `unixlike`,
`windows`, `common`, or `repository` to check only that scope; omit the
scope for a complete host inventory. A missing foreign-platform capability
does not block scoped work.

## Classify the change

Every change belongs to one of these scopes:

- `unixlike`: Nix, Home Manager, NixOS, WSL guest, or nix-darwin behavior.
- `windows`: native Windows desired state and reconciliation.
- `common`: explicitly platform-neutral material with its own contract.
- `adopt`: an explicit copy or pinned import from one domain into another.
- `repository`: version-control policy, hooks, CI dispatch, or reusable agent
  workflow support with no configuration or deployment output.

`repository` is a governance scope, not a fourth configuration domain. It has
no release tag and must not contain platform behavior that belongs to
`unixlike`, `windows`, or `common`.

One scope per commit, and therefore per branch and pull request. A commit's
scope is the classifier's answer over the paths it touches, and the release
tag, the CI lanes and the right to change a path all follow from it. The
subject's scope is a different thing: it names the domain the change
describes, so `docs(windows)` over `docs/policy/architecture.md`, which classifies
`repository`, is correct. If a common change and its platform adoption are
both needed, land them separately so neither release is synchronously coupled
to the other.

## Branch and commit flow

```text
master <- dev <- feature/<domain>-<topic> or fix/<domain>-<topic>
```

Examples are `feature/unixlike-shell`, `fix/windows-zellij`, and
`feature/common-terminal-colors`. Governance examples are
`feature/repository-vcs-audit` and `fix/repository-ci-dispatch`.

A branch is one reviewable increment: one issue, or what one judgement
covers. Cut it from `origin/dev`, and merge it through one pull request when
it is complete and green
(`docs/policy/decisions/repository/work-planned-and-verified-in-documents.md`). A spec
takes as many pull requests as it has evidence lanes and scopes, not as many
as it has steps: an increment is what one evidence lane verifies, and the
bookkeeping a verification produces travels with it
(`INV repository/pull-request-spans-an-evidence-lane`). "Plan and verify
work" below is how they are planned.

A commit marks a judgement point. It carries the change one decision
produced, however many files that is, and is not split further merely because
it has parts (`docs/policy/decisions/repository/commit-marks-a-judgement-point.md`). Scope the
subject, for example `feat(unixlike):`, `fix(windows):`, `chore(common):` or
`refactor(repository):`. A document classifies as the scope directory that
holds it, or the scope a file under `docs/status/` or
`docs/policy/definition-of-done/` is named for, so a domain's decision,
invariant, evidence item and status land in that domain's commit
(`docs/policy/decisions/repository/documents-classified-by-scope.md`).
Anything that still touches two scopes is two commits.

Branches interleave where one blocks another, and no rule is needed to make
them: the pre-commit hook refuses a staged path with no owning scope, so a
move cannot be committed before the classifier accepts its new paths, and the
old paths cannot be deleted before the move has merged. Where that happens
each half merges when it is ready.

Use merge commits for completed work; do not squash or rebase published work.
Do not commit directly to `master`.

`dev` requires an up-to-date branch, so one whose base has moved catches up
before it can merge and GitHub's auto-merge will not do it. Merge `dev` into
the branch locally and push: the pre-push hook and the native lanes then run
against the tree that will actually land, which is where this repository's
native evidence comes from. Do not use `gh pr update-branch`, which has
GitHub author that merge outside both. `git merge-tree --write-tree HEAD
origin/dev` shows the conflicts read-only first.

`dev` means the affected domain's repository checks pass. `master` means the
source change has been accepted; it no longer means every platform at that
commit has been exercised. Native readiness is represented by domain tags and
the evidence in `docs/policy/definition-of-done/`.

Use independent release tags:

- `unixlike-vYYYY.MM.DD`, with `.N` for another release that day;
- `windows-vYYYY.MM.DD`, with `.N` for another release that day;
- `common-vYYYY.MM.DD`, with `.N` for another release that day.

Keep `unixlike/flake.lock` refreshes in dedicated `chore(unixlike-deps)`
commits. A domain tag certifies only the named domain even though the commit
may contain accepted history from the others.

For a routine desired-state edit whose message is a template — a Homebrew
formula or cask, a `unixlike/flake.lock` refresh —
`tool/version-control/commit` shows the edit, the classification, the selected
checks, and the message, then applies it and commits on your confirmation. It
refuses on `master` and never bypasses a hook.

Run it from `dev`. On any other branch it commits where it stands, and with
`--publish` it arms auto-merge on the pull request already open from that
head, which on a branch carrying other work would merge that work
unfinished. Every edit it templates is `unixlike`, so on a `repository`
branch it would also produce a two-scope commit.

Add `--publish` and that one confirmation carries the change the rest of the
way. On `dev` the helper branches to `feature/<scope>-<topic>` from
`origin/dev`; on any other branch it commits where it is. It then pushes,
opens a pull request against `dev`, arms auto-merge, and prints the
pull-request URL. It never waits on CI and never merges: `Required checks` and
an up-to-date base still decide that, and a push the pre-push hook or the
remote rejects leaves the commit local. `--dry-run --publish` prints the
branch, the pull-request title and body, and every command, and writes
nothing.

`--publish` requires `Allow auto-merge` to be on in the repository settings and
`gh` to be authenticated for github.com; it refuses before writing anything if
either is missing. It pushes the branch rather than the one commit, so it lists
everything on the branch that is not yet on `dev` before you confirm. Where a
pull request from the branch is already open against `dev` it arms that one and
leaves its title and body alone.

Domain releases use immutable annotated tags. The target commit must be
reachable from `master`. The annotation records the domain and reports
evaluation, build, and native-runtime evidence separately, including explicit
`unavailable` or `not applicable` values. A `unixlike` or `windows`
annotation reports them once for each host the release speaks for, in a block
opened by `Host: <label>`; a `common` annotation reports them once.
`tool/version-control/plan-release` prints the template, and
`tool/version-control/audit` refuses a tag that departs from it. A label is
lowercase letters, digits and hyphens and names a kind of host — `darwin`,
`wsl-nixos`, `windows` — never a machine; keep machine names, account names
and machine identifiers out of the references too, because a pushed tag
cannot be edited. A host whose check failed is not released around. Create
and push a tag only when the user explicitly requests those mutations. Create
no GitHub Release: the annotation is the whole record. Activation and Windows
Apply happen after release and are not implied by a tag.

For agent-assisted work, invoke `run-version-control-workflow`. Its canonical
Agent Skills implementation is under `.agents/skills/`; model-specific
discovery files are adapters only. Audit and release planning are read-only by
default. This document remains the human fallback and the contract the skill
executes.

### zellij overlay

This subsection is disposable and carries the tag
`PROV unixlike/zellij-combining-marks`, so it is deleted with the measure it
describes.

`unixlike/modules/zellij/module.nix` carries upstream zellij-org/zellij#5500
for Darwin until nixpkgs ships a zellij whose source already has the fix;
`docs/provisional/unixlike/zellij-combining-marks.md` registers the measure and
names the condition that ends it. The overlay names no zellij version: it
applies the range with no fuzz to whatever zellij the lock brings in, so a
`unixlike/flake.lock` refresh that moves zellij is the ordinary one commit,
`tool/version-control/commit flake refresh`.

The flake checks `zellij-combining-marks`,
`zellij-combining-marks-refuses-a-patched-tree` and
`zellij-combining-marks-refuses-a-stale-vendor`, declared beside the overlay,
are what judge that refresh. `unixlike/tool/checks/test` builds them on every
system, so the refresh's pre-push and the merge gate refuse a lock whose
zellij the range no longer applies to; `just zellij-patch-check` builds the
first alone, and `just zellij-patch-check v<ver>` applies the range to an
upstream tag before a refresh brings it in. When they refuse:

1. Rebase the range in a fork and repoint the overlay's `url` and `hash` in a
   `fix(unixlike):` commit made before the refresh. The pin is the pull
   request's commit range `base...head` in the overlay's compare URL; a
   re-pin to a branch that gained commits moves the head, and a rebase moves
   both.
2. Refresh the lock again after it.

After a refresh that moves zellij, `just darwin-build` on the Mac and the
reproduction in `docs/policy/decisions/unixlike/zellij-patched-on-darwin-until-upstream.md`
are the build and runtime evidence; the checks prove only that the range
applies.

`.github/workflows/zellij-upstream-5500.yml` watches the pull request and
reports a bump or a merge as an issue. GitHub runs a `schedule` only from the
default branch, so the watcher does nothing until this file reaches `master`
through the next promotion; before that its shell body is run by hand with
`DRY_RUN=1`.

## Promote dev to master

Promotion is a deliberate source-acceptance operation, not a release. The only
valid promotion pull request has base `master` and head `dev` in this
repository. Keep at most one such pull request open. The repository maintainer
owns the promotion decision. There is no operational bypass; a different flow
requires an accepted policy change first.

1. Fetch `dev` and `master`, then run `tool/version-control/plan-promotion`.
2. Review every commit and owning scope in `master..dev`. Do not add a fix to
   the promotion pull request; land the fix through its owning branch into
   `dev`, then refresh the promotion.
3. Open a pull request from `dev` to `master` titled
   `chore(repository): promote dev to master`. Record included pull requests,
   scopes, check evidence, and known unavailable native evidence.
4. Require `Required checks`, resolved conversations, and an explicit merge
   request. Merge with a merge commit only.
5. Run local and remote version-control audits after the merge. Do not merge
   the promotion commit back into `dev`.
6. Plan domain release tags or deployments separately when their own evidence
   is available.

If promotion is wrong, revert or fix it through `dev` and promote again. Never
rewrite `master` or move an existing release tag. `dev` requires an up-to-date
base before merge; `master` does not, because it accepts only `dev` and its
promotion merge commit intentionally does not flow back into `dev`.

## Add or change governance

Before adding a rule, write a small governance decomposition:

1. Name the failure being prevented, owning scope, and decision owner.
2. State rationale and tool-independent invariants.
3. Define human prerequisites, ordered steps, recovery, and authorization
   boundaries without adding obligations absent from the policy.
4. Assign repeatable orchestration to a canonical skill and deterministic
   decisions to tools, hooks, CI, or remote settings.
5. Define evidence, positive and negative fixtures, current migration state,
   and the condition for removing superseded implementation.

Use `design-project-governance` from the sibling `skills` project to perform
this decomposition. The skill owns only the generic method; this repository
owns the result. A product-specific adapter must not own any part of either.

## Add or change an invariant

An invariant is a statement that must remain true of committed desired state
or repository tooling. `docs/policy/invariants/README.md` is the format; this is the
procedure.

1. Classify the invariant's scope. Its file goes under
   `docs/policy/invariants/<scope>/<slug>.md` and the change classifies as that scope.
2. Write the statement as one sentence naming no command, product, or model.
3. Point `rationale` at the section of `docs/policy/architecture.md` or `AGENTS.md`
   that justifies it. If none does, write that section first; a rule with no
   rationale is not ready to register.
4. Declare the enforcement. A `schema` or `tool` entry also declares a
   `fixture`; add the fixture in the same change and tag it with
   `INV <scope>/<slug>`. A `manual` entry names its evidence and is listed by
   id in its scope's `docs/policy/definition-of-done/<scope>.md`; because the checker requires that
   listing and refuses an unregistered tag in the same run, the entry and the
   evidence item land in one commit, which classifies as the entry's scope
   because both files sit under it.
   If nothing enforces it yet, open an
   issue and declare `pending #<n>` with an owner. Tag the fixture *unit* —
   the `Describe` or the banner section — or the pre-commit hook refuses the
   commit; `tool/version-control/invariants --untagged` names the unit.
5. Put the tag `INV <scope>/<slug>` in every declared locator: a header
   comment in a script, the test name or a comment above a fixture, the
   loader's refusal message.
6. Run `tool/version-control/invariants`. It runs again on every commit.

Removing an invariant removes its file and every tag that named it; the check
refuses an orphan tag. Weakening a statement is a governance change and is
reviewed as one.

## Register a provisional measure

A provisional measure is an experiment, a workaround, or a patch carried until
upstream ships a fix — anything the tree is meant to stop carrying.
`docs/provisional/README.md` is the format; this is the procedure. Register it in
the same change that adds it, not afterwards.

1. Classify the measure's scope. Its file goes under
   `docs/provisional/<scope>/<slug>.md` and the change classifies as that scope.
   Create the scope directory only if the measure needs it.
2. Write `statement` and `exit-when` as one sentence each: what the measure is,
   and the condition that ends it.
3. Set `watch` to the tracked path whose change is the signal, or to `manual`
   when only a person can tell. Leave the key out when neither applies.
4. Set `since` to the date the measure enters the tree and `review-by` to a
   date after it and at most 180 days later. Pick the date by which someone
   could tell whether `exit-when` came true, not the longest one allowed.
5. Open or name the issue where the measure and its exit are tracked, and
   point `decision` at the record that accepted it, `<path> § <heading>`. If
   no record accepted it, write one first through "Record a decision" below;
   a measure nothing decided is not ready to register. Name the `owner` who decides
   whether it is retired, extended or promoted.
6. Put the tag `PROV <scope>/<slug>` on every disposable line: the header
   comment above the block in a script or a Nix file, the comment above the
   PowerShell block, the running text of a document. A document explaining the
   registry writes the placeholder form and never a literal id.
7. Stage the entry and the tagged lines, then run
   `tool/version-control/provisional`. It reads the index, so an unstaged
   entry is invisible to it. It runs again on every commit and in CI.

## Retire, extend or promote a provisional measure

Every entry ends one of three ways, and `review-by` is the date the choice is
made rather than deferred. `tool/version-control/provisional --table` prints
what is registered and when each entry is next due.

Retire it when `exit-when` came true:

1. Delete the measure itself and every line tagged `PROV <scope>/<slug>`.
2. Delete `docs/provisional/<scope>/<slug>.md`, and the scope directory if that was
   its last entry.
3. Do both in one commit, classified as the entry's scope, with `repository`
   alongside for the supporting documents it deletes. The check refuses an
   entry no tag names and a tag no entry names, so half of this fails.

Extend it when `exit-when` has not come true and the measure is still the best
option:

1. Add a `reviewed: <YYYY-MM-DD> <why the horizon moved>` line to the prose,
   dated the day the review happened.
2. Move `review-by` to a date at most 180 days after that `reviewed:` date.
   The check measures the horizon from the later of `since` and the last
   `reviewed:` line, so an extension buys 180 days from the review, not from
   the original registration.
3. Say what changed since the last review. The `reviewed:` lines are the
   record of how long the measure has been about to end.

Promote it when the measure turned out to be the answer and is no longer
temporary:

1. Write a decision record through "Record a decision" below, saying what was
   learned and why the measure stays.
2. Delete the entry and every tag, as retirement does, and keep the code.
3. Whatever must now remain true of that code is an invariant, not a
   provisional entry; register it through "Add or change an invariant".

An overdue entry fails the check for a change in its own scope only, so a
change in another domain is never blocked by it. That is not a reprieve: the
next change to the owning scope stops until the entry is retired, extended or
promoted.

## Plan and verify work

Work with more than one acceptance criterion or more than one pull request
has a spec and a report. Any other change is a single pull request whose body
carries its evidence; an issue for it is optional. `docs/work/README.md` is
the format; this is the procedure.

1. Classify the outcome. The work item is `docs/work/<scope>/<slug>/`, and
   the spec has that one scope. Work whose outcome spans scopes is one spec
   per scope. An increment may classify differently from its spec, and its
   commit and pull request stay single-scope.
2. Write `spec.md`: the problem, the decisions with what was rejected, the
   increments — one for each evidence lane and scope the criteria need, not
   one for each step — and an `## Acceptance` table naming for each criterion the
   evidence lanes that must be verified. A criterion no check can decide
   names `review`. Set `review-by` to the date by which someone could tell
   whether the work is done. Argue a direction first in `study.md` when it
   needs a survey or a measurement, quoting each measurement with the date
   and the commit it was taken at.
3. Create `report.md` in the same commit, with one `pending` row per
   criterion. Before implementation, run
   `tool/version-control/work --working-tree docs/work/<scope>/<slug>` for
   read-only feedback on the new pair, including untracked files. This does
   not validate the proposed commit. When staging is authorized, stage both
   and run `tool/version-control/work --staged`; the hook runs that check too.
4. When implementation starts, open the execution issue. Its first line names
   the spec path; it holds the increments as a checklist and carries no
   acceptance criteria. Add `issue: #<n>` to the spec's header. A report
   issue that already exists — a bug, an upstream watch — links the spec and
   becomes the execution issue.
5. Work in increments, one branch and one pull request each. An increment is
   what one evidence lane verifies, not a step: the criteria an evaluation
   decides are one, the ones only a host decides are another. Its pull
   request carries what the verification produces — the report rows, written
   in a commit after the one the evidence was taken at, the status sentence,
   and the report's end when it verifies the last criterion. The spec and its
   report may be that pull request's first commit; they go ahead alone when
   the spec needs review first or the work is handed to another host or
   session. Gather what the spec owes in another scope into one pull request
   for that scope, and merge it before the spec's last pull request when a
   criterion rests on it. A pull request that carries only bookkeeping says
   in its body where its evidence was produced. Link the issue with
   `Refs #<n>`; a closing keyword is refused
   (`INV repository/no-closing-keyword`). Evidence is recorded per lane and
   never upgraded.
6. To change a criterion after the report exists, add a paragraph to the spec
   that opens `Amended YYYY-MM-DD` and names the criterion. The checker
   refuses a criterion removed or rewritten without one.
7. End the report as `done`, `abandoned` or `superseded`. The push to `dev`
   that carries it closes the execution issue with a comment linking the
   report (`INV repository/issue-closes-from-report`); nothing else closes
   one automatically, and `tool/version-control/audit-remote` reports an
   issue left open beside a terminal report. A durable rule the work produced lands
   in a decision record or an invariant that names the document as its
   source, never by citing the work item from a document that carries
   authority; `tool/version-control/design-citations` refuses that citation.

`docs/work/roadmap.md` states lanes and order, not schedule; change it when
the order of work changes. GitHub milestones are not used. A spec whose
`review-by` has passed while its report is pending is overdue:
`tool/version-control/work --overdue` lists it.

## Record a decision

Write a record when a choice is expensive to reverse or a reviewer will ask
why it was made. Add a file under `docs/policy/decisions/<scope>/` with the
header and format `docs/policy/decisions/README.md` defines; nothing lists it
by hand, `tool/version-control/records --table decisions` does.
Reversing a decision creates a new record, sets the old one to
`status: superseded` with `superseded-by`, and moves every pointer to it in
the same commit — the checker cannot tell a superseded record from a live
one. Prose and code cite a record by path only; a quoted heading is checked
by nothing and rots. Cite it from a registry entry with `decision:` when an
invariant rests on it.

## Observe before adding or removing

A sentence added to a policy document without a check behind it rots, and a
deletion is as easy to get wrong as an addition. Both pass through
`docs/policy/candidates/` first. `docs/policy/candidates/README.md` is the format; this is
the procedure.

1. Record what was met and where, not the rule you would like to exist.
2. Add a dated line under `Occurrences` each time the same thing is met
   again, with the evidence.
3. Promote when the criterion is met: make the change in its owning scope
   through the flows above and delete the candidate in the same pull
   request. The commit message names the candidate it promotes.
4. Drop when the date passes or the event occurs without promotion: delete
   the file. History is the record either way.

Two things do not wait: a change that is fatal on a host and invisible to
every gate, and the correction of tracked text that is false today. A
candidate is an observation. Nothing cites it as authority, and an agent
does not follow one as a rule.

## Unix-like changes

1. Put feature-oriented declarations under `unixlike/modules/`.
2. Put Unix-like source payloads in their owning Unix-like asset location.
3. Keep host composition in `unixlike/modules/flake/configurations.nix`.
4. Run narrow formatting, lint, evaluation, and native build checks.
5. Create a Unix-like release tag only after the required matching-host
   evidence exists, including a build of every configuration with
   `CHECKS_BUILD_ALL=1 unixlike/tool/checks/test` on a matching host.
6. Activate only when explicitly requested, from the intended Unix-like
   release.

Do not add Windows desired state to a Nix module merely because the same tool
also runs on Windows.

### Import the NixOS-WSL distribution

`just nixos-build <host>`, `just nixos-tarball <host>` (needs sudo) and
`just nixos-stage` produce the rootfs archive and copy it to a Windows drive;
`<host>` is the distribution's entry in the typed inventory of NixOS hosts,
and a recipe given no name, or one the flake does not export, refuses and
lists the names it does;
`docs/reference/troubleshooting.md` records why `wsl --import` will not read it from
`\\wsl.localhost\...`. Then, from PowerShell or CMD:

1. `wsl --import NixOS C:\WSL\NixOS C:\WSL\nixos.wsl` registers the
   distribution. Its first boot activates the toplevel and the composed
   home.
2. `wsl -d NixOS -u root -- passwd <account>` sets the account's password.
   The account is created locked and sudo asks for a password
   (`unixlike/modules/wsl.nix`), so until this has run nothing inside can become
   root; WSL's `-u root` needs no Linux authentication, and the password
   set this way survives every later activation.
3. If the host is to be reached over ssh, copy an `authorized_keys` into
   `\\wsl.localhost\NixOS\home\<account>\.ssh\`. Keys are host-owned
   (`unixlike/modules/ssh.nix`); the port is the one `unixlike/modules/sshd.nix`
   declares, and any mapping beyond the Windows host is Windows state.
4. `wsl -d NixOS`. The account logs into zsh, flakes are on, and
   `tool/doctor.sh unixlike` reports the host ready.

Rollback is `wsl --unregister NixOS`; Ubuntu is untouched throughout.

An import is how the distribution is created, not how it is updated:
"Update the registered NixOS-WSL distribution" below is the ordinary path,
and the archive still carries a default `/etc/nixos/configuration.nix` that
the cleanup step there removes.

### Update the registered NixOS-WSL distribution

The distribution is updated in place, from a clone of this repository inside
it, by the `nixos-test`, `nixos-switch`, `nixos-rollback` and
`nixos-generations` recipes. They act on the output named after the NixOS
host they run on and refuse where the flake exports none of that name, and
`just switch` refuses there, because it would
put the standalone Ubuntu home over the one the system composes. Home Manager
stays composed into the system, so a dotfile change is also a system switch
and needs `sudo`
(`docs/policy/decisions/unixlike/nixos-wsl-system-layer-ownership.md`). Activation
is the maintainer's to run: building and evaluating never imply it.

1. Inside the distribution, clone the repository once, and `git pull` in that
   clone for every update. `tool/doctor.sh unixlike` reports whether the host
   is ready.
2. Once per import, before the first switch from this flake: remove what the
   import left behind. The host is rebuilt from the flake alone
   (`INV unixlike/nixos-no-channel`), and nothing an activation does removes
   a channel or a configuration file that an import already wrote.

   ```sh
   sudo nix-channel --remove nixos-wsl
   sudo rm -rf /etc/nixos /root/.nix-channels /root/.nix-defexpr/channels
   sudo rm -f /nix/var/nix/profiles/per-user/root/channels /nix/var/nix/profiles/per-user/root/channels-*-link
   ```

   The distribution imported on 2026-09-06 registered a `nixos-wsl` channel,
   so run the first line there while `nix-channel` still exists: the switch
   that turns channels off removes the command. It answers `matched no
   installed derivations` where the channel was added and never updated,
   which is what an import leaves. An archive built after that switch
   registers no channel, and only the `rm` lines apply to it. The block
   carries no trailing comments on purpose: the account's interactive zsh
   does not read `#` as a comment and would pass the words on as arguments.
3. `just nixos-test` builds the system and activates it without making it the
   default, so a system that cannot start is gone at the next `wsl
   --terminate`. When it holds, `just nixos-switch` makes it the default, and
   `just nixos-generations` lists it.
4. If the change touched `/etc/wsl.conf` — anything under `wsl.*` in
   `unixlike/modules/wsl.nix` — run `wsl --terminate NixOS` from Windows and
   start the distribution again: WSL reads that file only at boot.
5. A rebuild that names no flake is expected to fail: `nixos-rebuild switch`
   stops on the search path, which carries no `nixos-config`. nixos-wsl's
   welcome text advises that command and `nix-channel --update`; neither
   describes this host.

Roll back with `just nixos-rollback`, which switches to the previous
generation; WSL has no boot loader to choose one from. It works only while
that generation still exists, and the store is collected weekly with
everything older than fourteen days (`unixlike/modules/nix/shared.nix`), so
that is the window. `just nixos-switch` after a rollback activates the
current configuration again. While that configuration is unchanged it is the
same generation again and not a further one: Nix reuses the highest-numbered
generation when it already holds the path, so the list shows a rollback only
between the two commands.

Importing again is recovery, not an update. It replaces the whole root file
system, so it loses `/home`, the account's password and
`~/.ssh/authorized_keys`; steps 2 and 3 of the import, and the cleanup step
above, are owed again afterwards.

### Install the UTM guest

The aarch64 guest on the Mac is installed by hand from the NixOS minimal ISO
and from this flake's `utm` output; partitioning and deployment tooling are a
later order of `docs/work/roadmap.md`. Everything here is the maintainer's to
run: an installation activates a system, and neither evaluation nor a build
implies it. An aarch64 system is only evaluated on the x86_64 hosts, so its
build, runtime and activation evidence comes from inside the guest and from
nowhere else.

1. In UTM, create a virtualised Linux machine (aarch64) that boots the
   aarch64 minimal ISO with UEFI: a VirtIO disk, the shared network, and a
   serial device, which is the console the guest is reached on before its
   network is (`unixlike/modules/host/utm.nix`).
2. In the installer, as root, create the two file systems under the labels
   the host is declared with. Nothing detected on the machine is stored, so
   the labels are the whole contract with the disk:

   ```sh
   parted /dev/vda -- mklabel gpt
   parted /dev/vda -- mkpart ESP fat32 1MiB 1GiB
   parted /dev/vda -- set 1 esp on
   parted /dev/vda -- mkpart root ext4 1GiB 100%
   mkfs.fat -F 32 -n boot /dev/vda1
   mkfs.ext4 -L nixos /dev/vda2
   mount /dev/disk/by-label/nixos /mnt
   mkdir -p /mnt/boot
   mount -o umask=077 /dev/disk/by-label/boot /mnt/boot
   ```

3. Confirm the inventory entry before anything is installed. `nixos-version`
   in the installer names the release of the installation medium; the `utm`
   entry of `unixlike/modules/flake/inventory.nix` carries that release as
   its `stateVersion`, not the pinned nixpkgs' if the two differ, and the
   account the guest is to have as its `user`. Correct either on a branch
   and install from that branch.
4. Clone the repository inside the installer (`nix-shell -p git`) and
   install from the clone. Root keeps no password, because sshd refuses root
   and the account reaches it through sudo:

   ```sh
   nixos-install --no-root-passwd --no-channel-copy --flake "path:./unixlike#utm"
   nixos-enter --root /mnt -c 'passwd <account>'
   ```

   `--no-channel-copy` leaves the live installer's channel available for
   tools such as `nix-shell -p git`, but does not copy its profile into the
   installed system. Turning channels off in the configuration does not
   remove a profile an earlier installation command already copied.

   The account is created without a password
   (`unixlike/modules/account.nix`), so until `passwd` has run nothing can
   log in or become root, and the password set this way survives every later
   activation.
5. Shut the guest down, remove the ISO in UTM and start it. Log in on the
   serial console with the password and put a public key in
   `~/.ssh/authorized_keys`; keys are host-owned
   (`unixlike/modules/sshd.nix`). From then on the guest is reached over ssh
   on port 22 with that key: sshd refuses a password, and the firewall admits
   no other port.
6. Clone the repository into the installed account's home, and run the
   recipes below from that clone as that account. If the installation used
   uncommitted inventory corrections, preserve them when transferring the
   clone; a fresh remote clone does not contain them. `just` is a Home
   Manager package for the account, not a root login-shell tool; the recipes
   invoke sudo where needed. `tool/doctor.sh unixlike` reports whether the
   host is ready.

If an earlier installation omitted `--no-channel-copy`, inspect the installed
system for root's `.nix-channels`, `.nix-defexpr/channels` and the channel
profile links under `/nix/var/nix/profiles/per-user/root`. Remove only those
channel registration files and links after confirming what exists. When
still in the ISO, these target paths are below `/mnt`; after booting the
installed system, they are below `/`. Do not remove the system profile or
Nix store paths. Re-running installation with `--no-channel-copy` prevents
another copy but does not remove an existing one.

The guest is updated in place from that clone with the recipes that act on
the output named after the running host: `just nixos-test` builds the system
and activates it without making it the boot default, `just nixos-switch`
makes it the default, `just nixos-generations` lists it, and
`just nixos-rollback` returns to the generation before. Unlike NixOS-WSL the
guest has a boot loader, so a generation that cannot start is also left
behind by choosing the previous one in the systemd-boot menu on the console.
Home Manager is composed into the system here too, so a dotfile change is a
system switch. A rebuild that names no flake stops on the search path, as on
every NixOS host of this repository (`INV unixlike/nixos-no-channel`).

Installing again is recovery, not an update: it replaces the root file
system, and steps 4 and 5 are owed again afterwards.

A guest that already runs NixOS — one installed with the graphical
installer — is adopted in place instead, which is how the present guest came
under this flake on 2026-09-20. Everything that follows changes the host and
is the maintainer's to run, from one root shell (`sudo -i`), because the
first switch removes the installer's account from under its own session:

1. Give root a password for the duration, so the console is a way back in
   under either generation, and lock it again (`passwd -l root`) once the new
   system has booted.
2. Relabel the file systems to the names the host is declared with:
   `e2label <root device> nixos`, and with `/boot` unmounted
   `fatlabel <EFI device> boot` (`nix-shell -p dosfstools`). The running
   generation mounts by UUID, so it still boots. `udevadm trigger --settle`
   and read `/dev/disk/by-label` before going on: a switch made while the
   root's label has not taken leaves a system that cannot find its root.
3. Set the `utm` entry's `stateVersion` to the release in the installed
   `/etc/nixos/configuration.nix`, on a branch, and clone that branch
   (`nix-shell -p git`). Then remove the installer's channel,
   `nix-channel --remove nixos`, while the command still exists.
4. Make the first switch by naming the output,
   `nixos-rebuild switch --flake "path:./unixlike#utm"`: the host still
   answers to the installer's name, so the host-bound recipes refuse.
5. In the same shell, `passwd <account>` and put a public key in the new
   account's `~/.ssh/authorized_keys`, owned by it; confirm a key login from
   another terminal before closing the shell or rebooting. The installer's
   account is gone, and the new one is created locked.
6. Reboot, log in as the account, remove `/etc/nixos`, the root channel
   files and the root clone, and clone the repository into the account's
   home. From there the update recipes above apply.

Do not roll back past the first generation of this flake: the installer's
generations hold no account this flake declares and recreate theirs without
a password. To exercise `just nixos-rollback`, make a second generation of
this flake first.

### Install the VMware guest

The x86_64 guest `vm` runs under VMware Workstation on a Linux or a Windows
host, and the procedure is the same on both
(`docs/policy/decisions/unixlike/x86-64-guest-runs-on-vmware-workstation.md`).
It is the UTM procedure above with `vm` for the output and the differences
below. Everything here is the maintainer's to run: an installation activates
a system, and neither evaluation nor the build the x86_64 hosts can make of
this output implies it.

1. Install VMware Workstation on the host by hand. No domain of this
   repository installs, configures or checks it.
2. Create a machine for a 64-bit Linux guest that boots the x86_64 minimal
   ISO, with the firmware type set to UEFI and secure boot off, before the
   first start: systemd-boot does not start from the BIOS firmware and is
   not signed. The disk controller and the network type are free — the
   initrd finds a SCSI, SATA or NVMe disk
   (`unixlike/modules/host/vmware.nix`), and NAT and a bridged network both
   hand out an address. The console is the machine's own screen; there is no
   serial device to add.
3. Follow steps 2 to 4 of the UTM procedure in the installer, with two
   changes. The disk is not `/dev/vda`: read its name from `lsblk`
   (`/dev/sda` on a SCSI or SATA controller, `/dev/nvme0n1` with partitions
   `p1` and `p2` on NVMe). The entry to confirm and the output to install
   are `vm`:

   ```sh
   nixos-install --no-root-passwd --no-channel-copy --flake "path:./unixlike#vm"
   nixos-enter --root /mnt -c 'passwd <account>'
   ```

4. Shut the guest down, disconnect the ISO and start it. Log in on the
   machine's screen with the password and put a public key in
   `~/.ssh/authorized_keys`; from then on the guest is reached over ssh on
   port 22 with that key, from the host or, on a bridged network, from the
   network the host is on.
5. Put the repository in the installed account's home and run its recipes
   as that account, as in the UTM procedure. Preserve any uncommitted
   inventory corrections from the installation clone. `tool/doctor.sh
   unixlike` reports whether the host is ready.

The guest is updated in place with the same recipes as the UTM guest, and a
guest that already runs NixOS is adopted in place by the steps stated there,
with `vm` for the output and the machine's screen for the console. The same
disk moved to the other host is the same guest; a second installation on
the other host is a second machine that answers to the same name.

### Activate the graphical profile on the VM guests

The installed VMware and UTM guests adopt the shared Niri and Noctalia
profile in that order. Everything in this section runs inside a guest and is
the maintainer's to run. Building and inspecting the candidate are read-only;
`just nixos-test`, `just nixos-switch`, reboot and rollback activate the guest
and each requires explicit authorization. Keep the hypervisor console open
and a second key-authenticated SSH session connected throughout the first
activation.

1. In the guest's repository clone, check out the reviewed ref and verify
   that the running host names the output it is about to build. Realise the
   complete candidate before any activation, then compare its closure with
   the current generation and read free space again:

   ```sh
   host=$(hostname)
   case "$host" in vm|utm) ;; *) printf 'not a graphical VM guest: %s\n' "$host" >&2; exit 1 ;; esac
   tool/doctor.sh unixlike
   df -h / /nix /boot
   candidate=$(nix build --no-link --print-out-paths "path:./unixlike#nixosConfigurations.$host.config.system.build.toplevel")
   current=$(readlink -f /run/current-system)
   nix path-info -Sh "$current" "$candidate"
   nix store diff-closures "$current" "$candidate"
   df -h / /nix /boot
   ```

   A successful build proves that this candidate is realised; it does not
   prove room for future generations. Continue only if the file system still
   has useful headroom while retaining the current generation for rollback.
   Do not garbage-collect to make the change fit: increase the virtual disk
   and its file system deliberately, then repeat the read-only block. Record
   the two `df` readings, candidate path and closure report as capacity
   evidence. The aarch64 UTM result must be built inside UTM or by another
   native aarch64 builder; an x86_64 evaluation is not that build evidence.
2. With activation authorized, run `just nixos-test`. It activates the
   candidate without changing the boot default. From the second SSH session,
   confirm the key-only route survived and no unit failed:

   ```sh
   just nixos-test
   test "$(readlink -f /run/current-system)" = "$candidate"
   systemctl is-active sshd greetd
   systemctl --failed
   ```

   On the hypervisor console, greetd must offer the Niri session. Log in and
   check the result from a terminal inside that session:

   ```sh
   niri msg outputs
   pgrep -a -u "$USER" niri
   noctalia config validate ~/.config/noctalia/config.toml
   noctalia msg panel-toggle launcher
   wpctl status
   nmcli general status
   ```

   Open WezTerm and Ghostty, exercise the Noctalia launcher and control
   centre, enter Korean text in a real graphical application, play audible
   output, and confirm the expected network connection. On VMware also read
   `systemctl status 'run-vmblock\x2dfuse.mount' vmware.service` and exercise
   any clipboard or pointer integration the host exposes. A command exiting
   zero does not replace observing the screen, input, sound or integration.
   If any check fails, keep the SSH session open, run `just nixos-rollback`,
   and do not make the candidate the boot default.
3. After the test activation holds, authorize and run `just nixos-switch`.
   Confirm that both the running system and boot profile name the candidate,
   then reboot from the hypervisor console:

   ```sh
   just nixos-switch
   test "$(readlink -f /run/current-system)" = "$candidate"
   test "$(readlink -f /nix/var/nix/profiles/system)" = "$candidate"
   just nixos-generations
   sudo systemctl reboot
   ```

   Enter through the console after reboot, repeat the graphical, Korean input,
   audio and network observations, and confirm a new key-authenticated SSH
   connection. If the new default does not boot, select the preceding
   generation in the systemd-boot menu.
4. Prove rollback while both generations remain. From the same reviewed
   source, move both system paths to the preceding generation, confirm the
   SSH route, then switch the intended graphical candidate back into place:

   ```sh
   just nixos-rollback
   rollback_target=$(readlink -f /run/current-system)
   test "$rollback_target" != "$candidate"
   test "$(readlink -f /nix/var/nix/profiles/system)" = "$rollback_target"
   systemctl is-active sshd
   just nixos-switch
   test "$(readlink -f /run/current-system)" = "$candidate"
   test "$(readlink -f /nix/var/nix/profiles/system)" = "$candidate"
   ```

   Record activation, reboot and rollback separately from the earlier build
   and runtime observations.

Finish these steps and record the VMware evidence before starting UTM. A
working graphical VMware guest is not evidence for aarch64 UTM rendering or
for UTM's native build.

### Install the AMD APU desktop

The physical x86_64 host `desktop` is installed by hand from the NixOS
minimal ISO and this flake's `desktop` output. Every command in this section
is the maintainer's to run. Partitioning irreversibly erases the selected
disk, installation activates a system, and evaluation or a build authorizes
neither action. Keep the installer booted in UEFI mode with secure boot off:
the declared systemd-boot loader is not signed.

1. Before changing a disk, inspect the machine and the installation medium:

   ```sh
   test -d /sys/firmware/efi && echo UEFI || echo BIOS
   nixos-version
   lsblk -o NAME,SIZE,TYPE,FSTYPE,LABEL,MOUNTPOINTS,MODEL
   lspci -nnk
   ```

   Stop if the first command answers `BIOS`. Confirm that the `desktop` entry
   in `unixlike/modules/flake/inventory.nix` names the account the installed
   host is to have and uses the installation medium's release as its
   `stateVersion`. Correct either on a branch before installation. The pinned
   nixpkgs release is not evidence for the state version.
2. Become root with `sudo -i`. Set `target_disk` to one whole disk, display it
   again, and require the exact confirmation before the first destructive
   command. Do not paste the block with `REPLACE_ME` unchanged:

   ```sh
   target_disk=/dev/REPLACE_ME
   test -b "$target_disk"
   test "$(lsblk -dnro TYPE "$target_disk")" = disk
   lsblk -o NAME,SIZE,TYPE,FSTYPE,LABEL,MOUNTPOINTS,MODEL "$target_disk"
   printf 'This erases every partition on %s. Type: erase %s\n' "$target_disk" "$target_disk"
   read -r confirmation
   test "$confirmation" = "erase $target_disk" || exit 1
   parted --script "$target_disk" -- mklabel gpt
   parted --script "$target_disk" -- mkpart ESP fat32 1MiB 1025MiB
   parted --script "$target_disk" -- set 1 esp on
   parted --script "$target_disk" -- mkpart cryptroot 1025MiB 100%
   partprobe "$target_disk"
   udevadm settle
   esp=$(lsblk -nrpo NAME,PARTN "$target_disk" | awk '$2 == 1 { print $1 }')
   crypt_partition=$(lsblk -nrpo NAME,PARTN "$target_disk" | awk '$2 == 2 { print $1 }')
   test -b "$esp"
   test -b "$crypt_partition"
   printf 'ESP: %s\nLUKS: %s\n' "$esp" "$crypt_partition"
   ```

   The two derived paths handle both names such as `/dev/sda1` and names such
   as `/dev/nvme0n1p1`. Stop if either path is empty or names an unexpected
   device.
3. Create the labels and subvolumes the configuration declares. The LUKS2
   passphrase is host state: choose it at the prompt, keep it outside the
   repository, and expect to enter it at every boot. There is no disk swap.

   ```sh
   mkfs.fat -F 32 -n boot "$esp"
   cryptsetup luksFormat --type luks2 --label cryptroot "$crypt_partition"
   udevadm settle
   test -b /dev/disk/by-label/cryptroot
   cryptsetup open /dev/disk/by-label/cryptroot cryptroot
   mkfs.btrfs -L nixos /dev/mapper/cryptroot
   mount /dev/mapper/cryptroot /mnt
   btrfs subvolume create /mnt/@
   btrfs subvolume create /mnt/@home
   btrfs subvolume create /mnt/@nix
   umount /mnt
   mount -o subvol=@,compress=zstd,noatime /dev/mapper/cryptroot /mnt
   mkdir -p /mnt/home /mnt/nix /mnt/boot
   mount -o subvol=@home,compress=zstd,noatime /dev/mapper/cryptroot /mnt/home
   mount -o subvol=@nix,compress=zstd,noatime /dev/mapper/cryptroot /mnt/nix
   mount -o umask=0077 /dev/disk/by-label/boot /mnt/boot
   lsblk -o NAME,SIZE,TYPE,FSTYPE,LABEL,MOUNTPOINTS,MODEL
   findmnt -R /mnt
   ```

4. Review the host's observed hardware before installing. Clone the exact
   branch or tag intended for installation with `nix-shell -p git`, then run
   the generator only as a probe:

   ```sh
   nix-shell -p git --run 'git clone -b <ref> https://github.com/shk95/configs.git /root/configs'
   cd /root/configs
   nixos-generate-config --root /mnt --show-hardware-config > /tmp/desktop-hardware.nix
   less /tmp/desktop-hardware.nix
   nix build --no-link "path:./unixlike#nixosConfigurations.desktop.config.system.build.toplevel"
   ```

   Compare the generated initrd modules, kernel modules, CPU support and file
   systems with the portable declarations in
   `unixlike/modules/host/desktop.nix` and `unixlike/modules/amd-apu.nix`.
   Do not copy the generated file or its UUIDs into the tree wholesale. If
   the machine needs a controller, kernel option or other fact absent from
   the portable base, stop and add only that reviewed fact through a
   Unix-like pull request; install from its reviewed branch after it builds.
5. Install from the reviewed clone and create the account's host-owned
   password. Root keeps no password:

   ```sh
   nixos-install --no-root-passwd --no-channel-copy --flake "path:./unixlike#desktop"
   nixos-enter --root /mnt -c 'passwd <account>'
   ```

   Shut down, remove the ISO, and boot the disk. The initrd must prompt for
   the LUKS passphrase before the graphical login appears. Log in on the
   console, put the public key in `~/.ssh/authorized_keys`, and confirm a key
   login before relying on ssh for recovery. The key is host state and never
   enters the repository.
6. Clone the same reviewed source into the installed account's home. Record
   evaluation, build, native runtime and activation separately. The first two
   can be repeated from the clone without changing the host:

   ```sh
   tool/doctor.sh unixlike
   just nixos-eval
   nix build --no-link "path:./unixlike#nixosConfigurations.desktop.config.system.build.toplevel"
   hostname
   nixos-version
   systemctl --failed
   nix shell --inputs-from path:./unixlike nixpkgs#pciutils --command lspci -nnk
   niri msg outputs
   wpctl status
   nmcli general status
   nix shell --inputs-from path:./unixlike nixpkgs#mesa-demos --command glxinfo -B
   nix shell --inputs-from path:./unixlike nixpkgs#vulkan-tools --command vulkaninfo --summary
   nix shell --inputs-from path:./unixlike nixpkgs#libva-utils --command vainfo
   ```

   Native evidence identifies the AMD display controller and `amdgpu` kernel
   driver, hardware rather than software rendering, a usable Vulkan device
   and VA-API driver, every connected display, Korean input in a real
   application, audible output, and the intended network connection. A
   command exiting zero does not replace observing the display, input or
   audio result.
7. Reboot once and repeat the LUKS unlock, login, display, input, audio and
   network observations. Test rollback only with explicit activation
   authorization. A system tag makes a distinct probe generation without a
   tracked source edit; `--no-reexec` keeps `nixos-rebuild --store-path` from
   trying the absent channel-era `nixos-config` path:

   ```sh
   rollback_before=$(readlink -f /run/current-system)
   rollback_probe=$(
     nix build --impure --no-link --print-out-paths --expr \
       'let f = builtins.getFlake (toString ./unixlike); p = f.nixosConfigurations.desktop.extendModules { modules = [ { system.nixos.tags = [ "rollback-check" ]; } ]; }; in p.config.system.build.toplevel'
   )
   sudo nixos-rebuild switch --no-reexec --store-path "$rollback_probe"
   test "$(readlink -f /run/current-system)" = "$rollback_probe"
   test "$(readlink -f /nix/var/nix/profiles/system)" = "$rollback_probe"
   just nixos-rollback
   test "$(readlink -f /run/current-system)" = "$rollback_before"
   test "$(readlink -f /nix/var/nix/profiles/system)" = "$rollback_before"
   just nixos-generations
   systemctl --failed
   ```

   A normal update uses `just nixos-test` before `just nixos-switch`, and
   `just nixos-generations` lists the paths.

If a new generation cannot boot, choose the previous generation from the
systemd-boot menu. If no installed generation boots, start the minimal ISO,
open and mount the existing layout, and enter it for repair:

```sh
sudo -i
cryptsetup open /dev/disk/by-label/cryptroot cryptroot
mount -o subvol=@,compress=zstd,noatime /dev/mapper/cryptroot /mnt
mkdir -p /mnt/home /mnt/nix /mnt/boot
mount -o subvol=@home,compress=zstd,noatime /dev/mapper/cryptroot /mnt/home
mount -o subvol=@nix,compress=zstd,noatime /dev/mapper/cryptroot /mnt/nix
mount -o umask=0077 /dev/disk/by-label/boot /mnt/boot
nixos-enter --root /mnt
```

From there, repair the source or make the earlier system profile current and
reinstall its boot entry. Repartitioning is recovery only when the encrypted
file system is intentionally being discarded; it is not an update or a
rollback.

### Create the OrbStack machine

The aarch64 OrbStack machine on the Mac is a sandbox: isolated, disposable,
and brought under this flake's `orbstack` output after OrbStack has created
it. Creating, isolating, restarting, switching, updating, rolling back and
deleting it all change a host and are the maintainer's to run; evaluation and
a build imply none of them.

1. Create the machine isolated, under the inventory's host name and from the
   image whose release the entry's `stateVersion` carries:
   `orb create --isolated nixos:25.11 orbstack`. An existing machine is
   isolated with `orb config set machine.orbstack.isolated true` and
   `orb restart orbstack`. Isolated, the machine mounts nothing of the Mac
   and gets no ssh agent; the network stays. Isolation is the OrbStack
   application's state and is not declared here.
   The account OrbStack creates is named after the Mac's, and the first
   switch keeps only the account the entry's `user` names, with immutable
   users: where the two differ, create the machine with `--user <user>`, or
   the switch removes the account OrbStack enters as.
2. Enter it with `orb -m orbstack`. The image has flakes off, a `nixos`
   channel, and neither `git` nor `just`. Clone the repository and remove
   the channel while the command still exists:

   ```sh
   nix-shell -p git --run 'git clone -b <ref> https://github.com/shk95/configs.git ~/configs'
   sudo nix-channel --remove nixos
   ```

   `<ref>` is the branch or tag to switch from. A plain clone checks out
   `master`, which carries a host only once a promotion has brought it there.

3. Make the first switch by naming the output; `nixos-rebuild` turns flakes
   on for itself:

   ```sh
   cd ~/configs
   sudo nixos-rebuild switch --flake "path:./unixlike#orbstack"
   ```

   The command exits with status 4 and that is expected from the image: its
   release and the flake's use different message bus implementations, and the
   reload of `dbus-broker.service` times out. The system is activated all the
   same, and the restart below settles it. OrbStack's agent, not sshd, is the
   way in, so the session survives the switch.
4. `orb restart orbstack` from the Mac, then read that the machine came back
   whole: `systemctl is-system-running` answers `running`,
   `systemd-binfmt.service` is still masked under `/run/systemd/system`, and
   no `binfmt_misc` is mounted. The kernel is shared by every OrbStack
   machine and by OrbStack's Docker (`INV unixlike/orbstack-shared-kernel`).
   Then remove what the image's channel left under root, which every later
   rebuild otherwise warns about:

   ```sh
   sudo rm -rf /root/.nix-defexpr/channels
   sudo rm -f /nix/var/nix/profiles/per-user/root/channels /nix/var/nix/profiles/per-user/root/channels-*-link
   ```

From then on the machine is updated in place from its clone with
`just nixos-test`, `just nixos-switch`, `just nixos-generations` and
`just nixos-rollback`, as the other NixOS hosts are. Roll back only to a
generation of this flake: the image's generations hold OrbStack's own
configuration. `/etc/nixos` is left in place on purpose. Nothing reads it —
the search path names the flake's nixpkgs alone
(`INV unixlike/nixos-no-channel`) — and it is the old side of the comparison
below.

After an OrbStack update, create a new machine and compare its
`/etc/nixos/orbstack.nix` and `/etc/nixos/configuration.nix` with the ones
kept in this machine, then carry any difference that OrbStack needs into
`unixlike/modules/host/orbstack.nix` and `unixlike/modules/account.nix`.
OrbStack generates those files outside the flake and says it will overwrite
them; the class declares by hand what they hold that OrbStack needs, and only
this reading finds a change. What the class leaves out on purpose is listed
in its header, so that it is not read as drift.

Recovery is `orb delete orbstack` and this procedure again, which takes
minutes; nothing in the machine is meant to be kept.

### Capture Karabiner drift

On the Mac, `just karabiner-check` reports whether the host still holds the
members `unixlike/modules/karabiner/` declares, and `just karabiner-capture`
reads drift that belongs in desired state back into the payloads and commits
it.

`apply` replaces the declared top-level keys wholesale. Before the first
activation on a Mac whose Karabiner state has not been captured, run `just
karabiner-check` and, on drift, `just karabiner-capture`, and switch from the
tree that carries the capture — `just darwin-switch` builds from `path:.`, so
it delivers the payloads in that working directory, not the ones on a branch
you have not checked out.

## Windows changes

Windows declarations, payloads, checks, and Apply logic live inside `windows/`
and are validated on native Windows.

1. Edit `windows/desired/manifest.json` for features, packages, and
   managed-file policy. Every package, managed file, the font, and the terminal
   delegation names exactly one declared feature; a new payload without one is
   rejected when the manifest loads.
2. Edit owned payloads below `windows/desired/files/`.
3. Update PowerShell under `windows/src/` when reconciliation semantics change.
4. Run native Windows tests and read-only host verification.
5. Create a Windows release tag only after the required native evidence exists.

Native read-only verification is:

```powershell
.\windows\win-env.ps1 setup-dev
.\windows\win-env.ps1 validate
.\windows\win-env.ps1 test
.\windows\win-env.ps1 check
```

`win-env.ps1` is the domain's one entry point: each verb runs one script under
`windows/tools/` (`setup-dev.ps1`, `check-desired-state.ps1`, `test.ps1`,
`bootstrap.ps1 -Check`) and returns that script's exit status unchanged, so
the evidence a verb produces is the script's; a command the script refuses
ends the run at 1. CI and the hooks run those scripts directly.

A branch that has not been pushed yet can still reach a native Windows
clone of this repository through the filesystem: in that clone, fetch the
branch from the Unix-like session's main checkout — never from a linked
worktree, whose `gitdir` file names a path Git for Windows cannot resolve —
check it out, run the commands above under that host's own `pwsh`, and
switch the clone back to its previous branch afterwards. Once the branch is
pushed, `origin` is the transport and no path across the boundary is needed.

`setup-dev.ps1` installs the contributor toolchain declared in
`windows/toolchain.json`, which is also what CI installs from, so local Windows
and CI use the same Pester discovery, scope, and assertion semantics and the
same Lua compiler. Without it the checks still run: a source whose parser is
absent is reported as unverified and the command exits 69, so Windows work
remains pushable from a clone that has not installed anything.

Apply is a deployment, not verification, and requires an explicit request:

```powershell
.\windows\win-env.ps1 apply
```

A host may deploy part of the manifest with `-Minimal`, `-Feature`, `-Add`, or
`-All`; `README.md` describes the selection model. Selection is host state and
is recorded in `state.json`, so a change to the feature model is a Windows
desired-state change while a host's chosen set is not. Report which selection
produced any `-Check` or Apply evidence, because a check that passed under a
minimal selection says nothing about the features it excluded.

A change made in an application's own UI moves back into desired state with
`.\windows\win-env.ps1 capture` (`windows/tools/capture.ps1`), which reads the
managed targets, writes only
this repository's payloads — a JSON payload pretty-printed to this
repository's two-space style — and ends at one confirmation before committing.
Preview it with `-WhatIf` first. It restates the guards of
`tool/version-control/commit` rather than calling it, including its branch
rule: it refuses on `master`, on a dirty index, and on a payload that already
has uncommitted changes, and never bypasses a hook. On `dev` it branches to
`feature/windows-capture-<feature>` from a freshly fetched `origin/dev` (or a
name given with `-Branch`) before it commits, reported in the plan before the
`[y/N]`, so a capture run on `dev` never leaves a commit on that protected
branch; on any other branch the commit stays there. Read its refusals rather
than working around them, and read the hook output under its commit: Git for
Windows runs the POSIX hooks natively, but a clone that has not set
`core.hooksPath` runs none of them.

Add `-Publish` and that same confirmation pushes the branch, opens one pull
request against `dev`, arms auto-merge and prints the pull-request URL. It is
the Windows copy of `--publish` above and behaves the same way: it never waits
on CI and never merges, a rejected push leaves every commit local on the named
branch, and nothing retries with a bypass. It requires `gh` authenticated for
github.com and `Allow auto-merge` on in the repository settings, and refuses
before writing anything if either is missing, if a pull request from the same
branch is open against another base, or if the remote already has the branch
the run would create; a pull request already open against `dev` from that
branch is armed unchanged. It pushes a branch rather than a commit, so it
lists whatever the branch already carries beyond `dev` before the `[y/N]`.
`-WhatIf -Publish` prints the branch, the title, the body and every command
and writes nothing. Promotion to `master` and release remain the flows above.

A capture's commit makes the host read as unchanged, so a rerun after a publish
that did not finish captures nothing. With `-Publish` that run resumes the
publish instead of stopping at "Nothing to capture": on a topic branch whose
every commit beyond `origin/dev` has the subject capture gives its commits and
changes only `windows/desired/**`, one confirmation (`Publish these commits?
[y/N]`) pushes the branch unless `origin` already has it at that commit, opens
or reuses the pull request against `dev`, and arms auto-merge. A branch whose
push was rejected, one pushed by hand with no pull request, and one whose
auto-merge was never armed all finish this way; run it on that branch. Any
other commit on the branch refuses the run, so push it and open the pull
request yourself. It never resumes on `dev` or `master`, and on `dev` it names
a local `feature/windows-capture-<feature>` branch that still carries commits.
The detached-HEAD, staged-change and uncommitted-payload refusals still apply.
The resumed pull request says its commits came from an earlier run, and when
nothing was pushed it says no pre-push hook ran rather than showing hook
output.

`windows/tools/test.ps1` leaves out the Pester cases that run `capture.ps1`
end to end in a child PowerShell, and says which ones it skipped. Set
`WIN_ENV_E2E=1` to run them; the `windows-latest` CI job does, so the merge
gate covers them and a local push stays quick.

## Common changes

Do not create common material by default. First show that independently owned
Unix-like and Windows implementations have stable, genuinely platform-neutral
semantics.

When common ownership is justified:

Until the domain exists, no path under `common/` classifies; the change that
creates it restores classification, dispatch and the gate job first, or the
first commit is refused as having no owning scope.

1. Put it under `common/`, not under either platform domain.
2. Document its contract, supported consumers, and exclusions.
3. Give it consumer-independent checks.
4. Release it with a `common-v...` tag. It deploys nowhere.
5. Adopt it later through a separate Unix-like or Windows change.

Copying is the default adoption mechanism. Record provenance when useful, but
the destination owns the copy and does not owe future byte equality. A direct
import requires a pinned common version and an explicit decision explaining
why the coupling is acceptable.

## Verify

Run checks in proportion to the affected domain.

For Unix-like changes:

```sh
unixlike/tool/checks/format
unixlike/tool/checks/lint
unixlike/tool/checks/payloads
unixlike/tool/checks/test
```

The fixtures that prove the Unix-like checks refuse what they must —
`unixlike/tool/checks/payloads-test`, `flake-test`, `composition-test`,
`eval-coverage-test`, `prerequisite-test` and `import-order-test` — run in
the CI unix job. Run one by hand when its check or its fixtures change.
`import-order-test` composes every host twice and is merge-gate only by
design (`INV unixlike/import-order-independence`).

`unixlike/tool/checks/payloads` parses every source payload declared in
`unixlike/payloads.json` with the tool that consumes it. Evaluation does not
cover them: Nix copies a payload into the store without reading it.

`unixlike/tool/checks/test` evaluates every declared Unix-like configuration
and builds configurations native to the current host when appropriate. Foreign
evaluation is not native build or activation evidence.

For Windows changes, run the native Windows commands above. Unix-like Nix
evaluation is not part of Windows verification.

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
tool/version-control/test
tool/version-control/invariants
tool/version-control/provisional
tool/version-control/domain-reads
tool/version-control/design-citations
tool/version-control/records
tool/version-control/audit
tool/version-control/audit-remote  # when gh is authenticated
tool/version-control/hook-evidence
```

`tool/version-control/audit --history` runs on every push and in the
repository-wide CI scan job, and judges committed history alone. It reads
`dev` and `master` as `origin/dev` and `origin/master` when those refs
exist, and the local branches only when they do not, so a local `dev` or
`master` that lags or leads its remote neither blocks a push nor lets one
through unchecked. A clone that has not fetched is judged against the remote
as it last saw it. Every local tag is still judged, including one the push
does not carry: a stray local `*-v*` tag still fails the push until it is
deleted. The full form, which also judges this clone — local branch names,
the hooks setting — and reads the local branches first, is a read-only look
by hand, because a clone's scratch branch is not a property of the change
being pushed. `tool/version-control/plan-release` checks reachability from
the local `master`, because it plans a tag this clone creates.

The history form also judges, through `.githooks/commit-msg`, the non-merge
subjects of the commits being published: the pre-push hook names the tips it
pushes, and CI names `HEAD`, which for a pull request is the merge GitHub
would make. A commit made without the hooks or with `--no-verify` therefore
fails the push that carries it, and the pull request, before it merges. A
commit on a branch the push does not carry is not judged.

### Desired-state hygiene

`tool/version-control/hygiene` scans the tracked tree for undeclared user and
host names, absolute home paths, tracked runtime state, and machine-unique
identifiers. It runs on every commit from `.githooks/pre-commit` beside the
secret scan and outside domain dispatch, and again in CI, because the invariant
is repository-wide rather than scoped to the domain being changed.

```sh
tool/version-control/hygiene
```

When it reports something, in order of preference:

1. Remove the value. A leaked value is desired state that names one machine.
2. If it is a user or host name that genuinely belongs in desired state,
   declare it in `unixlike/modules/flake/inventory.nix` first. That is a
   `unixlike` change and lands as its own change.
3. If it is a runtime artefact, delete it and add an ignore rule. The ignore
   rule alone changes nothing once the file is tracked; it has to leave the
   index too.
4. Only when the reported text is genuinely not what it looks like, add one
   `<path>`, tab, `<literal string>` row to `tool/version-control/hygiene.allow`
   with a comment giving the reason. Both halves of "one string at one path"
   are enforced, not conventions: an entry whose literal no longer occurs at
   its path fails the check and is removed together with the text it forgave,
   and an entry that forgives more than one line fails as the whole-file
   exclusion it is. Write a literal specific enough to name the occurrence.

Adding an allow entry is a governance change and is reviewed as one. There is
no operational bypass: `git commit --no-verify` skips every hook and leaves CI
to reject the same content.

A bare account name written into prose is not detectable and is not covered.
Reading prose in the diff for one is a manual obligation recorded in
`docs/policy/definition-of-done/`.

### Cross-domain reads

`tool/version-control/domain-reads` scans each domain's code in the index —
the flake, the modules and the Unix-like checks on one side, the Windows
scripts on the other — for a path that names the other domain's tree, with
comments stripped and payload trees left out. It runs on every commit beside
the hygiene scan and in CI, because a read across the boundary is a property
of two trees rather than of the domain being changed.

```sh
tool/version-control/domain-reads
```

When it reports something, copy what the other domain owns into the domain
that reads it; the destination then owns the copy (`docs/policy/architecture.md`,
"Default rule: keep implementations separate"). There is no allow list: a
read across the boundary has no legitimate form.

### Design citations

`tool/version-control/design-citations` scans the index for a citation of a
work item from authority-bearing files. It runs on every commit and in CI.

```sh
tool/version-control/design-citations
```

When it reports something, decide which of the two the sentence is doing. If
it says where work documents live, name the directory rather than a file:
`docs/work/` passes and `docs/work/<file>` does not. If it rests on the
document's argument, put the accepted rule in a decision record or invariant,
or register a temporary measure, and cite that instead. There is no allow list.

### Document indexes

`tool/version-control/records` refuses an area README — decisions, candidates
or work — that names one of the area's documents: a record or candidate by
its file name, a work item by its `<scope>/<slug>`. The list is printed from
the headers instead, so a new record never edits a repository file
(`INV repository/document-index-generated`). It runs on every commit and in
CI.

```sh
tool/version-control/records
tool/version-control/records --table decisions
```

Branch protection on `dev` and `master` requires the stable `Required checks`
job. That job fails unless classification and secret scanning pass and every
selected domain job succeeds. Conditional domain job names are deliberately
not branch-protection contexts because unselected domains are skipped.
