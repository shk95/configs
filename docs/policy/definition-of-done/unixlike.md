# Definition of done: Unix-like

The checklist a Unix-like change owes on top of `repository.md` beside this
file, which every change owes.

- [ ] The change is owned by the flake, a Unix-like module, or a Unix-like
      payload rather than a cross-platform abstraction.
- [ ] The affected Home Manager, NixOS, or nix-darwin toplevel derivation
      evaluates.
- [ ] A native build is performed on a matching system when sources or packages
      changed.
- [ ] Foreign evaluation is reported as evaluation, not native build evidence.
- [ ] Every source payload is declared in `unixlike/payloads.json` and parsed by
      the tool that will consume it. Evaluation is not payload evidence: Nix
      copies these files without reading them.
- [ ] A key written into a generated configuration exists in the pinned
      tool's schema at the locked version, and a tool that rewrites its own
      configuration in place was started once against the rendered file —
      Home Manager installs that file as a read-only store symlink, so an
      in-place migration fails closed (INV unixlike/generated-config-key-in-schema).
- [ ] Activation is performed only when explicitly requested.
- [ ] Runtime claims name the host on which they were observed.
- [ ] A `unixlike-v...` tag is assigned only after required native evidence
      is available, including `CHECKS_BUILD_ALL=1 unixlike/tool/checks/test`
      on a matching host.
