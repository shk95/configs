# Definition of done

A successful evaluation is evidence, not activation. Report every unavailable
platform check instead of silently treating it as passed.

## Every change

- [ ] `tool/checks/format` passes.
- [ ] `tool/checks/lint` passes.
- [ ] `tool/checks/windows-generated` proves the committed Windows bundle is
      byte-identical to the flake output.
- [ ] `tool/checks/test` evaluates every Unix-like configuration and reports
      which native builds were performed.
- [ ] User-facing behavior and expensive decisions are documented.
- [ ] The final diff contains no unrelated or hand-edited generated content.

## Unix-like configuration

- [ ] The affected Home Manager, NixOS, or nix-darwin toplevel derivation
      evaluates.
- [ ] A native build is performed on a matching system when sources or packages
      changed.
- [ ] Activation is performed only when explicitly requested.
- [ ] Runtime claims name the host on which they were observed.

## Windows desired state

- [ ] The change originates in `modules/` or `assets/`.
- [ ] `tool/render-windows` was run and the generated result is included.
- [ ] JSON and Lua payload validation passes while building the bundle.
- [ ] Pester passes under native PowerShell when reconciliation behavior changed.
- [ ] `windows/bootstrap.ps1 -Check` is observed on native Windows when
      package detection, target paths, registry behavior, fonts, or application
      lifecycle behavior changed.
- [ ] Apply is run only when explicitly requested, followed by a second
      read-only check.

## Context and workflow

- [ ] Stable judgement belongs in `AGENTS.md`, not a model-specific adapter.
- [ ] Shared procedure belongs in `CONTRIBUTING.md`.
- [ ] A decision expensive to reverse belongs in `docs/status.md`.
- [ ] A recurring issue is indexed in `docs/troubleshooting.md` by its literal
      symptom.
