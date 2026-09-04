# Capture restores exactly one placeholder

date: 2026-08-30
scope: windows
status: accepted
source: 9f1e8ce:docs/status.md § Capture moves a host change into desired state

The placeholder direction is deliberately asymmetric. Apply expands exactly one
content placeholder, `__LOCALAPPDATA_JSON__`, to the JSON-escaped spelling of
that directory. Capture therefore restores that one spelling and reports every
other one — the raw spelling of the same directory, and either spelling of the
profile and roaming directories — as unrepresentable, and refuses the file.
Writing `{USERPROFILE}` into a payload instead would look like a capture and
deploy as literal text, leaving the host holding the placeholder and every later
check reporting drift no Apply could clear. Extending the deploy side to expand
more placeholders is a change to what a payload means on a host, so it belongs
to its own issue with its own evidence rather than to the tool that would
benefit from it. Until then a payload needing another host directory is edited
by hand, and the refusal says so.
