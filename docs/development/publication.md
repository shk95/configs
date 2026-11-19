# Publish and maintain history

For local orientation use `tool/configs workflow inspect`. The release
controller's `tool/configs release inspect`, when `CONFIGS_RELEASE_ENABLED=1`,
refreshes origin/tags and reads hosted PR/check state; it may fetch a patch
head and write synthetic merge-tree objects. It is not a local-only query.
Its `advance`, `publish` and `refresh-pr` operations have separate write effects.
Use them only for the requested release operation, not to prepare ordinary work.

## Candidate CI without a PR

Push a named topic only when requested, then explicitly dispatch CI on master
with the reviewed full `base` and `head` inputs. The head must already be
available in this repository; the base must still be current master and an
ancestor of the candidate. The CI workflow explicitly limits its token to
Contents read, grants PR read only to the topic metadata job, and disables
checkout credential persistence. Candidate code receives no write capability.

```sh
gh workflow run ci.yml --ref master -f base=<full-master-SHA> -f head=<full-candidate-SHA>
# Verify only:
tool/configs workflow check --base <full-master-SHA> --head <full-candidate-SHA> --ci-run <run-id>
# Or verify and integrate when authorized:
tool/configs workflow merge --base <full-master-SHA> --head <full-candidate-SHA> --ci-run <run-id>
```

