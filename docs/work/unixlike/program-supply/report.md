# Program supply verification
kind: report
spec: docs/work/unixlike/program-supply/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Compared the relocation with master across seven synthetic configurations. Ordered packages, configuration placement, and Homebrew declarations match. Git preserves the moved payload bytes and LF PowerShell checkout. The import-order fixture passes. |
| AC2 | verified | The catalog exposes 134 definitions. The provider suite passes 50 selection and inventory probes and 17 refusal probes, including effective Git and Darwin settings, package-free native settings, duplicate casks, and supplier platform constraints. The external consumer and data-only inspector exercise the published contract. |
| AC3 | verified | The fake-installer and shell fixtures check the install command, failure propagation, preservation, and PATH precedence. Native aarch64-darwin and aarch64-linux builds use locked mise to parse the generated fragment and verify offline reuse of an installed version. |
| AC4 | verified | Provider formatting, lint, the complete provider suite, and all seven exported evaluations pass. The native Darwin mise and Paneru checks pass. All eight host outputs evaluate with an explicit provider override. The normalized Darwin output matches the pre-extraction 6 formulae, 37 casks, 26 App Store entries, and Homebrew operating policy. |

The provider checks cover Unix-like source tree
`ac8b6e1dcb58bb3013537a6b0af87be300706894`. Host evaluation uses the same
source with the paired consumer extraction and leaves the consumer lock
untouched. Consumer integration requires adoption of a provider release
containing the catalog.

Native runtime for mise-supplied application binaries and behavior after
updates are unverified. Host closure builds and activation were not run.
