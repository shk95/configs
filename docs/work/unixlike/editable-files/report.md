# Writable configuration files verification
kind: report
spec: docs/work/unixlike/editable-files/spec.md
status: done

Source base: `466804b5cc5b4183eac6c9a2b01344c819216482` on the selected
`feature/unixlike-live-config` linked workspace. No master integration or real
host activation is part of this work.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | The 13 Nix composition probes in `editable-files-test` pass: exact Linux/Darwin selections, both Paneru XDG modes, linked Ghostty theme, future WezTerm file default, per-file opt-in, activation ordering and a consumer that does not manage a Nix package. |
| AC2 | verified | Eleven native Python fixtures pass on aarch64-darwin, covering incoming-relative patch reconstruction, generation changes, missing/identical/empty files, final-newline and CRLF handling, sequential occupied/incomplete backup names, symlink migration, invalid input, concurrent writer/edit refusal and backup/root/replacement failures. Disposable-home integration registers real indirect backup and old-directory GC roots, verifies root reuse, applies the diff to recover prior bytes and confirms immediate writable edits. Four live Zellij wrapper tests use a stub CLI to verify runtime edits, KDL parsing, environment precedence and exact configuration-path agreement. |
| AC3 | verified | Working-tree `format`, `lint` and the full tracked provider `test` suite pass. The final focused runner builds the generated 13-file Darwin manifest with pinned writer dependencies and executes only its placement command against a temporary home; all 13 sources become writable regular files. Provider verification evaluates 11 constructor scenarios, import-order stability and seven exported synthetic toplevels. |
| AC4 | verified | Reviewed the accepted decision, invariant, definition-of-done addition, finite program selections and status entry. Diff prose carries no private account/host identity. Source ownership remains Unix-like. No master integration, publication, consumer adoption or host activation was performed. |

## Evidence boundaries

The checks ran against the dirty source in this topic; the containing commit
records the prepared implementation. Format/lint and the new focused runner
were rerun after relevant corrections. The full suite passed with `TMPDIR`
canonicalized to its physical path: its first attempt exposed the existing
macOS `/var` versus `/private/var` path comparison in `just_entry_test.py`.
No unrelated test was modified to work around that environment detail.

Build evidence covers provider-owned generated settings/manifest, writer
dependencies and disposable test artifacts. Runtime evidence covers this writer
in temporary homes, not Paneru, Ghostty, WezTerm or Zellij application sessions.
No complete real-host closure was built and no Home Manager/system activation
was run. The current aarch64-darwin flake has zero native flake checks;
`nix flake check` omitted Linux systems. Their compositions were evaluated,
not natively built. Existing Darwin-specific Karabiner platform-guard/fallback
cases report their native-host skips separately.

## Operational result

Existing files receive `<name>.backup-000001/` siblings containing only their
incoming-relative patch, metadata and a GC-root reference to the incoming
baseline. Incomplete backup numbers remain reserved. Existing source files,
backup history and unselected children are preserved. No retention pruning,
automatic diff reapplication or application restart was added. Source payload
contents and generated setting keys are unchanged.

## Independent review — 2026-11-15

A separate read-only reviewer inspected the original `9cda0ba` implementation
and reproduced three P2 findings in disposable fixtures:

1. Splitting an old store-directory link left unselected children without a GC
   root. The writer now roots the old store object before replacing that link,
   preserving it on root failure. Real-root tests include reuse by a second
   migrated directory.
2. Interpolating nullable `config.nix.package` rejected a valid externally managed
   Nix consumer. The helper now has its own pinned `pkgs.nix` dependency and a
   Darwin constructor regression probe.
3. The Zellij shell function fixed `session_name` at build time. Bare invocations
   now parse live KDL with pinned `kdl-py` and pass the same `--config` file and
   quoted session argument to Zellij. This also resolves the discovery mismatch
   between an existing home config directory and `XDG_CONFIG_HOME`. Explicit
   CLI arguments bypass the helper unchanged.

