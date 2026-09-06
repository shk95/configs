# Karabiner desired state is compared and applied by projection

date: 2026-09-05
scope: unixlike
status: accepted
issue: #177
reopen-when: Karabiner writes host state below the top level of `karabiner.json`, so a declared key would carry both desired state and runtime state.

Karabiner-Elements is installed as a Homebrew cask and owns its configuration
file. It unlinks and rewrites `~/.config/karabiner/karabiner.json` on every save
and its documentation asks that the file not be symlinked, so the delivery every
other Unix-like payload uses — `xdg.configFile`, a link into the Nix store — is
the one delivery this file cannot have. Desired state is therefore a copy: an
activation script writes the file, and the application is free to rewrite it
afterwards.

A copy raises the question a link never has to answer, which is what the
repository owns in a file the application also writes. The answer is a
projection onto the top-level keys the payload declares. The payload owns every
key it declares and everything beneath it; the host's undeclared top-level keys
are runtime, are preserved when the file is written, and are never captured. One
mechanism decides all three directions — what drifts, what is written, what is
captured — so the read and the write cannot disagree about what desired state
covers.

The alternative was a list of keys to ignore, kept beside the payload. That is a
second declaration of what the payload owns, free to drift from the payload
itself, and it fails open: a key nobody thought about reaches desired state.
A projection has only the payload, so a key is captured if and only if the
payload declares it, and widening coverage is an edit to the payload. The
Windows domain reached the same conclusion for its subset payloads in
`docs/decisions/jsonsubset-captured-by-projection.md`; this is that idea copied
into the Unix-like domain, with its own tool, its own fixture and its own
invariant, not a shared implementation.

The projection is deliberately one level deep. `machine_specific` is the only
undeclared top-level key the host was described as holding on 2026-09-05, it is
keyed by a per-machine identifier, and it holds nothing this repository wants to
manage. `profiles[].devices` sits below a declared key and is therefore desired
state, captured with everything else under `profiles`: a connected keyboard's
settings are user intent, not host runtime, and treating them as runtime would
mean a payload that cannot express them. The `reopen-when` above names the shape
that would break this: host state written *inside* a declared key, where a
top-level rule can no longer separate the two.

The Korean input-source toggle is not Karabiner's. Karabiner maps Right Command
to F18; F18 is bound to the "select the previous input source" action by symbolic
hotkey 60 in `com.apple.symbolichotkeys`, with 61 disabled. That dictionary held
74 entries on the host described in #177 on 2026-09-05, and nix-darwin's
`CustomUserPreferences` and Home Manager's `targets.darwin.defaults` both write a
whole preference key, so either would replace the other 72 entries with the two
this repository declares. `defaults write … -dict-add <n>` merges one entry and
is the only writer that leaves the rest alone. The same asymmetry is why the
hotkeys are their own payload with their own projection: the declared entry
numbers are the unit of ownership, exactly as the top-level keys are for the
document. `plutil` renders plist booleans as JSON booleans, so `enabled` is
written and compared as `true` or `false` rather than as `1` or `0`.

Reloading the preference is best effort. `activateSettings -u` is private and
undocumented; a failure is a warning rather than an error, because the entries
are already written and a logout applies them either way.

Delivery is a Home Manager activation script rather than a nix-darwin system
activation script. Both are available on the Mac, and the difference that
decides it is the user context: the file lives in the user's home and the
preference domain is the user's, so a Home Manager activation runs as the right
account without elevating, and one script covers both halves. It also keeps the
change on one evidence lane — a Home Manager generation — rather than splitting
it across the system closure.

Capture is a command in the existing commit helper rather than a second guard.
Writing a payload back from a host is a version-control operation: it stages,
classifies, refuses an untracked or already-modified payload, and asks once
before committing. Those guards exist; a standalone capture script would
reimplement them and would be the second place a mistake could be made.

`karabiner_cli --lint-complex-modifications` is not the check for this payload.
It lints a complex-modification rule file as the assets directory holds them, not
a `karabiner.json` root document, so pointing it at the payload asks it a
question it does not answer. `tool/checks/payloads` parses both payloads as JSON,
which is the evidence a payload check can honestly give, and the projection's own
fixtures carry the rest.

**The payload committed with this record is a reconstruction, not a capture.**
The host file is on the Mac and was not available on the machine that wrote it;
it was rebuilt from the description in #177 dated 2026-09-05 and is unverified
against the real host until that Mac runs `check`. Because `apply` replaces the
declared top-level keys wholesale, a first activation against a payload that does
not match the host would discard whatever the description got wrong. The
requirement this branch therefore carries is that the Mac runs `just
karabiner-check` before any activation and, on drift, `just karabiner-capture`,
so that desired state is the host's own values before anything is written back.
