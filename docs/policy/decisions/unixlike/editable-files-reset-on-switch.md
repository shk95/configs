# Individually selected writable files reset on switch
date: 2026-11-15
scope: unixlike
status: accepted

Nix remains the source of the desired configuration. Store symlinks are the
default. An explicit per-file opt-out permits frequent interactive adjustments
without a switch: activation deploys an owner-writable regular file instead of
a link, and the application can read that file through its usual path.

Every switch installs the chosen incoming generation's contents unconditionally.
Interactive changes last until that switch; they are never merged into the new
generation or imported into repository source automatically. Rollback uses the
same rule with the generation being activated as its baseline.

Before replacement, any existing file is compared with the incoming source.
The unified patch has the incoming source on the minus side and the existing
contents on the plus side. Applying it to the exact incoming source reconstructs
the previous contents. This direction was chosen so every backup is understood
against the generation that replaced the file, even when the declaration itself
also changed. The patch is not described as user edits alone.

Backups live beside their file as `<name>.backup-000001/`, increasing the maximum
existing numeric suffix. Each directory contains `changes.patch`, `metadata.json`
and `baseline`, an indirect GC root for the incoming store object. Metadata
records the incoming source path, both content hashes, activation generation,
timestamp, sequence and prior mode/link identity. Identical contents still have
an empty patch and metadata; a missing file has no previous contents to back up.
An interrupted backup remains reserved and is never reused. There is no automatic
retention limit, renumbering or deletion. Number, rather than modification time
or lexical ordering, identifies the latest backup.

The GC root is needed because a diff alone is insufficient after its baseline
has been collected. Retaining the incoming source avoids full previous-file
snapshots and keeps each patch independent of other backups. This deliberately
retains store data for as long as its backup remains. Backups have private
directory/file permissions; new configuration files are owner-readable and
owner-writable (and owner-executable only when explicitly declared executable).

Read-only preflight validates all selected sources and destinations. Activation
backs up all pre-existing selected files before replacing the first one, and
uses a temporary sibling plus rename for each replacement. A failure stops the
activation; it does not claim to roll back already completed replacements.
A home-local lock excludes concurrent runs of this writer, and content checks
refuse observed concurrent edits, but applications do not share that lock.
Programs should not save during switch. Re-reading or restarting an application
is separate from deploying its configuration.

The initial selection is exactly Zellij `config.kdl`, Ghostty `config`, Paneru's
single active Lua file, and the ten currently declared WezTerm configuration
files. Ghostty's theme stays linked. Paneru follows the selected Home Manager
XDG mode: `~/.paneru.lua` or `$XDG_CONFIG_HOME/paneru/init.lua`, never both.
WezTerm's five config Lua files, three platform Lua files, main Lua file and
`fonts.json` are individually selected. Future WezTerm files inherit no opt-out.

`configs.editableFiles` names exact `home.file` keys; an XDG configuration key is
`config.xdg.configHome + "/" + name`. The owning program declares its finite
selection with overridable defaults. No directory entry is accepted as a file.
Previous store-directory links are split into real directories, keeping
unselected children linked to their original sources and preserving their
contents. Before splitting, the previous store object is retained through an
indirect root in `$XDG_STATE_HOME/configs/directory-baselines/`; those roots are
not pruned automatically, including when an activation is interrupted.
Ordinary Home Manager link placement does not own the selected files;
the generated source and applicable on-change callbacks remain available.
Parent-directory links to locations outside the store are refused rather than
writing through a link into a separately owned source tree.

To return a file to normal link deployment, set its selection to false. An
existing writable file then follows ordinary Home Manager collision handling:
preserve and move it explicitly, or use the consumer's reviewed backup procedure
before activating. Disabling a program leaves its writable files and backup
history in place rather than deleting local data. Karabiner's projected document
management and all Windows configuration remain independently owned.

Reviewed 2026-11-15: retain old directory objects before materialization so
unselected leaf links remain readable after the old generation is collected.
The writer's Nix executable is its own pinned runtime dependency, independent
of whether a consumer asks Home Manager to manage a Nix package. The Zellij
shell function parses the live KDL session name for bare invocations, preserving
the existing attach/create/resurrection path without fixing the name at build
time. Explicit CLI arguments pass through unchanged; absent session names defer
to Zellij's native behavior.

Reviewed 2026-11-17 against the current master's Zellij 0.46.0: the session
name occupies `attach`'s positional session argument. In that version `--`
introduces an initial command, so it must not precede the session name. Names
beginning with `-` and the reserved `options`/`help` subcommands are refused
explicitly to avoid interpreting a configured name as CLI syntax. The focused
fixture checks this boundary with the pinned native CLI parser, exiting before
session lookup or application startup.

Reviewed 2026-11-17: file-placement ownership checks cover declarations composed
by this provider. The regression fixture compares selected actual targets with
other selected and enabled ordinary Home Manager targets across exported
configurations and the desktop/XDG probes, rejecting identical or
ancestor/descendant ownership. This does not add a reusable-module assertion
restricting consumer extensions or
attempt to coordinate independent configuration managers. Existing contents at
a selected destination still follow the backup and replacement policy above.