The reviewer reran the final focused runner successfully: 11 writer tests,
4 Zellij wrapper tests, 13 composition probes, actual GC-root registration and
reuse, and native placement of the generated 13-file manifest in a temporary
home. All three findings were resolved and the reviewer found no additional
confirmed must-fix issue. No real application session or host activation was
performed. Format, lint and the full tracked provider suite also passed after
the corrections, with the final Zellij discovery change independently covered
by the final focused runner. The maintainer authorized amending the topic commit only; no master
integration or publication is included.

## Current-master compatibility — 2026-11-17

The current working tree is based on master
`4b9c31ac7cb28d2f96c36dd3b1176d9c6a492a6d`, with the imported editable-file
feature already present as uncommitted changes. Its pinned Zellij is 0.46.0;
the original topic used 0.45.1. In 0.46.0, arguments after `attach --` are an
initial command, so the original helper's `attach --create -- unixlike` lost
the intended session name. The helper now passes the name as the positional
session argument before any command separator. Names beginning with `-` and
the reserved `options`/`help` subcommands are refused before exec.

The focused runtime now includes the pinned native Zellij. Its six wrapper
tests include CLI parser probes that append an invalid index and must fail
before session lookup. Deliberately invalid KDL prevents startup even if a
regression swallows that index after `--`. The old argument form reached the
configuration error (exit 1), while the corrected form rejects the index at
argument parsing (exit 2). Existing live-edit, path selection and quoting
coverage remains in place. The eleven writer tests, thirteen composition
probes, real GC-root integration and generated thirteen-file temporary-home
placement pass, as do format and lint. No host activation or application
session was started, and the existing uncommitted work is preserved.
The full tracked provider suite also passes on aarch64-darwin, including
evaluation of all seven synthetic toplevels and import-order independence.
Linux composition remains evaluation evidence, not a native Linux build.

## Ownership boundary and simplification — 2026-11-17

Independent review reproduced overlapping ownership when a consumer added a
second `home.file` declaration for an editable target. The maintainer clarified
that ownership control covers configs-owned declarations; independently added
consumer declarations and other configuration managers are outside that scope.
No global assertion over final consumer compositions was added.

The provider fixture now inspects the Home Manager configurations reached by
all seven exported outputs, plus the Linux/Darwin desktop and Darwin XDG probes.
It compares actual selected
targets with other selected and enabled ordinary file targets. Eight small
positive/negative cases exercise identical paths, selected aliases, ordinary
placement still enabled on a selected entry, ancestor and descendant paths,
distinct sibling prefixes and disabled ordinary entries.
Together with the existing thirteen probes this produces thirty-one composition
checks, all passing. This prevents internal ownership regressions without
restricting external extensions through the reusable module.

Snapshots now retain only named `data`, `mode` and `link` fields. Unused inode
and modification-time values and tuple indexes were removed. Backup metadata
and byte-comparison behavior are unchanged; the twelve writer tests verify
regular-file mode and leaf-symlink metadata as well as existing backup/failure
cases. The six Zellij tests, real GC-root checks and native thirteen-file
temporary-home placement also pass. Existing on-change callbacks remain,
including Linux Ghostty's actual configuration validator.

Format, lint and the full tracked provider suite pass on aarch64-darwin; all
seven synthetic toplevels evaluate. The final checker-only case for ordinary
placement remaining enabled on a selected entry was covered by a fresh focused
runner (31 composition checks, 12 writer tests, 6 Zellij tests and real temporary-
home integration). Linux results are evaluation evidence. No commit, host
activation or unrelated-work cleanup was performed.

## Local source delivery — 2026-11-17

After the verification above, the maintainer explicitly authorized committing
the complete prepared feature and follow-up corrections in the current master
checkout. The delivery amendment in the spec records this authorization; no
publication, consumer adoption or host activation is included.
