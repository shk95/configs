# Host declarations own selection and complete unit sources

date: 2026-09-30
scope: windows
status: accepted
issue: #427
source: docs/work/windows/host-consumer-contract/spec.md

Version 1 host environments select optional features explicitly; core and declared
feature dependencies are included. An empty selection is core only. A connected
settings document chooses the provider default or complete host content for one
unit. Connections are explicit relative files, never directory discovery. Changed
formats, source/tool identity, original inputs or generated payloads require
regeneration before Check or Apply. A clean local provider checkout at a full SHA
is the initial acquisition boundary; it performs no implicit source update.

The selected payload defines the unit's owned projection. JsonSubset writes update
only its object keys in an existing app document and retain unmanaged keys; arrays
are owned whole. This does not merge provider defaults into host desired content.
Externally generated Terminal profiles and foreign PowerShell profile blocks remain
preserved. Disabled units and deselected features leave existing documents, hooks
and installed packages alone. Generation performs no Apply.

The initial client evidence baseline is Windows 10 IoT Enterprise LTSC 21H2 x64,
build 19044. Terminal settings/fonts/profiles remain included. Default terminal
delegation is an explicitly excluded capability in generated mode: no registry
query or write is used as client guarantee evidence. Legacy source-only checks
retain their historical support-limit behavior. Windows 11 is outside this initial
support contract; hosted native fixtures prove their fixture behavior and never
substitute for LTSC client observations.

The provider no longer offers .wslconfig, personal FancyZones custom layouts or
personal layout hotkeys. It retains generic FancyZones default layouts, settings
and Workspaces/settings.json. Legacy export names retired selections as blocking
migration actions and never silently drops them. Existing host files are not
removed or rewritten by retirement. Legacy helpers and historical evidence remain
readable; a generation runtime state cannot be captured into provider source while
W2 host-original capture is still pending.

Generation Apply outcomes use state schema 3 and identify the actual generation,
completed operations and success/partial failure independently from capture. Old
state schemas 1/2 remain readable; schema 1 export reconstructs selection only from
its recorded provider manifest. Failure cannot retain a current success claim.
