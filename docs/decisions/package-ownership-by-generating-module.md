# A package is owned by the module that configures it

date: 2026-09-03
scope: unixlike
status: accepted
source: 9f1e8ce:docs/status.md § Unix-like Home Manager and package ownership

A package is owned by the feature module that generates its configuration; a
package with nothing to configure is owned by the shared package list in
`homeManager.shared`, whether or not Home Manager offers a module for it
(`INV unixlike/package-ownership`, decided 2026-09-03 over the alternative of
enabling every available module, which would have been twelve behaviour
changes). A package belongs in a system module only when a service,
activation script, or root/system account needs it; installing the same
interactive package into both HM and `environment.systemPackages` is not a
way to make it more available. The Darwin system `EDITOR` therefore uses an
absolute Neovim store path while the user-facing Neovim package remains
HM-owned. The only identical derivations remaining in both final profiles are
`zsh` and `nix-zsh-completions`: nix-darwin contributes them for the global
shell initialization while HM contributes them for the portable per-user zsh
configuration. They are evaluator-owned requirements rather than duplicate
package-list entries.
