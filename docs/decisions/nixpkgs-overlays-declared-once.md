# nixpkgs overlays are declared once for every flavour

date: 2026-09-05
scope: unixlike
status: accepted
issue: #175
reopen-when: A flavour needs an overlay the others must not see.

`modules/flake/nixpkgs.nix` already declares `nixpkgsConfig` once and reads it
from the standalone home's `pkgs` and from `nixpkgs.config` in
`flake/configurations.nix`, because a fact shared by every flavour that is
instead written per class drifts silently — that file exists because
`allowUnfree` had already drifted that way once. `nixpkgsOverlays` is the same
option for overlays: `lazyAttrsOf (functionTo (functionTo attrs))`, default
`{}`, keyed by name rather than by a list. Overlay functions are
`final: prev: {…}`, so the type nests two `functionTo`s around the `attrs`
they return; declaring it as a list would have worked identically for a
single-entry set, but a second overlay would then be merged in whatever order
`import-tree`'s directory walk collected the two feature files that
contributed them, and the merged `pkgs` — reaching every flavour through
`perSystem` and through `useGlobalPkgs` — would silently depend on file
naming. `INV unixlike/import-order-independence` (`tool/checks/import-order`)
is exactly the check that would start failing then; keying by name and reading
the option back with `attrValues` keeps the merge order name-deterministic
regardless of walk order, so the check keeps passing by construction rather
than by coincidence.

The option is consumed twice, the same way `nixpkgsConfig` is: `perSystem`'s
`_module.args.pkgs` in `nixpkgs.nix` reads it for the standalone flavour, and
`flake/configurations.nix` reads it into `nixpkgs.overlays` beside
`nixpkgs.config` in both the NixOS and the darwin module lists, because
`useGlobalPkgs` makes home-manager take the system's `pkgs` and refuses its
own `nixpkgs.*` options outright — the same reason `nixpkgsConfig` is read in
two places rather than one. This commit adds no overlay; the option's value is
`{}` on every flavour, so every host's toplevel derivation path is unchanged.
The alternative rejected is declaring an overlay inside a class module and
repeating it across the classes a flavour-specific package touches, which is
the exact duplication `nixpkgsConfig` was created to remove for `config` and
would recreate for `overlays`.

A flavour-specific overlay — the motivating case is a Darwin-only zellij
patch — still lands in this one option, not in a class module, and expresses
its restriction inside the overlay function itself (for example
`prev.lib.optionalAttrs prev.stdenv.hostPlatform.isDarwin { … }`), because the
option has no per-flavour axis: every overlay in `nixpkgsOverlays` reaches
every flavour's `pkgs`. `reopen-when` above names the case that would change
that: a flavour needing an overlay the others must not merely no-op through
but must not evaluate at all, which this shape cannot express without
threading a flavour name through the option.
