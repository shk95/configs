# Report: group Unix-like modules without changing composition

kind: report
spec: docs/work/unixlike/module-layout/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | The study assigns all 89 tracked module-tree files; the moved tree has 89 files, and each moved file was restored byte-for-byte from its original `HEAD` path. |
| AC2 | verified | `composition-test` accepted 63 feature files and refused both host naming and forced class decisions; `flake/configurations.nix` is unchanged. |
| AC3 | pending | `payloads` parsed all 16 declarations after their path update; the Karabiner, PowerShell, WezTerm and Zellij payload files are byte-identical to the originals, and `karabiner-test` passed. Repository-owned literal path readers must land in their own scope before this criterion closes. |
| AC4 | verified | All seven output derivation paths exactly equal the `13df09d` pre-move baseline after `module-classes.nix` keeps the pre-grouping concern path as its stable sort key. |
| AC5 | verified | `composition-test` and `import-order-test` passed; 73 Nix modules compose to identical toplevels in walk and reverse order, and the negative fixtures refused their violations. |
| AC6 | pending | The Unix-like decision and status describe the grouped tree. Repository architecture, guidance, command paths and fixtures are prepared in a separate working-tree increment; its review and integration are required before this row closes. |

## Evidence lanes

- Evaluation: All 7 outputs evaluate and have exactly the same derivation paths as the 2026-09-24 `13df09d` baseline. `flake-test` passed its schema section. The default macOS run hit a `/var` symlink in the installation-plan fixture; rerunning with `TMPDIR=/private/tmp` reached the explicit x86_64 requirement for that fixture, so its native lane remains unavailable here.
- Build: not required for this physical move because every output derivation path is unchanged; no new build evidence is claimed.
- Native runtime: not requested for a physical source relocation.
- Activation: not requested.
- Review: 89 source files are accounted for. Initial output drift came from a generated `.zshrc` comment changed during reference editing and from path-based sorting that moved `glow` in the package list. Restoring original module bytes and preserving the old concern sort keys restored all seven derivation paths. The prepared repository-scope path update and fixture tests pass in the working tree; its separate review and integration remain.

The current pre-move baseline at `13df09d` is: Darwin `v6ch2n1ky8jbhfqvw0r7115p8k2gk3cp`, standalone home `i89pyhjwb73d7dgjh1grghwxv2jbsq9b`, desktop `hkxgm958ysyblf0dabwa6dr8s7ax87fq`, NixOS-WSL `wzslxac8k9v1kp35gc9wmcc23ni7k3i9`, OrbStack `hgna2sjsqyac3b36laf92d8vpn42vbzj`, UTM `93jzqjx2bxc0yhc9crz00lx786ij9rrd`, and VMware `a9bcrq0lxwz2kha0rvxpj805nyqyvvls` (all `/nix/store/...drv`).
