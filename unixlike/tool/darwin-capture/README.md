# Darwin settings documents

The pinned `darwin-capture` app previews observed Karabiner settings or symbolic
hotkeys60/61 and saves the reviewed projection to explicit host-owned JSON
documents. It does not connect a document to a host, edit Nix, publish Git changes
or apply application settings.

Pin one full provider commit for both commands. Use absolute canonical paths
outside provider source/store, app directories and observed originals, with
existing destination parents. The preview output must be a new file.

```sh
nix run 'github:shk95/configs/<full-commit>?dir=unixlike#darwin-capture' -- \
  preview --unit karabiner --document /host-repository/settings/karabiner.json \
  --unit symbolic-hotkeys --document /host-repository/settings/hotkeys.json \
  --output /private-preview-directory/proposal.json
nix run 'github:shk95/configs/<same-full-commit>?dir=unixlike#darwin-capture' -- \
  save --preview /private-preview-directory/proposal.json
```

Review readers, destinations, complete projected settings and source transitions
in the mode-600 proposal before Save. Keep it private: it contains observed
settings, local paths and consistency identities. Save validates schema/tool
binding, rereads inputs and targets, and recomputes the proposal. It refuses stale
or inconsistent data. This provides consistency, not a signature, author
authentication or protection against replacing an entire coherent proposal.

Each document replacement is atomic; several replacements are not one transaction.
Save reports completed, unchanged, refused and incomplete results, preserves
completed documents and leaves remaining originals intact. After a refusal or
partial save, obtain another explicit preview of the actual current state.

Documents have exactly three fields:

```json
{"formatVersion":1,"source":"host","settings":{"global":{"check_for_updates":false},"profiles":[{"name":"Example","selected":true}]}}
```

Host source replaces the entire managed unit. Karabiner owns required global and
nonempty profiles parents, each taken whole. The hotkey unit owns required
entries60/61 taken whole, with boolean enabled and a standard three-integer
parameter value within signed 64-bit bounds. Enabled=false disables a hotkey; entry deletion or OS/app factory
reset is unsupported. Runtime siblings outside these boundaries survive apply
and never enter capture. Optional nested members disappear through whole-parent
replacement; arrays have no identity merge.

Configs source returns to provider defaults while retaining object-valued settings
as dormant recovery data. It never merges that data into defaults or performs an
app factory reset. Documents and managed settings must be representable by Nix:
decoded strings and object keys exclude NUL, and integers fit signed 64-bit
bounds throughout nested data, including dormant recovery. Fractional/exponent
numbers retain floating semantics. Unmanaged reader siblings are projected out
before this check. Active unsupported shapes, absent required parents, obsolete
app-format members, app-normalized required/known profile empties, duplicate keys
and malformed UTF-8/JSON refuse. The initial finite shape contract does not certify
arbitrary host extensions or every application version. Native-tested empty nested
modifiers, manipulator parameters and rule description remain valid; a general
deletion/reset interpretation is not inferred.

Connect documents explicitly through public Home Manager extensions:

```nix
homeModules = [{
  providerDarwin.capture.karabiner.settingsDocument = ./settings/karabiner.json;
  providerDarwin.capture.symbolicHotkeys.settingsDocument = ./settings/hotkeys.json;
}];
```

Each unit has an enable boolean defaulting true and a nullable settingsDocument
path defaulting null. Null uses provider defaults. Effective management also
requires final Karabiner selection and existing appSettings gates. Disabling a
unit excludes its document reads and provider apply operation without changing
app selection or the other unit. The consumer chooses adoption/activation.

Preview's `--host` and `--hotkeys-host` select synthetic JSON reader inputs for
fixtures. Otherwise the current Karabiner file and read-only macOS defaults
export/plutil conversion supply input. Missing readers are unavailable(exit69);
readable unsupported data refuses(exit1). Successful preview/save exits0.

The legacy tool, project flags, section markers and capture-to-Git caller remain
compatible until separately owned retirement. They are the historical provider
payload route and do not save host documents. The module's new permanent
check/apply adapter and this app share the versioned unit contract; they do not
turn a legacy publication command into Save.
