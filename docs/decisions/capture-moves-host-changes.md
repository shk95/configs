# Capture moves a host change into desired state

date: 2026-08-30
scope: windows
status: accepted
issue: #73
issue: #77
source: 9f1e8ce:docs/status.md § Capture moves a host change into desired state
source: 9f1e8ce:docs/status.md § A JsonSubset payload is captured by projection

Every direction between this repository and a Windows host ran one way until
now. `bootstrap.ps1 -Check` reported `<id> settings` drift and Apply overwrote
the host from the payload; moving a change the other way was manual, which meant
finding the target, copying it under `windows/desired/files/`, restoring
placeholders by hand, remembering which files are runtime state, and writing a
commit. `tool/version-control/hygiene` and the payload assertions in the Pester
suite catch the mistakes that work invites; neither does the work.

`windows/tools/capture.ps1` does it, and it is a copy of the shape of
`tool/version-control/commit` rather than a caller of it. The Windows domain
must stay authorable and deployable without a Unix-like host and the
maintainer's two clones are separate checkouts, so the guards are restated in
PowerShell: refuse on `master`, refuse a dirty index, refuse a payload that
already has uncommitted changes, never bypass a hook, and end every run at one
interactive confirmation with no unattended mode. The branch rule is restated
too (#77, after the maintainer's first real capture landed a commit on `dev`,
which is protected and had to be moved by hand): on `dev`, fetch `origin/dev`
and branch to `feature/windows-capture-<feature>` from it before committing; on
any other branch, commit where it is. A captured JSON payload is also
pretty-printed to this repository's two-space style before it is written,
regardless of how the host application wrote it, so the diff the operator
confirms at the `[y/N]` prompt is the diff a reviewer reads. The decisions live
in `windows/src/WinEnv.psm1` where they have fixtures; the script owns only what
needs a terminal and a Git repository.

Drift is decided by `Test-WinEnvManagedFile`, the function `-Check` uses, and
the payload variant by `Resolve-WinEnvManagedFile`. A second comparison
implementation would eventually disagree with the first, and the failure would
be a capture that reports as changed what the check reports as clean.

2026-08-31: A ranking decision is worth recording. A build-conditional entry on
a host whose build is undetermined is refused outright, which is stricter than
Apply: Apply reads a null build as the variant every supported build honours,
and that is safe because it deploys the lower payload, while capture writing
host content into a payload no host selected would put one machine's state into
a file another machine deploys.

2026-08-30: Three rules earned their shape from review rather than from
design. The account-path refusal
carries the same three axes `tool/version-control/hygiene` enforces
repository-wide -- a drive-letter path in either separator, the POSIX form, and
the WSL UNC form -- because a Windows Terminal starting directory or a WezTerm
setting routinely holds a WSL path, and the account-name refusal only backstops
a leak that names this host's own account. Capture does not lean on the commit
hook for that check, because hooks stay opt-in per clone: a fresh clone with
`core.hooksPath` unset must refuse the same leak the hook would have caught. The
generated-profile rule drops a host profile with no usable guid and refuses a
capture whose kept profiles repeat one, because either shape written into a
payload makes every later `-Check` and Apply throw instead of reporting drift,
and a payload that cannot be compared is worse than the drift it came from. And
a capture whose payload text equals the one already committed is reported as
nothing to commit rather than carried into the commit path, where an empty `git
add` would make `git commit` fail and read as a hook rejection: the host drifted
in a way desired state cannot express, and saying that is the whole answer.

Evidence is split accordingly. The Unix-like Pester run covers every rule just
listed, including the branch rule against a throwaway repository and bare
remote, and is not Windows evidence: the fixtures hand the module a host no
machine has to be. What is owed from the maintainer's host is one real capture
after a change made in an application's own UI, showing the branch line in the
plan and a readable diff, and the hooks' behaviour on that host.
