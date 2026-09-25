# Definition of done: Windows

The checklist a Windows change owes on top of `repository.md` beside this
file, which every change owes.

- [ ] The change is owned and semantically validated by the Windows domain.
- [ ] `windows/win-env.ps1 validate`
      validates the manifest and every PowerShell, JSON, INI, KDL, and Lua
      source with native tooling, and names any source it had no parser for
      instead of failing or skipping it.
- [ ] Pester passes under native PowerShell when reconciliation behavior changed.
- [ ] `windows/win-env.ps1 check` is
      observed on native Windows when package detection, target paths,
      registry behavior, fonts, configuration parsing, or application
      lifecycle behavior changed.
- [ ] The feature selection that produced the observed evidence is named. A
      check that ran under a partial selection is evidence for that selection
      only and reports the rest as not selected, never as verified.
- [ ] The Windows build the observation ran on is named beside it, and each
      item of the Windows 10 support boundary table in `docs/status/windows.md` is
      reported in its boundary state — unverified below the boundary, never
      verified there (INV windows/support-boundary-named).
- [ ] Missing native tooling is reported as unverified rather than valid, and
      reaches its caller as exit status 69 rather than as a failure.
- [ ] Apply is run only when explicitly requested, followed by another
      read-only check.
- [ ] A `windows-v...` tag is assigned only after required native evidence is
      available.
- [ ] The source change lives in `windows/desired/`, `windows/src/`, Windows
      tests, or Windows-native tooling rather than a Nix module.
