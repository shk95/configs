# PowerShell is configured per domain by copying

date: 2026-08-13
scope: unixlike
scope: windows
status: accepted
reopen-when: both implementations show stable semantics that would justify a common component
source: 9f1e8ce:docs/status.md § PowerShell 7 ownership
source: 9f1e8ce:docs/status.md § Windows authority split

PowerShell 7 is configured in both deployable domains without a cross-domain
runtime dependency. The Unix-like Home Manager feature owns the package and
the CurrentUserAllHosts profile for Linux, WSL, and macOS. Windows continues to
own its WinGet package declaration, managed profile payload, and profile hook.

Pester follows the same split. The Windows domain treats it as contributor
tooling: `windows/toolchain.json` pins 5.7.1 and `windows/tools/setup-dev.ps1`
installs it from the PowerShell Gallery, deliberately outside the manifest so
no user host reports drift for a test framework. The Unix-like domain, as of
2026-09-04, places the same version into every home from
`modules/powershell.nix`: nixpkgs carries no Pester, so the module fetches the
Gallery package by hash and lays it under the user module path pwsh searches
first. The two pins are independent copies. What this buys is local evidence:
`pre-push` on a Linux, WSL, or macOS clone runs the Windows suite under the
home's own pwsh and reports a result instead of an unverified 69, while the
`windows-latest` CI job remains the native merge gate.

The two profiles independently adopt the same small, platform-neutral
interactive policy: PSReadLine suppresses duplicate history entries, moves the
cursor to the end of a recalled history match, and uses history prediction when
the installed PSReadLine supports it. The policy runs only in an interactive,
non-redirected ConsoleHost and produces no output, because profiles may also be
loaded by SSH, Git, scp, and other protocols.

The copies remain locally owned and may diverge.

The Unix-like Zellij keymap was adopted by copying the Windows implementation.
The copies intentionally differ in platform-owned shell and session values and
have no synchronization dependency.

2026-08-13: Windows tests target Pester 5.7.1 through `windows/tools/test.ps1`.
The exact version is shared by local native verification and CI so Pester
discovery, scope, and assertion behavior cannot silently change with a runner
image. Test setup runs in `BeforeAll`, and assertions use the parameterized
Pester 5 syntax.
