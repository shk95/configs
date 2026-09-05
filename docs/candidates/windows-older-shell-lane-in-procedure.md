# Name the older-shell lane and its two scripts in the Windows procedure and evidence list

kind: addition
scope: windows
first-observed: 2026-09-05
target: CONTRIBUTING.md § Windows changes (which scripts stay within the shell the host ships); docs/definition-of-done.md § Windows domain (the lane as an evidence item)
promote-when: the fixture that holds the lane is found insufficient once, or either section is edited anyway
drop-when: no new occurrence by 2027-03-05

## Observation

The registry entry `windows/pre-bootstrap-shell-compatible` and its fixtures hold `win-env.ps1` and `tools/bootstrap.ps1` to the shell the host ships, because `apply` must run on a host that has no newer shell yet. The procedure and the evidence list do not name the lane; whether text is needed beside the fixture is the observation. A third place runs under the older shell and is not held: the module's elevated PowerToys stop launches `powershell.exe` with an encoded script.

## Evidence

- `windows/win-env.ps1` header; `windows/src/WinEnv.psm1`, the `Start-Process -FilePath 'powershell.exe'` call.
- Observed on 5.1.19041.7663: no verb 64, help 0, unknown 64, check 69, check -Force 1.

## Occurrences

- 2026-09-05: the lane was exercised by hand for #170; the fixture landed with the entry.
