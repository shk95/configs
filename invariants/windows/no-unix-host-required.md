id: windows/no-unix-host-required
statement: The Windows checks and suite read only the Windows tree and run without the Unix-like toolchain.
rationale: docs/architecture.md § Windows domain
enforced-by: pending #124
owner: repository maintainer

The suite byte-compares a Unix-like payload (the WezTerm font list), and the
merge-gate job parses every PowerShell file in the checkout, which reaches a
Unix-like asset. Both are the violations #124 names from the repository
side; this side owns the fix to its suite. The suite already runs under a
Unix-like pwsh with graduated skips, so "without the Unix-like toolchain"
means without Nix, not without pwsh.
