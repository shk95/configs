# The provisional registry records what must become false

date: 2026-09-05
scope: repository
status: accepted
issue: #174
reopen-when: The registry holds more than five entries, or a second consumer needs an overdue notification workflow.

The repository enumerates what must remain true under `invariants/<scope>/`
and enforces it on every commit. Nothing enumerated what must eventually
become false. `flake.nix` calls its NixOS-WSL support an experiment with
exit criteria that exist nowhere but that comment, and the zellij overlay
#175 introduces will be the first patch this repository carries against an
unmerged upstream change. Each is temporary by intention and permanent by
neglect, because nothing holds a date against it.

As of 2026-09-05 such measures are registered under `provisional/<scope>/`,
one file per measure, and `tool/version-control/provisional` checks the
registration against the tree in both directions
(`INV repository/provisional-registry-coverage`). The registry deliberately
copies the invariant registry's shape — one file per entry, a parsed header,
a two-way tag check, fixtures in `tool/version-control/test` — because a
second registry that is read the same way costs a reader nothing new.

Time is the third axis, beside `exit-when` and `watch`. An entry carries a
`review-by` date at most 180 days after the later of `since` and its last
`reviewed:` line, and passing that date fails the check rather than warning.
An overdue entry fails only for a commit or a pull request in its own scope:
`AGENTS.md` forbids requiring an unrelated domain to pass in order to
validate the changed one, so an overdue Windows measure blocks Windows work
and is reported, not enforced, elsewhere.

Rejected on the same day:

- Recording such items only as open conditions in `docs/status.md`. That is
  where they were, and nothing enforced them.
- Issues only. An issue is not tied to the lines in the tree, so the measure
  and its record drift apart silently.
- A scheduled workflow that opens an issue when an entry goes overdue. A
  second generic mechanism for what is at present one instance, and it
  reports after the fact instead of at the commit that could have removed
  the measure.
- Failing every scope on an overdue entry. That blocks unrelated work and
  invites the bypass the registry exists to prevent.
- Warning only. Neglect is exactly what the registry is for.

The costs are accepted rather than hidden. The check is time-dependent, so
its result changes without the tree changing; that is the point, and it is
why the reference date is explicit. In CI the reference is the date of the
commit under test — `github.event.pull_request.head.sha` when there is one,
because a pull request's checkout is a synthetic merge commit whose date is
the run time — so re-running an old commit gives the same answer twice.
Under `pre-commit` the reference is today, which is the commit being made.