The shared reader verifies the live run and attempt, workflow revision and
file, base, head, checkout, tree, and selected job results and runner platforms.
It verifies selected steps that can be skipped within a job. When the
workflow differs from the reviewed base, it also verifies that the required
execution units ran successfully and rejects `continue-on-error`.
The artifact name includes its attempt. Use a complete CI run or rerun all jobs
to refresh the evidence. A dispatch uses the reviewed master's workflow. For a
candidate that changes the workflow file, use same-repository PR CI to exercise
that definition. `workflow check` prints the accepted evidence.
`workflow merge` also rechecks the
destination, clean state and resulting tree. A changed master requires new
combined-result verification.
The `windows:runtime` unit requires hosted proof for CI acquisition and
controller behavior. The `repository:windows-git` fixture also runs locally
with Git for Windows and its shell. Local native Windows validate/test supply the domain
suite for ordinary Windows inputs. Settings changes select their owning
platform's suite. Focused local settings checks are described in
[Development feedback](verification.md#development-feedback-before-a-commit).

## GitHub integration

Master accepts direct commits and topic no-ff merges. CI runs on master push
and optional same-repository topic PRs. A push checks its own incoming history
and repository policy. It can reuse a PR's Unix-like or Windows provider suite
when the pushed commit has the reviewed PR parents and identical tree and
workflow. An unavailable proof runs the suite. Repository fixtures and the
Windows runtime-controller unit run when selected. The stable `Required
checks` result remains required evidence for the bounded automated patch writer.
Master protection applies to administrators and disallows deletion. Ordinary
credentials cannot force push; the optional reviewed maintenance App is the
sole force exception. Master has no mandatory PR, status-check or conversation admission. Hosted PRs
use merge commits only; squash and rebase merging remain disabled.

Prepare policy and tools locally before explicitly migrating remote protection.
`tool/configs audit-remote` reads actual settings when remote inspection is
requested. It never repairs them. Changing source does not change GitHub
settings. Retired dev may be retained; review preservation before separately
authorized deletion. There is no dev-to-master promotion or automatic cutover.

## Explicitly approved history maintenance

Ordinary pre-push rejects non-fast-forward branch updates even when the Git
command includes a force flag. No local `--approved` switch bypasses it.
Read-only preparation is `tool/configs history-rewrite plan --old <full-SHA>
--new <full-SHA> --reason <reason>`. Planning is not execution permission.

For an authorized exception, dispatch `history-rewrite.yml` on master with
immutable old/new/reason inputs. Review the displayed plan and uploaded
`history-recovery` bundle before a human approves the `history-rewrite`
environment. The protected job mints the dedicated App token and the executor
checks the live approval, first run attempt, accepted tooling, declared App,
unchanged remote old SHA and bundle hash. It scans the incoming history for
secrets, pushes only the specified master ref with an explicit expected-old
lease, and confirms actual remote state.
Protection is never disabled or edited. Published domain tag ancestry stays.
A failed/ambiguous result preserves recovery and does not authorize another
operation. A new target or retry requires a new reviewed dispatch.

Adoption is separate and requires explicit authorization to change remote
settings. The supported personal/public repository path combines classic
protection with a branch ruleset:

1. Keep classic force disabled while preparing the dedicated App and reviewed
   environment. Declare its public IDs through policy.json's variable names;
   keep its private key only in that environment. Require individual human
   reviewers without administrator bypass and admit only the exact master
   branch, with no wildcard branches or tags.
2. Install the named active branch ruleset from policy.json for exactly
   `refs/heads/master`, with only `non_fast_forward`, no extra conditions and
   one bypass actor: the declared App's numeric ID as `Integration`, mode
   `always`. No other effective or inherited ruleset is admitted by this
   contract. Verify this restriction before enabling classic force; retain
   classic administrator enforcement and deletion denial.
3. Grant the App only Contents write, Actions read, Administration read and
   Variables read. The protected workflow requests that same limited token.
   GitHub's implicit Metadata read permission is also allowed.
   These grants support source writes and the live run/approval, protection,
   ruleset and variable reads. Do not increase write privileges merely to
   bypass a failed preflight.
4. Run `tool/configs history-rewrite preflight --app-slug <declared-app-slug>`
   and `tool/configs audit-remote` with the intended
   credentials. They require visible bypass actors and exact effective rules;
   missing metadata or permissions refuse. Qualify the approved live path
   separately before claiming operation. To retire the exception, disable
   classic force first, then remove the ruleset or App capability.

Ordinary tools must have no access to the App key. Neither planning nor
preflight performs a write or grants execution approval. The executor never
edits protection. Administrators able to change server settings remain a trust
boundary; the rule is not an OS or credential sandbox.

GitHub's [ruleset creation contract](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)
supports the App bypass on a public personal repository. The
[ruleset read API](https://docs.github.com/en/rest/repos/rules#get-a-repository-ruleset)
can hide bypass actors from callers without sufficient access; a hidden list
is unavailable evidence. Source preparation and simulated API fixtures do not
qualify the actual installed App or hosted execution.

## Bounded scheduled release

`.github/workflows/release.yml` is the shared Unix-like input patch workflow.
`CONFIGS_RELEASE_ENABLED=1` enables operation; `CONFIGS_RELEASE_SCHEDULE_ENABLED=1`
also enables its daily 01:17 Asia/Seoul schedule.
Configure release-control for accepted master writers and either the existing
CONFIGS_RELEASE_TOKEN or CONFIGS_RELEASE_APP_ID and CONFIGS_RELEASE_APP_PRIVATE_KEY.
The writer needs Contents/PR write and Actions/Checks read with protected merge
permission; no bypass. Candidate execution has no writer credentials. No general
release approval or Windows operation belongs to this path.

### Change the CI proof format

Finish any pending patch with the current writer. The maintainer sets
`CONFIGS_RELEASE_ENABLED=0`, lets active writers finish, and runs
`tool/configs release inspect --upgrade-readiness`. Once it reports ready,
adopt the new format and resume the writer.

### Input patch operation

The workflow selects current master and refreshes nixpkgs, home-manager,
nix-darwin and nixos-wsl. Unchanged inputs produce no PR or tag. Changed inputs
produce one single-commit branch feature/unixlike-input-patch-<base SHA prefix>
with only the lock and the next patch release declaration. The writer scans
both files and the commit message before the first remote API write. It opens a master PR,
requires matching PR CI proof from the shared reader, and rechecks the current
PR body and head. The writer creates a merge commit with the exact reviewed
parents and tree and sends it through a protected fast-forward Git update. The
push hook compares the receiver's advertised `master` to the reviewed base.
The receiver compares that old object while applying the ref update. The writer
confirms the delivered commit and waits for GitHub's PR merge association before
tagging. The immutable Unix-like tag names the verified CI run and
attempt. Completion of same-repository PR CI wakes the planner. The shared
proof reader determines whether the patch may advance. Delayed or missing
schedules have no guaranteed catch-up.
Ready master topics reserve the destination. Unrelated Draft PRs allow the
patch to proceed. A draft input patch waits for its author to mark it ready.
The patch still needs current master and exact proof before the writer merges.

Master Unix-like configuration source must match its published release before
input patching; finish any unpublished development release first.

The writer refuses ambiguous managed PR state. A moved master makes an
unmerged patch stale; preserve it for inspection and restart explicitly.
Ordinary development commits directly to master or merges a checked topic.
Development release versions and tags remain the maintainer's responsibility.

### Manual operation and recovery

Choose Actions → Manual Unix-like input patch → Run workflow → master or run:

```sh
gh workflow run manual-release.yml --ref master
```

REST clients POST to /repos/shk95/configs/actions/workflows/manual-release.yml/dispatches
with ref=master and Actions write permission. The thin manual entry calls the same
shared workflow and waits in its writer job up to 60 minutes, polling every
30 seconds. Failure/cancellation of checks, stale candidates and expired waits
stop visibly while preserving the PR. Scheduled inspection defers to active manual
runs; cancel unwanted runs rather than leaving them pending. Both entry points
serialize writer jobs and preserve already completed remote work.

On failure inspect current PR/check state, repair the source or rerun transient
CI failure, then rerun the whole workflow or dispatch again. If master moved
before patch merge, close the stale patch PR and restart from current master;
the automation never rebases or merges a stale patch. If an orphan branch at the
same base conflicts with the intended lock, inspect and explicitly retire it
before retrying. Existing matching branches/PRs are reused after ambiguous writes.

A known missing patch tag is completed before a new refresh. Reruns verify
existing targets and annotations and create only missing tags. The planner
finds the original patch merge on master's first-parent history when its
Unix-like source is still current, including after repository-only changes.
If newer Unix-like work has landed, dispatch Unix-like input patch with
`source=<original full merge SHA>`. Recovery requires a reachable input
patch merge and its exact PR CI proof. Use `tool/configs release inspect`
for diagnosis and `tool/configs release publish --source <SHA>` for explicit
publication recovery.

Current PRs/Actions/tags are the execution record, with no state database or result
copy commit. Report manual qualification separately from actual schedule events.
