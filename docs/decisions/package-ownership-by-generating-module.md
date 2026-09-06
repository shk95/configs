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

Extended 2026-09-06 (#190): NixOS contributes `zsh` to its system profile for
the same evaluator-owned reason nix-darwin does, reached from the other
direction — declaring an account's login shell is what installs that shell
system-wide, and the NixOS-WSL host declares one (`modules/wsl-shell.nix`),
while Home Manager contributes zsh for the per-user configuration. Only the
shell is duplicated there; `nix-zsh-completions` is not, because nothing on
that host enables the NixOS zsh module. Read back on the host after the
first activation.

Extended 2026-09-06 (#195): "the shared package list" names the class through
which a package with nothing to configure reaches every home. A package meant
for one home only is declared once, in a class the composition file gives
that home alone (`homeManager.agents`, `modules/agents.nix`). The rule's
substance — one declaring module — is unchanged; the class, not a second
list, decides where the package reaches
(`docs/decisions/home-manager-platform-classes.md`).
