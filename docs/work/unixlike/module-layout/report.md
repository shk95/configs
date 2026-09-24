# Report: group Unix-like modules without changing composition

kind: report
spec: docs/work/unixlike/module-layout/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | The study assigns all 89 tracked module-tree files; the moved tree has 89 files, and Git recorded all 89 as byte-identical renames from `13df09d`. |
| AC2 | verified | `composition-test` accepted 63 feature files and refused both host naming and forced class decisions; `flake/configurations.nix` is unchanged. |
| AC3 | verified | `payloads` parsed all 16 declarations after their path update; the Karabiner, PowerShell, WezTerm and Zellij payload files are byte-identical to the originals, and `karabiner-test` passed. Repository-owned literal path readers moved in PR #369. An active-source search found no old module path outside dated work and decision records. |
| AC4 | verified | All seven output derivation paths exactly equal the `13df09d` pre-move baseline after `module-classes.nix` keeps the pre-grouping concern path as its stable sort key. |
| AC5 | verified | `composition-test` and `import-order-test` passed; 73 Nix modules compose to identical toplevels in walk and reverse order, and the negative fixtures refused their violations. |
| AC6 | verified | The Unix-like decision and status describe the grouped tree. PR #369 updated repository architecture, guidance, command paths and fixtures; its repository job, common scans and Required checks passed before merge to `dev` as `3f2a501`. |

## Evidence lanes

- Evaluation: All 7 outputs evaluate and have exactly the same derivation paths as the 2026-09-24 `13df09d` baseline. The complete Unix-like CI job and Required checks passed for PR #368 on x86_64 Linux, including `flake-test` and `import-order-test`. The local macOS `flake-test` passed its schema section but could not run the x86_64 installation fixture.
- Build: The pre-push gate built `darwinConfigurations.shk-macbook` on aarch64 Darwin; PR #368 CI built `homeConfigurations.user1` on x86_64 Linux. The NixOS outputs were evaluated, not built for this move. Their derivation paths are unchanged from the baseline; no new host build is claimed.
- Native runtime: not requested for a physical source relocation.
- Activation: not requested.
- Review: 89 source files are accounted for. Initial output drift came from a generated `.zshrc` comment changed during reference editing and from path-based sorting that moved `glow` in the package list. Restoring original module bytes and preserving the old concern sort keys restored all seven derivation paths. Unix-like PR #368 merged to `dev` as `9d55c3b`; repository PR #369 merged as `3f2a501`. Both passed Required checks. Local and remote version-control audits reported no failures after both merges.

The current pre-move baseline at `13df09d` is: Darwin `v6ch2n1ky8jbhfqvw0r7115p8k2gk3cp`, standalone home `i89pyhjwb73d7dgjh1grghwxv2jbsq9b`, desktop `hkxgm958ysyblf0dabwa6dr8s7ax87fq`, NixOS-WSL `wzslxac8k9v1kp35gc9wmcc23ni7k3i9`, OrbStack `hgna2sjsqyac3b36laf92d8vpn42vbzj`, UTM `93jzqjx2bxc0yhc9crz00lx786ij9rrd`, and VMware `a9bcrq0lxwz2kha0rvxpj805nyqyvvls` (all `/nix/store/...drv`).

## Outcome

The grouped module layout and its active path readers are integrated in
`dev`. This report records source layout and evaluation evidence only; it
does not certify a domain release or authorize host activation.
