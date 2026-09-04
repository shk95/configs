# Home Manager platform classes are overlays

date: 2026-08-12
scope: unixlike
status: accepted
source: 9f1e8ce:docs/status.md § Unix-like Home Manager and package ownership
source: 9f1e8ce:docs/status.md § Unix-like desktop boundary

Every current Unix-like home imports `homeManager.shared`: standalone Home
Manager on Ubuntu WSL, Home Manager embedded in NixOS-WSL, and Home Manager
embedded in nix-darwin. Shared modules own portable shell behavior, configured
programs, and interactive command-line packages. The platform classes are
overlays, not parallel implementations:

- `homeManager.wsl` contains behavior required by both WSL flavours;
- `homeManager.wslStandalone` supplies the account and Nix settings that a
  system integration would otherwise supply;
- `homeManager.desktop` contains graphical Unix-like programs;
- `homeManager.darwin` contains macOS-only user behavior.

`homeManager.shared` contains portable command-line behavior, not every
program that happens to run on more than one Unix-like kernel. Graphical
terminal emulators belong to `homeManager.desktop`, which Darwin consumes and
both WSL outputs omit. A future graphical Linux configuration can adopt the
same class without turning WSL into a desktop host by implication.

Ghostty keeps its native `xterm-ghostty` terminfo locally. Its shell
integration tries to install that entry on SSH destinations and falls back to
`xterm-256color` only when the destination cannot accept it. Globally
downgrading `TERM` would hide capabilities on every host to accommodate the
few that need a fallback.
