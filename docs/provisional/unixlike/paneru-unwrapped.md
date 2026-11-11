id: unixlike/paneru-unwrapped
kind: upstream-pending
statement: Darwin transforms the upstream Paneru final package into its unwrapped Lua-enabled binary so Accessibility permission belongs to Paneru rather than Nix Bash, refusing environment additions that would need a wrapper.
since: 2026-11-11
exit-when: The locked upstream Paneru module supports Paneru-specific Accessibility permission without this local transformation and passes the native runtime comparison with Bash permission disabled.
watch: unixlike/flake.lock
review-by: 2026-12-11
issue: #461
decision: docs/policy/decisions/unixlike/paneru-unwrapped-until-upstream.md § Use the unwrapped Paneru package until upstream fixes permission attribution
owner: repository maintainer

The issue is upstream [karinushka/paneru#461](https://github.com/karinushka/paneru/issues/461).
The disposable code is the tagged inline module in the Paneru module's imports,
the sibling native flake check, the two tagged refusal probes in
`unixlike/tool/checks/provider-api-test`, and the tagged status paragraph.
Remove those together with this entry when retiring the measure. The decision
record preserves the rationale and observed runtime evidence.

The transformation uses the upstream read-only option's `apply` hook; it
does not copy upstream modules, patch source during evaluation, update inputs,
or install a second package. Added executable or Lua search paths are rejected
instead of silently being dropped. The package still includes the Lua runtime.
