# SDKMAN is adopted but not owned

date: 2026-08-16
scope: unixlike
status: accepted
source: 9f1e8ce:docs/status.md § Unix-like Home Manager and package ownership

SDKMAN is adopted but not owned. `homeManager.shared` sources
`$HOME/.sdkman/bin/sdkman-init.sh` only when that file exists, last in the zsh
`initContent`, because SDKMAN rewrites PATH and declarative packages must
keep precedence. Installing it stays with the user; there is deliberately no
package, activation script, or generated payload for it, and no bash or
PowerShell equivalent of the hook. The JVM toolchain is split on purpose:
`gradle` is a shared Nix package, while JDK distributions and their version
switching belong to SDKMAN. Declaring a JDK in Nix as well would put two
version authorities on one PATH, and the later SDKMAN initialization would
win. The Windows domain has no SDKMAN equivalent and needs none — SDKMAN is a
POSIX shell-function installer, so JVM work on a Windows host happens inside
a WSL Unix-like home. Its absence from `windows/desired/manifest.json` is a
decision, not a gap.
