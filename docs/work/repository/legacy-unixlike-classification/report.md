# Retained Unix-like classification verification
kind: report
spec: docs/work/repository/legacy-unixlike-classification/spec.md
status: done

## Evidence boundary

Root reviewed the original master classifier and the retained editor file at pickup
1a65cac6f7a75adf1465a9345daa847072fade3e. Its 549 dev paths and 294 master paths
have no unclassified answer under the proposed map. Nix editor settings remain
unchanged here; relocation is a separate Unix-like task. No master promotion or
operating input was selected.

Source 8aad5f1912c8045db92163b514475d87ddbae784 passed the complete CI run
[36836609658](https://github.com/shk95/configs/actions/runs/36836609658).
Source 6acd8406ac3ebb7a8563a215694dcd08e119c626 adds direct historical/negative
classifier cases in the independently executed native preview fixture. Its
[Linux policy job](https://github.com/shk95/configs/actions/runs/36838637565/job/110292123759),
[native Windows policy job](https://github.com/shk95/configs/actions/runs/36838637565/job/110292123749)
and [policy scan](https://github.com/shk95/configs/actions/runs/36838637565/job/110292123742)
passed. These source fixtures prove the repository contract; final-head Required
checks remain the independent Ready/integration gate. No unavailable or pending
foreign runtime lane is upgraded.

Local macOS repository fixtures passed with functional Python 3.13.15 and Git
2.55.0, including release-preview, 24 controller families and retirement regressions.
Policy checks verified 79 invariants, zero pending/untagged fixtures, three current
provisional entries, domain reads, hygiene, work pairing and design citations.
CI selection independently chose repository, Unix-like and Windows suites for the
classifier change. Normal commit and push hooks passed without bypass.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review: original master maps the six legacy namespaces to unixlike and editor content is Nix-only. Fixtures: full Linux/macOS suite and direct native-Windows preview cases accept seven historical locations plus the new domain editor path and refuse seven unrelated/similar paths. Policy checks: classifier, scope invariant and work preflight passed. Affected dispatch: selector fixtures and actual CI classification select all affected suites; complete first-source CI and the reinforced source's Linux/Windows governance jobs passed. |
| AC2 | verified | Review: registered measure has an observable master-tree retirement condition and 2026-10-31 review, with no new root-domain authority. Fixtures: retained-package/controller tests passed on Linux and Windows; all eight manifest SHA256 entries independently rehashed exactly. Policy checks: provisional coverage, semantic package isolation, invariants and hygiene passed. |
