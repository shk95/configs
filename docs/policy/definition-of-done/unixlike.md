# Definition of done: Unix-like

The checklist a Unix-like change owes on top of `repository.md` beside this
file, which every change owes.

- [ ] The change is owned by the flake, a Unix-like module, or a Unix-like
      payload rather than a cross-platform abstraction.
- [ ] The affected Home Manager, NixOS, or nix-darwin toplevel derivation
      evaluates.
- [ ] Provider-owned source transformations and generated configuration artifacts
      are checked on matching verification systems when affected. Consumer host builds are not provider prerequisites.
- [ ] Foreign evaluation is reported as evaluation, not native build evidence.
- [ ] Every source payload is declared in `unixlike/payloads.json` and parsed by
      the tool that will consume it. Evaluation is not payload evidence: Nix
      copies these files without reading them.
- [ ] A key written into a generated configuration exists in the pinned
      tool's schema at the locked version, and a tool that rewrites its own
      configuration in place was started once against the rendered file.
      Normal deployment uses a read-only store symlink; an explicit writable-file
      opt-out still requires valid generated keys and applicable migration
      evidence (INV unixlike/generated-config-key-in-schema).
- [ ] Activation is performed only when explicitly requested.
- [ ] A writable-file opt-out is declared for each selected file; incoming-relative
      numbered backups, retained baselines, dry-run behavior and failure
      preservation are verified (INV unixlike/editable-file-generation-backup).
- [ ] For a tool supply or settings ownership change, the Unix-like maintainer
      records the selected platform and installation owner, configuration owner,
      optional version constraint, duplicate-command disposition and applicable
      native compatibility evidence; Nix remains central to configuration and
      program supply, with Homebrew supplementing it on macOS and mise supplying selected Linux
      tools; local tools and old versions remain preserved by default
      (INV unixlike/tool-supply-ownership). A policy-only adoption records the
      existing implementation and does not imply a supplier migration.
- [ ] Any optional runtime reproduction names its system and exact selection;
      ordinary provider verification makes no host runtime claim.
- [ ] A `unixlike-v...` tag certifies the public API, synthetic composition
      evaluation, payload validation, generated-file parsing and provider-owned tooling. Host closure
      builds, boot, desktop sessions and activation belong to the consumer.
      Consumer configuration builds are reported separately and are never
      inferred from the provider suite.
