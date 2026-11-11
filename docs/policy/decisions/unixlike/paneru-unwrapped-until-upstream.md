# Use the unwrapped Paneru package until upstream fixes permission attribution

Accepted on 2026-11-11 for the Unix-like Darwin module. The maintainer requested
the tested wrapper-free execution path and a local commit; host activation
remains a separate operation.

The pinned upstream module wraps every Lua-enabled package in a Bash script,
including when no additional environment variables are required. A native
macOS 26.7.3 comparison of Paneru 0.5.2 at input revision
`3efa72bb7bf791ba9009f9c5990e628d6ecd631a` showed that TCC attributed the
original daemon's Accessibility request to Nix Bash. Paneru-specific grants
were insufficient, while granting Bash access worked.

Skipping the empty wrapper and replacing it with a native wrapper were tested
independently. With Bash permission disabled and each Paneru executable granted
access, both loaded the existing Lua configuration, discovered 32 windows,
and answered state queries. Retesting the original wrapper still failed;
restarting the unwrapped variant succeeded again. The same original Mach-O,
Lua configuration, GUI launchd label, and Home Manager store-waiting shell were
used throughout. The results are published in
[karinushka/paneru#461](https://github.com/karinushka/paneru/issues/461).

The provider selects the unwrapped upstream package through the final-package
option's transformation hook, preserving upstream ownership of installation,
configuration delivery, and launchd. Lua remains compiled in. Both the CLI
and service receive the same package. Nonempty `extraPackages` or
`extraLuaPackages` are refused because their environment setup would otherwise
be discarded. Supporting them requires a separately verified native wrapper.

The provisional entry `docs/provisional/unixlike/paneru-unwrapped.md` defines
review and retirement. A Darwin flake check verifies that the service selects
a native Mach-O with LuaJIT; constructor probes refuse unsupported environment
additions. These checks do not establish TCC grants on a consumer host.
The prior runtime comparison establishes the behavior of the selected binary;
evaluation and build evidence for the committed configuration do not imply
consumer adoption or activation.
