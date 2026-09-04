# Homebrew owns Mac App Store and macOS GUI applications

date: 2026-08-12
scope: unixlike
status: accepted
source: 9f1e8ce:docs/status.md § Unix-like Home Manager and package ownership

Homebrew owns Mac App Store applications, macOS GUI applications, and the few
command-line tools that cannot use the shared Nix package. In the current
lock, `bettercap` is broken on Darwin, so Homebrew owns it on macOS while
shared HM installs it on Linux. Ghostty is another intentional split:
Homebrew owns the macOS application and HM owns its cross-Unix configuration
with `programs.ghostty.package = null` on Darwin.
`homebrew.onActivation.cleanup` is explicitly `"none"`; the generated
Brewfile is an install/upgrade inventory, not an exclusive declaration that
removes manually installed items.
