# U2 Darwin capture pickup investigation
kind: study
date: 2026-09-30
scope: unixlike
status: open

## Source and authority inspected

This new study records the U2 pickup investigation at configs
`86abcea4eadd1e4403ec9025eedb7009daf54886`, with pre-amendment spec revision
`6082cf9a61c3b01f03eff7cef602b84f62bcd5c7`. It does not restore the former
study or treat its historical proposals as current design. The latest AC3
ownership-transfer/minimal-surface amendments supply the work acceptance.
Durable ownership remains in architecture, the public environment/host boundary
decision and the projection decision/invariant until explicitly reconciled.

The actual module at `unixlike/modules/programs/karabiner/module.nix` gates one
combined activation on final Karabiner app selection and existing appSettings
booleans. It passes two hard-coded payloads. The script's project/check/apply
derive scope from payload keys; apply merges whole top-level document members and
individual declared hotkey entries. Current Karabiner parents are global/profiles;
symbolic entries are 60/61. The root commit helper's capture stages and publishes
provider payloads, so it cannot serve the new host-original destination.

The public template's delivered root input is
`c76752dc1ec285dce721ae02a2f139c9f32dcb76?dir=unixlike`; its one synthetic
example uses mkNixos and native homeModules/systemModules. That source inspection
does not supply a Darwin settings-document consumer or U2 evaluation. U2 must use
an independent synthetic mkDarwin case through public homeModules, with no private
identity, required template checkout or implicit consumer update.

## Concrete choices and their cost

| Choice | Reason and consequence |
| --- | --- |
| Two independently enabled units; existing app gates retained | Preserves ordinary provider opt-out and app lifecycle ownership; no arbitrary registry |
| Nullable settingsDocument via public homeModules | Explicit file connection; no file discovery, Nix reverse compiler or first-connection Nix edit |
| Shared versioned unit contract for all directions | Scope cannot shrink when host data omits an optional nested member; no parallel ignore list |
| Required global/profiles and entries 60/61 | Missing owned parents/entries refuse; nested optional absence uses whole parent replacement |
| Explicit host/configs source | Host replaces its entire unit; configs restores provider defaults while retaining dormant recovery data |
| Preview artifact then explicit save | Caller-reviewed data/ownership proposal with schema/binding/reread/recomputed-projection consistency; no author authentication or last-applied inference |
| Atomic each document, truthful partial result | A second write can fail after the first completes; no cross-file transaction or rollback promise |
| Additive pinned darwin-capture app/package | No Git helper dependency; retain legacy project marker protocol/caller fixtures until repository retirement |

The proposed spellings and proof matrix are in the dated spec amendment. Save
creates or replaces only an explicitly selected host document; it neither connects
that document in Nix nor authorizes application. Consumer connection/adoption and
root usage/commit-helper retirement retain separate owners and reviews. The
existing Justfile capture recipe is Unix-like-owned, so U2 rather than the
repository lane owns its compatibility/refusal change. Caller inventory binds
Justfile's karabiner-capture recipe to root commit capture, README's older
reads-and-commits instruction, commit helper capture_command and the root capture
fixtures. No legacy publish flag silently becomes a host-original Save.

## Official app-format investigation

Official [root-format documentation](https://karabiner-elements.pqrs.org/docs/json/root-data-structure/)
describes the document concerns, but live documentation is not a pinned native
parser. The fixed [v16.3.0 core configuration source](https://github.com/pqrs-org/Karabiner-Elements/blob/v16.3.0/src/share/core_configuration/core_configuration.hpp)
inserts a default profile when the parsed profile array is empty. The proposed
initial format therefore refuses empty profiles rather than promising stable
all-profile deletion. Whole-array replacement is retained for supported nonempty
profiles. Empty nested arrays/objects need shape-specific positive/refusal proof.

The fixed [v16.3.0 global configuration source](https://github.com/pqrs-org/Karabiner-Elements/blob/v16.3.0/src/share/core_configuration/details/global_configuration.hpp)
removes ask_for_confirmation_before_quitting, whose current provider value is false.
The current provider already uses check_for_updates=false; there is no older
update-key spelling in this payload and no rename to perform. The obsolete false
member is the concrete compatibility review gap, not proof that all observed
settings or all versions are incompatible. A bounded U2 candidate may remove that
ignored member while preserving the current update preference; final native
parser/roundtrip proof and root review are needed before accepting the correction.
A source worker must distinguish an equivalent adapter/default correction from a
changed supported preference before editing; unsupported data refuses instead of
silent conversion or loss. Broad app-schema mirroring and Homebrew version pinning
remain rejected. Application factory-reset behavior is not inferred.

Static native inventory on 2026-09-30 read only bundle version metadata and binary
headers: Karabiner-Elements 16.3.0, bundle build 16.3.0, host arm64; the app and
installed karabiner_cli are universal arm64/x86_64 binaries and the CLI path exists.
Neither executable was started. No user configuration, hotkey dictionary, device
identity or profile contents were inspected. This selects a potential native
fixture baseline, not a successful reader/schema/runtime test or support expansion.

## Remaining evidence and ownership

The current Unix-like decision explicitly places capture in the commit helper;
the invariant also names its fixture. U2's source PR must date the scope-owned
decision/invariant reconciliation and add actual host-document enforcement while
preserving historical #177/#178 observations and the single projection rule.
Legacy project tags/fixture locators stay until the caller retirement is
coordinated; adding the new tool alone does not relocate their enforcement.
The separately assigned repository PR then removes root publishing commands and
their corresponding fixtures without orphan tags or an unverified transition.
It does not own the Justfile. If the existing project flags/two section markers
cannot remain compatible, a reviewed repository fail-closed retirement must merge
before that protocol changes; new root usage follows actual CLI delivery. An
added temporary adapter needs a scoped provisional entry, not a hidden exception.

No implementation, new public option, packaged capture command, evaluation,
native build, real reader test, original save or activation is supplied by this
study. The future source worker records current dev and the accepted pickup
revision independently, preserves raw/native versus synthetic evidence, and stops
for substantive compatibility, deletion, support or ownership changes. AC3 and
the parent report remain pending; independent release/parent outcomes are not
closed by this investigation.
