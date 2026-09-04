# Windows Terminal's generated profiles are tolerated on read

date: 2026-08-30
scope: windows
status: accepted
source: 9f1e8ce:docs/status.md § Windows authority split

The read side of `files/terminal/settings.json` carries a tolerance the write
side does not. Windows Terminal materialises the profiles its fragment
extensions and dynamic generators discover back into `settings.json` so they can
be edited: on the maintainer's host it added a `Git Bash` profile carrying
`"source": "Git"` beside the two the payload declares, seconds after Apply had
overwritten the file. Under `ExactJson` that reserialisation was drift, so
post-apply validation threw before `Write-WinEnvState` ran and left a fully
deployed host unrecorded, and every later `-Check` reported the same drift on
any host that actually runs Windows Terminal. The entry now declares
`ExactJsonWithGeneratedProfiles`: everything outside `profiles.list` is still
compared exactly, each declared profile is matched by `guid` and must be equal,
and an undeclared entry is accepted only when it carries a non-empty `source`,
which is how Windows Terminal records that a generator produced it. An
undeclared profile without a `source` remains drift, because a person or another
tool wrote it. This does not reopen the whole-payload write decision
(`docs/decisions/feature-selection-closed.md`). Apply still writes the whole
payload, the payload still declares neither `Git Bash` nor
`disabledProfileSources`, and nothing merges the host's file on write; the
tolerance is a read-side statement about one application co-owning one file,
which is why it is a declared comparison mode on a single manifest entry that
the loader refuses on an entry whose parser is not `Json`. Declaring a mode no
earlier loader can honour is a manifest shape change, so this is a
`SchemaVersion` bump, 3 to 4, with `ProjectVersion` moving 0.4.0 to 0.5.0 the
way the schema 2 to 3 bump
(`docs/decisions/wslconfig-selected-by-windows-build.md`) moved 0.3.0 to 0.4.0.
Without it a manifest paired with an older module would load as schema 3 and
then fail at comparison time as an unknown mode, rather than saying the schema
is unsupported. **No `state.json` schema changes**: an applied host keeps its
recorded selection, sees a changed desired-state hash and a higher project
version, and redeploys.

