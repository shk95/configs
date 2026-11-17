id: unixlike/editable-file-generation-backup
statement: Configuration files use immutable declarative deployment by default, while each explicitly selected writable text file is replaced with the incoming generation after preserving any existing contents as a numbered diff relative to that incoming source, without overwriting prior backups.
rationale: AGENTS.md § Goal and authority
enforced-by: schema unixlike/modules/foundation/editable-files.nix
enforced-by: tool unixlike/tool/editable-files
enforced-by: fixture unixlike/tool/checks/editable-files-test
enforced-by: fixture unixlike/tool/checks/editable-files-test.py
enforced-by: fixture unixlike/tool/checks/zellij-session-test.py
enforced-by: fixture unixlike/tool/checks/fixtures/editable-files.nix
decision: docs/policy/decisions/unixlike/editable-files-reset-on-switch.md § Individually selected writable files reset on switch

The incoming generation is always the comparison baseline, including on rollback
and repeated activation of the same generation. A patch goes from that baseline
to the contents immediately before replacement: minus lines belong only to the
incoming source and plus lines belong only to the existing file. This includes
declarative changes between generations, not just interactive user edits.

Each existing file receives an adjacent numbered backup directory, including
when its diff is empty. Existing numbers are scanned numerically and never
reassigned; incomplete or foreign occupied backup names are retained. The
backup contains a unified diff, metadata and an indirect root retaining the
incoming store source. No complete copy of the previous file is kept.

Preflight performs no writes. Backup failures stop replacement. Replacement of
each file is atomic, and previously completed files have their own backups if a
later operation fails. There is no claim of an atomic transaction over an entire
home or of locking out application writes. An observed edit during activation
refuses replacement; applications should not save concurrently with switch.

The selection is finite and file-specific. Neither an application name nor a
directory grants opt-out to future files. This whole-file mechanism is separate
from the finite-member projection used for host-written Karabiner documents.
When an old store-directory link is split, its source object is rooted before
the link is replaced, so preserved unselected children survive collection of
the previous generation.
Consumers of selected settings read their deployed files at invocation time;
in particular, the Zellij shell function reads the live session name rather than
overriding it with a value captured at evaluation.

Provider composition fixtures check that selected targets do not overlap other
selected or enabled ordinary Home Manager file targets in configs-owned
compositions. This is a provider regression check, not a global assertion over
consumer extensions or a controller for other tools writing to the home directory.
