# Windows host declaration example

Copy this example to a separate host-owned directory. Set `provider.commit` to
the full commit returned by the pinned provider's `inspect` command; the zero
value here is a placeholder and is refused for a real checkout.

Run the selected provider's Windows entry point under PowerShell 7:

```powershell
.\windows\win-env.ps1 inspect -SourceRoot C:\provider
.\windows\win-env.ps1 generate -SourceRoot C:\provider -Environment C:\host\environment.json -Output C:\generated\current
C:\generated\current\windows\win-env.ps1 check -Generation C:\generated\current
```

The empty feature list selects core only. A unit document chooses either
`source: configs` with `settings: null`, or `source: host` with complete unit
content (a JSON object for Json units, a string for text/script units). It never
merges provider defaults into the host content. `enabled: false` stops managing
a unit and its related profile hook without removing an existing file or hook.
Connections use explicit relative paths and cannot share a document or escape
this host directory. Unselected or disabled documents retain structural checks
and undergo active payload validation on reselection.

Environment and settings documents are strict UTF-8 JSON (an optional UTF-8 BOM
is accepted). Duplicate or case-ambiguous keys, invalid bytes and UTF-16 input
are refused. Use the selected checkout's own inspect/generate entry point and
modules. Its tracked Windows files must be clean; assume-unchanged/skip-worktree
index flags are refused because they can hide changes from normal Git status.

Generation requires the active native parsers. Originals, selection, source,
payloads or tools changing require regeneration. A failed generation leaves
no first result and preserves a previous result while refusing it for changed
inputs. Use a dedicated output directory outside provider and host originals;
run the generated entry point so its tools match the declared result.

`export-selection -SourceRoot C:\provider -State C:\host\legacy-state.json`
prints a read-only proposal and migration blockers. Omit State for a first-use
core-only proposal. Schema 1 needs its recorded provider manifest available in
the local clone. Retired WSL selection is an explicit blocker. The provider no
longer manages .wslconfig, personal custom layouts or layout hotkeys; retain and
manage those in the host. Generic FancyZones default layouts can still choose
a complete host document. Runtime/session files stay outside desired inputs.

The initial client baseline is Windows 10 IoT Enterprise LTSC 21H2 x64,
build 19044; default terminal delegation is explicitly excluded. Check is
read-only and reports remaining drift or unavailable evidence normally.
Generation and Check do not authorize Apply. Host-original capture previews
supported settings and writes originals only with explicit Save; legacy provider
publication parameters are removed. Capture refuses generated configuration and
excluded runtime state. The parent contract and API release remain separately
assessed.
# Host capture

After selecting a feature in an external host declaration, preview one enabled
unit with the exact provider checkout. First capture requires an explicit relative
document path; capture never selects features or enables units automatically.

```powershell
pwsh -NoProfile -File C:\provider\windows\win-env.ps1 capture -SourceRoot C:\provider -Environment C:\host\environment.json -Unit advancedPaste -Document settings/paste.json
```

Review the complete source=host payload and first connection. Add `-Save` only
when writing those originals is intended, or `-Save -WhatIf` to keep it a preview.
Later capture uses the existing connection, so omit Document. For multiple Unit
IDs, supplied Document paths align in the same order. Existing connections cannot
be renamed by capture. An unconnected document left by connection failure is
inert; retry must explicitly name a matching document. Conflicting content refuses.

Save does not Apply, update provider defaults or publish Git. Host documents
remain private/external. Regenerate after saving before any explicit Check/Apply
against a generated configuration; old generation identity is intentionally stale.
