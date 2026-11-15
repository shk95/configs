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

The initial provider selected the unwrapped upstream package through the
final-package option's transformation hook, preserving upstream ownership of
installation,
configuration delivery, and launchd. Lua remains compiled in. Both the CLI
and service receive the same package. Nonempty `extraPackages` or
`extraLuaPackages` were refused because their environment setup would otherwise
be discarded. Their retirement follows upstream adoption below.

The former provisional entry recorded review and retirement conditions. A
local Darwin flake check verified a native Mach-O with LuaJIT; constructor
probes refused unsupported environment additions. Such checks do not establish
TCC grants on a consumer host.
The prior runtime comparison establishes the behavior of the selected binary;
evaluation and build evidence for the committed configuration do not imply
consumer adoption or activation.

## Upstream adoption and retirement

The provider adopts upstream
[ec21fb5](https://github.com/karinushka/paneru/commit/ec21fb5eae97a2af942a7dfb737d027663e3f460),
Paneru 0.5.3. The lock records this exact revision alongside the existing
Paneru source declaration. Upstream skips an empty wrapper and uses
makeBinaryWrapper when executable or Lua paths are added.

The local finalPackage transformation from `d97fc92`, its extra-path refusal
probes, temporary native check and provisional registration are removed
together. The current Lua payload and upstream service integration remain.
Existing commits and release declarations are preserved; this is a forward
adoption and retirement change, not a rewrite of master history.

The 0.5.3 package at `ec21fb5` was tested on 2026-11-15 on macOS 26.7.3,
Apple Silicon, through Home Manager's sh/wait4path/exec launch stage and the
current Lua payload. Both cases used the unmodified upstream module.

| Case | Nix Bash access | Accessibility subject/decision | Runtime after initialization |
| --- | --- | --- | --- |
| No extra arguments | off | Raw Paneru, authValue=2 | Current Lua loaded; query returned eight windows |
| Extra Lua arguments | off | Paneru native wrapper, authValue=2 | Extra Lua module and current Lua loaded; query returned eight windows |

Requests and decisions were correlated in TCC logs. The extra module was
required inside the daemon, verifying that nonempty Lua wrapper arguments
were used. The new raw/native paths each needed a Paneru-specific grant;
existing grants for older executable paths did not cover them. Both test
grants were disabled afterward and the original service/plist was restored.
The other existing grants were preserved. Temporary test source, raw logs and
query snapshots remain in private Git metadata rather than this commit.

Evaluation and focused native package builds passed, as did the full provider
suite. These runtime observations cover initialization, Lua/module loading and
window-state queries. No Home Manager or nix-darwin generation was activated.
The upstream adoption satisfies the former provisional measure's exit condition.
