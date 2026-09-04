id: windows/no-unix-host-required
statement: The Windows checks and suite read only the Windows tree and run without the Unix-like toolchain.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

The suite used to byte-compare the Unix-like WezTerm font list, which made
a Unix-like edit fail Windows evidence; that case is gone, and the Windows
copy is held to the Windows manifest alone, because similarity between
independently owned copies is never a failure. The fixture scans every
script under the Windows tree as PowerShell tokens and refuses a string, a
bare argument, or a token nested in an expandable string that names a
Unix-like root — the payload and module trees, the flake, its checks — so a
comment that mentions one is not a read and a new script is covered on
arrival; a path built at run time from pieces is the one shape a lexical
scan cannot see. The repository's own git metadata, resolved from the repository
root for the applied-commit record, is repository state rather than another
domain's tree. "Without the Unix-like toolchain" means without Nix, not
without a PowerShell: the suite already runs under a Unix-like pwsh with
graduated skips. The merge-gate job's own repository-wide parse loop is the
repository side of #124.
