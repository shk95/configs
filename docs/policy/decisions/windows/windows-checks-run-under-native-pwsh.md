# Windows checks run only under the host's own pwsh

date: 2026-08-31
scope: windows
status: accepted
source: 9f1e8ce:docs/status.md § Windows authority split

Local hooks are a Windows evidence source, but only under the `pwsh` that
belongs to the host running them (#113). `modules/powershell.nix` installs a
Unix-like `pwsh` into every home this repository configures, so `pre-push`
runs `check-desired-state.ps1` and `windows/tools/test.ps1` directly under
it on a Linux or macOS clone, including WSL — where a `pwsh.exe` is also
reachable through Windows interop but is never used for this, because Windows'
script execution policy refuses an unsigned script reached that way. `pre-push`
detects an actual Windows host the same way `tool/version-control/commit`'s
`--publish` guard does (`uname -s` reporting `MINGW*` / `MSYS*` / `CYGWIN*`,
Git for Windows' own `sh`) and only there reaches for `pwsh.exe`. A host
with neither pwsh reports the Windows checks as unverified rather than failing.
