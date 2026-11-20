# Host program settings migration evidence
kind: report
spec: docs/work/unixlike/host-program-settings/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Source review traces the host modules through the eight public constructor calls. The provider retains installation, integration, schema checks and minimal defaults. Nix evaluation selects host values and complete files through the existing options. |
| AC2 | verified | All eight hosts evaluated under the unchanged lock and under the local provider override. Seven hosts matched their previous system and home derivations exactly in both comparisons. Darwin's generated home files and writable-file manifest matched exactly. Its activation script matched outside the Karabiner invocation, and both JSON inputs to that invocation matched the earlier settings. Paneru's selected input matched its prior evaluated file. Its locally edited running file was preserved. |
| AC3 | verified | The provider suite passed and the final provider evaluation, format and lint passed. The aarch64 Darwin build realized the generated configuration and the writable-file manifest. The provider and transferred Lua, JSON, KDL and PowerShell files passed their parsers. Niri sources for the public fixture and UTM passed a KDL parse. The installed Ghostty validator accepted its generated config and Lazygit loaded its read-only generated YAML in a temporary repository. The read-only Karabiner adapter matched both managed units on the Mac. |

## Evidence limits

The comparison used the Unix-like provider tree based on `a47bf10` and the
consumer's `unixlike-v2.0.0` lock. The local override used the same provider
inputs on both sides of the comparison. Native checks here used aarch64
Darwin. Linux Niri and Noctalia native checks require a Linux builder.
Whole-host builds and activation were unperformed.
