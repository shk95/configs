# Hooks run under Git for Windows

date: 2026-08-31
scope: repository
status: accepted
issue: #77
issue: #79
source: 9f1e8ce:docs/status.md § A JsonSubset payload is captured by projection

One thing this repository did not know until the maintainer's host answered it:
whether the POSIX shell hooks under `.githooks` run under Git for Windows. They
do. The maintainer's first hook-gated commit there (#77, `capture.ps1`, git
2.50.1.windows.1) exercised `core.hooksPath` and ran `.githooks/pre-commit`
under Git for Windows' `sh`, which found and ran
`tool/version-control/hygiene` and the rest of the local check chain the same
way a Unix-like clone does. The one incompatibility that surfaced was not
missing hook support: MSYS argument conversion silently rewrote a leading-`/`
argv element before a native binary saw it, which made the stale-entry check
in `tool/version-control/hygiene` search for a mangled string and reject a
clean commit (#79). Every governance script that passes such an argument to a
native binary now disables that conversion (`MSYS_NO_PATHCONV` and
`MSYS2_ARG_CONV_EXCL`, both inert on every other platform), so a Windows
commit through the hooks reaches the same verdict a Unix-like one does.
`capture.ps1` still reports whether `core.hooksPath` is `.githooks` rather than
assuming it, because hooks stay opt-in per clone regardless of platform.
